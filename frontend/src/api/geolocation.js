const DEFAULT_LOCATION = {
  lat: 37.7749,
  lng: -122.4194,
};

// Without an explicit timeout the browser waits forever when the user
// neither accepts nor dismisses the permission prompt.
const GEOLOCATION_OPTIONS = {
  timeout: 10000,
  maximumAge: 60000,
};

export const FALLBACK_LOCATION_LABEL = "San Francisco";

export const LOCATION_SOURCE = {
  DEVICE: "device",
  FALLBACK: "fallback",
};

export function getCurrentLocation() {
  console.info("[geolocation] Requesting current position");

  if (!navigator.geolocation) {
    console.warn(
      "[geolocation] Browser does not support geolocation; using San Francisco default",
      DEFAULT_LOCATION
    );
    return Promise.resolve({
      coords: DEFAULT_LOCATION,
      source: LOCATION_SOURCE.FALLBACK,
    });
  }

  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        console.info("[geolocation] Current position received");
        resolve({
          coords: {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          },
          source: LOCATION_SOURCE.DEVICE,
        });
      },
      (error) => {
        console.warn(
          "[geolocation] Failed to get current position; using San Francisco default",
          { code: error.code, message: error.message },
          DEFAULT_LOCATION
        );
        resolve({
          coords: DEFAULT_LOCATION,
          source: LOCATION_SOURCE.FALLBACK,
        });
      },
      GEOLOCATION_OPTIONS
    );
  });
}
