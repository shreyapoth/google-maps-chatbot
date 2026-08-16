from uuid import UUID

from pydantic import (
    BaseModel,
    field_validator,
)

from app.contracts.coordinates import Coordinates


class ChatRequest(BaseModel):
    message: str
    location: Coordinates
    thread_id: UUID

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        stripped_message = value.strip()
        if not stripped_message:
            raise ValueError("Message is required")
        return stripped_message


class ChatResponse(BaseModel):
    reply: str
    thread_id: UUID
