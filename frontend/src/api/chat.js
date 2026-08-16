import { getCurrentLocation } from "./geolocation";
import { API_ROUTES } from "./apiRoutes";

const THREAD_STORAGE_KEY = "maps-chat-thread-id";

export function getChatThreadId() {
  const existing = sessionStorage.getItem(THREAD_STORAGE_KEY);
  if (existing) return existing;

  const threadId = crypto.randomUUID();
  sessionStorage.setItem(THREAD_STORAGE_KEY, threadId);
  return threadId;
}

export async function sendChatMessage(message) {
  const threadId = getChatThreadId();
  const { coords, source } = await getCurrentLocation();
  console.info("[chat] Sending message", {
    endpoint: API_ROUTES.chat,
    threadId,
    coords,
    locationSource: source,
  });

  let response;
  try {
    response = await fetch(API_ROUTES.chat, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        thread_id: threadId,
        location: {
          latitude: coords.lat,
          longitude: coords.lng,
        },
      }),
    });
  } catch (error) {
    console.error("[chat] Fetch failed before backend response", error);
    throw error;
  }

  console.info("[chat] Backend response received", {
    status: response.status,
    ok: response.ok,
  });

  if (!response.ok) {
    const errorText = await response.text();
    console.error("[chat] Chat request failed", {
      status: response.status,
      body: errorText,
    });
    throw new Error(messageForFailedChat(response.status, errorText));
  }

  const data = await response.json();
  return { reply: data.reply, threadId: data.thread_id, locationSource: source };
}

function messageForFailedChat(status, errorText) {
  // A 504 is only the clock. NVIDIA often answers on the next try, so don't
  // present it as a broken request.
  if (status === 504 || errorCode(errorText) === "AGENT_TIMEOUT") {
    return "Hit a little traffic. Try sending that again?";
  }

  return `Chat request failed: ${status}`;
}

function errorCode(errorText) {
  try {
    return JSON.parse(errorText)?.detail?.code;
  } catch {
    return undefined;
  }
}
