from __future__ import annotations

import json
from typing import Any, AsyncGenerator, Dict, Type

import aiofiles
from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    Response,
    UploadFile,
)
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from app.api.dependency.auth.user import AuthUserDep
from app.api.dependency.service import (
    MappingJobServiceDep,
)
from app.exceptions import BadRequest, EntityNotPresent
from app.model.job import MappingStatus
from app.schema.mapping.job import (
    CreateMappingExecutionRequest,
    CreateMappingJobRequest,
    HandleDynamicMappingJobRequest,
    MappingExecutionResponse,
    MappingJobResponse,
    UpdateMappingJobRequest,
)
from app.service.upload.handlers.csv import CSVStreamFileHandler
from app.service.upload.handlers.json import JSONStreamFileHandler
from app.service.upload.handlers.utils import StreamFileHandler
from app.service.upload.handlers.xml import XMLStreamFileHandler
from app.service.upload.upload import get_handler

router = APIRouter(prefix="/jobs", tags=["job"])


_HANDLER_MAP: Dict[str, Type[StreamFileHandler]] = {
    "json": JSONStreamFileHandler,
    "csv": CSVStreamFileHandler,
    "xml": XMLStreamFileHandler,
}


@router.post("", response_model=MappingJobResponse)
async def create_mapping_job(
    job_svc: MappingJobServiceDep,
    body: CreateMappingJobRequest,
    user: AuthUserDep,
) -> MappingJobResponse:
    user_id = body.user_id if body.user_id and user.is_admin else user.id
    job = await job_svc.create_mapping_job(req=body, user_id=user_id)
    return job


@router.get("/{job_id}", response_model=MappingJobResponse)
async def read_mapping_job(
    job_id: int,
    job_svc: MappingJobServiceDep,
    _: AuthUserDep,
) -> MappingJobResponse:
    """Get a mapping job by ID."""
    job = await job_svc.read_mapping_job(job_id=job_id)
    return job


@router.get("/user/{user_id}", response_model=list[MappingJobResponse])
async def read_jobs_by_user(
    user_id: int,
    svc: MappingJobServiceDep,
) -> list[MappingJobResponse]:
    """Get a mapping blueprint by user."""
    blueprints = await svc.read_jobs_for_user(user_id=user_id)

    return blueprints


@router.get("/organization/{org_id}", response_model=list[MappingJobResponse])
async def read_jobs_by_organization(
    org_id: int,
    svc: MappingJobServiceDep,
) -> list[MappingJobResponse]:
    """Get a mapping blueprint by user."""
    blueprints = await svc.read_jobs_for_organization(
        organization_id=org_id,
        include=("executions", "input_definition", "organization"),
    )

    return blueprints


@router.patch(
    "/{job_id}",
    response_model=MappingJobResponse,
)
async def update_mapping_job(
    job_id: int,
    body: UpdateMappingJobRequest,
    job_svc: MappingJobServiceDep,
    _: AuthUserDep,
) -> MappingJobResponse:
    """Update a mapping job by ID."""
    job = await job_svc.update_mapping_job(
        mapping_job_id=job_id,
        changes=body,
    )
    return job


@router.delete("/{job_id}")
async def delete_mapping_job(
    job_id: int,
    job_svc: MappingJobServiceDep,
    _: AuthUserDep,
) -> None:
    """Delete a mapping job by ID."""
    await job_svc.delete_mapping_job(mapping_job_id=job_id)


@router.post(
    "/{job_id}/execute/{source_mapping_id}",
    response_model=MappingExecutionResponse,
)
async def create_mapping_execution(
    job_id: int,
    source_mapping_id: int,
    file: UploadFile,
    tasks: BackgroundTasks,
    svc: MappingJobServiceDep,
) -> MappingExecutionResponse:
    # Convert to JSON
    if not file.content_type or not file.filename:
        raise BadRequest("File content type is required")

    job = await svc.read_mapping_job(job_id=job_id)

    if job.status != MappingStatus.RUNNING:
        await svc.set_mapping_job_status(
            job_id,
            status=MappingStatus.PENDING,
        )

    Handler = get_handler(file.content_type)

    if not Handler:
        raise BadRequest("Unsupported file type")

    handler = Handler(filename=file.filename, file_type=file.content_type)
    await handler.create_file()
    content = await file.read()
    await handler.write_data(content.decode("utf-8").splitlines())
    await handler.finalize()

    # Create mapping execution with service
    execution = await svc.create_mapping_execution(
        input_file_name=handler.file_info.path,
        original_file_name=file.filename,
        req=CreateMappingExecutionRequest(
            mapping_job_id=job_id,
            source_mapping_id=source_mapping_id,
            data_size_bytes=file.size,
            dynamic=False,
            json_data=None,
        ),
    )

    # Start the mapping execution in the background
    tasks.add_task(svc.execute_mapping_execution, execution.id)

    return execution


@router.get(
    "/{job_id}/execution/{execution_id}/download",
)
async def download_mapping_execution(
    # job_id: int,
    execution_id: int,
    svc: MappingJobServiceDep,
    _: AuthUserDep,
) -> FileResponse:
    execution = await svc.read_mapping_execution(mapping_execution_id=execution_id)

    if not execution.output_file_name:
        raise BadRequest("No output file available for this execution")

    # Return the file as a response
    return FileResponse(
        path=execution.output_file_name,
        filename=execution.output_file_name.split("/")[-1],
        media_type="application/octet-stream",
    )


@router.get("/{job_id}/download")
async def download_mapping_job(
    job_id: int,
    svc: MappingJobServiceDep,
    _: AuthUserDep,
) -> Response:
    job = await svc.read_mapping_job(
        job_id=job_id,
        include=("executions", "executions.source_mapping"),
    )

    assert job.executions is not None

    # keep only executions that have a real file on disk
    executions: list[MappingExecutionResponse] = [
        execution
        for execution in job.executions
        if execution.output_file_name is not None
    ]

    if not executions:
        raise EntityNotPresent("No execution produced a JSON output")

    total_bytes = sum(exe.data_size_bytes for exe in executions)
    filename = f"mapping_job_{job_id}_outputs.json"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    # small to medium payloads - keep in memory
    if total_bytes <= 1 * 1024 * 1024 * 50:  # 50 MB
        aggregated: Dict[str, Any] = {}

        for exe in executions:
            if exe.output_file_name is None:
                continue
            async with aiofiles.open(exe.output_file_name) as fh:
                aggregated[
                    getattr(exe.source_mapping, "target_path", f"execution_{exe.id}")
                ] = json.loads(await fh.read())

        return JSONResponse(aggregated, media_type="application/json", headers=headers)

    # huge payloads - stream the file
    async def stream() -> AsyncGenerator[bytes, None]:
        yield b"{"
        first = True

        for exe in executions:
            if exe.output_file_name is None:
                continue

            key = getattr(exe.source_mapping, "target_path", f"execution_{exe.id}")

            if not first:
                yield b","

            first = False
            yield json.dumps(key).encode()
            yield b":"

            async with aiofiles.open(exe.output_file_name, "rb") as fh:
                while chunk := await fh.read(64_000):
                    yield chunk

        yield b"}"

    return StreamingResponse(stream(), media_type="application/json", headers=headers)


@router.post("/dynamic/{uuid}/{source_mapping_id}")
async def handle_dynamic_mapping(
    uuid: str,
    source_mapping_id: int,
    body: HandleDynamicMappingJobRequest,
    svc: MappingJobServiceDep,
    _: AuthUserDep,
) -> object:
    """Handle a dynamic mapping request.

    Args:
        uuid: The UUID of the mapping job
        source_mapping_id: The ID of the source mapping to use
        data: The JSON data to map (max 1MB)
    """
    # Check data size
    data_size = len(json.dumps(body.data).encode("utf-8"))
    if data_size > 1024 * 1024:  # 1MB
        raise HTTPException(
            status_code=400,
            detail="Request body too large (max 1MB)",
        )

    result = await svc.handle_dynamic_mapping(
        uuid=uuid,
        source_mapping_id=source_mapping_id,
        data=body.data,
        forward=body.forward,
    )
    return result


# async def _stream_and_send(
#     *,
#     svc: MappingApplyServiceDep,
#     job_svc: MappingJobServiceDep,
#     blueprint_id: int,
#     input_definition_id: int,
#     payload: list[Any],
#     ws: WebSocket,
#     user_id: int,
#     organization_id: int | None = None,
#     job_id: int,
# ) -> None:
#     """
#     Feed `payload` through MappingApplyService and forward every
#     chunk to the websocket.
#     """
#     # Calculate data size
#     data_size = len(json.dumps(payload).encode("utf-8"))

#     # get the mapping job and update the data size and status
#     job = await job_svc.read_mapping_job(job_id)
#     # first check if the user has permission to update the job
#     if job.user_id != user_id or job.organization_id != organization_id:
#         raise PermissionError("User does not have permission to update this job")
#     await job_svc.update_mapping_job(
#         job.id,
#         {
#             "data_size_bytes": data_size,
#             "status": MappingStatus.RUNNING,
#             "started_at": datetime.now(),
#         },
#     )

#     try:
#         async for chunk in svc.apply_stream(
#             blueprint_id=blueprint_id,
#             input_definition_id=input_definition_id,
#             input_jsons=payload,
#         ):
#             await ws.send_json(chunk)
#             # Update job status based on chunk status
#             if chunk.get("status") == "failed":
#                 await job_svc.update_mapping_job(
#                     job.id,
#                     {"status": MappingStatus.FAILED, "completed_at": datetime.now()},
#                 )
#             elif chunk.get("status") == "success":
#                 await job_svc.update_mapping_job(
#                     job.id,
#                     {
#                         "status": MappingStatus.COMPLETED,
#                         "completed_at": datetime.now(),
#                     },
#                 )
#     except Exception as e:
#         # Update job status on error
#         await job_svc.update_mapping_job(
#             job.id,
#             UpdateMappingJobRequest.model_validate(
#                 {"status": MappingStatus.FAILED, "completed_at": datetime.now()}
#             ),
#         )
#         raise e


# @router.websocket("/schema_apply_ws")
# async def schema_apply_ws(
#     ws: WebSocket,
#     svc: MappingApplyServiceDep,
#     job_svc: MappingJobServiceDep,
#     user_id: int = Query(...),
#     organization_id: int | None = Query(None),
# ) -> None:
#     await ws.accept()
#     try:
#         raw = await ws.receive_json()
#         req = ApplyJSONAtaRequest(**raw)

#         await _stream_and_send(
#             svc=svc,
#             job_svc=job_svc,
#             job_id=req.job_id,
#             blueprint_id=req.blueprint_id,
#             input_definition_id=req.input_definition_id,
#             payload=req.input_jsons,
#             ws=ws,
#             user_id=user_id,
#             organization_id=organization_id,
#         )

#     except WebSocketDisconnect:
#         pass
#     except Exception as e:  # noqa: BLE001
#         await ws.send_json(
#             {"status": "fatal_error", "error": f"Failed to apply schema: {str(e)}"}
#         )
#     finally:
#         await ws.close()


# @router.websocket("/upload_and_map_file_ws")
# async def upload_and_map_file_ws(
#     ws: WebSocket,
#     svc: MappingApplyServiceDep,
#     job_svc: MappingJobServiceDep,
#     user_id: int = Query(...),
#     logger: LogServiceDep,
#     organization_id: int | None = Query(None),
# ) -> None:
#     """
#     1. client sends `{action:"start_upload", …}`
#     2. stream `{action:"send_entities", file_type, filename, entities:[…]}`
#        until `{action:"end_of_file"}`
#     3. for every completed file we push it through MappingApplyService
#        and stream the results back.
#     """
#     await ws.accept()
#     handlers: dict[str, StreamFileHandler] = {}

#     try:
#         # first message must be the metadata handshake
#         if (await ws.receive_json()).get("action") != "start_upload":
#             raise ValueError("first message must be start_upload")

#         while True:
#             msg = await ws.receive_json()
#             fname: str = ""

#             match msg["action"]:
#                 case "upload_complete":
#                     break

#                 case "send_entities":
#                     fname = msg["filename"]
#                     ftype: str = msg["file_type"]
#                     entities = msg["entities"]

#                     if fname not in handlers:
#                         Handler = _HANDLER_MAP.get(ftype)
#                         if not Handler:
#                             raise ValueError(f"unsupported file_type {ftype}")
#                         handler = Handler(filename=fname, file_type=ftype)
#                         handler.create_file()
#                         handlers[fname] = handler

#                     handlers[fname].write_data(entities)
#                     continue

#                 case "end_of_file":
#                     fname = msg["filename"]
#                     info = handlers[fname]
#                     info.finalize()

#                     await _stream_and_send(
#                         svc=svc,
#                         job_svc=job_svc,
#                         blueprint_id=msg["blueprint_id"],
#                         input_definition_id=msg["input_definition_id"],
#                         job_id=msg["job_id"],
#                         payload=_read_json(info.file_info.path),
#                         ws=ws,
#                         user_id=user_id,
#                         organization_id=organization_id,
#                     )
#                     continue

#                 case _:
#                     raise ValueError(f"unknown action {msg['action']}")

#     except Exception:
#         await logger.error(
#             "Error while using the websocket on /upload_and_map_file_ws",
#         )
#         await ws.send_json(
#             {"status": "error", "message": "Failed to upload and map file"}
#         )
#     finally:
#         await ws.close()


# def _read_json(path: str | Path) -> Any:
#     with open(path, "r", encoding="utf-8") as fp:
#         return json.load(fp)


# @router.websocket("/extract_schema_ws")
# async def extract_schema_ws(
#     ws: WebSocket,
#     logger: LogServiceDep,
# ) -> None:
#     """WebSocket endpoint for uploading files for extracting the schema."""
#     await ws.accept()
#     handlers: dict[str, StreamFileHandler] = {}

#     try:
#         # first message must be the metadata handshake
#         if (await ws.receive_json()).get("action") != "start_upload":
#             raise ValueError("first message must be start_upload")

#         while True:
#             msg = await ws.receive_json()

#             if msg["action"] == "upload_complete":
#                 break

#             if msg["action"] == "send_entities":
#                 fname = msg["filename"]
#                 ftype = msg["file_type"]
#                 entities = msg["entities"]

#                 if fname not in handlers:
#                     Handler = _HANDLER_MAP.get(ftype)
#                     if not Handler:
#                         raise ValueError(f"unsupported file_type {ftype}")
#                     handler = Handler(filename=fname, file_type=ftype)
#                     await handler.create_file()
#                     handlers[fname] = handler

#                 await handlers[fname].write_data(entities)

#         # Finalize all files and generate schemas
#         for handler in handlers.values():
#             await handler.finalize()
#             await handler.get_schema()

#         result = {
#             "status": "success",
#             "file_info": {
#                 fname: {
#                     "entities": handler.file_info.count,
#                     "schema": handler.file_info.extracted_schema,
#                 }
#                 for fname, handler in handlers.items()
#             },
#         }

#         await ws.send_json(result)

#     except Exception:
#         await logger.error(
#             "Error while using the websocket on /extract_schema_ws",
#         )
#         await ws.send_json(
#             {"status": "error", "message": "Failed to extract schema('s)"}
#         )
#     finally:
#         await ws.close()
