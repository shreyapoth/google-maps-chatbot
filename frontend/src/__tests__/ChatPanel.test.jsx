import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import ChatPanel from "../components/ChatPanel";

function stubDeviceLocation() {
  vi.stubGlobal("navigator", {
    geolocation: {
      getCurrentPosition: vi.fn((success) =>
        success({ coords: { latitude: 30.27, longitude: -97.74 } })
      ),
    },
  });
}

function askQuestion(question) {
  fireEvent.change(screen.getByPlaceholderText("Ask about places or directions..."), {
    target: { value: question },
  });
  fireEvent.click(screen.getByRole("button", { name: "Send" }));
}

describe("ChatPanel", () => {
  afterEach(() => {
    cleanup();
    sessionStorage.clear();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it("shows the question and the assistant reply", async () => {
    stubDeviceLocation();
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ reply: "Torchy's is 4 minutes away." }),
        })
      )
    );

    render(<ChatPanel />);
    askQuestion("tacos near me");

    expect(screen.getByText("tacos near me")).toBeInTheDocument();
    expect(await screen.findByText("Torchy's is 4 minutes away.")).toBeInTheDocument();
  });

  it("clears the input and re-enables the button after a reply", async () => {
    stubDeviceLocation();
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ reply: "ok" }) }))
    );

    render(<ChatPanel />);
    askQuestion("tacos near me");

    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Send" })).not.toBeDisabled()
    );
    expect(screen.getByPlaceholderText("Ask about places or directions...")).toHaveValue("");
  });

  it("surfaces a backend failure without losing the question", async () => {
    stubDeviceLocation();
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({ ok: false, status: 502, text: () => Promise.resolve("upstream failed") })
      )
    );

    render(<ChatPanel />);
    askQuestion("tacos near me");

    expect(await screen.findByText("Chat request failed: 502")).toBeInTheDocument();
    expect(screen.getByText("tacos near me")).toBeInTheDocument();
  });

  it("asks the user to retry after a timeout", async () => {
    stubDeviceLocation();
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: false,
          status: 504,
          text: () =>
            Promise.resolve(JSON.stringify({ detail: { code: "AGENT_TIMEOUT" } })),
        })
      )
    );

    render(<ChatPanel />);
    askQuestion("tacos near me");

    expect(
      await screen.findByText("Hit a little traffic. Try sending that again?")
    ).toBeInTheDocument();
    expect(screen.getByText("tacos near me")).toBeInTheDocument();
  });

  it("warns when the reply is based on the fallback location", async () => {
    vi.stubGlobal("navigator", {
      geolocation: {
        getCurrentPosition: vi.fn((_success, failure) =>
          failure({ code: 1, message: "User denied Geolocation" })
        ),
      },
    });
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ reply: "ok" }) }))
    );

    render(<ChatPanel />);
    askQuestion("anything nearby?");

    expect(await screen.findByText(/based on San Francisco/)).toBeInTheDocument();
  });

  it("sends a suggestion when one is clicked", async () => {
    stubDeviceLocation();
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({ ok: true, json: () => Promise.resolve({ reply: "Two cafes nearby." }) })
      )
    );

    render(<ChatPanel />);
    fireEvent.click(screen.getByRole("button", { name: "Coffee near me" }));

    expect(await screen.findByText("Two cafes nearby.")).toBeInTheDocument();
    expect(JSON.parse(fetch.mock.calls[0][1].body).message).toBe("Coffee near me");
  });

  it("hides the suggestions once the conversation starts", async () => {
    stubDeviceLocation();
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.resolve({ ok: true, json: () => Promise.resolve({ reply: "ok" }) }))
    );

    render(<ChatPanel />);
    askQuestion("tacos near me");

    await waitFor(() => expect(screen.getByText("ok")).toBeInTheDocument());
    expect(screen.queryByRole("button", { name: "Coffee near me" })).not.toBeInTheDocument();
  });

  it("ignores an empty submission", () => {
    stubDeviceLocation();
    vi.stubGlobal("fetch", vi.fn());

    render(<ChatPanel />);
    askQuestion("   ");

    expect(fetch).not.toHaveBeenCalled();
  });
});
