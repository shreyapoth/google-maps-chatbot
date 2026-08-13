import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../App";

describe("App", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("renders the chatbot shell", () => {
    render(<App />);

    expect(screen.getByText("Google Maps Chatbot")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Enter a destination...")).toBeInTheDocument();
  });

  it("uses device location when requesting a route", async () => {
    const getCurrentPosition = vi.fn((success) =>
      success({ coords: { latitude: 47.6062, longitude: -122.3321 } })
    );
    vi.stubGlobal("navigator", { geolocation: { getCurrentPosition } });
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              duration_minutes: 12,
              distance_miles: 3.4,
              polyline: null,
            }),
        })
      )
    );

    render(<App />);
    fireEvent.change(screen.getByPlaceholderText("Enter a destination..."), {
      target: { value: "current location to Pike Place Market" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Find Route" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    expect(fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/routes/directions",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          origin: { lat: 47.6062, lng: -122.3321 },
          destination: "Pike Place Market",
        }),
      })
    );
  });
});
