"""Organizations"""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import INVITE_EXPIRATION_DAYS
from app.model.organization import Invite, Organization, OrganizationRole
from app.model.user import User
from app.schema.mapping.blueprint import CreateMappingRequest, JsonataGenerationResponse
from app.schema.organization import CreateOrganizationRequest
from app.service.session import AuthSessionService

"""Organizations"""


@pytest.fixture
async def organization(session) -> Organization:
    org = Organization(name="Test Org")
    session.add(org)
    await session.flush()
    return org


@pytest.fixture
async def invite(user, organization, session):
    inv = Invite(
        email=user.email,
        organization_id=organization.id,
        token="token",
        expires_at=datetime.now() + timedelta(days=INVITE_EXPIRATION_DAYS),
    )
    session.add(inv)
    await session.flush()
    return inv


@pytest.fixture
async def roles(organization, session):
    admin = OrganizationRole(name="admin", organization_id=organization.id)
    editor = OrganizationRole(name="editor", organization_id=organization.id)
    session.add_all([admin, editor])
    await session.flush()
    return admin, editor


@pytest.fixture
async def populated_org(user, other_user, roles, session, org_svc):
    org = await org_svc.create_organization(
        user_id=user.id, req=CreateOrganizationRequest(name="Rosé fanclub")
    )
    await org_svc.add_user_to_organization(
        org_id=org.id, user_id=other_user.id, role_id=roles[1].id
    )
    await session.commit()

    # Reload with relationships
    stmt = (
        select(Organization)
        .options(selectinload(Organization.users))
        .where(Organization.id == org.id)
    )
    result = await session.execute(stmt)
    return result.scalar_one()


"""Users"""


@pytest.fixture
async def user(session) -> User:
    u = User(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        password=User.hash_password("securepassword123"),
        is_verified=True,
    )
    session.add(u)
    await session.flush()
    return u


@pytest.fixture
async def blocked_user(session) -> User:
    u = User(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        password=User.hash_password("securepassword123"),
        is_verified=True,
        blocked_at=datetime.now(),
    )
    session.add(u)
    await session.flush()
    return u


@pytest.fixture
async def other_user(session) -> User:
    u = User(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        password=User.hash_password("securepassword123"),
        is_verified=True,
    )
    session.add(u)
    await session.flush()
    return u


@pytest.fixture
async def rose_user(session) -> User:
    u = User(
        first_name="Rosé",
        last_name="Park",
        email="rose@blackpink.com",
        password=User.hash_password("on_the_ground123"),
        is_verified=True,
    )
    session.add(u)
    await session.flush()
    return u


@pytest.fixture
async def session_id(user: User, session):
    sess_svc = AuthSessionService(session)
    s = await sess_svc.create_session(user_id=user.id)
    return s.session_id


@pytest.fixture
async def other_session_id(other_user: User, session):
    sess_svc = AuthSessionService(session)
    s = await sess_svc.create_session(user_id=other_user.id)
    return s.session_id


@pytest.fixture
async def admin(session):
    u = User(
        first_name="Admin",
        last_name="Root",
        email="root@example.com",
        password=User.hash_password("toor"),
        is_verified=True,
        is_admin=True,
    )
    session.add(u)
    await session.flush()
    return u


@pytest.fixture
async def admin_session_id(admin: User, session):
    sess_svc = AuthSessionService(session)
    s = await sess_svc.create_session(user_id=admin.id)
    return s.session_id


"""Blueprints"""


@pytest.fixture
def mapping_payload() -> dict:
    return CreateMappingRequest(
        name="Test Mapping",
        input_json_schema={"type": "object"},
        output_json_schema={"type": "object"},
        jsonata_mapping="$foo",
        model_id="jsonata",
    ).model_dump()


@pytest.fixture
def mapping_generation() -> dict:
    return JsonataGenerationResponse(
        mapping="$foo",
        retries=0,
        corrupted=False,
    ).model_dump()


"""Models"""


@pytest.fixture
def model_payload() -> dict:
    return {
        "id": "model_id",
        "name": "Model A",
        "tailor_prompt": ["Prompt A", "Prompt B"],
        "base_model": "gemini",
    }
