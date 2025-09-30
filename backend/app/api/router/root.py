from fastapi import APIRouter, status
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from sqlalchemy import text

from app.api.dependency.database import DbSessionDep
from app.config import ASSETS_PATH
from app.logger import logger

router = APIRouter(tags=["root"])


@router.get("/")
async def root() -> RedirectResponse:
    """Root endpoint"""
    return RedirectResponse(url="/api/openapi.json")


@router.get("/health")
async def health(session: DbSessionDep) -> JSONResponse:
    """Health check endpoint"""
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        return JSONResponse(
            {"status": "error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return JSONResponse(
        {"status": "ok"},
        status_code=status.HTTP_200_OK,
    )


@router.get("/rose", status_code=status.HTTP_200_OK)
async def rose() -> FileResponse:
    """Get ROSE"""
    logger.info("ROSE endpoint called")
    return FileResponse(ASSETS_PATH / "img/rose.jpg")
