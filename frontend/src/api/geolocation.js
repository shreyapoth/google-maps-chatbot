const DEFAULT_LOCATION = {
  lat: 37.7749,
  lng: -122.4194,
};

export function getCurrentLocation() {
  console.info("[geolocation] Requesting current position");

  if (!navigator.geolocation) {
    console.warn(
      "[geolocation] Browser does not support geolocation; using San Francisco default",
      DEFAULT_LOCATION
    );
    return Promise.resolve(DEFAULT_LOCATION);
  }

  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        console.info("[geolocation] Current position received");
        resolve({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
      },
      (error) => {
        console.warn(
          "[geolocation] Failed to get current position; using San Francisco default",
          error,
          DEFAULT_LOCATION
        );
        resolve(DEFAULT_LOCATION);
      }
    );
  });
}
