import { useState } from "react";
import { requestDirections } from "../api/routes";
import { getDestinationFromInput } from "../utils/routeInput";

export default function ChatPanel({ onResult }) {
  const [destination, setDestination] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    const routeDestination = getDestinationFromInput(destination);
    if (!routeDestination) return;
    console.info("[chat] Finding route", { input: destination, routeDestination });

    setLoading(true);
    setError("");

    try {
      const route = await requestDirections(routeDestination);
      onResult({
        message: `Route to ${routeDestination}`,
        routes: [route],
      });
      setDestination("");
    } catch (routeError) {
      console.error("[chat] Route lookup failed", routeError);
      setError(routeError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <form className="chat" onSubmit={handleSubmit}>
        <input
          value={destination}
          onChange={(event) => setDestination(event.target.value)}
          placeholder="Enter a destination..."
        />
        <button disabled={loading}>{loading ? "Finding..." : "Find Route"}</button>
      </form>
      {error && <p className="error">{error}</p>}
    </>
  );
}
