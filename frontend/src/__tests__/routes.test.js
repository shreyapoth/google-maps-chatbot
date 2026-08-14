import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { requestDirections } from "../api/routes";

const ROUTE_RESPONSE = { duration_minutes: 12, distance_miles: 3.4, polyline: null };

function stubGeolocation(getCurrentPositionImpl) {
  vi.stubGlobal("navigator", {
    geolocation: { getCurrentPosition: vi.fn(getCurrentPositionImpl) },
  });
}

function stubFetch(response) {
  vi.stubGlobal("fetch", vi.fn(() => Promise.resolve(response)));
}

describe("requestDirections", () => {
  beforeEach(() => {
    vi.spyOn(console, "info").mockImplementation(() => {});
    vi.spyOn(console, "warn").mockImplementation(() => {});
    vi.spyOn(console, "error").mockImplementation(() => {});
    stubGeolocation((success) =>
      success({ coords: { latitude: 47.6062, longitude: -122.3321 } })
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("sends only the coordinates as the origin", async () => {
    stubFetch({ ok: true, status: 200, json: () => Promise.resolve(ROUTE_RESPONSE) });

    await requestDirections("Pike Place Market");

    const [url, request] = fetch.mock.calls[0];
    expect(url).toBe("http://localhost:8000/routes/directions");
    // The backend validates origin as Coordinates, so no location metadata
    // may ride along in the body.
    expect(JSON.parse(request.body)).toEqual({
      origin: { lat: 47.6062, lng: -122.3321 },
      destination: "Pike Place Market",
    });
  });

  it("returns the parsed route on success", async () => {
    stubFetch({ ok: true, status: 200, json: () => Promise.resolve(ROUTE_RESPONSE) });

    await expect(requestDirections("Pike Place Market")).resolves.toEqual(ROUTE_RESPONSE);
  });

  it("throws with the upstream status when the backend fails", async () => {
    stubFetch({ ok: false, status: 502, text: () => Promise.resolve("upstream error") });

    await expect(requestDirections("Pike Place Market")).rejects.toThrow(
      "Route request failed: 502"
    );
  });

  it("falls back to a default origin when the device location is denied", async () => {
    stubGeolocation((_success, failure) => failure({ code: 1, message: "denied" }));
    stubFetch({ ok: true, status: 200, json: () => Promise.resolve(ROUTE_RESPONSE) });

    await requestDirections("Pike Place Market");

    const [, request] = fetch.mock.calls[0];
    expect(JSON.parse(request.body).origin).toEqual({ lat: 37.7749, lng: -122.4194 });
  });
});
