import { getCurrentLocation } from "./geolocation";
import { API_ROUTES } from "./apiRoutes";

export async function requestDirections(destination) {
  const { coords, source } = await getCurrentLocation();
  console.info("[routes] Requesting directions", {
    endpoint: API_ROUTES.directions,
    origin: coords,
    locationSource: source,
    destination,
  });

  let response;
  try {
    response = await fetch(API_ROUTES.directions, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ origin: coords, destination }),
    });
  } catch (error) {
    console.error("[routes] Fetch failed before backend response", error);
    throw error;
  }

  console.info("[routes] Backend response received", {
    status: response.status,
    ok: response.ok,
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error("[routes] Backend route request failed", {
      status: response.status,
      body: errorText,
    });
    throw new Error(`Route request failed: ${response.status}`);
  }

  return response.json();
}
