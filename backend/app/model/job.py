from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model.base import Base

if TYPE_CHECKING:
    from app.model.blueprint import InputDefinition, SourceMapping
    from app.model.organization import Organization
    from app.model.user import User


class MappingStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class MappingJobType(Enum):
    STATIC = "STATIC"
    DYNAMIC = "DYNAMIC"


class MappingJob(Base):
    __tablename__ = "mapping_jobs"
    __table_args__ = (
        Index("ix_mapping_jobs_user_id", "user_id"),
        Index("ix_mapping_jobs_organization_id", "organization_id"),
        Index("ix_mapping_jobs_uuid", "uuid"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[str] = mapped_column(
        String, unique=True, nullable=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    type: Mapped[MappingJobType] = mapped_column(SAEnum(MappingJobType), nullable=False)
    external_api_endpoint: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[MappingStatus] = mapped_column(
        SAEnum(MappingStatus), nullable=False, default=MappingStatus.PENDING
    )

    # The user who created the mapping job.
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="cascade"), nullable=False
    )
    user: Mapped[User] = relationship("User", back_populates="mapping_jobs")

    # The organization that the mapping job belongs to.
    organization_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("organizations.id", ondelete="cascade"), nullable=True
    )

    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="mapping_jobs"
    )

    # The input definition that the mapping job is associated with.
    input_definition_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("input_definitions.id", ondelete="cascade"), nullable=False
    )
    input_definition: Mapped["InputDefinition"] = relationship(
        back_populates="mapping_jobs"
    )

    # The executions that are associated with this mapping job.
    executions: Mapped[list["MappingJobExecution"]] = relationship(
        back_populates="mapping_job"
    )

    @property
    def mapping_duration_ms(self) -> int:
        if self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds() * 1000)
        return int((datetime.now() - self.created_at).total_seconds() * 1000)


class MappingJobExecution(Base):
    __tablename__ = "mapping_job_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    data_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[MappingStatus] = mapped_column(
        SAEnum(MappingStatus), nullable=False, default=MappingStatus.PENDING
    )
    attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0", default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Input and output file names for the mapping job execution.
    original_file_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    input_file_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    output_file_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # The JSON data that was used to run the mapping job execution.
    json_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Error message if the mapping job execution failed.
    error_message: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # The mapping job that this execution is associated with.
    mapping_job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("mapping_jobs.id", ondelete="cascade"), nullable=False
    )
    mapping_job: Mapped["MappingJob"] = relationship(
        "MappingJob", back_populates="executions"
    )

    # The source mapping that this execution is associated with.
    source_mapping_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("source_mappings.id", ondelete="cascade"), nullable=False
    )
    source_mapping: Mapped["SourceMapping"] = relationship(
        "SourceMapping", back_populates="executions"
    )
