import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import NearbySearchPanel from "../components/NearbySearchPanel";

const FALLBACK_NOTICE = /these results are near San Francisco/i;

function stubNearbyPlacesResponse() {
  vi.stubGlobal(
    "fetch",
    vi.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        json: () =>
          Promise.resolve({
            places: [
              {
                place_id: "ChIJ123",
                name: "Test Cafe",
                formatted_address: "1 Main St",
                location: { latitude: 1, longitude: 2 },
                primary_type: "cafe",
                types: ["cafe"],
              },
            ],
          }),
      })
    )
  );
}

function stubGeolocation(getCurrentPositionImpl) {
  vi.stubGlobal("navigator", {
    geolocation: { getCurrentPosition: vi.fn(getCurrentPositionImpl) },
  });
}

describe("NearbySearchPanel", () => {
  beforeEach(() => {
    vi.spyOn(console, "info").mockImplementation(() => {});
    vi.spyOn(console, "warn").mockImplementation(() => {});
    stubNearbyPlacesResponse();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("warns that results are not nearby when the device location is unavailable", async () => {
    stubGeolocation((_success, failure) => failure({ code: 1, message: "denied" }));
    const onResult = vi.fn();

    render(<NearbySearchPanel onResult={onResult} />);
    fireEvent.click(screen.getByRole("button", { name: "Find nearby restaurants" }));

    await waitFor(() => expect(screen.getByText(FALLBACK_NOTICE)).toBeInTheDocument());
    expect(onResult).toHaveBeenCalledWith({
      message: "Found 1 restaurants near San Francisco. Pick one for directions.",
      routes: [],
    });

    const [, request] = fetch.mock.calls[0];
    expect(JSON.parse(request.body).location).toEqual({
      latitude: 37.7749,
      longitude: -122.4194,
    });
  });

  it("does not warn when the device location is used", async () => {
    stubGeolocation((success) =>
      success({ coords: { latitude: 47.6062, longitude: -122.3321 } })
    );
    const onResult = vi.fn();

    render(<NearbySearchPanel onResult={onResult} />);
    fireEvent.click(screen.getByRole("button", { name: "Find nearby restaurants" }));

    await waitFor(() => expect(screen.getByText("Test Cafe")).toBeInTheDocument());
    expect(screen.queryByText(FALLBACK_NOTICE)).not.toBeInTheDocument();
    expect(onResult).toHaveBeenCalledWith({
      message: "Found 1 restaurants nearby. Pick one for directions.",
      routes: [],
    });
  });

  it("stops showing the loading state after a failed search", async () => {
    stubGeolocation((success) =>
      success({ coords: { latitude: 47.6062, longitude: -122.3321 } })
    );
    vi.spyOn(console, "error").mockImplementation(() => {});
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve({ ok: false, status: 502, text: () => Promise.resolve("boom") }))
    );

    render(<NearbySearchPanel onResult={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "Find nearby restaurants" }));

    await waitFor(() =>
      expect(screen.getByText("Nearby search failed: 502")).toBeInTheDocument()
    );
    expect(screen.getByRole("button", { name: "Find nearby restaurants" })).toBeEnabled();
  });
});
