METERS_PER_MILE = 1609.344

def meters_to_miles(meters: int) -> float:
    return round(meters / METERS_PER_MILE, 1)
