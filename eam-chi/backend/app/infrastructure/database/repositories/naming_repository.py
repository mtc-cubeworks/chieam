"""
Naming Repository
==================
Concrete SQLAlchemy implementation for naming series data access.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.core_eam.models.series import Series


class NamingRepository:
    """Concrete naming repository backed by SQLAlchemy."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_next_id(self, prefix: str, digits: int) -> str:
        result = await self.db.execute(select(Series).where(Series.name == prefix))
        series = result.scalar_one_or_none()

        if not series:
            series = Series(name=prefix, current=0)
            self.db.add(series)

        series.current += 1
        await self.db.flush()

        return f"{prefix}-{str(series.current).zfill(digits)}"

    async def get_current_value(self, prefix: str) -> Optional[int]:
        result = await self.db.execute(select(Series).where(Series.name == prefix))
        series = result.scalar_one_or_none()
        return series.current if series else None
