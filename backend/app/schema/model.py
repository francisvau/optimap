from typing import List, Optional

from app.schema import BaseSchema


class CreateModelRequest(BaseSchema):
    """Create Model Request"""

    name: str
    tailor_prompt: List[str]
    base_model: str


class UpdateModelRequest(BaseSchema):
    """Update Model Request"""

    name: Optional[str] = None
    tailor_prompt: Optional[List[str]] = None
    base_model: Optional[str] = None


class ModelResponse(BaseSchema):
    """Model Response"""

    id: str
    name: str
    tailor_prompt: List[str]
    base_model: str
