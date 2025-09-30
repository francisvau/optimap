from fastapi import APIRouter, status

from app.api.dependency.auth.user import UserSelfOrAdminDep, VisibleUsersDep
from app.api.dependency.service import (
    MappingJobServiceDep,
    OrganizationServiceDep,
    UserServiceDep,
)
from app.schema.organization import OrganizationResponse
from app.schema.user import (
    UserCreateRequest,
    UserResponse,
    UserStatsResponse,
)

router = APIRouter(prefix="/users", tags=["user"])


@router.get("", response_model=list[UserResponse])
async def read_users(users: VisibleUsersDep) -> list[UserResponse]:
    """Return all users if admin; only self otherwise."""
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    svc: UserServiceDep,
) -> UserResponse:
    """Create a new user account."""
    return await svc.create_user(req=request)


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    svc: UserServiceDep,
) -> UserResponse:
    """Get a user by ID."""
    return await svc.read_user(user_id)


@router.get("/{user_id}/organizations", response_model=list[OrganizationResponse])
async def read_user_organizations(
    user_id: UserSelfOrAdminDep,
    svc: OrganizationServiceDep,
) -> list[OrganizationResponse]:
    """Return all organizations the user is a member of."""
    return await svc.read_organizations_for_user(user_id)


@router.get("/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: UserSelfOrAdminDep,
    svc: UserServiceDep,
    job_svc: MappingJobServiceDep,
) -> UserStatsResponse:
    """Return mapping statistics for a user."""
    return await svc.get_user_stats(user_id=user_id, job_svc=job_svc)
