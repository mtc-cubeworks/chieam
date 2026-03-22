"""
Position Diagram Feature
========================
Single endpoint that provides complete diagram data for Cytoscape visualization.
"""
from pathlib import Path
from typing import Any, Optional
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user_from_token
from app.core.serialization import record_to_dict
from app.core.exceptions import ForbiddenError
from app.meta.registry import MetaRegistry
from app.models.attachment import Attachment
from app.services.rbac import RBACService
from app.infrastructure.database.repositories.entity_repository import get_entity_model

router = APIRouter(tags=["features"])


def _attachment_path_to_public_url(file_path: Optional[str]) -> Optional[str]:
    if not file_path:
        return None

    path = Path(file_path)
    upload_root = Path(settings.UPLOAD_DIR).resolve()

    try:
        relative_path = path.resolve().relative_to(upload_root)
    except ValueError:
        return None

    return f"/uploads/{relative_path.as_posix()}"


@router.get("/diagram/position", name="get_position_diagram")
async def get_position_diagram(
    location: Optional[str] = Query(None),
    system: Optional[str] = Query(None),
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Get complete diagram data for position visualization.
    
    Returns positions with display names and all position relations in a single response.
    Frontend can directly use this data without additional parsing.
    """
    user = await get_current_user_from_token(authorization, db)
    
    # Check permissions for both entities
    position_meta = MetaRegistry.get("position")
    relation_meta = MetaRegistry.get("position_relation")
    
    if not position_meta or not relation_meta:
        return {
            "status": "error",
            "message": "Position or position_relation entity not found"
        }
    
    if not await RBACService.check_permission_async(db, user, "position", "read"):
        raise ForbiddenError("You don't have permission to access positions")
    
    if not await RBACService.check_permission_async(db, user, "position_relation", "read"):
        raise ForbiddenError("You don't have permission to access position relations")
    
    # Get models
    position_model = get_entity_model("position")
    relation_model = get_entity_model("position_relation")
    
    if not position_model or not relation_model:
        return {
            "status": "error",
            "message": "Models not found"
        }
    
    # Fetch positions
    position_query = select(position_model)
    if location:
        position_query = position_query.where(position_model.location == location)
    if system:
        position_query = position_query.where(position_model.system == system)
    position_result = await db.execute(position_query.limit(500))
    positions = position_result.scalars().all()

    # Manually resolve linked names for asset_class, system, and location
    positions_dict = [record_to_dict(pos) for pos in positions]

    attachment_ids = {
        value
        for value in [
            *[pos.get("attach_img") for pos in positions_dict if pos.get("attach_img")],
        ]
        if value
    }

    # Get asset class names and icons
    asset_class_ids = {pos.get("asset_class") for pos in positions_dict if pos.get("asset_class")}
    asset_class_names = {}
    asset_class_icons = {}
    if asset_class_ids:
        asset_class_model = get_entity_model("asset_class")
        if asset_class_model:
            asset_result = await db.execute(select(asset_class_model).where(asset_class_model.id.in_(asset_class_ids)))
            asset_class_records = [record_to_dict(ac) for ac in asset_result.scalars()]
            attachment_ids.update(
                ac_dict.get("class_icon")
                for ac_dict in asset_class_records
                if ac_dict.get("class_icon")
            )
            attachment_result = await db.execute(select(Attachment).where(Attachment.id.in_(attachment_ids))) if attachment_ids else None
            attachment_url_map = {
                attachment.id: _attachment_path_to_public_url(attachment.file_path)
                for attachment in (attachment_result.scalars().all() if attachment_result else [])
            }
            for ac_dict in asset_class_records:
                asset_class_names[ac_dict["id"]] = ac_dict.get("name", ac_dict["id"])
                asset_class_icons[ac_dict["id"]] = attachment_url_map.get(ac_dict.get("class_icon"))
    else:
        attachment_url_map = {}

    # Get system names
    system_ids = {pos.get("system") for pos in positions_dict if pos.get("system")}
    system_names = {}
    if system_ids:
        system_model = get_entity_model("system")
        if system_model:
            system_result = await db.execute(select(system_model).where(system_model.id.in_(system_ids)))
            for sys in system_result.scalars():
                sys_dict = record_to_dict(sys)
                system_names[sys_dict["id"]] = sys_dict.get("name", sys_dict["id"])
    
    # Get location names
    location_ids = {pos.get("location") for pos in positions_dict if pos.get("location")}
    location_names = {}
    if location_ids:
        location_model = get_entity_model("location")
        if location_model:
            location_result = await db.execute(select(location_model).where(location_model.id.in_(location_ids)))
            for loc in location_result.scalars():
                loc_dict = record_to_dict(loc)
                location_names[loc_dict["id"]] = loc_dict.get("name", loc_dict["id"])

    # Update position data with resolved names
    for pos_dict in positions_dict:
        if pos_dict.get("asset_class") and pos_dict["asset_class"] in asset_class_names:
            pos_dict["asset_class_name"] = asset_class_names[pos_dict["asset_class"]]
        if pos_dict.get("system") and pos_dict["system"] in system_names:
            pos_dict["system_name"] = system_names[pos_dict["system"]]
        if pos_dict.get("location") and pos_dict["location"] in location_names:
            pos_dict["location_name"] = location_names[pos_dict["location"]]

        asset_class_icon = None
        if pos_dict.get("asset_class"):
            asset_class_icon = asset_class_icons.get(pos_dict["asset_class"])
        pos_dict["node_image"] = asset_class_icon or attachment_url_map.get(pos_dict.get("attach_img"))
    
    # Transform positions into Cytoscape nodes
    nodes = []
    for pos_dict in positions_dict:
        # Get display name from title_field
        display_name = ""
        if position_meta.title_field and position_meta.title_field in pos_dict:
            display_name = pos_dict[position_meta.title_field]
        else:
            display_name = pos_dict.get("id", "")
        
        # Build node label using resolved names (already available from _link_titles)
        asset_class_name = pos_dict.get("asset_class_name") or ""
        system_name = pos_dict.get("system_name") or ""
        asset = pos_dict.get("current_asset") or ""
        
        parts = []
        if asset_class_name: parts.append(f"[{asset_class_name}]")
        parts.append(display_name)
        if asset: parts.append(f"({asset})")
        
        label = " ".join(parts) or pos_dict.get("description") or pos_dict.get("id", "")
        
        nodes.append({
            "data": {
                "id": pos_dict.get("id", ""),
                "label": label,
                "asset": pos_dict.get("current_asset") or None,
                "assetClass": pos_dict.get("asset_class_name") or "",
                "system": pos_dict.get("system_name") or "",
                "systemId": pos_dict.get("system") or None,
                "location": pos_dict.get("location_name") or "",
                "locationId": pos_dict.get("location") or None,
                "image": pos_dict.get("node_image") or None,
            }
        })

    visible_node_ids = {node["data"]["id"] for node in nodes if node["data"].get("id")}

    # Fetch relations after nodes are known so edges can be trimmed to visible nodes only
    relation_result = await db.execute(select(relation_model).limit(500))
    relations = relation_result.scalars().all()

    # Transform relations into Cytoscape edges (only valid ones)
    edges = []
    for rel in relations:
        rel_dict = record_to_dict(rel)
        pos_a = rel_dict.get("position_a")
        pos_b = rel_dict.get("position_b")
        
        # Only include relations with both positions
        if pos_a and pos_b and pos_a in visible_node_ids and pos_b in visible_node_ids:
            edges.append({
                "data": {
                    "id": rel_dict.get("id", ""),
                    "source": pos_a,
                    "target": pos_b,
                    "label": rel_dict.get("position_relation_type") or ""
                }
            })
    
    system_filter_options = sorted(
        [
            {"label": name, "value": sys_id}
            for sys_id, name in system_names.items()
            if sys_id and name
        ],
        key=lambda item: item["label"],
    )
    location_filter_options = sorted(
        [
            {"label": name, "value": loc_id}
            for loc_id, name in location_names.items()
            if loc_id and name
        ],
        key=lambda item: item["label"],
    )

    return {
        "status": "success",
        "nodes": nodes,
        "edges": edges,
        "filters": {
            "location": location_filter_options,
            "system": system_filter_options,
            "selected": {
                "location": location,
                "system": system,
            },
        },
    }
