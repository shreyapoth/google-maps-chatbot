from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

class GooglePlace(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    display_name: GooglePlaceDisplayName = Field(alias="displayName")
    formatted_address: str | None = Field(default=None, alias="formattedAddress")
    location: GooglePlaceLocation | None = None
    primary_type: str | None = Field(default=None, alias="primaryType")
    types: list[str] = []
    rating: float | None = None
    user_rating_count: int | None = Field(default=None, alias="userRatingCount")
    price_level: str | None = Field(default=None, alias="priceLevel")
    google_maps_uri: str | None = Field(default=None, alias="googleMapsUri")

class GooglePlaceDisplayName(BaseModel):
    text: str

class GooglePlaceLocation(BaseModel):
    latitude: float
    longitude: float

class GooglePlacesNearbySearchResponse(BaseModel):
    places: list[GooglePlace] = []


