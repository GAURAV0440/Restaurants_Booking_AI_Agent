import os
import json
import re
from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from agent.prompts import SYSTEM_PROMPT
from agent.tools_schema import TOOL_SCHEMA
from agent.router import execute_tool

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"


# -------------------------------------------------
# UNIVERSAL CLEANER: removes leaks, tool calls, junk
# -------------------------------------------------
def clean_llm_output(text: str) -> str:
    if not isinstance(text, str):
        return text

    # Remove ANY = search_restaurants {..} leaks
    text = re.sub(r'=\s*\w+\s*[{<].*?[}>]', '', text, flags=re.DOTALL)

    # Remove <function> ... </function>
    text = re.sub(r'<function.*?</function>', '', text, flags=re.DOTALL)

    # Remove stray function=name>{..}
    text = re.sub(r'function=\w+>.*?\}', '', text, flags=re.DOTALL)

    # Remove raw JSON blocks ONLY when they look like tool args (with specific patterns)
    text = re.sub(r'\{"cuisine":[^}]*\}', '', text)
    text = re.sub(r'\{"name":[^}]*\}', '', text)
    text = re.sub(r'\{"required":[^}]*\}', '', text)

    # Remove angle brackets completely
    text = re.sub(r'[<>]', '', text)

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# -------------------------------------------------
# TOOL OUTPUT FORMATTER
# -------------------------------------------------
def format_tool_output(name, output):

    # Search / Recommend Restaurants
    if name in ["search_restaurants", "recommend_restaurants"]:
        restaurants = (
            output.get("restaurants")
            or output.get("results")
            or []
        )

        if not restaurants:
            return "No restaurants found for your request."

        text = "Available Restaurants:\n\n"
        for r in restaurants:
            text += (
                f"• {r['name']} (ID: {r['id']})\n"
                f"  Cuisine: {r['cuisine']}\n"
                f"  Rating: {r['rating']}⭐\n"
                f"  Location: {r['location']}\n"
                f"  Available Tables: {r['available_tables']}\n\n"
            )
        return text

    # Availability
    if name == "check_availability":
        return "✔ A table is available at that time." if output.get("available") else "❌ No table available."

    # Reservation
    if name == "create_reservation":
        if output.get("success") and "reservation" in output:
            r = output["reservation"]
            return (
                "✅ Reservation Confirmed!\n\n"
                f"Restaurant ID: {r['restaurant_id']}\n"
                f"Date: {r['date']}\n"
                f"Time: {r['time']}\n"
                f"Guests: {r['guests']}\n"
                f"Phone: {r['phone_number']}\n"
                f"Booked For: {r['user_name']}"
            )
        return "❌ Reservation failed. Please try again."

    # Name Lookup
    if name == "find_restaurant_by_name":
        if output.get("success"):
            r = output["restaurant"]
            return f"Perfect! I found {r['name']} (ID: {r['id']}) in {r['location']}. What's your full name?"
        if output.get("matches"):
            text = "I found multiple matches:\n\n"
            for r in output["matches"]:
                text += f"• {r['name']} (ID: {r['id']}) - {r['location']}\n"
            text += "\nWhich one would you like to book?"
            return text
        return "Restaurant not found. Please try again."

    # Fallback
    return clean_llm_output(json.dumps(output, indent=2))


# -------------------------------------------------
# CALL LLM WITH TOOL SUPPORT
# -------------------------------------------------
def call_llm(messages):
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOL_SCHEMA,
        tool_choice="auto"
    )


# -------------------------------------------------
# MAIN AGENT LOGIC
# -------------------------------------------------
def agent_reply(user_input, history):

    # Build context
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_input})

    # Get LLM response
    response = call_llm(messages)
    choice = response.choices[0]
    msg = choice.message

    # -------------------------------------------------
    # TOOL CALL DETECTED
    # -------------------------------------------------
    if msg.tool_calls:

        tool_call = msg.tool_calls[0]
        tool_name = tool_call.function.name
        raw_args = tool_call.function.arguments

        try:
            raw_args = raw_args.strip()
            raw_args = re.sub(r',\s*}', '}', raw_args)
            raw_args = re.sub(r',\s*]', ']', raw_args)
            args = json.loads(raw_args)

        except Exception:
            return "I couldn't process the booking details. Please repeat."

        # Execute tool safely
        output = execute_tool(tool_name, args)

        # ALWAYS clean tool output
        return clean_llm_output(format_tool_output(tool_name, output))

    # -------------------------------------------------
    # NO TOOL CALL → CHECK FOR HIDDEN TOOL CALLS IN CONTENT
    # -------------------------------------------------
    content = msg.content or ""
    
    # Check if the content contains raw tool calls that should have been proper tool calls
    if any(tool_name in content for tool_name in ["search_restaurants", "create_reservation", "check_availability", "find_restaurant_by_name"]):
        # Try to extract and execute tool calls from content
        
        # Pattern for search_restaurants with cuisine
        if "search_restaurants" in content and "cuisine" in content:
            # Extract cuisine from the content
            cuisine_match = re.search(r'"cuisine":\s*"([^"]+)"', content)
            if cuisine_match:
                cuisine = cuisine_match.group(1)
                output = execute_tool("search_restaurants", {"cuisine": cuisine})
                return format_tool_output("search_restaurants", output)
        
        # Pattern for find_restaurant_by_name
        if "find_restaurant_by_name" in content and "name" in content:
            name_match = re.search(r'"name":\s*"([^"]+)"', content)
            if name_match:
                name = name_match.group(1)
                output = execute_tool("find_restaurant_by_name", {"name": name})
                return format_tool_output("find_restaurant_by_name", output)
    
    # COMPREHENSIVE CUISINE DETECTION - Handle all cuisines properly
    # Define all available cuisines with variations and aliases
    cuisine_mapping = {
        "indian": "Indian", "italian": "Italian", "japanese": "Japanese", "chinese": "Chinese",
        "barbecue": "Barbecue", "bbq": "Barbecue", "seafood": "Seafood", "mexican": "Mexican",
        "greek": "Greek", "french": "French", "steakhouse": "Steakhouse", "steak": "Steakhouse",
        "vegetarian": "Vegetarian", "veg": "Vegetarian", "korean": "Korean", "thai": "Thai",
        "mediterranean": "Mediterranean", "fast food": "Fast Food", "fastfood": "Fast Food",
        "desserts": "Desserts", "dessert": "Desserts", "north indian": "North Indian",
        "south indian": "South Indian", "turkish": "Turkish", "turkey": "Turkish",
        "moroccan": "Moroccan", "american": "American", "middle eastern": "Middle Eastern",
        "spanish": "Spanish", "healthy": "Healthy", "mughlai": "Mughlai", "african": "African",
        "russian": "Russian", "persian": "Persian", "iranian": "Persian", "brazilian": "Brazilian",
        "vietnamese": "Vietnamese", "caribbean": "Caribbean", "german": "German",
        "nepalese": "Nepalese", "nepal": "Nepalese", "indonesian": "Indonesian",
        "cuban": "Cuban", "swedish": "Swedish", "ethiopian": "Ethiopian",
        "lebanese": "Lebanese", "lebanon": "Lebanese", "hawaiian": "Hawaiian",
        "singaporean": "Singaporean", "austrian": "Austrian", "irish": "Irish",
        "polish": "Polish", "syrian": "Syrian", "ukrainian": "Ukrainian",
        "continental": "Continental", "sushi": "Japanese", "pasta": "Italian",
        "pizza": "Italian", "noodles": "Chinese", "curry": "Indian", "taco": "Mexican",
        "pho": "Vietnamese", "kebab": "Turkish", "tapas": "Spanish"
    }
    
    # Check if user is asking for any cuisine (including variations)
    user_lower = user_input.lower()
    for cuisine_key, cuisine_value in cuisine_mapping.items():
        if (cuisine_key in user_lower or 
            (cuisine_key + " restaurant") in user_lower or 
            (cuisine_key + " food") in user_lower or
            (cuisine_key + " place") in user_lower or
            ("book " + cuisine_key) in user_lower or
            ("table " + cuisine_key) in user_lower):
            
            output = execute_tool("search_restaurants", {"cuisine": cuisine_value})
            return format_tool_output("search_restaurants", output)
    
    # Also handle booking requests with guest count
    booking_patterns = [
        r"book.*?table.*?for\s+(\d+).*?(at|in)\s+([a-zA-Z\s]+)(?:\s+restaurant)?",
        r"table.*?for\s+(\d+).*?(at|in)\s+([a-zA-Z\s]+)(?:\s+restaurant)?",
        r"reservation.*?for\s+(\d+).*?(at|in)\s+([a-zA-Z\s]+)(?:\s+restaurant)?"
    ]
    
    for pattern in booking_patterns:
        match = re.search(pattern, user_lower)
        if match:
            guests = int(match.group(1))
            restaurant_type = match.group(3).strip()
            
            # Check if restaurant_type matches any cuisine
            for cuisine_key, cuisine_value in cuisine_mapping.items():
                if cuisine_key in restaurant_type:
                    output = execute_tool("search_restaurants", {"cuisine": cuisine_value, "guests": guests})
                    return format_tool_output("search_restaurants", output)
    
    clean = clean_llm_output(content)

    # Fallback if empty
    if not clean:
        return "I can help you book a restaurant. What cuisine would you like?"

    return clean
