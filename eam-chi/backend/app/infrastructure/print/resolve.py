from __future__ import annotations

from typing import Optional
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.meta.registry import MetaRegistry
from app.services.document_query import get_doc


async def resolve_link_display(
    entity_name: str,
    record_id: Optional[str],
    db: AsyncSession,
) -> str:
    if not record_id:
        return ""

    meta = MetaRegistry.get(entity_name)
    title_field = meta.title_field if meta else "id"

    doc = await get_doc(entity_name, record_id, db, as_dict=True)
    if not doc:
        return str(record_id)

    value = doc.get(title_field)
    if value is None or value == "":
        return str(record_id)

    return str(value)


async def resolve_many_link_displays(
    entity_name: str,
    record_ids: list[str],
    db: AsyncSession,
) -> dict[str, str]:
    unique_ids = sorted({rid for rid in record_ids if rid})
    if not unique_ids:
        return {}

    results = await asyncio.gather(
        *[resolve_link_display(entity_name, rid, db) for rid in unique_ids],
        return_exceptions=True,
    )

    out: dict[str, str] = {}
    for rid, result in zip(unique_ids, results):
        if isinstance(result, Exception):
            out[rid] = rid
        else:
            out[rid] = result

    return out
