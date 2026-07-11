import { getCurrentLocation } from "./geolocation";
import { API_ROUTES } from "./apiRoutes";

export async function requestBasicRoute(destination) {
  const origin = await getCurrentLocation();
  console.info("[routes] Requesting basic route", {
    endpoint: API_ROUTES.basicRoute,
    origin,
    destination,
  });

  let response;
  try {
    response = await fetch(API_ROUTES.basicRoute, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ origin, destination }),
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
