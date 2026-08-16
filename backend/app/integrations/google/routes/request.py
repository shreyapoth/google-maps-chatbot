from app.contracts.route import BasicRouteRequest

GOOGLE_ROUTES_FIELD_MASK = (
    "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
)


def build_compute_routes_body(route_request: BasicRouteRequest) -> dict:
    return {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": route_request.origin.latitude,
                    "longitude": route_request.origin.longitude,
                }
            }
        },
        "destination": {"placeId": route_request.destination.place_id},
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "computeAlternativeRoutes": False,
    }


def build_compute_routes_headers(api_key: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": GOOGLE_ROUTES_FIELD_MASK,
    }
