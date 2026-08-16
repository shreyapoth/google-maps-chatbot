import { afterEach, describe, expect, it, vi } from "vitest";
import { sendChatMessage } from "../api/chat";
import { LOCATION_SOURCE } from "../api/geolocation";

function stubDeviceLocation() {
  vi.stubGlobal("navigator", {
    geolocation: {
      getCurrentPosition: vi.fn((success) =>
        success({ coords: { latitude: 30.27, longitude: -97.74 } })
      ),
    },
  });
}

function stubDeniedLocation() {
  vi.stubGlobal("navigator", {
    geolocation: {
      getCurrentPosition: vi.fn((_success, failure) =>
        failure({ code: 1, message: "User denied Geolocation" })
      ),
    },
  });
}

describe("sendChatMessage", () => {
  afterEach(() => {
    sessionStorage.clear();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("posts the message with the caller's coordinates and a thread id", async () => {
    stubDeviceLocation();
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ reply: "Two spots nearby.", thread_id: "thread-1" }),
        })
      )
    );

    const result = await sendChatMessage("find me tacos");
    const body = JSON.parse(fetch.mock.calls[0][1].body);

    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/chat",
      expect.objectContaining({ method: "POST" })
    );
    expect(body.message).toBe("find me tacos");
    expect(body.location).toEqual({ latitude: 30.27, longitude: -97.74 });
    expect(body.thread_id).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    );
    expect(result).toEqual({
      reply: "Two spots nearby.",
      threadId: "thread-1",
      locationSource: LOCATION_SOURCE.DEVICE,
    });
  });

  it("reuses the same thread id for every message in the tab", async () => {
    stubDeviceLocation();
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ reply: "ok", thread_id: "thread-1" }),
        })
      )
    );

    await sendChatMessage("first");
    await sendChatMessage("second");

    const first = JSON.parse(fetch.mock.calls[0][1].body);
    const second = JSON.parse(fetch.mock.calls[1][1].body);
    expect(first.thread_id).toBe(second.thread_id);
  });

  it("reports the fallback location when the browser denies geolocation", async () => {
    stubDeniedLocation();
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ reply: "ok" }) }))
    );

    const result = await sendChatMessage("anything nearby?");

    expect(JSON.parse(fetch.mock.calls[0][1].body).location).toEqual({
      latitude: 37.7749,
      longitude: -122.4194,
    });
    expect(result.locationSource).toBe(LOCATION_SOURCE.FALLBACK);
  });

  it("throws when the backend rejects the request", async () => {
    stubDeviceLocation();
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({ ok: false, status: 502, text: () => Promise.resolve("upstream failed") })
      )
    );

    await expect(sendChatMessage("find me tacos")).rejects.toThrow("Chat request failed: 502");
  });

  it("asks the user to retry when the assistant only timed out", async () => {
    stubDeviceLocation();
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: false,
          status: 504,
          text: () =>
            Promise.resolve(
              JSON.stringify({
                detail: {
                  code: "AGENT_TIMEOUT",
                  message: "Hit a little traffic. Try sending that again?",
                },
              })
            ),
        })
      )
    );

    await expect(sendChatMessage("find me tacos")).rejects.toThrow(
      "Hit a little traffic. Try sending that again?"
    );
  });
});
