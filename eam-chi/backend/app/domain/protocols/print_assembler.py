"""
Print Data Assembler Protocol
==============================
Defines the contract for entity-specific print data assemblers.
Each assembler knows how to gather and shape data for its entity's print template.
"""
from typing import Protocol, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession


class PrintDataAssembler(Protocol):
    """Protocol for entity-specific print data assemblers."""

    entity_name: str

    async def assemble(
        self,
        record: dict,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """
        Assemble template context data from a raw record dict.
        Returns a dict of template variables ready for Jinja2 rendering.
        """
        ...

    def get_template_name(self) -> str:
        """Return the Jinja2 template filename (e.g. 'purchase_order.html')."""
        ...
