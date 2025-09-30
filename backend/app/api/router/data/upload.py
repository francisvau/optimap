# import json

# from fastapi import APIRouter, File, Form, UploadFile, status

# from app.api.dependency.auth.user import AuthUserDep
# from app.api.dependency.service import UploadServiceDep
# from app.exceptions import BadRequest
# from app.schema.upload import (
#     BulkFileUploadRequest,
#     BulkFileUploadResponse,
# )

# router = APIRouter(tags=["upload"])


# @router.post(
#     "/upload",
#     response_model=BulkFileUploadResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# async def upload_files(
#     user: AuthUserDep,
#     svc: UploadServiceDep,
#     metadata: str = Form(...),
#     files: list[UploadFile] = File(...),
# ) -> BulkFileUploadResponse:
#     metadata_dict = json.loads(metadata)  # Parse the metadata string to a dictionary
#     request = BulkFileUploadRequest.model_validate(metadata_dict)

#     if not files or not request.files:
#         raise BadRequest("No files provided")

#     successful_uploads = []
#     failed_uploads = []

#     for file in files:
#         upload_response = await svc.handle_file_upload(
#             upload_file=file, user_id=user.id
#         )

#         if upload_response.upload_status == "success":
#             successful_uploads.append(upload_response)
#         else:
#             failed_uploads.append(upload_response)

#     return BulkFileUploadResponse(
#         successful_uploads=successful_uploads, failed_uploads=failed_uploads
#     )
