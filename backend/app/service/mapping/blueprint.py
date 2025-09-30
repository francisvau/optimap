from __future__ import annotations

from datetime import datetime
from typing import Iterable

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependency.engine import EngineClient
from app.exceptions import BadRequest, EntityNotPresent
from app.model.blueprint import (
    InputDefinition,
    MappingBlueprint,
    OutputDefinition,
    SourceMapping,
)
from app.schema.mapping.blueprint import (
    BlueprintResponse,
    CreateBlueprintRequest,
    CreateInputDefinitionRequest,
    CreateMappingRequest,
    CreateOutputDefinitionRequest,
    InputDefinitionResponse,
    JsonataGenerationRequest,
    JsonataGenerationResponse,
    OutputDefinitionResponse,
    PreviousMapping,
    SourceMappingResponse,
    UpdateBlueprintRequest,
    UpdateInputDefinitionRequest,
    UpdateMappingRequest,
    UpdateOutputDefinitionRequest,
)
from app.service.base import build_load_options
from app.service.log import LogService
from app.util.schema import align_schema


class MappingBlueprintService:
    """Business logic for mapping blueprints."""

    BLUEPRINT_REL_DEFAULT = (
        "input_definitions",
        "output_definition",
        "input_definitions.source_mappings",
    )
    BLUEPRINT_REL_MAP = {
        "user": selectinload(MappingBlueprint.user),
        "organization": selectinload(MappingBlueprint.organization),
        "output_definition": selectinload(MappingBlueprint.output_definition),
        "input_definitions": selectinload(
            MappingBlueprint.input_definitions.and_(InputDefinition.is_selected)
        ),
        "input_definitions.source_mappings": selectinload(
            MappingBlueprint.input_definitions.and_(InputDefinition.is_selected)
        ).selectinload(InputDefinition.source_mappings),
    }

    INPUT_DEFINITION_REL_DEFAULT = ("source_mappings",)
    INPUT_DEFINITION_REL_MAP = {
        "blueprint": selectinload(InputDefinition.blueprint),
        "source_mappings": selectinload(InputDefinition.source_mappings),
    }

    def __init__(
        self,
        db: AsyncSession,
        engine_client: EngineClient,
        logger: LogService,
    ) -> None:
        self.db = db
        self.client = engine_client
        self.logger = logger

    async def create_blueprint(
        self, *, req: CreateBlueprintRequest, user_id: int
    ) -> BlueprintResponse:
        """Create a new mapping blueprint."""
        values = req.model_dump(by_alias=False) | {
            "user_id": user_id,
        }

        # Create the blueprint.
        blueprint = await self.db.scalar(
            insert(MappingBlueprint).values(values).returning(MappingBlueprint)
        )

        if blueprint is None:
            raise BadRequest("Failed to create blueprint")

        # Create the empty output definition.
        await self.create_output_definition(
            blueprint.id, req=CreateOutputDefinitionRequest()
        )

        return BlueprintResponse.model_validate(blueprint.to_dict())

    async def read_blueprint(
        self,
        blueprint_id: int,
        *,
        include: Iterable[str] = BLUEPRINT_REL_DEFAULT,
    ) -> BlueprintResponse:
        """Read a mapping blueprint by its ID. The *include* parameter"""
        options = build_load_options(include, self.BLUEPRINT_REL_MAP)

        blueprint = await self.db.scalar(
            select(MappingBlueprint)
            .where(MappingBlueprint.id == blueprint_id)
            .options(*options)
        )

        if not blueprint:
            raise EntityNotPresent("Blueprint not found")

        return BlueprintResponse.model_validate(
            blueprint.to_dict() | {"usage_count": 0}
        )

    async def read_blueprints_for_user(
        self,
        user_id: int,
        *,
        include: Iterable[str] = BLUEPRINT_REL_DEFAULT,
    ) -> list[BlueprintResponse]:
        """Read all mapping blueprints for a user."""
        # Load the blueprints for the user.
        options = build_load_options(include, self.BLUEPRINT_REL_MAP)

        scalars = await self.db.scalars(
            select(MappingBlueprint)
            .where(MappingBlueprint.user_id == user_id)
            .options(*options)
        )

        return [
            BlueprintResponse.model_validate(blueprint.to_dict() | {"usage_count": 0})
            for blueprint in scalars.all()
        ]

    async def read_blueprints_for_organization(
        self,
        org_id: int,
        *,
        include: Iterable[str] = BLUEPRINT_REL_DEFAULT,
    ) -> list[BlueprintResponse]:
        """Read all mapping blueprints for a organization."""
        # Load the blueprints for the organization.
        options = build_load_options(include, self.BLUEPRINT_REL_MAP)

        scalars = await self.db.scalars(
            select(MappingBlueprint)
            .where(MappingBlueprint.organization_id == org_id)
            .options(*options)
        )

        return [
            BlueprintResponse.model_validate(blueprint.to_dict() | {"usage_count": 0})
            for blueprint in scalars.all()
        ]

    async def update_blueprint(
        self, blueprint_id: int, *, changes: UpdateBlueprintRequest
    ) -> BlueprintResponse:
        """Update a mapping blueprint."""
        values = changes.model_dump(
            exclude_unset=True,
            by_alias=False,
        )

        updated = await self.db.scalar(
            update(MappingBlueprint)
            .where(MappingBlueprint.id == blueprint_id)
            .values(values)
            .returning(MappingBlueprint)
        )

        if updated is None:
            raise EntityNotPresent("Blueprint not found")

        return BlueprintResponse.model_validate(updated.to_dict())

    async def delete_blueprint(self, blueprint_id: int) -> None:
        """Delete a mapping blueprint."""
        # Delete the blueprint from the database.
        exists = await self.db.execute(
            delete(MappingBlueprint).where(MappingBlueprint.id == blueprint_id)
        )

        if exists.rowcount == 0:
            raise EntityNotPresent("Blueprint not found")

    async def create_input_definition(
        self,
        *,
        blueprint_id: int,
        req: CreateInputDefinitionRequest,
    ) -> InputDefinitionResponse:
        """Add a new input definition to a mapping blueprint."""
        blueprint = await self.db.get(MappingBlueprint, blueprint_id)

        if not blueprint:
            raise EntityNotPresent("Blueprint not found")

        values = req.model_dump(by_alias=False) | {
            "blueprint_id": blueprint_id,
            "is_selected": True,
        }

        # Insert and get the new ID
        definition = await self.db.scalar(
            insert(InputDefinition)
            .values(values)
            .returning(InputDefinition)
            .options(selectinload(InputDefinition.blueprint))
        )

        if definition is None:
            raise ValueError("Failed to retrieve inserted InputDefinition")

        return InputDefinitionResponse.model_validate(definition.to_dict())

    async def create_input_definition_version(
        self,
        *,
        base_input_def_id: int,
    ) -> InputDefinitionResponse:
        # Retrieve the base InputDefinition with its SourceMappings
        base_stmt = (
            select(InputDefinition)
            .options(selectinload(InputDefinition.source_mappings))
            .where(InputDefinition.id == base_input_def_id)
        )
        result = await self.db.execute(base_stmt)
        base_input_def = result.scalars().first()

        if not base_input_def:
            raise EntityNotPresent("Base input definition not found")

        # Unselect previous versions in the group
        await self.db.execute(
            update(InputDefinition)
            .where(InputDefinition.version_group_id == base_input_def.version_group_id)
            .values(is_selected=False)
        )

        # Prepare values for the new InputDefinition
        new_values = {
            "name": base_input_def.name,
            "description": base_input_def.description,
            "blueprint_id": base_input_def.blueprint_id,
            "version_group_id": base_input_def.version_group_id,
            "version": base_input_def.version + 1,
            "is_selected": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        # Insert the new InputDefinition
        insert_result = await self.db.execute(
            insert(InputDefinition).values(new_values).returning(InputDefinition.id)
        )
        new_id = insert_result.scalar_one()

        # Copy SourceMappings from the base InputDefinition
        new_source_mappings = [
            {
                "name": source_mapping.name,
                "file_type": source_mapping.file_type,
                "input_json_schema": source_mapping.input_json_schema,
                "jsonata_mapping": source_mapping.jsonata_mapping,
                "output_json_schema": source_mapping.output_json_schema,
                "model_id": source_mapping.model_id,
                "target_path": source_mapping.target_path,
                "input_definition_id": new_id,  # Link to the new InputDefinition
            }
            for source_mapping in base_input_def.source_mappings
        ]
        print("-------\nsource mappings\n-------\n", new_source_mappings)
        print("-------\nsource mappings\n-------\n")

        # Insert new SourceMappings if there are any
        if new_source_mappings:
            await self.db.execute(insert(SourceMapping).values(new_source_mappings))

        # Retrieve the new InputDefinition with its blueprint
        select_stmt = (
            select(InputDefinition)
            .options(
                selectinload(InputDefinition.blueprint),
                selectinload(InputDefinition.source_mappings),
            )
            .filter(InputDefinition.id == new_id)
        )
        select_result = await self.db.execute(select_stmt)
        new_input_def = select_result.scalars().first()

        if new_input_def is None:
            raise ValueError("Failed to retrieve inserted InputDefinition")

        return InputDefinitionResponse.model_validate(new_input_def.to_dict())

    async def select_input_definition_version(
        self, blueprint_id: int, input_id: int
    ) -> InputDefinitionResponse:
        """Select a specific version of an input definition."""
        # Step 1: Get the version to select
        input_def = await self.db.scalar(
            select(InputDefinition).where(
                InputDefinition.id == input_id,
                InputDefinition.blueprint_id == blueprint_id,
            )
        )

        if input_def is None:
            raise EntityNotPresent("Input definition not found")

        # Step 2: Deselect currently selected version in the same version group
        await self.db.execute(
            update(InputDefinition)
            .where(
                InputDefinition.blueprint_id == blueprint_id,
                InputDefinition.version_group_id == input_def.version_group_id,
                InputDefinition.is_selected,
            )
            .values(is_selected=False)
        )

        # Step 3: Select the new version
        definition = await self.db.scalar(
            update(InputDefinition)
            .where(InputDefinition.id == input_def.id)
            .values(is_selected=True)
            .returning(InputDefinition)
        )

        if definition is None:
            raise EntityNotPresent("Input definition not found")

        return InputDefinitionResponse.model_validate(definition.to_dict())

    async def get_input_definition_versions(
        self, input_definition_id: int
    ) -> list[InputDefinitionResponse]:
        """Return all versions of an input definition by its version group."""
        # Step 1: Get the target input definition
        result = await self.db.execute(
            select(InputDefinition).where(InputDefinition.id == input_definition_id)
        )
        input_def = result.scalars().first()

        if input_def is None:
            raise EntityNotPresent("Input definition not found")

        # Step 2: Get all versions in the same version group
        versions_stmt = (
            select(InputDefinition)
            .where(InputDefinition.version_group_id == input_def.version_group_id)
            .order_by(InputDefinition.version.asc())
        )

        result = await self.db.execute(versions_stmt)
        versions = result.scalars().all()

        return [InputDefinitionResponse.model_validate(v.to_dict()) for v in versions]

    async def read_input_definition(
        self, input_id: int, *, include: tuple[str] = INPUT_DEFINITION_REL_DEFAULT
    ) -> InputDefinitionResponse:
        """Read an input definition by its ID."""
        options = build_load_options(include, self.INPUT_DEFINITION_REL_MAP)

        input = await self.db.scalar(
            select(InputDefinition)
            .where(InputDefinition.id == input_id)
            .options(*options)
        )

        if not input:
            raise EntityNotPresent("Input definition not found")

        return InputDefinitionResponse.model_validate(input.to_dict())

    async def update_input_definition(
        self,
        input_id: int,
        *,
        changes: UpdateInputDefinitionRequest,
    ) -> InputDefinitionResponse:
        """Update an input definition in a mapping blueprint."""
        values = changes.model_dump(
            exclude_unset=True,
            by_alias=False,
        )

        if not values:
            raise BadRequest("No changes to update")

        updated = await self.db.scalar(
            update(InputDefinition)
            .where(InputDefinition.id == input_id)
            .values(values or {})
            .returning(InputDefinition),
        )

        if not updated:
            raise EntityNotPresent("Input definition not found")

        return InputDefinitionResponse.model_validate(updated.to_dict())

    async def delete_input_definition(self, input_id: int) -> None:
        """Delete an input definition from a mapping blueprint."""
        inp = await self.db.execute(
            delete(InputDefinition).where(InputDefinition.id == input_id)
        )

        if inp.rowcount == 0:
            raise EntityNotPresent("Input definition not found")

    async def create_output_definition(
        self,
        blueprint_id: int,
        *,
        req: CreateOutputDefinitionRequest,
    ) -> OutputDefinitionResponse:
        """Add a new output definition to a mapping blueprint."""
        # Delete the existing output definition for the blueprint.
        await self.db.execute(
            delete(OutputDefinition).where(
                OutputDefinition.blueprint_id == blueprint_id
            )
        )

        values = req.model_dump(by_alias=False) | {
            "blueprint_id": blueprint_id,
        }

        output = await self.db.scalar(
            insert(OutputDefinition).values(values).returning(OutputDefinition)
        )

        if output is None:
            raise BadRequest("Failed to create output definition")

        return OutputDefinitionResponse.model_validate(output)

    async def read_output_definition(
        self,
        blueprint_id: int,
    ) -> OutputDefinitionResponse:
        """Read an output definition by its ID."""
        output = await self.db.scalar(
            select(OutputDefinition).where(
                OutputDefinition.blueprint_id == blueprint_id
            )
        )

        if not output:
            raise EntityNotPresent("Output definition not found")

        return OutputDefinitionResponse.model_validate(output)

    async def update_output_definition(
        self,
        blueprint_id: int,
        *,
        changes: UpdateOutputDefinitionRequest,
    ) -> OutputDefinitionResponse:
        """Update an output definition in a mapping blueprint."""
        values = changes.model_dump(exclude_unset=True, by_alias=False)

        result = await self.db.scalar(
            update(OutputDefinition)
            .where(OutputDefinition.blueprint_id == blueprint_id)
            .values(values)
            .returning(OutputDefinition),
        )

        if result is None:
            raise EntityNotPresent("Output definition not found")

        return OutputDefinitionResponse.model_validate(result)

    async def delete_output_definition(self, output_id: int) -> None:
        """Delete an output definition from a mapping blueprint."""
        deleted = await self.db.execute(
            delete(OutputDefinition).where(OutputDefinition.id == output_id)
        )

        if deleted.rowcount == 0:
            raise EntityNotPresent("Output definition not found")

    async def create_source_mapping(
        self, input_id: int, *, req: CreateMappingRequest
    ) -> SourceMappingResponse:
        """Create a new source mapping."""
        input = await self.db.scalar(
            select(InputDefinition).where(InputDefinition.id == input_id)
        )

        if not input:
            raise EntityNotPresent("Input definition not found")

        # Align the input JSON schema to the output JSON schema.
        # This is done by checking and aligning the root type of the input schema to that of the output schema.
        input_schema = align_schema(req.input_json_schema, req.output_json_schema)

        values = req.model_dump(by_alias=False) | {
            "input_definition_id": input_id,
            "input_json_schema": input_schema,
        }

        source_mapping = await self.db.scalar(
            insert(SourceMapping).values(values).returning(SourceMapping)
        )

        if source_mapping is None:
            raise BadRequest("Failed to create source mapping")

        return SourceMappingResponse.model_validate(source_mapping)

    async def read_source_mapping(self, mapping_id: int) -> SourceMappingResponse:
        """Read a source mapping by its ID."""
        source_mapping = await self.db.scalar(
            select(SourceMapping).where(SourceMapping.id == mapping_id)
        )

        if not source_mapping:
            raise EntityNotPresent("Source mapping not found")

        return SourceMappingResponse.model_validate(source_mapping)

    async def delete_source_mapping(self, mapping_id: int) -> None:
        """Delete source mappings."""
        # Delete the source mapping from the database.
        deleted = await self.db.execute(
            delete(SourceMapping).where(SourceMapping.id == mapping_id)
        )

        if deleted.rowcount == 0:
            raise EntityNotPresent("Source mapping not found")

    async def update_source_mapping(
        self, mapping_id: int, *, req: UpdateMappingRequest
    ) -> SourceMappingResponse:
        """Update a source mapping."""
        # Read the source mapping from the database.
        source_mapping = await self.db.scalar(
            select(SourceMapping).where(SourceMapping.id == mapping_id)
        )

        if source_mapping is None:
            raise EntityNotPresent("Source mapping not found")

        # Align the input JSON schema to the output JSON schema.
        # This is done by checking and aligning the root type of the input schema to that of the output schema.
        input_schema = align_schema(
            req.input_json_schema or source_mapping.input_json_schema,
            req.output_json_schema or source_mapping.output_json_schema,
        )

        values = req.model_dump(exclude_unset=True, by_alias=False) | {
            "input_json_schema": input_schema,
        }

        # Update the source mapping in the database.
        updated = await self.db.scalar(
            update(SourceMapping)
            .where(SourceMapping.id == mapping_id)
            .values(values)
            .returning(SourceMapping),
        )

        if updated is None:
            raise EntityNotPresent("Could not update source mapping")

        return SourceMappingResponse.model_validate(updated)

    async def read_latest_source_mappings_for_organization(
        self, organization_id: int | None, limit: int = 3
    ) -> list[PreviousMapping]:
        """
        Reads the latest source mappings for a given organization.
        """
        if organization_id is None:
            return []

        stmt = (
            select(SourceMapping)
            .join(
                InputDefinition, SourceMapping.input_definition_id == InputDefinition.id
            )
            .join(MappingBlueprint, InputDefinition.blueprint_id == MappingBlueprint.id)
            .where(MappingBlueprint.organization_id == organization_id)
            .where(SourceMapping.jsonata_mapping.isnot(None))
            .limit(limit)
        )
        source_mapping_models = (await self.db.scalars(stmt)).all()

        previous_mappings_list: list[PreviousMapping] = []
        for sm_model in source_mapping_models:
            previous_mappings_list.append(
                PreviousMapping(
                    input_json_schema=sm_model.input_json_schema,
                    output_json_schema=sm_model.output_json_schema,
                    jsonata_mapping=sm_model.jsonata_mapping,
                )
            )

        return previous_mappings_list

    async def generate_jsonata_mapping(
        self, *, request: JsonataGenerationRequest
    ) -> JsonataGenerationResponse:
        """Generate a JSONata mapping."""
        # Model dump should be done with by_alias=False to ensure that the keys are not converted to camelCase.
        # This is because the engine expects the keys to be in snake_case.
        jsonata = await self.client.request(
            "POST", "/mappings/generate", json=request.model_dump(by_alias=False)
        )

        return JsonataGenerationResponse.model_validate(jsonata)
