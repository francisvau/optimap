from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import pytest

from app.config import AUTH_SESSION_EXPIRE
from app.exceptions import EntityNotPresent
from app.schema.session import AuthSessionResponse


@pytest.mark.asyncio
async def test_create_new_session(session_svc, user):
    """First create_session returns a row that can be read back."""
    created = await session_svc.create_session(user_id=user.id)
    fetched = await session_svc.read_session(created.session_id)

    assert isinstance(created, AuthSessionResponse)
    assert fetched.session_id == created.session_id
    assert fetched.user_id == user.id


@pytest.mark.asyncio
async def test_extend_existing_session(session_svc, user):
    """Second create_session for same user keeps id and bumps expiry."""
    first = await session_svc.create_session(user_id=user.id)
    first_exp = first.expires_at

    second = await session_svc.create_session(user_id=user.id)
    stored = await session_svc.read_session(first.session_id)

    assert second.session_id == first.session_id
    assert stored.expires_at > first_exp


@pytest.mark.asyncio
async def test_new_session_expiry_window(session_svc, user):
    """expires_at is roughly AUTH_SESSION_EXPIRE hours in the future."""
    now = datetime.now()
    sess = await session_svc.create_session(user_id=user.id)
    delta = sess.expires_at - now
    expected = timedelta(hours=AUTH_SESSION_EXPIRE)

    assert expected - timedelta(minutes=1) <= delta <= expected + timedelta(minutes=1)


@pytest.mark.asyncio
async def test_multiple_users_get_distinct_sessions(session_svc, user, other_user):
    """Separate users receive independent session ids."""
    s1 = await session_svc.create_session(user_id=user.id)
    s2 = await session_svc.create_session(user_id=other_user.id)

    assert s1.session_id != s2.session_id
    assert s1.user_id == user.id
    assert s2.user_id == other_user.id


@pytest.mark.asyncio
async def test_update_session_expire(session_svc, user):
    """update_session_expire sets expiry to a past timestamp."""
    sess = await session_svc.create_session(user_id=user.id)

    await session_svc.update_session_expire(sess.session_id)
    expired = await session_svc.read_session(sess.session_id)

    assert expired.expires_at <= datetime.now()


@pytest.mark.asyncio
async def test_update_session_expire_unknown(session_svc):
    """Unknown session id in update_session_expire raises."""
    with pytest.raises(EntityNotPresent):
        await session_svc.update_session_expire(str(uuid.uuid4()))


@pytest.mark.asyncio
async def test_read_session_user_success(session_svc, user):
    """read_session_user returns the linked user."""
    sess = await session_svc.create_session(user_id=user.id)
    resp = await session_svc.read_session_user(sess.session_id)

    assert resp.id == user.id
    assert resp.email == user.email


@pytest.mark.asyncio
async def test_read_session_user_not_found(session_svc):
    """read_session_user with bad id raises."""
    with pytest.raises(EntityNotPresent):
        await session_svc.read_session_user("invalid-id")


@pytest.mark.asyncio
async def test_read_session_success(session_svc, user):
    """read_session fetches stored session."""
    sess = await session_svc.create_session(user_id=user.id)
    fetched = await session_svc.read_session(sess.session_id)

    assert fetched.session_id == sess.session_id
    assert fetched.user_id == user.id


@pytest.mark.asyncio
async def test_read_session_not_found(session_svc):
    """read_session with unknown id raises."""
    with pytest.raises(EntityNotPresent):
        await session_svc.read_session("missing-id")
