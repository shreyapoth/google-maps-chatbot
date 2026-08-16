import ChatPanel from "./components/ChatPanel";
import MapView from "./components/MapView";

export default function App() {
  return (
    <main className="app">
      <aside className="sidebar">
        <header className="sidebar-header">
          <span className="brand-mark" aria-hidden="true" />
          <h1>Google Maps Chatbot</h1>
        </header>
        <ChatPanel />
      </aside>
      <MapView />
    </main>
  );
}
