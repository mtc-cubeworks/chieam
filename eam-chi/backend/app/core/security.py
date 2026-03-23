from typing import Optional
from dataclasses import dataclass, field
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from jose import jwt, JWTError
import bcrypt
from app.core.database import get_db


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


@dataclass
class CurrentUser:
    id: str
    username: str
    roles: list[str]
    role_ids: list[str] = field(default_factory=list)
    is_superuser: bool = False
    employee_id: Optional[str] = None
    site_ids: list[str] = field(default_factory=list)
    department_ids: list[str] = field(default_factory=list)
    data_scope: str = "own"  # highest scope from roles: own < team < site < all


async def get_current_user_from_token(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> CurrentUser:
    """Extract user from JWT token."""
    from app.core.config import settings
    from app.models.auth import User
    
    # Default anonymous user with no permissions
    if not authorization or not authorization.startswith("Bearer "):
        return CurrentUser(
            id="anonymous",
            username="anonymous",
            roles=[],
            role_ids=[],
            is_superuser=False
        )
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("user_id")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        
        if db:
            result = await db.execute(
                select(User).where(User.username == username).options(selectinload(User.roles))
            )
            user = result.scalar_one_or_none()
            
            if user:
                # Determine highest data_scope from all user roles
                _SCOPE_RANK = {"own": 0, "team": 1, "site": 2, "all": 3}
                highest_scope = "own"
                for r in user.roles:
                    rs = getattr(r, "data_scope", "own") or "own"
                    if _SCOPE_RANK.get(rs, 0) > _SCOPE_RANK.get(highest_scope, 0):
                        highest_scope = rs

                # Load employee_id + site/department assignments
                employee_id = user.employee_id
                site_ids: list[str] = []
                department_ids: list[str] = []
                if employee_id:
                    try:
                        from app.modules.core_eam.models.employee_site import EmployeeSite
                        es_result = await db.execute(
                            select(EmployeeSite).where(EmployeeSite.employee == employee_id)
                        )
                        for es in es_result.scalars().all():
                            if es.site and es.site not in site_ids:
                                site_ids.append(es.site)
                            if es.department and es.department not in department_ids:
                                department_ids.append(es.department)
                    except Exception:
                        pass

                return CurrentUser(
                    id=user.id,
                    username=user.username,
                    roles=[r.name for r in user.roles],
                    role_ids=[r.id for r in user.roles],
                    is_superuser=user.is_superuser,
                    employee_id=employee_id,
                    site_ids=site_ids,
                    department_ids=department_ids,
                    data_scope=highest_scope,
                )
        
        # Fallback if no db session - use token data
        return CurrentUser(
            id=user_id or "unknown",
            username=username,
            roles=[],
            role_ids=[],
            is_superuser=False
        )
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def get_current_user() -> CurrentUser:
    """Deprecated: Returns anonymous user. Use get_current_user_from_token instead."""
    return CurrentUser(
        id="anonymous",
        username="anonymous",
        roles=[],
        role_ids=[],
        is_superuser=False
    )
