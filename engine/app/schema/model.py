from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict

from app.model.model import BaseModelType


class UpdateModelRequest(BaseModel):
    name: Optional[str] = None
    tailor_prompt: Optional[List[str]] = None
    base_model: Optional[BaseModelType] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "name": "Updated model name",
                "tailor_prompt": ["updated prompt1", "updated prompt2"],
                "base_model": "deepseek",
            }
        },
    )
