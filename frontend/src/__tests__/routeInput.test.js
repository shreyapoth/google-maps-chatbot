import { describe, expect, it } from "vitest";
import { getDestinationFromInput } from "../utils/routeInput";

describe("getDestinationFromInput", () => {
  it.each([
    ["current location to Pike Place Market", "Pike Place Market"],
    ["from current location to Pike Place Market", "Pike Place Market"],
    ["from my current location to Pike Place Market", "Pike Place Market"],
    ["My Current Location To Pike Place Market", "Pike Place Market"],
    ["  current location to  Pike Place Market  ", "Pike Place Market"],
  ])("strips the current-location prefix from %j", (input, expected) => {
    expect(getDestinationFromInput(input)).toBe(expected);
  });

  it("leaves a plain destination untouched", () => {
    expect(getDestinationFromInput("  Pike Place Market ")).toBe("Pike Place Market");
  });

  it("returns an empty string for blank input", () => {
    expect(getDestinationFromInput("   ")).toBe("");
  });

  it("keeps a destination that merely mentions the phrase later", () => {
    expect(getDestinationFromInput("Museum of Current Location")).toBe(
      "Museum of Current Location"
    );
  });
});
