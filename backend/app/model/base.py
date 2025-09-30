from typing import Any, Optional

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    def to_dict(self, visited: Optional[set[object]] = None) -> dict[str, Any]:
        """
        Convert the SQLAlchemy model instance to a dictionary, skipping unloaded
        relationships and avoiding infinite recursion.
        """
        if visited is None:
            visited = set()

        if self in visited:
            return {}

        visited.add(self)
        data: dict[str, Any] = {}
        insp = inspect(self)

        # Add all loaded column attributes
        for col_attr in insp.mapper.column_attrs:
            if col_attr.key not in insp.unloaded:
                data[col_attr.key] = getattr(self, col_attr.key)

        # Add loaded relationships
        for rel in insp.mapper.relationships:
            key = rel.key

            if key in insp.unloaded:
                continue  # skip unloaded relationship

            value = getattr(self, key)

            if value is None:
                data[key] = None
            elif rel.uselist:
                # Relationship is a list/collection
                children_list = []

                for child in value:
                    if child in visited:
                        continue  # avoid infinite recursion
                    children_list.append(child.to_dict(visited=visited))

                data[key] = children_list
            else:
                # Relationship is a single object
                if value in visited:
                    continue  # avoid infinite recursion
                data[key] = value.to_dict(visited=visited)

        visited.remove(self)

        return data

    def __repr__(self) -> str:
        """
        Return a string representation of the model instance.
        """
        class_name = self.__class__.__name__
        return f"<{class_name} {self.to_dict()}>"
