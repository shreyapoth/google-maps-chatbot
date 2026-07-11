export function getCurrentLocation() {
  console.info("[geolocation] Requesting current position");

  if (!navigator.geolocation) {
    console.error("[geolocation] Browser does not support geolocation");
    return Promise.reject(new Error("Geolocation is not supported"));
  }

  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        console.info("[geolocation] Current position received");
        resolve({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
      },
      (error) => {
        console.error("[geolocation] Failed to get current position", error);
        reject(error);
      }
    );
  });
}
