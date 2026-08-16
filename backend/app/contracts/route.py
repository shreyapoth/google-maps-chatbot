from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from app.contracts.coordinates import Coordinates

class BasicRouteRequest(BaseModel):
    origin: Coordinates
    destination: Destination

    @field_validator("destination")
    def validate_destination(cls, v):
        if not v:
            raise ValueError("Destination is required")
        return v

class Destination(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    place_id: str = Field(alias="placeId")

class BasicRouteResponse(BaseModel):
    duration_minutes: int
    distance_miles: float
    polyline: str | None
