def google_duration_to_minutes(duration: str) -> int:
    seconds = int(duration.rstrip("s"))
    return round(seconds / 60)
