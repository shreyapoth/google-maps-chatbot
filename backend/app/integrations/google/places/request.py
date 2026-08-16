from app.contracts.place import (
    PlaceNearbySearchRequest,
    PlaceTextSearchRequest,
)

GOOGLE_PLACES_NEARBY_SEARCH_FIELD_MASK = (
    "places.id,"
    "places.displayName,"
    "places.formattedAddress,"
    "places.location,"
    "places.primaryType,"
    "places.types"
)

# Google caps a bias circle at 50km, which covers a metro area without ruling
# anything out, since a bias only orders results rather than filtering them.
TEXT_SEARCH_BIAS_RADIUS_METERS = 50000.0

GOOGLE_PLACES_TEXT_SEARCH_FIELD_MASK = (
    "places.id,"
    "places.displayName,"
    "places.formattedAddress,"
    "places.location,"
    "places.primaryType,"
    "places.types"
)


def build_nearby_search_body(request: PlaceNearbySearchRequest) -> dict[str, object]:
    return {
        "includedTypes": request.included_types,
        "maxResultCount": request.max_results,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": request.location.latitude,
                    "longitude": request.location.longitude,
                },
                "radius": request.radius,
            }
        },
    }


def build_nearby_search_headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": GOOGLE_PLACES_NEARBY_SEARCH_FIELD_MASK,
    }


def build_text_search_body(request: PlaceTextSearchRequest) -> dict[str, object]:
    body: dict[str, object] = {"textQuery": request.text_query}

    if request.location_bias is not None:
        body["locationBias"] = {
            "circle": {
                "center": {
                    "latitude": request.location_bias.latitude,
                    "longitude": request.location_bias.longitude,
                },
                "radius": TEXT_SEARCH_BIAS_RADIUS_METERS,
            }
        }

    return body


def build_text_search_headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": GOOGLE_PLACES_TEXT_SEARCH_FIELD_MASK,
    }
