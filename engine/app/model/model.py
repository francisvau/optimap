from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.model import PyObjectId


class BaseModelType(str, Enum):
    groq = "groq"
    gemini = "gemini"
    deepseek = "deepseek"
    openai = "openai"


class AIModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    tailor_prompt: List[str]
    base_model: BaseModelType

    model_config = ConfigDict(
        populate_by_name=True,  # Tells the validator you can work with id instead of _id
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "name": "A default model",
                "tailor_prompt": ["prompt1", "prompt2"],
                "base_model": "deepseek",
            }
        },
    )
