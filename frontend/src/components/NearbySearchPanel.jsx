import { useState } from "react";
import { FALLBACK_LOCATION_LABEL, LOCATION_SOURCE } from "../api/geolocation";
import { requestNearbyPlaces } from "../api/places";
import { requestDirections } from "../api/routes";
import PlaceCard from "./PlaceCard";

export default function NearbySearchPanel({ onResult }) {
  const [places, setPlaces] = useState([]);
  const [loading, setLoading] = useState(false);
  const [routingPlaceId, setRoutingPlaceId] = useState(null);
  const [usedFallbackLocation, setUsedFallbackLocation] = useState(false);
  const [error, setError] = useState("");

  async function handleNearbySearch() {
    setLoading(true);
    setError("");
    setPlaces([]);
    setUsedFallbackLocation(false);

    try {
      const data = await requestNearbyPlaces(["restaurant"]);
      const isFallbackLocation = data.locationSource === LOCATION_SOURCE.FALLBACK;
      const searchArea = isFallbackLocation ? `near ${FALLBACK_LOCATION_LABEL}` : "nearby";

      setPlaces(data.places ?? []);
      setUsedFallbackLocation(isFallbackLocation);
      onResult({
        message: `Found ${data.places?.length ?? 0} restaurants ${searchArea}. Pick one for directions.`,
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

      {usedFallbackLocation && (
        <p className="location-notice">
          Couldn&apos;t get your location, so these results are near {FALLBACK_LOCATION_LABEL}.
        </p>
      )}

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
