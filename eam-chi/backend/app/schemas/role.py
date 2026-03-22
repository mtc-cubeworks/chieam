from typing import Optional
from pydantic import BaseModel, Field, validator


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Role name is required")
    description: Optional[str] = Field(None, max_length=500, description="Role description")
    is_active: Optional[bool] = True

    @validator('name')
    def validate_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Role name is required")
        return v.strip()

    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            return v.strip()
        return v


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if v.strip() == "":
                raise ValueError("Role name cannot be empty")
            return v.strip()
        return v

    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            return v.strip()
        return v
