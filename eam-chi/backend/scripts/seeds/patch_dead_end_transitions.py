#!/usr/bin/env python3
"""
Patch workflow transitions to fix dead-end states.

Dead-end states are states with no outbound transitions, leaving documents
stranded. This script adds missing transitions (e.g., Reopen from Cancelled,
Revise from Rejected) without destroying existing transitions.

Safe to run multiple times — skips transitions that already exist.
"""
import asyncio
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import async_session_maker
from app.models.workflow import (
    Workflow,
    WorkflowAction,
    WorkflowState,
    WorkflowStateLink,
    WorkflowTransition,
    generate_slug,
)

# (target_entity, from_state_label, action_label, to_state_label)
DEAD_END_FIXES: list[tuple[str, str, str, str]] = [
    # Work Order: Cancelled → Reopen → Requested
    ("work_order", "Cancelled", "Reopen", "Requested"),
    # Work Order Activity: On Hold → Resume → In Progress
    ("work_order_activity", "On Hold", "Resume", "In Progress"),
    # Purchase Request: Rejected → Revise Purchase Request → Draft
    ("purchase_request", "Rejected", "Revise Purchase Request", "Draft"),
    # Purchase Order: Rejected → Reopen → Draft
    ("purchase_order", "Rejected", "Reopen", "Draft"),
    # Purchase Order: Cancelled → Reopen → Draft
    ("purchase_order", "Cancelled", "Reopen", "Draft"),
    # Purchase Order Line: Cancelled → Reopen → Draft
    ("purchase_order_line", "Cancelled", "Reopen", "Draft"),
    # Purchase Order Line: Rejected → Reopen → Draft
    ("purchase_order_line", "Rejected", "Reopen", "Draft"),
    # Purchase Request Line: Rejected → Reopen → Draft
    ("purchase_request_line", "Rejected", "Reopen", "Draft"),
    # RFQ: Cancelled → Reopen → Draft
    ("request_for_quotation", "Cancelled", "Reopen", "Draft"),
    # Stock Count: allow re-plan if needed
    # (Stock Count Closed is a true terminal — no fix needed)
    # Maintenance Request: Completed → Reopen → In Progress
    # (Already implemented in code — ensure transition exists)
    ("maintenance_request", "Completed", "Reopen", "In Progress"),
    # Item Issue: Issued → Reopen → Draft  (for corrections)
    ("item_issue", "Issued", "Reopen", "Draft"),
]


async def get_state(db, slug: str) -> WorkflowState | None:
    res = await db.execute(select(WorkflowState).where(WorkflowState.slug == slug))
    return res.scalar_one_or_none()


async def get_action(db, slug: str) -> WorkflowAction | None:
    res = await db.execute(select(WorkflowAction).where(WorkflowAction.slug == slug))
    return res.scalar_one_or_none()


async def patch_dead_ends() -> None:
    async with async_session_maker() as db:
        added = 0
        skipped = 0
        errors = []

        for entity, from_label, action_label, to_label in DEAD_END_FIXES:
            # Get the workflow for this entity
            res = await db.execute(
                select(Workflow)
                .where(Workflow.target_entity == entity, Workflow.is_active == True)
                .options(selectinload(Workflow.transitions))
            )
            wf = res.scalar_one_or_none()
            if not wf:
                errors.append(f"  ⚠ No active workflow for '{entity}'")
                continue

            from_st = await get_state(db, generate_slug(from_label))
            to_st = await get_state(db, generate_slug(to_label))
            act = await get_action(db, generate_slug(action_label))

            if not from_st:
                errors.append(f"  ⚠ State '{from_label}' not found for {entity}")
                continue
            if not to_st:
                errors.append(f"  ⚠ State '{to_label}' not found for {entity}")
                continue
            if not act:
                errors.append(f"  ⚠ Action '{action_label}' not found for {entity}")
                continue

            # Check if transition already exists
            existing = any(
                t.from_state_id == from_st.id
                and t.action_id == act.id
                and t.to_state_id == to_st.id
                for t in wf.transitions
            )
            if existing:
                skipped += 1
                continue

            # Ensure from_state is linked to this workflow
            res2 = await db.execute(
                select(WorkflowStateLink)
                .where(
                    WorkflowStateLink.workflow_id == wf.id,
                    WorkflowStateLink.state_id == from_st.id,
                )
            )
            if not res2.scalar_one_or_none():
                # Add the state link
                max_sort = max((t.sort_order or 0 for t in wf.transitions), default=0)
                db.add(WorkflowStateLink(
                    workflow_id=wf.id,
                    state_id=from_st.id,
                    is_initial=False,
                    sort_order=max_sort + 10,
                ))

            # Add transition
            max_sort = max((t.sort_order or 0 for t in wf.transitions), default=0)
            db.add(WorkflowTransition(
                workflow_id=wf.id,
                from_state_id=from_st.id,
                action_id=act.id,
                to_state_id=to_st.id,
                sort_order=max_sort + 1,
                allowed_roles=None,  # open to all roles
            ))
            added += 1
            print(f"  ✅ {entity}: {from_label} → [{action_label}] → {to_label}")

        await db.commit()

        print(f"\n{'='*50}")
        print(f"Dead-end fix results: {added} added, {skipped} already existed")
        if errors:
            print(f"Warnings ({len(errors)}):")
            for e in errors:
                print(e)


async def main() -> None:
    await patch_dead_ends()


if __name__ == "__main__":
    asyncio.run(main())
