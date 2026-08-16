import { useState } from "react";
import { sendChatMessage } from "../api/chat";
import { FALLBACK_LOCATION_LABEL, LOCATION_SOURCE } from "../api/geolocation";

const SUGGESTIONS = [
  "Coffee near me",
  "Find a gas station",
  "How long to the airport?",
];

export default function ChatPanel() {
  const [message, setMessage] = useState("");
  const [transcript, setTranscript] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [usedFallbackLocation, setUsedFallbackLocation] = useState(false);

  async function ask(question) {
    if (!question || loading) return;

    console.info("[chat] Asking the assistant", { question });
    setTranscript((entries) => [...entries, { role: "user", text: question }]);
    setMessage("");
    setLoading(true);
    setError("");

    try {
      const { reply, locationSource } = await sendChatMessage(question);
      setUsedFallbackLocation(locationSource === LOCATION_SOURCE.FALLBACK);
      setTranscript((entries) => [...entries, { role: "assistant", text: reply }]);
    } catch (chatError) {
      console.error("[chat] Message failed", chatError);
      setError(chatError.message);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    ask(message.trim());
  }

  return (
    <section className="chat-panel">
      <div className="chat-transcript" aria-live="polite">
        {transcript.length === 0 && !loading && (
          <div className="chat-empty">
            <p className="chat-empty-title">Where would you like to go?</p>
            <p className="chat-empty-body">
              Ask for places nearby or directions from where you are.
            </p>
            <div className="chat-suggestions">
              {SUGGESTIONS.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  className="chip"
                  onClick={() => ask(suggestion)}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {transcript.map((entry, index) => (
          <p key={index} className={`chat-message chat-message-${entry.role}`}>
            {entry.text}
          </p>
        ))}

        {loading && (
          <p className="chat-message chat-message-assistant chat-pending">
            <span className="dot" />
            <span className="dot" />
            <span className="dot" />
          </p>
        )}
      </div>

      {usedFallbackLocation && (
        <p className="location-notice">
          Couldn&apos;t get your location, so answers are based on {FALLBACK_LOCATION_LABEL}.
        </p>
      )}

      {error && <p className="error">{error}</p>}

      <form className="composer" onSubmit={handleSubmit}>
        <span className="composer-icon" aria-hidden="true" />
        <input
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ask about places or directions..."
          aria-label="Message"
        />
        <button className="composer-send" aria-label="Send" disabled={loading} />
      </form>
    </section>
  );
}
