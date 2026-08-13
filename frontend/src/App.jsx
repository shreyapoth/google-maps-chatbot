import { useState } from "react";
import ChatPanel from "./components/ChatPanel";
import MapView from "./components/MapView";
import NearbySearchPanel from "./components/NearbySearchPanel";
import RouteCard from "./components/RouteCard";

export default function App() {
  const [result, setResult] = useState({
    message: "Enter a destination to route from your current location.",
    routes: [],
  });

  return (
    <main className="app">
      <section className="panel">
        <h1>Google Maps Chatbot</h1>
        <p>{result.message}</p>
        <ChatPanel onResult={setResult} />
        <NearbySearchPanel onResult={setResult} />
        {result.routes.map((route, index) => (
          <RouteCard key={index} route={route} />
        ))}
      </section>
      <MapView />
    </main>
  );
}
