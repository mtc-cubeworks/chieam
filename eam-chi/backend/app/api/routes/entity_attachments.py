"""
Entity Attachment Routes
========================
Upload, list, download, and delete file attachments for any entity record.
"""
from typing import Optional
import os
import uuid
import mimetypes
from pathlib import Path
from jose import jwt, JWTError

from fastapi import APIRouter, Depends, Header, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user_from_token
from app.meta.registry import MetaRegistry
from app.models.attachment import Attachment
from app.schemas.base import ActionResponse
from app.services.rbac import RBACService

router = APIRouter(tags=["attachments"])

UPLOAD_ROOT = Path(settings.UPLOAD_DIR)


def _get_attachment_config(entity_name: str):
    """Get attachment config for an entity, returns None if not allowed."""
    meta = MetaRegistry.get(entity_name)
    if not meta:
        return None
    config = meta.attachment_config
    if not config or not config.allow_attachments:
        return None
    return config


async def _get_authorized_attachment(
    entity: str,
    record_id: str,
    attachment_id: str,
    authorization: Optional[str],
    token: Optional[str],
    db: AsyncSession,
):
    meta = MetaRegistry.get(entity)
    if not meta:
        return ActionResponse(status="error", message=f"Entity '{entity}' not found")

    auth_header = authorization
    if token and not auth_header:
        auth_header = f"Bearer {token}"

    user = await get_current_user_from_token(auth_header, db)
    if not await RBACService.check_permission_async(db, user, entity, "read"):
        return ActionResponse(status="error", message="Permission denied")

    result = await db.execute(
        select(Attachment).where(
            Attachment.id == attachment_id,
            Attachment.entity_name == entity,
            Attachment.record_id == record_id,
        )
    )
    attachment = result.scalar_one_or_none()
    if not attachment:
        return ActionResponse(status="error", message="Attachment not found")

    file_path = Path(attachment.file_path)
    if not file_path.exists():
        return ActionResponse(status="error", message="File not found on disk")

    return attachment, file_path


@router.get("/{entity}/{record_id}/attachments", name="list_attachments")
async def list_attachments(
    entity: str,
    record_id: str,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """List all attachments for a specific entity record."""
    meta = MetaRegistry.get(entity)
    if not meta:
        return ActionResponse(status="error", message=f"Entity '{entity}' not found")

    user = await get_current_user_from_token(authorization, db)
    if not await RBACService.check_permission_async(db, user, entity, "read"):
        return ActionResponse(status="error", message="Permission denied")

    result = await db.execute(
        select(Attachment)
        .where(Attachment.entity_name == entity, Attachment.record_id == record_id)
        .order_by(Attachment.created_at.desc())
    )
    attachments = result.scalars().all()

    data = [
        {
            "id": a.id,
            "file_name": a.original_name,
            "file_size": a.file_size,
            "mime_type": a.mime_type,
            "uploaded_by": a.uploaded_by,
            "description": a.description,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in attachments
    ]

    return {"status": "success", "data": data, "total": len(data)}


@router.post("/{entity}/{record_id}/attachments", name="upload_attachment")
async def upload_attachment(
    entity: str,
    record_id: str,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Upload a file attachment to a specific entity record."""
    meta = MetaRegistry.get(entity)
    if not meta:
        return ActionResponse(status="error", message=f"Entity '{entity}' not found")

    user = await get_current_user_from_token(authorization, db)
    if not await RBACService.check_permission_async(db, user, entity, "update"):
        return ActionResponse(status="error", message="Permission denied")

    config = _get_attachment_config(entity)
    if not config:
        return ActionResponse(
            status="error",
            message=f"Attachments are not enabled for '{meta.label}'"
        )

    # Check max attachments
    count_result = await db.execute(
        select(func.count())
        .select_from(Attachment)
        .where(Attachment.entity_name == entity, Attachment.record_id == record_id)
    )
    current_count = count_result.scalar() or 0
    if current_count >= config.max_attachments:
        return ActionResponse(
            status="error",
            message=f"Maximum attachments ({config.max_attachments}) reached"
        )

    # Validate file extension
    original_name = file.filename or "unnamed"
    ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    if config.allowed_extensions and ext not in config.allowed_extensions:
        return ActionResponse(
            status="error",
            message=f"File type '.{ext}' not allowed. Allowed: {', '.join(config.allowed_extensions)}"
        )

    # Read file content
    content = await file.read()
    file_size = len(content)

    # Validate file size
    max_bytes = config.max_file_size_mb * 1024 * 1024
    if file_size > max_bytes:
        return ActionResponse(
            status="error",
            message=f"File too large ({file_size / 1024 / 1024:.1f} MB). Max: {config.max_file_size_mb} MB"
        )

    # Save file to disk
    entity_dir = UPLOAD_ROOT / entity / record_id
    entity_dir.mkdir(parents=True, exist_ok=True)

    file_id = str(uuid.uuid4())
    stored_name = f"{file_id}.{ext}" if ext else file_id
    file_path = entity_dir / stored_name

    with open(file_path, "wb") as f:
        f.write(content)

    # Detect MIME type
    mime_type = file.content_type or mimetypes.guess_type(original_name)[0] or "application/octet-stream"

    # Save to database
    attachment = Attachment(
        id=file_id,
        entity_name=entity,
        record_id=record_id,
        file_name=stored_name,
        original_name=original_name,
        file_path=str(file_path),
        file_size=file_size,
        mime_type=mime_type,
        uploaded_by=user.username if user else None,
        description=description,
    )
    db.add(attachment)
    await db.commit()
    await db.refresh(attachment)

    return ActionResponse(
        status="success",
        message="File uploaded successfully",
        data={
            "id": attachment.id,
            "file_name": attachment.original_name,
            "file_size": attachment.file_size,
            "mime_type": attachment.mime_type,
            "uploaded_by": attachment.uploaded_by,
            "description": attachment.description,
            "created_at": attachment.created_at.isoformat() if attachment.created_at else None,
        },
    )


@router.get("/{entity}/{record_id}/attachments/{attachment_id}/download", name="download_attachment")
async def download_attachment(
    entity: str,
    record_id: str,
    attachment_id: str,
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Download a specific attachment file."""
    result = await _get_authorized_attachment(entity, record_id, attachment_id, authorization, token, db)
    if isinstance(result, ActionResponse):
        return result

    attachment, file_path = result

    return FileResponse(
        path=str(file_path),
        filename=attachment.original_name,
        media_type=attachment.mime_type or "application/octet-stream",
    )


@router.get("/{entity}/{record_id}/attachments/{attachment_id}/view", name="view_attachment")
async def view_attachment(
    entity: str,
    record_id: str,
    attachment_id: str,
    authorization: Optional[str] = Header(None),
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """View a specific attachment inline so browsers/canvas renderers can use it as an image resource."""
    result = await _get_authorized_attachment(entity, record_id, attachment_id, authorization, token, db)
    if isinstance(result, ActionResponse):
        return result

    attachment, file_path = result

    return FileResponse(
        path=str(file_path),
        filename=attachment.original_name,
        media_type=attachment.mime_type or "application/octet-stream",
        content_disposition_type="inline",
    )


@router.delete("/{entity}/{record_id}/attachments/{attachment_id}", name="delete_attachment")
async def delete_attachment(
    entity: str,
    record_id: str,
    attachment_id: str,
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Delete a specific attachment."""
    meta = MetaRegistry.get(entity)
    if not meta:
        return ActionResponse(status="error", message=f"Entity '{entity}' not found")

    user = await get_current_user_from_token(authorization, db)
    if not await RBACService.check_permission_async(db, user, entity, "update"):
        return ActionResponse(status="error", message="Permission denied")

    result = await db.execute(
        select(Attachment).where(
            Attachment.id == attachment_id,
            Attachment.entity_name == entity,
            Attachment.record_id == record_id,
        )
    )
    attachment = result.scalar_one_or_none()
    if not attachment:
        return ActionResponse(status="error", message="Attachment not found")

    # Delete file from disk
    file_path = Path(attachment.file_path)
    if file_path.exists():
        os.remove(file_path)

    # Delete from database
    await db.delete(attachment)
    await db.commit()

    return ActionResponse(status="success", message="Attachment deleted")
