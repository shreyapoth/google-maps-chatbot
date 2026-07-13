from __future__ import annotations

from pydantic import (
    BaseModel,
    Field,
)


class GoogleRoutesPolyline(BaseModel):
    encoded_polyline: str | None = Field(default=None, alias="encodedPolyline")


class GoogleRoute(BaseModel):
    duration: str
    distance_meters: int = Field(alias="distanceMeters")
    polyline: GoogleRoutesPolyline | None = None


class GoogleRoutesResponse(BaseModel):
    routes: list[GoogleRoute]
