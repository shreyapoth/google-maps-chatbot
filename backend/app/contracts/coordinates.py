from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
)

class Coordinates(BaseModel):
    latitude: float = Field(validation_alias=AliasChoices("latitude", "lat"))
    longitude: float = Field(validation_alias=AliasChoices("longitude", "lng"))
