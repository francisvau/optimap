import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model.base import Base
from app.schema.mapping.schema import Schema

if TYPE_CHECKING:
    from app.model.job import MappingJob, MappingJobExecution
    from app.model.organization import Organization
    from app.model.user import User


class SourceMapping(Base):
    __tablename__ = "source_mappings"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    file_type: Mapped[Optional[str]] = mapped_column(default=None)
    input_json_schema: Mapped[Schema] = mapped_column(JSON)
    jsonata_mapping: Mapped[Optional[str]] = mapped_column(default=None)
    output_json_schema: Mapped[Schema] = mapped_column(JSON)
    model_id: Mapped[Optional[str]] = mapped_column(default=None)
    target_path: Mapped[str] = mapped_column(server_default="")

    # The input definition associated with this source mapping.
    input_definition_id: Mapped[int] = mapped_column(
        ForeignKey("input_definitions.id", ondelete="CASCADE")
    )

    input_definition: Mapped["InputDefinition"] = relationship(
        back_populates="source_mappings"
    )

    # The mapping executions associated with this source mapping.
    executions: Mapped[list["MappingJobExecution"]] = relationship(
        back_populates="source_mapping"
    )


class InputDefinition(Base):
    __tablename__ = "input_definitions"
    __table_args__ = (UniqueConstraint("id", "version_group_id", "version"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), server_onupdate=func.now()
    )

    # An input definition has one or more mappings.
    source_mappings: Mapped[list["SourceMapping"]] = relationship(
        back_populates="input_definition"
    )

    # The mapping jobs associated with this input definition.
    mapping_jobs: Mapped[list["MappingJob"]] = relationship(
        back_populates="input_definition"
    )

    # An input definition is associated with a blueprint.
    blueprint_id: Mapped[int] = mapped_column(
        ForeignKey("blueprints.id", ondelete="CASCADE")
    )
    blueprint: Mapped["MappingBlueprint"] = relationship(
        back_populates="input_definitions"
    )

    # Version control
    version_group_id: Mapped[str] = mapped_column(
        default=lambda: str(uuid.uuid4()), index=True
    )
    version: Mapped[int] = mapped_column(default=1)
    is_selected: Mapped[bool] = mapped_column(default=False)


class OutputDefinition(Base):
    __tablename__ = "output_definitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(default=None)
    json_schema: Mapped[Schema] = mapped_column(JSON)
    description: Mapped[Optional[str]] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )

    # An output definition is associated with a blueprint.
    blueprint_id: Mapped[int] = mapped_column(
        ForeignKey("blueprints.id", ondelete="CASCADE")
    )
    blueprint: Mapped["MappingBlueprint"] = relationship(
        back_populates="output_definition"
    )


class MappingBlueprint(Base):
    __tablename__ = "blueprints"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[Optional[str]] = mapped_column(default=None)
    model_prompt: Mapped[Optional[str]] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )

    # A blueprint is associated with a user.
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="blueprints")

    # A blueprint is optionally associated with an organization.
    organization_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True
    )
    organization: Mapped[Optional["Organization"]] = relationship(
        back_populates="blueprints"
    )

    # A blueprint has one or more input definitions.
    input_definitions: Mapped[list["InputDefinition"]] = relationship(
        back_populates="blueprint", cascade="all, delete", passive_deletes=True
    )

    # A blueprint has one output definition.
    output_definition: Mapped["OutputDefinition"] = relationship(
        back_populates="blueprint",
        uselist=False,
        cascade="all, delete",
        passive_deletes=True,
    )
