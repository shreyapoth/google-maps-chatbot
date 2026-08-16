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
