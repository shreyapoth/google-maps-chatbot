import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { LOCATION_SOURCE, getCurrentLocation } from "../api/geolocation";

const SAN_FRANCISCO = { lat: 37.7749, lng: -122.4194 };

function stubGeolocation(getCurrentPositionImpl) {
  const getCurrentPosition = vi.fn(getCurrentPositionImpl);
  vi.stubGlobal("navigator", { geolocation: { getCurrentPosition } });
  return getCurrentPosition;
}

describe("getCurrentLocation", () => {
  beforeEach(() => {
    vi.spyOn(console, "info").mockImplementation(() => {});
    vi.spyOn(console, "warn").mockImplementation(() => {});
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("reports the device position when permission is granted", async () => {
    stubGeolocation((success) =>
      success({ coords: { latitude: 47.6062, longitude: -122.3321 } })
    );

    await expect(getCurrentLocation()).resolves.toEqual({
      coords: { lat: 47.6062, lng: -122.3321 },
      source: LOCATION_SOURCE.DEVICE,
    });
  });

  it("reports a fallback location when permission is denied", async () => {
    stubGeolocation((_success, failure) =>
      failure({ code: 1, message: "User denied Geolocation" })
    );

    await expect(getCurrentLocation()).resolves.toEqual({
      coords: SAN_FRANCISCO,
      source: LOCATION_SOURCE.FALLBACK,
    });
  });

  it("reports a fallback location when the browser has no geolocation support", async () => {
    vi.stubGlobal("navigator", {});

    await expect(getCurrentLocation()).resolves.toEqual({
      coords: SAN_FRANCISCO,
      source: LOCATION_SOURCE.FALLBACK,
    });
  });

  it("asks the browser for a position with a finite timeout", async () => {
    const getCurrentPosition = stubGeolocation((success) =>
      success({ coords: { latitude: 1, longitude: 2 } })
    );

    await getCurrentLocation();

    const [, , options] = getCurrentPosition.mock.calls[0];
    expect(Number.isFinite(options.timeout)).toBe(true);
    expect(options.timeout).toBeGreaterThan(0);
  });

  it("settles instead of hanging when the prompt is never answered", async () => {
    vi.useFakeTimers();
    // Stands in for a browser that honors the timeout option and reports
    // TIMEOUT; without one it would never invoke either callback.
    stubGeolocation((_success, failure, options) => {
      if (Number.isFinite(options?.timeout)) {
        setTimeout(() => failure({ code: 3, message: "Timeout expired" }), options.timeout);
      }
    });

    const pendingLocation = getCurrentLocation();
    await vi.advanceTimersByTimeAsync(60000);

    await expect(pendingLocation).resolves.toEqual({
      coords: SAN_FRANCISCO,
      source: LOCATION_SOURCE.FALLBACK,
    });
  });
});
