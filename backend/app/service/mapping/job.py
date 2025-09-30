import asyncio
import json
import pathlib
import uuid
from datetime import datetime, timedelta
from typing import Any, Iterable
from urllib.parse import urlparse

import aiofiles
import aiohttp
import jsonata  # type: ignore
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import UPLOAD_DIR
from app.exceptions import BadRequest, EntityNotPresent
from app.model.blueprint import InputDefinition, MappingBlueprint
from app.model.job import MappingJob, MappingJobExecution, MappingJobType, MappingStatus
from app.schema.mapping.job import (
    CreateMappingExecutionRequest,
    CreateMappingJobRequest,
    MappingExecutionResponse,
    MappingJobResponse,
    UpdateMappingExecutionRequest,
    UpdateMappingJobRequest,
)
from app.service.base import build_load_options


class MappingJobService:
    """Business logic for mapping jobs"""

    JOB_REL_DEFAULT = ("executions", "input_definition")
    JOB_REL_MAP = {
        "executions": selectinload(MappingJob.executions).selectinload(
            MappingJobExecution.source_mapping
        ),
        "input_definition": selectinload(MappingJob.input_definition).options(
            selectinload(InputDefinition.source_mappings),
            selectinload(InputDefinition.blueprint),
        ),
        "user": selectinload(MappingJob.user),
        "organization": selectinload(MappingJob.organization),
    }

    def __init__(
        self,
        db: AsyncSession,
    ) -> None:
        self.db = db

    async def handle_dynamic_mapping(
        self,
        uuid: str,
        source_mapping_id: int,
        data: object,
        forward: bool = True,
    ) -> object:
        """Handle a dynamic mapping request.

        Args:
            uuid: The UUID of the mapping job
            source_mapping_id: The ID of the source mapping to use
            data: The JSON data to map
        """
        # Get the job by UUID
        job = await self.db.scalar(
            select(MappingJob)
            .where(MappingJob.uuid == uuid)
            .options(
                selectinload(MappingJob.input_definition).selectinload(
                    InputDefinition.source_mappings
                )
            )
        )

        if not job:
            raise EntityNotPresent(f"Mapping job with UUID {uuid} not found")

        # Validate source mapping
        source_mapping = next(
            (
                sm
                for sm in job.input_definition.source_mappings
                if sm.id == source_mapping_id
            ),
            None,
        )
        if not source_mapping:
            raise EntityNotPresent(
                f"Source mapping {source_mapping_id} not found in job's input definition"
            )

        # Create a new execution for this dynamic request
        execution_response = await self.create_mapping_execution(
            input_file_name=None,
            original_file_name=None,
            req=CreateMappingExecutionRequest(
                mapping_job_id=job.id,
                source_mapping_id=source_mapping_id,
                data_size_bytes=len(json.dumps(data).encode("utf-8")),
            ),
            dynamic=True,
            json_data=data,
        )

        # Get the actual execution object from the database
        execution = await self.db.scalar(
            select(MappingJobExecution)
            .where(MappingJobExecution.id == execution_response.id)
            .options(selectinload(MappingJobExecution.source_mapping))
        )

        if not execution:
            raise EntityNotPresent(
                f"Mapping execution with ID {execution_response.id} not found"
            )

        try:
            # Apply the mapping
            result = await self.apply_dynamic_mapping_execution(execution, data)

            # Update execution status
            await self.update_mapping_execution(
                execution.id,
                UpdateMappingExecutionRequest(
                    status=MappingStatus.SUCCESS,
                    completed_at=datetime.now(),
                ),
            )

            # If external API endpoint is configured, post the result
            if job.external_api_endpoint is None:
                raise BadRequest("External API endpoint is not configured for this job")

            if forward:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        job.external_api_endpoint,
                        json=result,
                        headers={"Content-Type": "application/json"},
                    ) as response:
                        if not response.ok:
                            raise BadRequest(
                                f"Failed to post results to external endpoint: {response.status}"
                            )

            return result

        except Exception as e:
            # Update execution status on error
            await self.update_mapping_execution(
                execution.id,
                UpdateMappingExecutionRequest(
                    status=MappingStatus.FAILED,
                    completed_at=datetime.now(),
                    error_message=str(e),
                ),
            )
            raise BadRequest(f"Failed to process dynamic mapping: {str(e)}")

    async def apply_dynamic_mapping_execution(
        self, execution: MappingJobExecution, data: object
    ) -> object:
        """Apply mapping to data and return the result."""
        mapping_expr = execution.source_mapping.jsonata_mapping

        # offload the CPU‐bound JSONata eval to a thread
        try:
            return await asyncio.to_thread(jsonata.Jsonata(mapping_expr).evaluate, data)
        except Exception as exc:
            raise BadRequest(f"JSONata evaluation failed: {exc}") from exc

    async def _validate_endpoint(self, endpoint: str) -> None:
        """Validate that an external API endpoint is reachable."""
        try:
            # Parse URL to validate format
            parsed = urlparse(endpoint)
            if not all([parsed.scheme, parsed.netloc]):
                raise BadRequest("Invalid URL format for external API endpoint")

            # Make HEAD request to check if endpoint is reachable
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.head(endpoint) as response:
                    if not response.ok:
                        raise BadRequest(
                            f"External API endpoint returned status {response.status}"
                        )
        except aiohttp.ClientError as e:
            raise BadRequest(f"External API endpoint is not reachable: {str(e)}")
        except Exception as e:
            raise BadRequest(f"Failed to validate external API endpoint: {str(e)}")

    async def create_mapping_job(
        self,
        *,
        user_id: int,
        req: CreateMappingJobRequest,
        include: Iterable[str] = JOB_REL_DEFAULT,
    ) -> MappingJobResponse:
        """Create a new mapping job."""
        blueprint = await self.db.scalar(
            select(MappingBlueprint)
            .join(InputDefinition, InputDefinition.blueprint_id == MappingBlueprint.id)
            .where(InputDefinition.id == req.input_definition_id)
        )

        if blueprint is None:
            raise EntityNotPresent(
                f"Input definition with ID {req.input_definition_id} not found"
            )

        # Validate dynamic job type requires external_api_endpoint
        if req.type == MappingJobType.DYNAMIC:
            if not req.external_api_endpoint:
                raise BadRequest(
                    "Dynamic mapping jobs require an external API endpoint"
                )
            await self._validate_endpoint(req.external_api_endpoint)

        # merge the request data with the user ID and status
        values = req.model_dump(by_alias=False) | {
            "user_id": user_id,
            "status": MappingStatus.PENDING,
            "organization_id": blueprint.organization_id,
        }

        # create the job
        options = build_load_options(include, self.JOB_REL_MAP)

        job = await self.db.scalar(
            insert(MappingJob).values(values).returning(MappingJob).options(*options)
        )

        if job is None:
            raise EntityNotPresent("Failed to create mapping job")

        return MappingJobResponse.model_validate(job.to_dict())

    async def read_mapping_job(
        self, job_id: int, *, include: Iterable[str] = JOB_REL_DEFAULT
    ) -> MappingJobResponse:
        """Retrieve a mapping job by ID."""
        options = build_load_options(include, self.JOB_REL_MAP)

        job = await self.db.scalar(
            select(MappingJob).where(MappingJob.id == job_id).options(*options)
        )

        if job is None:
            raise EntityNotPresent(f"Mapping job with ID {job_id} not found")

        return MappingJobResponse.model_validate(job.to_dict())

    async def read_jobs_for_user(
        self, user_id: int, *, include: Iterable[str] = JOB_REL_DEFAULT
    ) -> list[MappingJobResponse]:
        """Retrieve all mapping jobs for a user."""
        options = build_load_options(include, self.JOB_REL_MAP)

        jobs = await self.db.scalars(
            select(MappingJob).where(MappingJob.user_id == user_id).options(*options)
        )

        return [MappingJobResponse.model_validate(job.to_dict()) for job in jobs]

    async def read_jobs_for_organization(
        self, organization_id: int, *, include: Iterable[str] = JOB_REL_DEFAULT
    ) -> list[MappingJobResponse]:
        """Retrieve all mapping jobs for an organization, including the organization itself."""
        options = build_load_options(include, self.JOB_REL_MAP)

        jobs = await self.db.scalars(
            select(MappingJob)
            .where(MappingJob.organization_id == organization_id)
            .options(*options)
        )

        return [MappingJobResponse.model_validate(job.to_dict()) for job in jobs]

    async def update_mapping_job(
        self,
        mapping_job_id: int,
        *,
        changes: UpdateMappingJobRequest,
        include: Iterable[str] = JOB_REL_DEFAULT,
    ) -> MappingJobResponse:
        """Update a mapping job with provided data."""
        # Get current job to check type
        current_job = await self.db.scalar(
            select(MappingJob).where(MappingJob.id == mapping_job_id)
        )
        if current_job is None:
            raise EntityNotPresent(f"Mapping job with ID {mapping_job_id} not found")

        # Validate dynamic job type requires external_api_endpoint
        new_type = changes.type if changes.type is not None else current_job.type
        new_endpoint = (
            changes.external_api_endpoint
            if changes.external_api_endpoint is not None
            else current_job.external_api_endpoint
        )

        if new_type == MappingJobType.DYNAMIC:
            if not new_endpoint:
                raise BadRequest(
                    "Dynamic mapping jobs require an external API endpoint"
                )
            await self._validate_endpoint(new_endpoint)

        options = build_load_options(include, self.JOB_REL_MAP)
        values = changes.model_dump(by_alias=False, exclude_unset=True)

        job = await self.db.scalar(
            update(MappingJob)
            .where(MappingJob.id == mapping_job_id)
            .values(values)
            .returning(MappingJob)
            .options(*options)
        )

        if job is None:
            raise EntityNotPresent(f"Mapping job with ID {mapping_job_id} not found")

        return MappingJobResponse.model_validate(job.to_dict())

    async def set_mapping_job_status(
        self,
        mapping_job_id: int,
        *,
        status: MappingStatus,
    ) -> None:
        """Set the status of a mapping job."""
        job = await self.db.scalar(
            update(MappingJob)
            .where(MappingJob.id == mapping_job_id)
            .values(status=status)
            .returning(MappingJob)
        )

        if job is None:
            raise EntityNotPresent(f"Mapping job with ID {mapping_job_id} not found")

    async def delete_mapping_job(self, mapping_job_id: int) -> None:
        """Delete a mapping job by ID."""
        result = await self.db.execute(
            delete(MappingJob)
            .where(MappingJob.id == mapping_job_id)
            .returning(MappingJob.id)
        )
        deleted_id = result.scalar_one_or_none()

        if deleted_id is None:
            raise EntityNotPresent(f"Mapping job with ID {mapping_job_id} not found")

        await self.db.commit()

    async def apply_mapping_execution(
        self, execution: MappingJobExecution, data: dict[str, Any]
    ) -> pathlib.Path:
        mapping_expr = execution.source_mapping.jsonata_mapping

        # offload the CPU‐bound JSONata eval to a thread
        try:
            result = await asyncio.to_thread(
                jsonata.Jsonata(mapping_expr).evaluate, data
            )
        except Exception as exc:
            raise BadRequest(f"JSONata evaluation failed: {exc}") from exc

        output_file = UPLOAD_DIR / f"execution_{uuid.uuid4()}.json"

        # write file asynchronously
        try:
            async with aiofiles.open(output_file, "w", encoding="utf-8") as f:
                await f.write(json.dumps(result, ensure_ascii=False))
        except OSError as exc:
            raise BadRequest(f"Failed to write output file: {exc}") from exc

        return output_file

    async def execute_mapping_execution(self, execution_id: int) -> None:
        """
        Execute a mapping job: load input, apply mapping, update statuses atomically.

        Minimizes DB round-trips by using a transaction and operating on ORM objects.
        """
        async with self.db.begin():
            execution = await self.db.scalar(
                select(MappingJobExecution)
                .where(MappingJobExecution.id == execution_id)
                .options(
                    selectinload(MappingJobExecution.source_mapping),
                    selectinload(MappingJobExecution.mapping_job).selectinload(
                        MappingJob.executions
                    ),
                )
            )

            if execution is None:
                raise EntityNotPresent(f"Execution {execution_id} not found")
            execution.attempts += 1
            execution.started_at = datetime.now()
            execution.status = MappingStatus.RUNNING
            execution.mapping_job.status = MappingStatus.RUNNING

        try:
            if execution.input_file_name is None:
                raise BadRequest("No input file specified for execution")

            raw = pathlib.Path(execution.input_file_name).read_text(encoding="utf-8")
            output_path = await self.apply_mapping_execution(execution, json.loads(raw))

        except BadRequest as err:
            async with self.db.begin():
                execution.status = MappingStatus.FAILED
                execution.error_message = str(err)
                execution.completed_at = datetime.now()

                # fail parent job immediately
                execution.mapping_job.status = MappingStatus.FAILED
                execution.mapping_job.completed_at = datetime.now()
            return

        except Exception as err:
            async with self.db.begin():
                execution.status = MappingStatus.FAILED
                execution.error_message = f"Unexpected error: {err}"
                execution.completed_at = datetime.now()

                # fail parent job immediately
                execution.mapping_job.status = MappingStatus.FAILED
                execution.mapping_job.completed_at = datetime.now()
            return

        # success path: update execution and, if all children succeeded, the parent job
        async with self.db.begin():
            execution.status = MappingStatus.SUCCESS
            execution.output_file_name = str(output_path)
            execution.completed_at = datetime.now()

            job = execution.mapping_job

            if all(e.status == MappingStatus.SUCCESS for e in job.executions):
                job.status = MappingStatus.SUCCESS

            if all(e.completed_at is not None for e in job.executions):
                job.completed_at = datetime.now()

    async def create_mapping_execution(
        self,
        *,
        input_file_name: str | None,
        original_file_name: str | None,
        req: CreateMappingExecutionRequest,
        json_data: object | None = None,
        dynamic: bool = False,
    ) -> MappingExecutionResponse:
        """Create a new mapping execution."""
        if dynamic:
            values = req.model_dump(by_alias=False) | {
                "input_file_name": None,
                "original_file_name": None,
                "json_data": json_data,
                "status": MappingStatus.PENDING,
                "completed_at": None,
                "started_at": None,
                "error_message": None,
            }
        else:
            values = req.model_dump(by_alias=False) | {
                "input_file_name": input_file_name,
                "original_file_name": original_file_name,
                "status": MappingStatus.PENDING,
                "completed_at": None,
                "started_at": None,
                "error_message": None,
            }

        if not dynamic:
            # For non-dynamic executions, update existing if found
            existing = await self.db.scalar(
                update(MappingJobExecution)
                .where(
                    MappingJobExecution.mapping_job_id == req.mapping_job_id,
                    MappingJobExecution.source_mapping_id == req.source_mapping_id,
                )
                .values(values)
                .returning(MappingJobExecution)
                .options(
                    selectinload(MappingJobExecution.mapping_job),
                    selectinload(MappingJobExecution.source_mapping),
                )
            )

            if existing:
                # if the mapping execution already exists, update it
                job = await self.db.scalar(
                    select(MappingJob).where(MappingJob.id == existing.mapping_job_id)
                )

                if job is not None and job.status is not MappingStatus.PENDING:
                    job.status = MappingStatus.PENDING
                    await self.db.commit()

                return MappingExecutionResponse.model_validate(existing.to_dict())

        # Create new execution (either because it's dynamic or no existing execution found)
        mapping_execution = await self.db.scalar(
            insert(MappingJobExecution)
            .values(values)
            .returning(MappingJobExecution)
            .options(
                selectinload(MappingJobExecution.mapping_job),
                selectinload(MappingJobExecution.source_mapping),
            )
        )

        if mapping_execution is None:
            raise EntityNotPresent("Failed to create mapping execution")

        return MappingExecutionResponse.model_validate(mapping_execution.to_dict())

    async def update_mapping_execution(
        self, mapping_execution_id: int, changes: UpdateMappingExecutionRequest
    ) -> MappingExecutionResponse:
        """Update a mapping execution with provided data."""
        values = changes.model_dump(by_alias=False, exclude_unset=True)

        mapping_execution = await self.db.scalar(
            update(MappingJobExecution)
            .where(MappingJobExecution.id == mapping_execution_id)
            .values(values)
            .returning(MappingJobExecution)
            .options(
                selectinload(MappingJobExecution.mapping_job),
                selectinload(MappingJobExecution.source_mapping),
            )
        )

        if mapping_execution is None:
            raise EntityNotPresent(
                f"Mapping execution with ID {mapping_execution_id} not found"
            )

        return MappingExecutionResponse.model_validate(mapping_execution.to_dict())

    async def read_mapping_execution(
        self, mapping_execution_id: int
    ) -> MappingExecutionResponse:
        """Retrieve a mapping execution by ID."""
        mapping_execution = await self.db.scalar(
            select(MappingJobExecution)
            .where(MappingJobExecution.id == mapping_execution_id)
            .options(
                selectinload(MappingJobExecution.mapping_job),
                selectinload(MappingJobExecution.source_mapping),
            )
        )

        if mapping_execution is None:
            raise EntityNotPresent(
                f"Mapping execution with ID {mapping_execution_id} not found"
            )

        return MappingExecutionResponse.model_validate(mapping_execution.to_dict())

    async def read_executions_for_organization(
        self, organization_id: int, days: int | None = None
    ) -> list[MappingExecutionResponse]:
        """Retrieve all mapping executions for a specific organization, optionally filtering by recent days."""
        stmt = (
            select(MappingJobExecution)
            .join(MappingJob)
            .where(MappingJob.organization_id == organization_id)
            .options(
                selectinload(MappingJobExecution.mapping_job),
                selectinload(MappingJobExecution.source_mapping),
            )
        )

        if days is not None:
            since = datetime.now() - timedelta(days=days)
            stmt = stmt.where(MappingJobExecution.completed_at >= since)

        executions = await self.db.scalars(stmt)
        return [
            MappingExecutionResponse.model_validate(exec.to_dict())
            for exec in executions
        ]

    async def read_executions_for_user(
        self, user_id: int, days: int | None = None
    ) -> list[MappingExecutionResponse]:
        """Retrieve all mapping executions for a specific user, optionally filtering by recent days."""
        stmt = (
            select(MappingJobExecution)
            .join(MappingJob)
            .where(MappingJob.user_id == user_id)
            .options(
                selectinload(MappingJobExecution.mapping_job),
                selectinload(MappingJobExecution.source_mapping),
            )
        )

        if days is not None:
            since = datetime.now() - timedelta(days=days)
            stmt = stmt.where(MappingJobExecution.completed_at >= since)

        executions = await self.db.scalars(stmt)
        return [
            MappingExecutionResponse.model_validate(exec.to_dict())
            for exec in executions
        ]

    # async def read_mapping_execution(
    #     self, mapping_execution_id: int
    # ) -> MappingExecutionResponse:
    #     """Retrieve a mapping execution by ID."""
    #     result = await self.db.execute(
    #         select(MappingExecution).where(MappingExecution.id == mapping_execution_id)
    #     )
    #     mapping_execution = result.scalar_one_or_none()

    #     if mapping_execution is None:
    #         raise EntityNotPresent(
    #             f"Mapping execution with ID {mapping_execution_id} not found"
    #         )

    #     return MappingExecutionResponse.model_validate(mapping_execution.to_dict())

    # async def update_mapping_execution(
    #     self, mapping_execution_id: int, update_data: dict[str, str | datetime | int]
    # ) -> MappingExecutionResponse:
    #     """Update a mapping execution with provided data."""
    #     mapping_execution = await self.db.scalar(
    #         update(MappingExecution)
    #         .where(MappingExecution.id == mapping_execution_id)
    #         .values(**update_data)
    #         .returning(MappingExecution)
    #         .options(
    #             selectinload(MappingExecution.mapping_job),
    #             selectinload(MappingExecution.source_mapping),
    #         )
    #     )

    #     if mapping_execution is None:
    #         raise EntityNotPresent(
    #             f"Mapping execution with ID {mapping_execution_id} not found"
    #         )

    #     return MappingExecutionResponse.model_validate(mapping_execution.to_dict())
