"""
Workflow Service
================
Database-driven workflow engine for state transitions.

Workflow configuration is stored in:
- workflow_states: Global state definitions
- workflow_actions: Global action definitions  
- workflows: Per-entity workflow configurations
- workflow_state_links: Links states to workflows
- workflow_transitions: Defines valid state transitions

Last Updated: 2026-01-29
"""
from typing import Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.security import CurrentUser
from app.models.workflow import (
    Workflow, WorkflowState, WorkflowAction, WorkflowStateLink, WorkflowTransition
)


class WorkflowService:
    """Workflow engine for state transitions (database-driven)."""
    
    # =========================================================================
    # WORKFLOW RETRIEVAL
    # =========================================================================
    
    @staticmethod
    async def get_workflow(db: AsyncSession, target_entity: str) -> Optional[Workflow]:
        """Get workflow configuration for an entity from database."""
        result = await db.execute(
            select(Workflow)
            .where(Workflow.target_entity == target_entity, Workflow.is_active == True)
            .options(
                selectinload(Workflow.state_links).selectinload(WorkflowStateLink.state),
                selectinload(Workflow.transitions).selectinload(WorkflowTransition.from_state),
                selectinload(Workflow.transitions).selectinload(WorkflowTransition.action_ref),
                selectinload(Workflow.transitions).selectinload(WorkflowTransition.to_state),
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_initial_state(db: AsyncSession, target_entity: str) -> Optional[str]:
        """Get the initial state slug for an entity's workflow."""
        workflow = await WorkflowService.get_workflow(db, target_entity)
        if not workflow:
            return None
        
        initial_link = next((sl for sl in workflow.state_links if sl.is_initial), None)
        return initial_link.state.slug if initial_link else None
    
    # =========================================================================
    # WORKFLOW METADATA (for frontend)
    # =========================================================================
    
    @staticmethod
    async def get_workflow_meta(db: AsyncSession, target_entity: str) -> Optional[dict]:
        """Get workflow metadata as dict for frontend."""
        workflow = await WorkflowService.get_workflow(db, target_entity)
        if not workflow:
            return None
        
        # Find initial state
        initial_link = next((sl for sl in workflow.state_links if sl.is_initial), None)
        initial_state_slug = initial_link.state.slug if initial_link else None
        
        # Build states dict
        states_dict = {}
        for sl in workflow.state_links:
            state = sl.state
            # Find actions available from this state
            actions = []
            for t in workflow.transitions:
                if t.from_state_id == state.id:
                    actions.append({
                        "slug": t.action_ref.slug,
                        "label": t.action_ref.label,
                        "target_slug": t.to_state.slug,
                        "target_label": t.to_state.label,
                    })
            states_dict[state.slug] = {
                "slug": state.slug,
                "label": state.label,
                "color": state.color,
                "is_initial": sl.is_initial,
                "actions": actions,
            }
        
        return {
            "enabled": True,
            "initial_state": initial_state_slug,
            "states": states_dict,
        }
    
    # =========================================================================
    # ACTIONS & TRANSITIONS
    # =========================================================================
    
    @staticmethod
    async def get_available_actions(
        db: AsyncSession,
        target_entity: str,
        current_state_slug: str,
        user: CurrentUser
    ) -> list[dict]:
        """Get available workflow actions for current state."""
        workflow = await WorkflowService.get_workflow(db, target_entity)
        if not workflow:
            return []
        
        user_roles = set(getattr(user, 'roles', []) or []) if user else set()
        is_super = 'SystemManager' in user_roles if user_roles else False
        
        available = []
        for t in workflow.transitions:
            if t.from_state.slug == current_state_slug:
                roles = t.get_allowed_roles()
                if roles and not is_super and not user_roles.intersection(roles):
                    continue
                available.append({
                    "action_slug": t.action_ref.slug,
                    "action_label": t.action_ref.label,
                    "to_state_slug": t.to_state.slug,
                    "to_state_label": t.to_state.label,
                })
        return available
    
    @staticmethod
    async def validate_transition(
        db: AsyncSession,
        target_entity: str,
        current_state_slug: str,
        action_slug: str,
        user: CurrentUser = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate if transition is allowed.
        
        Returns: (is_valid, target_state_slug, error_message)
        """
        workflow = await WorkflowService.get_workflow(db, target_entity)
        if not workflow:
            return False, None, f"No workflow found for entity '{target_entity}'"
        
        user_roles = set(getattr(user, 'roles', []) or []) if user else set()
        is_super = 'SystemManager' in user_roles if user_roles else False
        
        for t in workflow.transitions:
            if t.from_state.slug == current_state_slug and t.action_ref.slug == action_slug:
                roles = t.get_allowed_roles()
                if roles and not is_super and not user_roles.intersection(roles):
                    return False, None, f"You do not have permission to perform '{action_slug}'. Required roles: {', '.join(roles)}"
                return True, t.to_state.slug, None
        
        return False, None, f"Action '{action_slug}' not available from state '{current_state_slug}'"

    @staticmethod
    async def get_action_label(
        db: AsyncSession,
        target_entity: str,
        action_slug: str,
    ) -> Optional[str]:
        """
        Look up the human-readable label for a workflow action slug.
        Returns the label string or None if not found.
        """
        workflow = await WorkflowService.get_workflow(db, target_entity)
        if not workflow:
            return None
        for t in workflow.transitions:
            if t.action_ref.slug == action_slug:
                return t.action_ref.label
        return None


# Singleton instance for convenience
workflow_service = WorkflowService()

# Backwards compatibility alias
WorkflowDBService = WorkflowService
workflow_db_service = workflow_service
