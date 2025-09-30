from enum import Enum


class Permission(str, Enum):
    VIEW_BLUEPRINT = "view_blueprint"
    MANAGE_BLUEPRINT = "manage_blueprint"
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    CREATE_STATIC_JOB = "create_static_job"
    VIEW_STATIC_JOB = "view_static_job"
    MANAGE_ORGANIZATION = "manage_organization"
