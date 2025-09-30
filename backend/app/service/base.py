from typing import Iterable, Mapping

from sqlalchemy.sql.base import ExecutableOption


def build_load_options(
    wants: Iterable[str],
    rel_map: Mapping[str, ExecutableOption],
) -> list[ExecutableOption]:
    """
    Return the list of ORM `Load` options that eagerly load only the
    relationships requested in *wants*.

    *rel_map* maps relationship names ➜ default eager-load option, e.g.

        rel_map = {
            "input_definitions": selectinload(…),
            "output_definition": selectinload(…),
        }

    Any relationship not in *wants* is automatically given `raiseload()`
    so accidental attribute access raises loudly.
    """
    opts = []

    for rel, eager in rel_map.items():
        if rel in wants:
            opts.append(eager)

    return opts
