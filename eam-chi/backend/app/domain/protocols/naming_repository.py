"""
Naming Repository Protocol
============================
Abstract interface for ID generation / naming series.
"""
from typing import Any, Optional, Protocol, runtime_checkable


@runtime_checkable
class NamingRepositoryProtocol(Protocol):
    """Interface for naming series data access."""

    async def get_next_id(self, prefix: str, digits: int) -> str:
        """Generate the next sequential ID for a given prefix."""
        ...

    async def get_current_value(self, prefix: str) -> Optional[int]:
        """Get the current counter value for a prefix."""
        ...
