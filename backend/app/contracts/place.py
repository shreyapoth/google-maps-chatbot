from __future__ import annotations

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)
from app.contracts.coordinates import Coordinates

class PlaceTextSearchRequest(BaseModel):
    text_query: str

    @field_validator("text_query")
    @classmethod
    def validate_text_query(cls, value: str) -> str:
        stripped_query = value.strip()
        if not stripped_query:
            raise ValueError("Text query is required")
        return stripped_query


class PlaceNearbySearchRequest(BaseModel):
    included_types: list[str] = Field(min_length=1)
    location: Coordinates
    radius: float = Field(default=5000.0, gt=0, le=50000)
    max_results: int = Field(default=10, ge=1, le=20)

    @field_validator("included_types")
    @classmethod
    def validate_included_types(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value if item and item.strip()]
        if not normalized:
            raise ValueError("At least one included type is required")
        return normalized

class PlaceResult(BaseModel):
    place_id: str
    name: str
    formatted_address: str | None
    location: Coordinates | None
    primary_type: str | None
    types: list[str]


class PlaceResponse(BaseModel):
    places: list[PlaceResult]
