from __future__ import annotations

from pydantic import (
    BaseModel,
    field_validator,
)

from app.contracts.coordinates import Coordinates

class BasicRouteRequest(BaseModel):
    origin: Coordinates
    destination: str

    @field_validator("origin")
    def validate_origin(cls, v):
        if not v:
            raise ValueError("Origin is required")
        return v

    @field_validator("destination")
    def validate_destination(cls, v):
        if not v:
            raise ValueError("Destination is required")
        return v


class BasicRouteResponse(BaseModel):
    duration_minutes: int
    distance_miles: float
    polyline: str | None
