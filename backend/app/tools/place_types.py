import ast
import json

# Google Places (New) only accepts included types from its own table and rejects
# anything else with INVALID_ARGUMENT, so the nearby tool checks a requested type
# against this set and falls back to a text search instead of failing the call.
# Every value below was verified against places:searchNearby.
PLACE_TYPES = frozenset(
    {
        "restaurant", "cafe", "coffee_shop", "bar", "bakery",
        "meal_takeaway", "meal_delivery", "fast_food_restaurant",
        "breakfast_restaurant", "brunch_restaurant", "sandwich_shop",
        "pizza_restaurant", "hamburger_restaurant", "mexican_restaurant",
        "italian_restaurant", "chinese_restaurant", "japanese_restaurant",
        "sushi_restaurant", "ramen_restaurant", "thai_restaurant",
        "indian_restaurant", "korean_restaurant", "vietnamese_restaurant",
        "mediterranean_restaurant", "greek_restaurant", "french_restaurant",
        "seafood_restaurant", "steak_house", "barbecue_restaurant",
        "vegetarian_restaurant", "vegan_restaurant", "ice_cream_shop",
        "dessert_shop", "juice_shop", "tea_house", "night_club",
        "gas_station", "electric_vehicle_charging_station", "parking",
        "grocery_store", "supermarket", "convenience_store", "liquor_store",
        "pharmacy", "drugstore", "hospital", "atm", "bank",
        "hotel", "motel", "gym", "park", "dog_park",
        "movie_theater", "museum", "art_gallery", "tourist_attraction", "zoo",
        "shopping_mall", "clothing_store", "book_store", "hardware_store",
        "car_repair", "car_wash", "laundry", "hair_salon", "spa",
        "library", "post_office", "police",
    }
)


def normalize_place_types(value: object) -> list[str]:
    # Llama 3.1 8B often sends "['gas_station']" as a string instead of a list.
    if isinstance(value, str):
        items = _split_place_type_string(value)
    elif isinstance(value, (list, tuple)):
        items = value
    elif value is None:
        items = []
    else:
        items = [value]

    return [item for item in (_clean_place_type(entry) for entry in items) if item]


def _split_place_type_string(value: str) -> list:
    stripped = value.strip()
    if not stripped:
        return []

    if stripped[0] in "[(":
        try:
            parsed = ast.literal_eval(stripped)
            if isinstance(parsed, (list, tuple)):
                return list(parsed)
        except (ValueError, SyntaxError):
            pass

        try:
            parsed = json.loads(stripped.replace("'", '"'))
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            pass

    return [part.strip() for part in stripped.split(",") if part.strip()]


def _clean_place_type(value: object) -> str:
    return str(value).strip().strip("'\"")

