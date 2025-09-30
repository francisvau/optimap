from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status

from app.api.dependency.auth.organization import (
    AuthAllOrganizationsDep,
    AuthOrganizationMemberDep,
    make_org_permissions_guard,
)
from app.api.dependency.auth.user import AuthUserDep
from app.api.dependency.mail import MailerDep
from app.api.dependency.service import (
    LogServiceDep,
    ModelServiceDep,
    OrganizationServiceDep,
    UserServiceDep,
)
from app.exceptions import BadRequest, DuplicateEntity, EntityNotPresent, Forbidden
from app.limiter import limiter
from app.model.log import LogAction
from app.model.organization import Organization
from app.model.permission import Permission
from app.schema.model import CreateModelRequest, ModelResponse, UpdateModelRequest
from app.schema.organization import (
    CreateOrganizationRequest,
    CreateOrganizationRoleRequest,
    InviteRequest,
    InviteResponse,
    JoinRequest,
    JoinResponse,
    OrganizationResponse,
    OrganizationRoleResponse,
    OrganizationStatsResponse,
    OrganizationUserResponse,
    PostInviteResponse,
    UpdateOrganizationRequest,
    UpdateOrganizationRoleRequest,
    UpdateOrganizationUserRequest,
    UpdateRoleRequest,
)
from app.util.mail import (
    send_invite_to_organization_mail,
    send_invite_to_unregistered_user_for_organization,
)

router = APIRouter(prefix="/organizations", tags=["organization"])

AuthManageUsersDep = Annotated[
    tuple[AuthUserDep, Organization],
    Depends(make_org_permissions_guard(Permission.MANAGE_USERS)),
]

AuthManageOrganizationDep = Annotated[
    tuple[AuthUserDep, Organization],
    Depends(make_org_permissions_guard(Permission.MANAGE_ORGANIZATION)),
]

"""Organization endpoints"""


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def create_organization(
    request: Request,
    body: CreateOrganizationRequest,
    svc: OrganizationServiceDep,
    user: AuthUserDep,
    logger: LogServiceDep,
) -> OrganizationResponse:
    """Create a new organization."""
    new_org_res = await svc.create_organization(req=body, user_id=user.id)

    await logger.info(
        f"User {user.id} is creating organization {new_org_res.id}",
        user_id=user.id,
        organization_id=new_org_res.id,
        persist=True,
        action=LogAction.CREATE,
    )

    return new_org_res


@router.get("", response_model=list[OrganizationResponse])
async def read_organizations(
    organizations: AuthAllOrganizationsDep,
) -> list[OrganizationResponse]:
    """List all organizations the user is a member of."""
    return organizations


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def read_organization(
    user_and_org: AuthOrganizationMemberDep,
    logger: LogServiceDep,
) -> OrganizationResponse:
    """Get details of a specific organization."""
    user, org = user_and_org

    await logger.info(
        f"User {user.id} is reading organization {org.id}",
        persist=False,
    )

    return org


@router.patch("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: int,
    update_data: UpdateOrganizationRequest,
    svc: OrganizationServiceDep,
    user_and_org: AuthManageOrganizationDep,
    logger: LogServiceDep,
) -> OrganizationResponse:
    """Update organization details."""
    user, organization = user_and_org

    await logger.info(
        f"User {user.id} is updating organization {organization.id}",
        user_id=user.id,
        organization_id=organization.id,
        persist=True,
        action=LogAction.UPDATE,
    )

    return await svc.update_organization(
        organization_id,
        changes=update_data,
    )


@router.delete("/{organization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    svc: OrganizationServiceDep,
    user_and_org: AuthManageOrganizationDep,
    logger: LogServiceDep,
) -> None:
    """Delete an organization."""
    user, organization = user_and_org

    await logger.info(
        f"User {user.id} is deleting organization {organization.id}",
        user_id=user.id,
        organization_id=organization.id,
        persist=True,
        action=LogAction.DELETE,
    )

    await svc.delete_organization(organization.id)


@router.get(
    "/{organization_id}/models",
    response_model=list[ModelResponse],
)
async def get_models_for_organization(
    model_svc: ModelServiceDep,
    user_org: AuthOrganizationMemberDep,
) -> list[ModelResponse]:
    """Get models for an organization."""
    # Check if the user is a member of the organization
    _, org = user_org

    # Get models for the organization
    models = await model_svc.get_models_by_ids(org.model_ids)
    return [ModelResponse.model_validate(model) for model in models]


@router.post("/{organization_id}/models", response_model=ModelResponse)
async def create_model_for_organization(
    organization_id: int,
    body: CreateModelRequest,
    model_svc: ModelServiceDep,
    org_svc: OrganizationServiceDep,
    _: AuthManageOrganizationDep,
) -> ModelResponse:
    """Create a new model for an organization."""
    model = await model_svc.create_model(req=body)
    await org_svc.attach_model_to_organization(
        model_id=model.id, org_id=organization_id
    )
    return ModelResponse.model_validate(model)


@router.patch(
    "/{organization_id}/models/{model_id}",
    response_model=ModelResponse,
)
async def update_model_for_organization(
    organization_id: int,
    model_id: str,
    body: UpdateModelRequest,
    model_svc: ModelServiceDep,
    org_svc: OrganizationServiceDep,
    _: AuthManageOrganizationDep,
) -> ModelResponse:
    """Update a model for an organization."""
    organization = await org_svc.read_organization(organization_id)

    if model_id not in organization.model_ids:
        raise Forbidden("Model not found in organization")

    model = await model_svc.update_model(model_id=model_id, req=body)

    return ModelResponse.model_validate(model)


@router.delete("/{organization_id}/models/{model_id}", status_code=204)
async def delete_model_for_organization(
    organization_id: int,
    model_id: str,
    model_svc: ModelServiceDep,
    org_svc: OrganizationServiceDep,
    _: AuthManageOrganizationDep,
) -> None:
    """Delete a model for an organization."""
    await org_svc.detach_model_from_organization(
        model_id=model_id, org_id=organization_id
    )

    await model_svc.delete_model(model_id=model_id)


@router.post(
    "/{organization_id}/invite",
    response_model=PostInviteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def invite_user(
    organization_id: int,
    request: InviteRequest,
    svc: OrganizationServiceDep,
    user_svc: UserServiceDep,
    mailer: MailerDep,
    user_and_org: AuthManageUsersDep,
    logger: LogServiceDep,
) -> PostInviteResponse:
    user, organization = user_and_org

    await logger.info(
        f"User {user.id} is inviting {request.user_email} to organization {organization.id}",
        user_id=user.id,
        organization_id=organization.id,
        persist=True,
        action=LogAction.CREATE,
        context={
            "invited_user_email": request.user_email,
        },
    )

    # Create the invite.
    try:
        invite = await svc.create_organization_invite(
            user_email=request.user_email,
            org_id=organization_id,
            role_id=request.role_id,
        )
    except DuplicateEntity:
        await logger.warning(
            f"User {user.id} tried to invite {request.user_email} to organization {organization.id} but an invite already exists",
            user_id=user.id,
            organization_id=organization.id,
            persist=True,
            action=LogAction.CREATE,
            context={
                "invited_user_email": request.user_email,
            },
        )

        raise DuplicateEntity("An invitation has already been sent to this email.")

    # Send the invite email.
    role = await svc.read_organization_role(request.role_id, org_id=organization_id)
    try:
        user = await user_svc.read_user_by_email(request.user_email)

        await send_invite_to_organization_mail(
            user, role.name, invite.token, organization, mailer
        )
    except EntityNotPresent as e:
        if str(e) != "User not found":
            raise e
        await send_invite_to_unregistered_user_for_organization(
            request.user_email,
            role.name,
            invite.token,
            organization,
            mailer,
        )

    return PostInviteResponse.model_validate(invite)


@router.post("/join", response_model=JoinResponse, status_code=status.HTTP_201_CREATED)
async def join_organization(
    request: JoinRequest,
    svc: OrganizationServiceDep,
    user: AuthUserDep,
    logger: LogServiceDep,
) -> JoinResponse:
    """Join an organization using an invite token."""
    invite = await svc.read_organization_invite_by_token(request.token)
    await svc.accept_organization_invite(invite_id=invite.id)
    await logger.info(
        f"User {user.id} joined organization {invite.organization_id} using token {request.token}",
        user_id=user.id,
        organization_id=invite.organization_id,
        persist=True,
        action=LogAction.CREATE,
    )
    return JoinResponse(organization_id=invite.organization_id)


@router.get("/{organization_id}/pending-invites", response_model=list[InviteResponse])
async def read_pending_invites(
    organization_id: int,
    svc: OrganizationServiceDep,
    _: AuthManageUsersDep,
) -> list[InviteResponse]:
    """List pending invites for an organization."""
    return await svc.read_pending_invites(organization_id)


@router.get("/{organization_id}/users", response_model=list[OrganizationUserResponse])
async def read_organization_users(
    organization_id: int,
    svc: OrganizationServiceDep,
    _: AuthManageUsersDep,
) -> list[OrganizationUserResponse]:
    """List all users in an organization."""
    return await svc.read_organization_users(organization_id)


@router.get(
    "/{organization_id}/users/{user_id}", response_model=OrganizationUserResponse
)
async def read_organization_user(
    organization_id: int,
    user_id: int,
    svc: OrganizationServiceDep,
    _: AuthManageUsersDep,
) -> OrganizationUserResponse:
    """Get details of a specific user in an organization."""
    return await svc.read_organization_user(org_id=organization_id, user_id=user_id)


@router.delete(
    "/{organization_id}/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_organization_user(
    organization_id: int,
    user_id: int,
    svc: OrganizationServiceDep,
    logger: LogServiceDep,
    user_and_org: AuthManageUsersDep,
) -> None:
    """Remove a user from an organization."""
    user, _ = user_and_org
    if user_id == user.id:
        raise BadRequest("Cannot remove the yourself from the organization")

    await svc.delete_organization_user(org_id=organization_id, user_id=user_id)
    await logger.info(
        f"User {user_id} removed from organization {organization_id}",
        user_id=user_id,
        organization_id=organization_id,
        persist=True,
        action=LogAction.DELETE,
    )


@router.post(
    "/{organization_id}/users/{user_id}/blacklist",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def blacklist_organization_user(
    organization_id: int,
    user_id: int,
    req: UpdateOrganizationUserRequest,
    svc: OrganizationServiceDep,
    user_and_org: AuthManageUsersDep,
) -> None:
    """Blacklist a user in an organization."""
    user, _ = user_and_org
    if user.id == user_id:
        raise BadRequest("Cannot blacklist yourself from the organization")

    await svc.update_organization_user(
        org_id=organization_id,
        user_id=user_id,
        changes=req.model_copy(
            update={
                "blacklisted_at": datetime.now(),
                "blacklisted_by_id": user.id,
            }
        ),
    )


@router.post(
    "/{organization_id}/users/{user_id}/whitelist",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def whitelist_organization_user(
    organization_id: int,
    user_id: int,
    svc: OrganizationServiceDep,
    _: AuthManageUsersDep,
) -> None:
    """whitelist a user"""
    await svc.update_organization_user(
        org_id=organization_id,
        user_id=user_id,
        changes=UpdateOrganizationUserRequest(
            blacklisted_at=None,
            blacklisted_by_id=None,
            blacklist_reason=None,
        ),
    )


@router.patch(
    "/{organization_id}/users/{user_id}",
    response_model=OrganizationUserResponse,
)
async def update_user_role(
    organization_id: int,
    user_id: int,
    request: UpdateRoleRequest,
    svc: OrganizationServiceDep,
    user_and_org: AuthManageUsersDep,
) -> OrganizationUserResponse:
    """Update a user's roles in an organization."""
    user, _ = user_and_org
    if user.id == user_id:
        raise BadRequest("Cannot update your own role in the organization")
    return await svc.update_organization_user_role(
        user_id=user_id,
        org_id=organization_id,
        role_id=request.role_id,
    )


@router.post(
    "/{organization_id}/roles",
    response_model=OrganizationRoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organization_role(
    organization_id: int,
    request: CreateOrganizationRoleRequest,
    svc: OrganizationServiceDep,
    _: AuthManageUsersDep,
) -> OrganizationRoleResponse:
    """Create a new role in an organization."""
    return await svc.create_organization_role(
        org_id=organization_id,
        req=request,
    )


@router.patch(
    "/{organization_id}/roles/{role_id}",
    response_model=OrganizationRoleResponse,
)
async def update_organization_role(
    organization_id: int,
    role_id: int,
    request: UpdateOrganizationRoleRequest,
    svc: OrganizationServiceDep,
    user_and_org: AuthManageUsersDep,
) -> OrganizationRoleResponse:
    """Update an existing role in an organization."""
    user, _ = user_and_org
    org_user = await svc.read_organization_user(org_id=organization_id, user_id=user.id)
    if org_user and org_user.role and org_user.role.id == role_id:
        raise BadRequest("Cannot update your own role in the organization")

    return await svc.update_organization_role(
        role_id,
        org_id=organization_id,
        changes=request,
    )


@router.get(
    "/{organization_id}/roles",
    response_model=list[OrganizationRoleResponse],
)
async def read_organization_roles(
    organization_id: int,
    svc: OrganizationServiceDep,
    _: AuthManageUsersDep,
) -> list[OrganizationRoleResponse]:
    """List all roles in an organization."""
    return await svc.read_organization_roles(organization_id)


@router.delete(
    "/{organization_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_organization_role(
    organization_id: int,
    role_id: int,
    svc: OrganizationServiceDep,
    _: AuthManageUsersDep,
) -> None:
    """Delete a role from an organization."""
    return await svc.delete_organization_role(role_id=role_id, org_id=organization_id)


@router.get(
    "/{organization_id}/stats",
    response_model=OrganizationStatsResponse,
)
async def get_organization_stats(
    organization_id: int, svc: OrganizationServiceDep, _: AuthManageOrganizationDep
) -> OrganizationStatsResponse:
    """Get statistics for an organization."""
    return await svc.get_organization_stats(org_id=organization_id)
