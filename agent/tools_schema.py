TOOL_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "search_restaurants",
            "description": "Find restaurants by cuisine, area, or guest requirement. MUST be used for: 'show Italian restaurants', 'list Mexican restaurants', 'find Indian food'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cuisine": {"type": "string", "description": "Cuisine mentioned by the user such as Italian, Mexican, Chinese, Indian."},
                    "location": {"type": "string", "description": "Area or city."},
                    "guests": {"type": "integer", "description": "Minimum seating capacity."}
                },
                "required": ["cuisine"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_restaurants",
            "description": "Return top rated restaurants for a cuisine and number of guests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cuisine": {"type": "string"},
                    "guests": {"type": "integer"}
                },
                "required": ["cuisine", "guests"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check table availability for a restaurant at date + time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_id": {"type": "integer", "description": "ID of the restaurant"},
                    "date": {"type": "string", "description": "Date in dd-mm-yyyy format (e.g., 25-12-2025)"},
                    "time": {"type": "string", "description": "Time in HH:MM format or with AM/PM"}
                },
                "required": ["restaurant_id", "date", "time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_reservation",
            "description": "Create final reservation after collecting all required details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_name": {"type": "string", "description": "Full name of the person making the reservation"},
                    "restaurant_id": {"type": "integer", "description": "ID of the restaurant from search results"},
                    "date": {"type": "string", "description": "Date in dd-mm-yyyy format (e.g., 25-12-2025)"},
                    "time": {"type": "string", "description": "Time in HH:MM format or with AM/PM"},
                    "guests": {"type": "integer", "description": "Number of guests for the reservation"},
                    "phone_number": {"type": "string", "description": "Phone number with country code (e.g., +91-9876543210)"}
                },
                "required": ["user_name", "restaurant_id", "date", "time", "guests", "phone_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_reservation",
            "description": "Cancel a reservation using reservation_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reservation_id": {"type": "integer"}
                },
                "required": ["reservation_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_reservation",
            "description": "Update date, time, or guest count.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reservation_id": {"type": "integer"},
                    "date": {"type": "string"},
                    "time": {"type": "string"},
                    "guests": {"type": "integer"}
                },
                "required": ["reservation_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_restaurant_by_name",
            "description": "Find restaurant ID by name when user mentions a specific restaurant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_name": {"type": "string"}
                },
                "required": ["restaurant_name"]
            }
        }
    }
]
