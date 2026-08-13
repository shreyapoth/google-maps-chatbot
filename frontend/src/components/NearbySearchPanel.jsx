import { useState } from "react";
import { requestNearbyPlaces } from "../api/places";
import { requestDirections } from "../api/routes";
import PlaceCard from "./PlaceCard";

export default function NearbySearchPanel({ onResult }) {
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(false);
  const [routingPlaceId, setRoutingPlaceId] = useState(null);
  const [error, setError] = useState("");

  async function handleNearbySearch() {
    setLoading(true);
    setError("");
    setPlaces([]);

    try {
      const data = await requestNearbyPlaces(["restaurant"]);
      setPlaces(data.places ?? []);
      onResult({
        message: `Found ${data.places?.length ?? 0} nearby restaurants. Pick one for directions.`,
        routes: [],
      });
    } catch (nearbyError) {
      console.error("[nearby] Search failed", nearbyError);
      setError(nearbyError.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleGetDirections(place) {
    const destination = place.formatted_address || place.name;
    setRoutingPlaceId(place.place_id);
    setError("");

    try {
      const route = await requestDirections(destination);
      onResult({
        message: `Route to ${destination}`,
        routes: [route],
      });
    } catch (routeError) {
      console.error("[nearby] Directions failed", routeError);
      setError(routeError.message);
    } finally {
      setRoutingPlaceId(null);
    }
  }

  return (
    <section className="nearby-panel">
      <p className="nearby-label">Temporary nearby search test</p>
      <button type="button" onClick={handleNearbySearch} disabled={loading || routingPlaceId}>
        {loading ? "Searching..." : "Find nearby restaurants"}
      </button>

      {error && <p className="error">{error}</p>}

      <div className="nearby-results">
        {places.map((place) => (
          <div key={place.place_id} className="nearby-result">
            <PlaceCard place={place} />
            <button
              type="button"
              onClick={() => handleGetDirections(place)}
              disabled={loading || Boolean(routingPlaceId)}
            >
              {routingPlaceId === place.place_id ? "Routing..." : "Get directions"}
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}
