from datetime import datetime
from typing import Any, Optional, Self

from pydantic import field_validator

from app.model.organization import OrganizationRole
from app.model.permission import Permission
from app.schema import BaseSchema
from app.schema.user import UserResponse


class CreateOrganizationRequest(BaseSchema):
    name: str
    address: Optional[str] = None
    system_prompt: Optional[str] = None
    branch: Optional[str] = None


class InviteRequest(BaseSchema):
    user_email: str
    role_id: int


class JoinRequest(BaseSchema):
    token: str


class JoinResponse(BaseSchema):
    organization_id: int


class OrganizationResponse(BaseSchema):
    id: int
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    system_prompt: Optional[str] = None
    model_ids: list[str]
    branch: Optional[str] = None


class InviteResponse(BaseSchema):
    id: int
    organization_id: int
    expires_at: datetime
    joined_at: datetime | None = None
    token: str
    email: Optional[str] = None


class PostInviteResponse(BaseSchema):
    id: int
    email: str
    organization_id: int
    expires_at: datetime
    joined_at: datetime | None = None


class OrganizationRoleValidators(BaseSchema):
    @field_validator("name", check_fields=False)
    def capitalize_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.capitalize()


class CreateOrganizationRoleRequest(OrganizationRoleValidators):
    name: str
    permissions: list[Permission]


class UpdateOrganizationRoleRequest(OrganizationRoleValidators):
    name: str | None = None
    permissions: list[Permission] | None = None


class OrganizationRoleResponse(BaseSchema):
    id: int
    name: str
    permissions: list[Permission]

    @field_validator("name", mode="before")
    @classmethod
    def lowercase_name(cls, v: str) -> str:
        return v.lower()

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> Self:
        if isinstance(obj, OrganizationRole):
            # Convert RolePermission[] to Permission[]
            obj = {
                "id": obj.id,
                "name": obj.name,
                "permissions": [rp.permission for rp in obj.permissions],
            }
        elif (
            isinstance(obj, dict)
            and obj.get("permissions")
            and isinstance(obj["permissions"][0], dict)
        ):
            # Defensive fallback: if dict has list of RolePermission-like dicts
            obj["permissions"] = [
                Permission(p["permission"]) for p in obj["permissions"]
            ]
        return super().model_validate(obj, **kwargs)


class OrganizationUserResponse(BaseSchema):
    id: int
    user_id: int
    organization_id: int
    created_at: datetime
    organization: Optional[OrganizationResponse] = None
    role: Optional[OrganizationRoleResponse] = None
    user: Optional[UserResponse] = None
    blacklisted_at: Optional[datetime] = None
    blacklisted_by_id: Optional[int] = None
    blacklist_reason: Optional[str] = None

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> Self:
        if isinstance(obj, dict):
            role_data = obj.get("role")
        else:
            role_data = getattr(obj, "role", None)
            obj = obj.__dict__

        if role_data is not None:
            obj["role"] = OrganizationRoleResponse.model_validate(role_data)

        return super().model_validate(obj, **kwargs)


class UpdateOrganizationRequest(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    system_prompt: Optional[str] = None
    branch: Optional[str] = None


class UpdateRoleRequest(BaseSchema):
    role_id: int


class UpdateOrganizationUserRequest(BaseSchema):
    blacklisted_at: Optional[datetime] = None
    blacklisted_by_id: Optional[int] = None
    blacklist_reason: Optional[str] = None


class OrganizationStatsResponse(BaseSchema):
    organization_id: int
    user_count: int
    role_count: int
    pending_invite_count: int
    admin_user_count: int
    bytes: float
    job_count: int
    min_execution_time: float
    max_execution_time: float
    avg_execution_time: float
