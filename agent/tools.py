import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.getcwd(), "data")
RESTAURANTS_FILE = os.path.join(DATA_DIR, "restaurants.json")
RESERVATIONS_FILE = os.path.join(DATA_DIR, "reservations.json")

def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# ---------------------- TOOL FUNCTIONS -------------------------

def normalize(text):
    return text.lower().strip() if text else None

def search_restaurants(cuisine=None, location=None, guests=None):
    restaurants = load_json(RESTAURANTS_FILE)
    results = []

    cuisine = normalize(cuisine)
    location = normalize(location)

    for r in restaurants:
        rc = normalize(r["cuisine"])
        rl = normalize(r["location"])

        if cuisine and cuisine not in rc:
            continue
        if location and location not in rl:
            continue
        if guests and r["seating_capacity"] < guests:
            continue

        results.append({
            "id": r["id"],
            "name": r["name"],
            "cuisine": r["cuisine"],
            "rating": r["rating"],
            "location": r["location"],
            "available_tables": r["available_tables"]
        })

    return {"restaurants": results}

def recommend_restaurants(cuisine, guests):
    restaurants = load_json(RESTAURANTS_FILE)
    results = []

    cuisine = normalize(cuisine)

    for r in restaurants:
        if (normalize(r["cuisine"]) == cuisine
            and r["available_tables"] > 0
            and r["seating_capacity"] >= guests):
            results.append(r)

    results.sort(key=lambda x: x["rating"], reverse=True)
    return {"results": results[:5]}

def check_availability(restaurant_id, date, time):
    # Validate date format (dd-mm-yyyy)
    try:
        datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        return {"available": False, "error": "Invalid date format. Please use dd-mm-yyyy"}
    
    reservations = load_json(RESERVATIONS_FILE)
    time = time.lower().replace(" ", "")

    for r in reservations:
        rt = r["time"].lower().replace(" ", "")
        if r["restaurant_id"] == restaurant_id and r["date"] == date and rt == time:
            return {"available": False}

    restaurants = load_json(RESTAURANTS_FILE)
    for r in restaurants:
        if r["id"] == restaurant_id and r["available_tables"] > 0:
            return {"available": True}

    return {"available": False}

def create_reservation(user_name, restaurant_id, date, time, guests, phone_number):
    # Validate all required parameters are provided
    if not all([user_name, restaurant_id, date, time, guests, phone_number]):
        return {"success": False, "error": "Missing required booking information"}
    
    # Validate date format (dd-mm-yyyy)
    try:
        datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        return {"success": False, "error": "Invalid date format. Please use dd-mm-yyyy format"}
    
    reservations = load_json(RESERVATIONS_FILE)
    reservation_id = len(reservations) + 1

    new_res = {
        "reservation_id": reservation_id,
        "user_name": user_name,
        "restaurant_id": restaurant_id,
        "date": date,
        "time": time,
        "guests": guests,
        "phone_number": phone_number,
        "created_at": datetime.now().isoformat()
    }

    reservations.append(new_res)
    save_json(RESERVATIONS_FILE, reservations)

    return {"success": True, "reservation": new_res}

def cancel_reservation(reservation_id):
    reservations = load_json(RESERVATIONS_FILE)
    updated = [r for r in reservations if r["reservation_id"] != reservation_id]

    if len(updated) == len(reservations):
        return {"success": False, "message": "Reservation not found"}

    save_json(RESERVATIONS_FILE, updated)
    return {"success": True}

def update_reservation(reservation_id, date=None, time=None, guests=None):
    reservations = load_json(RESERVATIONS_FILE)

    for r in reservations:
        if r["reservation_id"] == reservation_id:
            if date:
                r["date"] = date
            if time:
                r["time"] = time
            if guests:
                r["guests"] = guests

            save_json(RESERVATIONS_FILE, reservations)
            return {"success": True}

    return {"success": False, "message": "Reservation not found"}

def find_restaurant_by_name(restaurant_name):
    """Find restaurant ID by name with fuzzy matching"""
    restaurants = load_json(RESTAURANTS_FILE)
    
    # Clean the input name
    search_name = restaurant_name.lower().strip()
    # Remove common booking words
    search_name = search_name.replace("book", "").replace("table", "").replace("reservation", "").strip()
    
    matches = []
    exact_matches = []
    
    for r in restaurants:
        restaurant_name_lower = r["name"].lower()
        
        # Exact match (case-insensitive)
        if search_name == restaurant_name_lower:
            exact_matches.append({
                "id": r["id"],
                "name": r["name"],
                "cuisine": r["cuisine"],
                "location": r["location"]
            })
        # Fuzzy match - check if search term is in restaurant name OR restaurant name is in search term
        elif (search_name in restaurant_name_lower or 
              any(word in restaurant_name_lower for word in search_name.split() if len(word) > 2)):
            matches.append({
                "id": r["id"],
                "name": r["name"],
                "cuisine": r["cuisine"],
                "location": r["location"]
            })
    
    # Prefer exact matches
    if exact_matches:
        if len(exact_matches) == 1:
            return {"success": True, "restaurant": exact_matches[0]}
        else:
            return {"success": False, "message": "Multiple exact matches found", "matches": exact_matches}
    
    # Use fuzzy matches
    if len(matches) == 1:
        return {"success": True, "restaurant": matches[0]}
    elif len(matches) > 1:
        return {"success": False, "message": "Multiple restaurants found", "matches": matches}
    else:
        return {"success": False, "message": "No restaurant found with that name"}

AVAILABLE_TOOLS = {
    "search_restaurants": search_restaurants,
    "recommend_restaurants": recommend_restaurants,
    "check_availability": check_availability,
    "create_reservation": create_reservation,
    "cancel_reservation": cancel_reservation,
    "update_reservation": update_reservation,
    "find_restaurant_by_name": find_restaurant_by_name
}
