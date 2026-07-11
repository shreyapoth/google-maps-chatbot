const CURRENT_LOCATION_PREFIX = /^(from\s+)?(my\s+)?current\s+location\s+to\s+/i;

export function getDestinationFromInput(input) {
  return input.trim().replace(CURRENT_LOCATION_PREFIX, "").trim();
}
