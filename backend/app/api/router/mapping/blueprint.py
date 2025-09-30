from fastapi import APIRouter, status

from app.api.dependency.auth.blueprint import AuthBlueprintDep
from app.api.dependency.auth.user import AuthUserDep
from app.api.dependency.service import (
    LogServiceDep,
    MappingBlueprintServiceDep,
    OrganizationServiceDep,
)
from app.exceptions import EntityNotPresent
from app.model.log import LogAction
from app.schema.mapping.blueprint import (
    BlueprintResponse,
    CreateBlueprintRequest,
    CreateInputDefinitionRequest,
    CreateMappingRequest,
    GenerateMappingRequest,
    InputDefinitionResponse,
    JsonataGenerationRequest,
    JsonataGenerationResponse,
    OutputDefinitionResponse,
    SourceMappingResponse,
    UpdateBlueprintRequest,
    UpdateInputDefinitionRequest,
    UpdateMappingRequest,
    UpdateOutputDefinitionRequest,
)

router = APIRouter(prefix="/blueprints", tags=["blueprints"])

"""Blueprints"""


@router.post(
    "",
    response_model=BlueprintResponse,
    response_model_exclude_unset=True,
    status_code=status.HTTP_201_CREATED,
)
async def create_blueprint(
    body: CreateBlueprintRequest,
    user: AuthUserDep,
    blueprint_svc: MappingBlueprintServiceDep,
    organization_svc: OrganizationServiceDep,
    logger: LogServiceDep,
) -> BlueprintResponse:
    """Create a new mapping blueprint."""
    # Check if the user is a member of the organization
    if body.organization_id:
        is_member = await organization_svc.user_is_organization_member(
            org_id=body.organization_id, user_id=user.id
        )

        if not is_member:
            raise EntityNotPresent("organization does not exist")

    # Create and return the blueprint
    user_id = body.user_id if body.user_id and user.is_admin else user.id
    blueprint = await blueprint_svc.create_blueprint(req=body, user_id=user_id)

    await logger.info(
        message=f"Blueprint {blueprint.id} created by user {user.id} in organization {body.organization_id}",
        user_id=user.id,
        organization_id=body.organization_id,
        blueprint_id=blueprint.id,
        action=LogAction.CREATE,
        persist=True,
        context={"blueprint_id": blueprint.id},
    )

    return blueprint


@router.get("/{blueprint_id}", response_model=BlueprintResponse)
async def read_blueprint(
    blueprint_id: int,
    user_bp: AuthBlueprintDep,
    bp_svc: MappingBlueprintServiceDep,
    logger: LogServiceDep,
) -> BlueprintResponse:
    """Get a mapping blueprint."""
    user, bp = user_bp
    blueprint = await bp_svc.read_blueprint(blueprint_id)

    await logger.info(
        message=f"Blueprint {blueprint.id} read by user {user.id}",
        persist=False,
    )

    return blueprint


@router.get("/user/{user_id}", response_model=list[BlueprintResponse])
async def read_blueprints_by_user(
    user_id: int,
    svc: MappingBlueprintServiceDep,
    logger: LogServiceDep,
) -> list[BlueprintResponse]:
    """Get a mapping blueprint by user."""
    blueprints = await svc.read_blueprints_for_user(user_id=user_id)

    await logger.info(
        message=f"Blueprints read for user {user_id}",
        persist=False,
    )

    return blueprints


@router.get("/organization/{org_id}", response_model=list[BlueprintResponse])
async def read_blueprints_by_organization(
    org_id: int,
    svc: MappingBlueprintServiceDep,
) -> list[BlueprintResponse]:
    """Get a mapping blueprint by user."""
    blueprints = await svc.read_blueprints_for_organization(org_id=org_id)

    return blueprints


@router.patch("/{blueprint_id}", response_model=BlueprintResponse)
async def patch_blueprint(
    blueprint_id: int,
    body: UpdateBlueprintRequest,
    bp_svc: MappingBlueprintServiceDep,
    logger: LogServiceDep,
    user_bp: AuthBlueprintDep,
) -> BlueprintResponse:
    """Update a mapping blueprint."""
    user, _ = user_bp
    blueprint = await bp_svc.update_blueprint(blueprint_id, changes=body)

    await logger.info(
        message=f"Blueprint {blueprint.id} patched by user {user.id}",
        user_id=user.id,
        blueprint_id=blueprint.id,
        action=LogAction.UPDATE,
        persist=True,
        context={"blueprint_id": blueprint.id},
    )

    return blueprint


@router.delete("/{blueprint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blueprint(
    blueprint_id: int,
    bp_svc: MappingBlueprintServiceDep,
    logger: LogServiceDep,
    user_bp: AuthBlueprintDep,
) -> None:
    """Delete a mapping blueprint."""
    user, bp = user_bp
    await bp_svc.delete_blueprint(blueprint_id)

    await logger.info(
        message=f"Blueprint {bp.id} deleted by user {user.id}",
        persist=True,
        user_id=user.id,
        action=LogAction.DELETE,
        context={
            "blueprint_id": bp.id,
        },
    )


"""Output Definitions"""


@router.patch("/{blueprint_id}/output", response_model=OutputDefinitionResponse)
async def patch_output_definition(
    blueprint_id: int,
    body: UpdateOutputDefinitionRequest,
    bp_svc: MappingBlueprintServiceDep,
    logger: LogServiceDep,
    user_bp: AuthBlueprintDep,
) -> OutputDefinitionResponse:
    """Update an output definition in a mapping blueprint."""
    user, bp = user_bp
    out = await bp_svc.update_output_definition(blueprint_id, changes=body)

    await logger.info(
        message=f"Output definition {out.id} patched in blueprint {bp.id}",
        user_id=user.id,
        blueprint_id=bp.id,
        persist=True,
        action=LogAction.UPDATE,
        context={"output_definition_id": out.id},
    )

    return out


"""Input Definitions"""


@router.post(
    "/{blueprint_id}/input",
    response_model=InputDefinitionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_input_definition(
    blueprint_id: int,
    body: CreateInputDefinitionRequest,
    bp_svc: MappingBlueprintServiceDep,
    logger: LogServiceDep,
    user_bp: AuthBlueprintDep,
) -> InputDefinitionResponse:
    """Add an input definition to a mapping blueprint."""
    user, bp = user_bp
    inp = await bp_svc.create_input_definition(blueprint_id=bp.id, req=body)

    await logger.info(
        message=f"Input definition {inp.name} created in blueprint {bp.name} by user {user.id}",
        user_id=user.id,
        blueprint_id=bp.id,
        persist=True,
        action=LogAction.CREATE,
        context={"input_definition_id": inp.id},
    )

    return inp


@router.post(
    "/{blueprint_id}/input/{input_id}/select",
    status_code=status.HTTP_200_OK,
)
async def select_input_definition_version(
    blueprint_id: int,
    input_id: int,
    bp_svc: MappingBlueprintServiceDep,
    logger: LogServiceDep,
    user_bp: AuthBlueprintDep,
) -> InputDefinitionResponse:
    """
    Select a specific version of an input definition.
    """

    inp = await bp_svc.select_input_definition_version(blueprint_id, input_id)

    return inp


@router.get(
    "/{blueprint_id}/input/{input_id}/versions",
    response_model=list[InputDefinitionResponse],
)
async def list_input_definition_versions(
    blueprint_id: int,
    input_id: int,
    bp_svc: MappingBlueprintServiceDep,
    _: AuthBlueprintDep,
) -> list[InputDefinitionResponse]:
    """List all versions of an input definition."""
    return await bp_svc.get_input_definition_versions(input_id)


@router.post(
    "/{blueprint_id}/input/{input_definition_id}/new-version",
    response_model=InputDefinitionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_input_definition_version(
    input_definition_id: int,
    bp_svc: MappingBlueprintServiceDep,
    logger: LogServiceDep,
    user_bp: AuthBlueprintDep,
) -> InputDefinitionResponse:
    """Create a new version of an existing input definition."""
    user, _ = user_bp
    new_version = await bp_svc.create_input_definition_version(
        base_input_def_id=input_definition_id,
    )

    await logger.info(
        message=f"New version of input definition {new_version.name} created by {user.email}",
        user_id=user.id,
        persist=True,
        context={"input_definition_id": new_version.id, "base_id": input_definition_id},
    )

    return new_version


@router.patch(
    "/{blueprint_id}/input/{input_id}", response_model=InputDefinitionResponse
)
async def patch_input_definition(
    blueprint_id: int,
    input_id: int,
    body: UpdateInputDefinitionRequest,
    bp_svc: MappingBlueprintServiceDep,
    user_bp: AuthBlueprintDep,
    logger: LogServiceDep,
) -> InputDefinitionResponse:
    """Update an input definition in a mapping blueprint."""
    user, _ = user_bp
    inp = await bp_svc.update_input_definition(input_id, changes=body)

    await logger.info(
        message=f"Input definition {inp.id} patched by user {user.id} for blueprint {blueprint_id}",
        user_id=user.id,
        blueprint_id=blueprint_id,
        persist=True,
        action=LogAction.UPDATE,
        context={"input_definition_id": inp.id},
    )

    return inp


@router.get("/{blueprint_id}/input/{input_id}", response_model=InputDefinitionResponse)
async def read_input_definition(
    input_id: int,
    bp_svc: MappingBlueprintServiceDep,
    _: AuthBlueprintDep,
    logger: LogServiceDep,
) -> InputDefinitionResponse:
    """Get an input definition from a mapping blueprint."""
    inp = await bp_svc.read_input_definition(input_id)

    await logger.info(
        message=f"Input definition {inp.id} read",
        persist=False,
    )
    return inp


@router.delete(
    "/{blueprint_id}/input/{input_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_input_definition(
    blueprint_id: int,
    input_id: int,
    bp_svc: MappingBlueprintServiceDep,
    user_bp: AuthBlueprintDep,
    logger: LogServiceDep,
) -> None:
    """Delete an input definition from a mapping blueprint."""
    await bp_svc.delete_input_definition(input_id)

    user, _ = user_bp
    await logger.info(
        message=f"Input definition {input_id} deleted by user {user.id} "
        f"for blueprint {blueprint_id}",
        user_id=user.id,
        action=LogAction.DELETE,
        context={"input_definition_id": input_id, "blueprint_id": blueprint_id},
        persist=True,
    )


"""Source Mappings"""


@router.post(
    "/{blueprint_id}/input/{input_id}/mappings",
    response_model=SourceMappingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_mapping(
    blueprint_id: int,
    input_id: int,
    body: CreateMappingRequest,
    bp_svc: MappingBlueprintServiceDep,
    user_bp: AuthBlueprintDep,
    logger: LogServiceDep,
) -> SourceMappingResponse:
    """Create a new mapping for an input definition in a mapping blueprint."""
    user, _ = user_bp
    mapping = await bp_svc.create_source_mapping(input_id, req=body)

    await logger.info(
        message=f"Mapping {mapping.id} created for input definition {input_id} by user {user.id} on blueprint {blueprint_id}",
        user_id=user.id,
        blueprint_id=blueprint_id,
        persist=True,
        action=LogAction.CREATE,
        context={"input_definition_id": input_id, "mapping_id": mapping.id},
    )
    return mapping


@router.get(
    "/{blueprint_id}/input/{input_id}/mappings/{mapping_id}",
    response_model=SourceMappingResponse,
)
async def read_source_mapping(
    mapping_id: int,
    bp_svc: MappingBlueprintServiceDep,
    _: AuthBlueprintDep,
    logger: LogServiceDep,
) -> SourceMappingResponse:
    """Get a mapping for an input definition in a mapping blueprint."""
    mapping = await bp_svc.read_source_mapping(mapping_id)

    await logger.info(
        message=f"Mapping {mapping.id} read",
        persist=False,
    )
    return mapping


@router.patch(
    "/{blueprint_id}/input/{input_id}/mappings/{mapping_id}",
    response_model=SourceMappingResponse,
    response_model_exclude_unset=True,
)
async def patch_source_mapping(
    blueprint_id: int,
    input_id: int,
    mapping_id: int,
    body: UpdateMappingRequest,
    bp_svc: MappingBlueprintServiceDep,
    user_db: AuthBlueprintDep,
    logger: LogServiceDep,
) -> SourceMappingResponse:
    user, _ = user_db
    mapping = await bp_svc.update_source_mapping(mapping_id, req=body)

    await logger.info(
        message=f"Mapping {mapping.id} patched by user {user.id} for input definition {input_id} in blueprint {blueprint_id}",
        user_id=user.id,
        blueprint_id=blueprint_id,
        persist=True,
        action=LogAction.UPDATE,
        context={"input_definition_id": input_id, "mapping_id": mapping.id},
    )
    return mapping


@router.get("/{blueprint_id}/output", response_model=OutputDefinitionResponse)
async def read_output_definition(
    blueprint_id: int,
    bp_svc: MappingBlueprintServiceDep,
    _: AuthBlueprintDep,
    logger: LogServiceDep,
) -> OutputDefinitionResponse:
    """Get an output definition from a mapping blueprint."""
    out = await bp_svc.read_output_definition(blueprint_id)

    await logger.info(
        message=f"Output definition {out.id} read",
        persist=False,
    )
    return out


@router.delete(
    "/{blueprint_id}/input/{input_id}/mappings/{mapping_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_mapping(
    blueprint_id: int,
    input_id: int,
    mapping_id: int,
    bp_svc: MappingBlueprintServiceDep,
    user_bp: AuthBlueprintDep,
    logger: LogServiceDep,
) -> None:
    user, _ = user_bp

    await bp_svc.delete_source_mapping(mapping_id)

    await logger.info(
        message=f"Mapping {mapping_id} deleted by user {user.id} for input definition {input_id} in blueprint {blueprint_id}",
        user_id=user.id,
        blueprint_id=blueprint_id,
        persist=True,
        action=LogAction.DELETE,
        context={"mapping_id": mapping_id},
    )


@router.post(
    "/{blueprint_id}/input/{input_id}/mappings/{mapping_id}/generate",
    response_model=JsonataGenerationResponse,
)
async def generate_mapping(
    blueprint_id: int,
    input_id: int,
    mapping_id: int,
    body: GenerateMappingRequest,
    bp_svc: MappingBlueprintServiceDep,
    user_bp: AuthBlueprintDep,
    logger: LogServiceDep,
) -> JsonataGenerationResponse:
    """Generate a JSONata mapping for a source mapping in a mapping blueprint."""
    user, _ = user_bp

    if body.model is not None:
        await bp_svc.update_source_mapping(
            mapping_id,
            req=UpdateMappingRequest.model_validate({"model_id": body.model}),
        )

    source_mapping = await bp_svc.read_source_mapping(mapping_id)

    previous_mappings = []

    if body.finetuning:
        previous_mappings = await bp_svc.read_latest_source_mappings_for_organization(
            organization_id=body.organization_id
        )

    jsonata_generation_request = JsonataGenerationRequest(
        input_json_schema=source_mapping.input_json_schema,
        output_json_schema=source_mapping.output_json_schema,
        model_id=source_mapping.model_id,
        previous_mappings=previous_mappings,
    )

    jsonata_mapping = await bp_svc.generate_jsonata_mapping(
        request=jsonata_generation_request
    )

    await logger.info(
        message=f"JSONATA Mapping {mapping_id} generated by user {user.id} for input definition {input_id} in blueprint {blueprint_id}",
        user_id=user.id,
        persist=True,
        action=LogAction.READ,
        context={
            "input_definition_id": input_id,
            "mapping_id": mapping_id,
            "organization_id": body.organization_id,
            "finetuning": body.finetuning,
        },
    )

    return jsonata_mapping
