from __future__ import annotations

import time

import jwt as pyjwt
import pytest

from app.exceptions import ExpiredEntity, Unauthorized
from app.util.jwt import create_jwt_token, decode_jwt_token


@pytest.mark.asyncio
async def test_create_and_decode_roundtrip():
    """Token created by helper round-trips via decode."""
    token = create_jwt_token("user-1")
    payload = decode_jwt_token(token)

    assert payload["sub"] == "user-1"
    assert "exp" in payload


@pytest.mark.asyncio
async def test_additional_claims_preserved():
    """Arbitrary claims survive the encode/decode cycle."""
    token = create_jwt_token("alice", {"role": "admin", "foo": "bar"})
    payload = decode_jwt_token(token)

    assert payload["role"] == "admin"
    assert payload["foo"] == "bar"


@pytest.mark.asyncio
async def test_custom_ttl_minutes_effect():
    """exp is ≈ now + ttl; allow 2 s jitter."""
    ttl_min = 1
    before = time.time()

    token = create_jwt_token("ttl-user", ttl_minutes=ttl_min)
    payload = decode_jwt_token(token)
    after = time.time()

    exp = float(payload["exp"])

    low = before + ttl_min * 60 - 2
    high = after + ttl_min * 60 + 2

    assert low <= exp <= high


@pytest.mark.asyncio
async def test_default_ttl_is_20_minutes():
    """Default ttl is 20 min (allow a little drift)."""
    token = create_jwt_token("default-ttl")
    payload = decode_jwt_token(token)

    exp_seconds = float(payload["exp"]) - time.time()
    assert 19 * 60 <= exp_seconds <= 21 * 60


@pytest.mark.asyncio
async def test_expired_token_raises_expired_entity():
    """Token whose exp is in the past raises ExpiredEntity."""
    token = create_jwt_token("old", ttl_minutes=-1)

    with pytest.raises(ExpiredEntity):
        token = decode_jwt_token(token)


@pytest.mark.asyncio
async def test_invalid_signature_raises_unauthorized():
    """Token signed with a different secret is rejected."""
    other_secret = "differentsecret"
    wrong_token = pyjwt.encode({"sub": "x"}, other_secret, algorithm="HS256")

    with pytest.raises(Unauthorized):
        decode_jwt_token(wrong_token)


@pytest.mark.asyncio
async def test_garbage_string_raises_unauthorized():
    """Random string that isn’t JWT triggers Unauthorized."""
    with pytest.raises(Unauthorized):
        decode_jwt_token("not-a-token")


@pytest.mark.asyncio
async def test_non_dict_payload_raises(monkeypatch):
    """decode_jwt_token must error if decoded payload isn’t a dict."""

    def fake_decode(token, secret, algorithms):
        return ["not", "a", "dict"]

    monkeypatch.setattr(pyjwt, "decode", fake_decode)

    with pytest.raises(Unauthorized):
        decode_jwt_token("whatever")


@pytest.mark.asyncio
async def test_sub_and_other_claims_are_str_cast():
    """decode_jwt_token always casts keys/values to str."""
    token = create_jwt_token("42", {"age": 30})
    payload = decode_jwt_token(token)

    assert payload["sub"] == "42"  # str, not int
    assert payload["age"] == "30"  # str, not int
