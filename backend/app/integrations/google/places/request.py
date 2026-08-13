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
    "places.types,"
    "places.rating,"
    "places.userRatingCount,"
    "places.priceLevel,"
    "places.googleMapsUri"
)

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
    return {
        "textQuery": request.text_query,
    }


def build_text_search_headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": GOOGLE_PLACES_TEXT_SEARCH_FIELD_MASK,
    }
