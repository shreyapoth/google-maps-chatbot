def google_duration_to_minutes(duration: str) -> int:
    seconds = float(duration.removesuffix("s"))
    return round(seconds / 60)
