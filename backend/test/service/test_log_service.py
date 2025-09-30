from __future__ import annotations

import logging
from asyncio import sleep

import pytest

from app.model.log import LogLevel
from app.schema.log import LogQueryRequest


@pytest.mark.asyncio
async def test_console_only_logging(log_svc, session, caplog):
    """Non-persisting call logs to stdout and writes no DB row."""
    caplog.set_level(logging.INFO, logger="database-logger")

    await log_svc.info("hello console")

    assert "hello console" in caplog.text
    assert await log_svc.get_logs(request=LogQueryRequest(limit=1)) == []


@pytest.mark.asyncio
async def test_persisting_error_row(log_svc, user):
    """Persist=True stores a row and returns LogResponse."""
    resp = await log_svc.error("boom", user_id=user.id, persist=True)
    log = await log_svc.read_log(resp.id)

    assert resp.message == "boom"
    assert log.level == LogLevel.ERROR
    assert log.user.id == user.id


@pytest.mark.asyncio
async def test_context_and_org_fields(log_svc, organization):
    """Context and organization_id propagate to DB."""
    ctx = {"action": "create"}

    resp = await log_svc.info(
        "org created", context=ctx, organization_id=organization.id, persist=True
    )

    log = await log_svc.read_log(resp.id)

    assert log.context == ctx
    assert log.organization.id == organization.id


@pytest.mark.asyncio
async def test_all_levels_persist(log_svc):
    """Each helper persists with the correct level."""
    r_debug = await log_svc.debug("d", persist=True)
    r_warn = await log_svc.warning("w", persist=True)
    r_crit = await log_svc.critical("c", persist=True)

    log_debug = await log_svc.read_log(r_debug.id)
    log_warn = await log_svc.read_log(r_warn.id)
    log_crit = await log_svc.read_log(r_crit.id)

    levels = {log_debug.level, log_warn.level, log_crit.level}

    assert LogLevel.DEBUG in levels
    assert LogLevel.WARNING in levels
    assert LogLevel.CRITICAL in levels


@pytest.mark.asyncio
async def test_read_logs_order_and_limit(log_svc):
    """read_logs returns newest first and respects limit."""
    await log_svc.info("first", persist=True)
    await sleep(1)
    await log_svc.info("second", persist=True)
    latest = await log_svc.get_logs(request=LogQueryRequest(limit=1))

    assert len(latest) == 1
    assert latest[0].message == "second"


@pytest.mark.asyncio
async def test_debug_filtered_by_logger_level(log_svc):
    """DEBUG row is not stored when logger level is INFO."""
    logging.getLogger("database-logger").setLevel(logging.INFO)

    await log_svc.debug("filtered", persist=True)

    entries = await log_svc.get_logs(request=LogQueryRequest(limit=1))
    assert entries == []


@pytest.mark.asyncio
async def test_debug_persisted_when_level_lowered(log_svc):
    """DEBUG row is stored when logger level is DEBUG."""
    logging.getLogger("database-logger").setLevel(logging.DEBUG)

    resp = await log_svc.debug("stored", persist=True)
    row = await log_svc.read_log(resp.id)

    assert row.level == LogLevel.DEBUG


@pytest.mark.asyncio
async def test_empty_context_nullable(log_svc):
    """Context is NULL when omitted."""
    resp = await log_svc.info("simple", persist=True)
    row = await log_svc.read_log(resp.id)

    assert row.context is None


@pytest.mark.asyncio
async def test_multiple_rows_and_read_logs(log_svc):
    """read_logs lists all rows in reverse-chronological order."""
    await log_svc.info("a", persist=True)
    await sleep(1)
    await log_svc.info("b", persist=True)
    await sleep(1)
    await log_svc.info("c", persist=True)

    rows = await log_svc.get_logs(request=LogQueryRequest(limit=3))
    assert [r.message for r in rows] == ["c", "b", "a"]
