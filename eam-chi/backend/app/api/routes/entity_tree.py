"""
Entity tree endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.tree_service import TreeService
from app.infrastructure.database.repositories.tree import TreeRepository
from app.api.dependencies import get_db
from app.domain.exceptions import EntityNotFoundError
from app.meta.registry import MetaRegistry
from app.infrastructure.database.repositories.entity_repository import get_entity_model
from app.core.serialization import record_to_dict

router = APIRouter(tags=["tree"])


def get_tree_service(db_session=Depends(get_db)) -> TreeService:
    """Dependency injection for tree service."""
    tree_repository = TreeRepository(db_session)
    return TreeService(tree_repository)


@router.get("/{entity}/tree")
async def get_entity_tree(
    entity: str,
    parent_field: Optional[str] = Query(None, description="Override parent field"),
    title_field: Optional[str] = Query(None, description="Override title field"),
    tree_service: TreeService = Depends(get_tree_service)
) -> Dict[str, Any]:
    """Get tree data for an entity."""
    
    try:
        data = await tree_service.get_tree_data(
            entity_name=entity,
            parent_field=parent_field,
            title_field=title_field
        )
        
        return {
            "status": "success",
            "data": data,
            "count": len(data)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{entity}/hierarchy")
async def get_entity_hierarchy(
    entity: str,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Build a multi-level hierarchy tree starting from the given entity,
    following its `links` definitions recursively (max 5 levels deep).
    Returns a tree of: entity → linked children → their children, etc.
    Used for Organization → Sites → Departments cascade view.
    """
    try:
        meta = MetaRegistry.get(entity)
        if not meta:
            raise HTTPException(status_code=404, detail=f"Entity '{entity}' not found")

        async def build_level(entity_name: str, max_depth: int = 5) -> List[Dict[str, Any]]:
            if max_depth <= 0:
                return []
            level_meta = MetaRegistry.get(entity_name)
            if not level_meta:
                return []
            model = get_entity_model(entity_name)
            if not model:
                return []

            result = await db.execute(select(model))
            records = result.scalars().all()
            title_field = level_meta.title_field or "id"
            items = []
            for rec in records:
                d = record_to_dict(rec)
                item: Dict[str, Any] = {
                    "id": d.get("id"),
                    "label": d.get(title_field) or d.get("id"),
                    "entity": entity_name,
                    "data": d,
                    "children": [],
                }
                items.append(item)
            return items

        # Level 0: root entity
        root_items = await build_level(entity)

        # Follow links for each level
        links = meta.links or []
        for link_def in links:
            child_entity = link_def.entity if hasattr(link_def, "entity") else link_def.get("entity")
            fk_field = link_def.fk_field if hasattr(link_def, "fk_field") else link_def.get("fk_field")
            link_label = link_def.label if hasattr(link_def, "label") else link_def.get("label", child_entity)
            if not child_entity or not fk_field:
                continue

            child_meta = MetaRegistry.get(child_entity)
            if not child_meta:
                continue
            child_model = get_entity_model(child_entity)
            if not child_model:
                continue

            child_result = await db.execute(select(child_model))
            child_records = child_result.scalars().all()
            child_title = child_meta.title_field or "id"

            # Build a map: parent_id -> list of child items
            children_by_parent: Dict[str, List[Dict[str, Any]]] = {}
            child_items_flat: List[Dict[str, Any]] = []
            for rec in child_records:
                d = record_to_dict(rec)
                parent_id = d.get(fk_field)
                item: Dict[str, Any] = {
                    "id": d.get("id"),
                    "label": d.get(child_title) or d.get("id"),
                    "entity": child_entity,
                    "data": d,
                    "children": [],
                }
                child_items_flat.append(item)
                if parent_id:
                    children_by_parent.setdefault(parent_id, []).append(item)

            # Attach to root items
            for root_item in root_items:
                kids = children_by_parent.get(root_item["id"], [])
                root_item["children"].extend(kids)

            # Now follow grandchildren links for this child entity
            grandchild_links = child_meta.links or []
            for gc_link in grandchild_links:
                gc_entity = gc_link.entity if hasattr(gc_link, "entity") else gc_link.get("entity")
                gc_fk = gc_link.fk_field if hasattr(gc_link, "fk_field") else gc_link.get("fk_field")
                if not gc_entity or not gc_fk:
                    continue

                gc_meta = MetaRegistry.get(gc_entity)
                if not gc_meta:
                    continue
                gc_model = get_entity_model(gc_entity)
                if not gc_model:
                    continue

                gc_result = await db.execute(select(gc_model))
                gc_records = gc_result.scalars().all()
                gc_title = gc_meta.title_field or "id"

                gc_by_parent: Dict[str, List[Dict[str, Any]]] = {}
                for rec in gc_records:
                    d = record_to_dict(rec)
                    pid = d.get(gc_fk)
                    gc_item: Dict[str, Any] = {
                        "id": d.get("id"),
                        "label": d.get(gc_title) or d.get("id"),
                        "entity": gc_entity,
                        "data": d,
                        "children": [],
                    }
                    if pid:
                        gc_by_parent.setdefault(pid, []).append(gc_item)

                for child_item in child_items_flat:
                    gkids = gc_by_parent.get(child_item["id"], [])
                    child_item["children"].extend(gkids)

        return {
            "status": "success",
            "data": root_items,
            "count": len(root_items),
            "root_entity": entity,
            "root_label": meta.label or entity,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
