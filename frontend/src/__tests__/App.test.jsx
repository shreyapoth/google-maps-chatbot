import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import App from "../App";

describe("App", () => {
  afterEach(() => {
    cleanup();
    sessionStorage.clear();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("renders the chatbot shell", () => {
    render(<App />);

    expect(screen.getByText("Google Maps Chatbot")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("Ask about places or directions...")).toBeInTheDocument();
  });

  it("sends a chat message with the device location", async () => {
    const getCurrentPosition = vi.fn((success) =>
      success({ coords: { latitude: 47.6062, longitude: -122.3321 } })
    );
    vi.stubGlobal("navigator", { geolocation: { getCurrentPosition } });
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ reply: "Pike Place Market is 12 minutes away." }),
        })
      )
    );

    render(<App />);
    fireEvent.change(screen.getByPlaceholderText("Ask about places or directions..."), {
      target: { value: "how long to Pike Place Market?" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    const body = JSON.parse(fetch.mock.calls[0][1].body);
    expect(body.message).toBe("how long to Pike Place Market?");
    expect(body.location).toEqual({ latitude: 47.6062, longitude: -122.3321 });
    expect(body.thread_id).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    );
    expect(
      await screen.findByText("Pike Place Market is 12 minutes away.")
    ).toBeInTheDocument();
  });
});
