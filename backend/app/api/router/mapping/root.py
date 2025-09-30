from fastapi import APIRouter

from app.api.router.mapping import blueprint, job, schema

router = APIRouter(prefix="/mappings", tags=["mappings"])
router.include_router(blueprint.router)
router.include_router(job.router)
router.include_router(schema.router)
