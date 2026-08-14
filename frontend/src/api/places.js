import { getCurrentLocation } from "./geolocation";
import { API_ROUTES } from "./apiRoutes";

export async function requestNearbyPlaces(includedTypes = ["restaurant"]) {
  const { coords, source } = await getCurrentLocation();
  console.info("[places] Requesting nearby places", {
    endpoint: API_ROUTES.nearbyPlaces,
    coords,
    locationSource: source,
    includedTypes,
  });

  let response;
  try {
    response = await fetch(API_ROUTES.nearbyPlaces, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        included_types: includedTypes,
        location: {
          latitude: coords.lat,
          longitude: coords.lng,
        },
        radius: 5000,
        max_results: 5,
      }),
    });
  } catch (error) {
    console.error("[places] Fetch failed before backend response", error);
    throw error;
  }

  console.info("[places] Backend response received", {
    status: response.status,
    ok: response.ok,
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error("[places] Nearby search failed", {
      status: response.status,
      body: errorText,
    });
    throw new Error(`Nearby search failed: ${response.status}`);
  }

  const data = await response.json();
  return { ...data, locationSource: source };
}
