from __future__ import annotations

import pytest

from app.exceptions import DuplicateEntity, EntityNotPresent, Unauthorized
from app.schema.user import (
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)


@pytest.mark.asyncio
async def test_create_user_and_duplicate(user_svc):
    """Create succeeds, duplicate email raises."""
    req = UserCreateRequest(
        email="alice@example.com",
        first_name="Alice",
        last_name="A",
        password="pwd",
    )

    created = await user_svc.create_user(req)
    assert created.email == "alice@example.com"

    with pytest.raises(DuplicateEntity):
        await user_svc.create_user(req)


@pytest.mark.asyncio
async def test_read_user_by_creds(user_svc, user):
    """Read works by email and password."""
    user = await user_svc.read_user_by_email_and_password(
        user.email, "securepassword123"
    )

    assert user.id == user.id
    assert user.email == user.email


@pytest.mark.asyncio
async def test_read_user_by_id_and_email(user_svc):
    """Read works by id and email."""
    req = UserCreateRequest(
        email="bob@example.com",
        first_name="Bob",
        last_name="B",
        password="pwd",
    )

    bob = await user_svc.create_user(req)

    by_id = await user_svc.read_user(bob.id)
    assert by_id.email == "bob@example.com"

    by_email = await user_svc.read_user_by_email("bob@example.com")
    assert by_email.id == bob.id


@pytest.mark.asyncio
async def test_update_user_fields(user_svc):
    """First and last name update."""
    req = UserCreateRequest(
        email="carol@example.com",
        first_name="Carol",
        last_name="C",
        password="pwd",
    )

    carol = await user_svc.create_user(req)

    updated = await user_svc.update_user(
        carol.id,
        changes=UserUpdateRequest(first_name="Caroline", last_name="Chan"),
    )

    assert updated.first_name == "Caroline"
    assert updated.last_name == "Chan"


@pytest.mark.asyncio
async def test_update_user_not_found_raises(user_svc):
    """Non-existent id raises EntityNotPresent."""
    with pytest.raises(EntityNotPresent):
        await user_svc.update_user(999, changes=UserUpdateRequest(first_name="x"))


@pytest.mark.asyncio
async def test_update_password_success_and_not_found(user_svc):
    """Password update works; missing email raises."""
    req = UserCreateRequest(
        email="dave@example.com",
        first_name="Dave",
        last_name="D",
        password="pwd",
    )

    await user_svc.create_user(req)

    ok = await user_svc.update_user_password("dave@example.com", "newpwd")
    assert isinstance(ok, UserResponse)

    with pytest.raises(EntityNotPresent):
        await user_svc.update_user_password("absent@example.com", "pwd")


@pytest.mark.asyncio
async def test_verify_user_success_and_not_found(user_svc):
    """Verify flag set true; missing email raises."""
    req = UserCreateRequest(
        email="eve@example.com",
        first_name="Eve",
        last_name="E",
        password="pwd",
    )

    await user_svc.create_user(req)

    verified = await user_svc.update_user_verify("eve@example.com")
    assert verified.is_verified

    with pytest.raises(EntityNotPresent):
        await user_svc.update_user_verify("ghost@example.com")


@pytest.mark.asyncio
async def test_reset_password_by_token(monkeypatch, user_svc):
    """Valid token resets password; invalid token raises."""
    email = "frank@example.com"

    await user_svc.create_user(
        UserCreateRequest(
            email=email,
            first_name="Frank",
            last_name="F",
            password="pwd",
        )
    )

    monkeypatch.setattr(
        "app.service.user.decode_jwt_token",
        lambda token: {"sub": email},
    )

    ok = await user_svc.reset_password_by_token("valid", "newpwd")
    assert ok.email == email

    monkeypatch.setattr("app.service.user.decode_jwt_token", lambda token: {})

    with pytest.raises(Unauthorized):
        await user_svc.reset_password_by_token("broken", "x")


@pytest.mark.asyncio
async def test_verify_user_by_token(monkeypatch, user_svc):
    """Valid token verifies; invalid token raises."""
    email = "gina@example.com"

    await user_svc.create_user(
        UserCreateRequest(
            email=email,
            first_name="Gina",
            last_name="G",
            password="pwd",
        )
    )

    monkeypatch.setattr(
        "app.service.user.decode_jwt_token",
        lambda token: {"sub": email},
    )

    verified = await user_svc.verify_user_by_token("tok")
    assert verified.is_verified

    monkeypatch.setattr("app.service.user.decode_jwt_token", lambda token: {})

    with pytest.raises(Unauthorized):
        await user_svc.verify_user_by_token("bad")
