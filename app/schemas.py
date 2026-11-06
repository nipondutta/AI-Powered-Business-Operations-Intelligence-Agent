
from typing import Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question asked by the user"
    )


class ChatResponse(BaseModel):
    answer: str
    intent: str = "unknown"
    sources: list = Field(default_factory=list)
    sql: str | None = None
    data: Any = None
