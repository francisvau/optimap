# test/dependencie/test_auth.py

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import AUTH_KEY
from app.model.user import User
from app.util.jwt import create_jwt_token

# ---------------------------------------------------------------------------
#  Login & Logout
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_auth_unauthorized(async_client: AsyncClient) -> None:
    resp = await async_client.get("/auth/me")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_auth_authorized(async_client: AsyncClient, user: User) -> None:
    resp = await async_client.post(
        "/auth/login", json={"email": user.email, "password": "securepassword123"}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["email"] == user.email

    session_id = async_client.cookies.get(AUTH_KEY)
    assert session_id
    async_client.cookies.set(AUTH_KEY, session_id)

    me = await async_client.get("/auth/me")
    assert me.status_code == status.HTTP_200_OK
    assert me.json()["email"] == user.email


@pytest.mark.asyncio
async def test_auth_blocked_user(async_client: AsyncClient, blocked_user: User) -> None:
    """Blocked user cannot log in."""
    login_payload = {"email": blocked_user.email, "password": "securepassword123"}
    login_resp = await async_client.post("/auth/login", json=login_payload)

    assert login_resp.status_code == status.HTTP_403_FORBIDDEN
    assert login_resp.json().get("detail") == "Acount locked from application"
    assert async_client.cookies.get(AUTH_KEY) is None


@pytest.mark.asyncio
async def test_auth_logout(async_client: AsyncClient, user: User) -> None:
    await async_client.post(
        "/auth/login", json={"email": user.email, "password": "securepassword123"}
    )
    session_id = async_client.cookies.get(AUTH_KEY)
    async_client.cookies.set(AUTH_KEY, session_id)

    logout = await async_client.post("/auth/logout")
    assert logout.status_code == status.HTTP_204_NO_CONTENT
    assert AUTH_KEY not in logout.cookies

    async_client.cookies.delete(AUTH_KEY)
    assert (
        await async_client.get("/auth/me")
    ).status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_logout_without_cookie(async_client: AsyncClient):
    async_client.cookies.clear()
    resp = await async_client.post("/auth/logout")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    assert resp.json()["detail"] == "No session found"


# ---------------------------------------------------------------------------
#  Registration
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_auth_registration(async_client: AsyncClient) -> None:
    payload = {
        "email": "john.doe@test.com",
        "password": "securepassword123",
        "first_name": "John",
        "last_name": "Doe",
    }
    resp = await async_client.post("/auth/register", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_auth_duplicate_email_registration(
    async_client: AsyncClient, user: User
) -> None:
    payload = {
        "email": user.email,
        "password": "anotherpassword",
        "first_name": "Dummy2",
        "last_name": "Data2",
    }
    resp = await async_client.post("/auth/register", json=payload)
    assert resp.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_register_sets_cookie_and_email(async_client: AsyncClient):
    payload = {
        "email": "newuser@test.com",
        "password": "securepassword123",
        "first_name": "New",
        "last_name": "User",
    }
    resp = await async_client.post("/auth/register", json=payload)
    assert resp.status_code == status.HTTP_201_CREATED
    assert AUTH_KEY in async_client.cookies
    assert resp.json()["email"] == payload["email"]


# ---------------------------------------------------------------------------
#  Current-user
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_auth_get_current_user(async_client: AsyncClient, user: User) -> None:
    await async_client.post(
        "/auth/login", json={"email": user.email, "password": "securepassword123"}
    )
    session_id = async_client.cookies.get(AUTH_KEY)
    async_client.cookies.set(AUTH_KEY, session_id)
    me = await async_client.get("/auth/me")
    assert me.status_code == status.HTTP_200_OK
    assert me.json()["email"] == user.email


# ---------------------------------------------------------------------------
#  Forgot / reset password
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_auth_forgot_password(async_client: AsyncClient, user: User) -> None:
    resp = await async_client.post("/auth/forgot-password", json={"email": user.email})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["email"] == user.email


@pytest.mark.asyncio
async def test_auth_forgot_password_not_found(async_client: AsyncClient) -> None:
    resp = await async_client.post(
        "/auth/forgot-password", json={"email": "missing@test.com"}
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_forgot_password_returns_message(async_client: AsyncClient):
    payload = {
        "email": "forgotuser@test.com",
        "password": "securepassword123",
        "first_name": "Forgot",
        "last_name": "User",
    }
    await async_client.post("/auth/register", json=payload)
    resp = await async_client.post(
        "/auth/forgot-password", json={"email": payload["email"]}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["message"] == "Reset password e-mail sent successfully"


@pytest.mark.asyncio
async def test_auth_reset_password(async_client: AsyncClient, user: User) -> None:
    token = create_jwt_token(sub=user.email)
    resp = await async_client.post(
        "/auth/reset-password",
        json={"token": token, "new_password": "newsecurepassword123"},
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["email"] == user.email


@pytest.mark.asyncio
async def test_auth_reset_password_invalid_token(async_client: AsyncClient) -> None:
    resp = await async_client.post(
        "/auth/reset-password", json={"token": "bad", "new_password": "pw"}
    )
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_reset_password_response_message(async_client: AsyncClient):
    email = "resetme@test.com"
    await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "pw",
            "first_name": "Reset",
            "last_name": "Case",
        },
    )
    token = create_jwt_token(sub=email)
    resp = await async_client.post(
        "/auth/reset-password", json={"token": token, "new_password": "changed"}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["msg"] == "Password reset successfully"


# ---------------------------------------------------------------------------
#  Verification
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_auth_verify_request(async_client: AsyncClient, user: User) -> None:
    resp = await async_client.post("/auth/verify", json={"email": user.email})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["email"] == user.email


@pytest.mark.asyncio
async def test_auth_verify_request_not_found(async_client: AsyncClient) -> None:
    resp = await async_client.post("/auth/verify", json={"email": "missing@test.com"})
    assert resp.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_auth_verify_user(async_client: AsyncClient, user: User) -> None:
    token = create_jwt_token(sub=user.email)
    resp = await async_client.post(f"/auth/verify/{token}")
    assert resp.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_auth_verify_user_invalid_token(async_client: AsyncClient) -> None:
    resp = await async_client.post("/auth/verify/invalid")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_verify_token_sets_cookie_and_returns_204(async_client: AsyncClient):
    email = "verifyme@test.com"
    await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "pw",
            "first_name": "Verify",
            "last_name": "User",
        },
    )
    token = create_jwt_token(sub=email)
    resp = await async_client.post(f"/auth/verify/{token}")
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert AUTH_KEY in async_client.cookies


@pytest.mark.asyncio
async def test_verify_request_returns_message(async_client: AsyncClient):
    email = "verifymessage@test.com"
    await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "pw",
            "first_name": "Msg",
            "last_name": "Test",
        },
    )
    resp = await async_client.post("/auth/verify", json={"email": email})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["msg"] == "Verification e-mail sent successfully"


# ---------------------------------------------------------------------------
#  Profile update
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_auth_update_current_user(async_client: AsyncClient, user: User) -> None:
    await async_client.post(
        "/auth/login", json={"email": user.email, "password": "securepassword123"}
    )
    session_id = async_client.cookies.get(AUTH_KEY)
    async_client.cookies.set(AUTH_KEY, session_id)

    resp = await async_client.patch(
        "/auth/me", json={"first_name": "Updated", "last_name": "User"}
    )
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["firstName"] == "Updated"


# ---------------------------------------------------------------------------
#  Admin-only block/unblock
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_block_user_as_admin(
    async_client: AsyncClient, admin_session_id, user: User
) -> None:
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    resp = await async_client.post(f"/auth/block/{user.id}")
    assert resp.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_unblock_user_as_admin(
    async_client: AsyncClient, admin_session_id, user: User, session: AsyncSession
) -> None:
    async_client.cookies.set(AUTH_KEY, admin_session_id)
    await async_client.post(f"/auth/block/{user.id}")
    await session.refresh(user)

    resp = await async_client.post(f"/auth/unblock/{user.id}")
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    await session.refresh(user)
    assert user.blocked_at is None


@pytest.mark.asyncio
async def test_block_user_as_regular_user(
    async_client: AsyncClient, session_id, user: User, session: AsyncSession
) -> None:
    async_client.cookies.set(AUTH_KEY, session_id)
    resp = await async_client.post(f"/auth/block/{user.id}")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED
    await session.refresh(user)
    assert user.blocked_at is None


@pytest.mark.asyncio
async def test_unblock_user_as_regular_user(
    async_client: AsyncClient,
    session_id,
    admin_session_id,
    other_user: User,
    user: User,
) -> None:
    async_client.cookies.set(AUTH_KEY, session_id)
    resp = await async_client.post(f"/auth/unblock/{user.id}")
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    async_client.cookies.set(AUTH_KEY, admin_session_id)
    await async_client.post(f"/auth/block/{user.id}")

    async_client.cookies.set(AUTH_KEY, session_id)
    resp = await async_client.post(f"/auth/block/{other_user.id}")
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    async_client.cookies.set(AUTH_KEY, session_id)
    resp = await async_client.post(f"/auth/unblock/{other_user.id}")
    assert resp.status_code == status.HTTP_403_FORBIDDEN
