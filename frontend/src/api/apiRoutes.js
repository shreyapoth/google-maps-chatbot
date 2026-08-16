const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const API_ROUTES = {
  chat: `${API_URL}/chat`,
  directions: `${API_URL}/routes/directions`,
  nearbyPlaces: `${API_URL}/places/nearby`,
};
