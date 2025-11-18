import os
import json
import re
from dotenv import load_dotenv
load_dotenv()

from groq import Groq
from groq import BadRequestError
from agent.prompts import SYSTEM_PROMPT
from agent.tools_schema import TOOL_SCHEMA
from agent.router import execute_tool

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

def clean_llm_output(text: str) -> str:
    if not isinstance(text, str):
        return text

    text = re.sub(r'=\s*\w+\s*[{<].*?[}>]', '', text, flags=re.DOTALL)
    text = re.sub(r'<function.*?</function>', '', text, flags=re.DOTALL)
    text = re.sub(r'function=\w+>.*?\}', '', text, flags=re.DOTALL)
    text = re.sub(r'\{"cuisine":[^}]*\}', '', text)
    text = re.sub(r'\{"name":[^}]*\}', '', text)
    text = re.sub(r'\{"required":[^}]*\}', '', text)
    text = re.sub(r'[<>]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def format_tool_output(name, output):

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

    if name == "check_availability":
        return "✔ A table is available at that time." if output.get("available") else "❌ No table available."

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

    return clean_llm_output(json.dumps(output, indent=2))


def call_llm(messages):
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOL_SCHEMA,
        tool_choice="auto"
    )


def handle_cuisine_request_fallback(user_input):
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
        "polish": "Polish", "syrian": "Syrian", "ukrainian": "Ukrainian"
    }
    
    user_lower = user_input.lower()
    
    for cuisine_key, cuisine_value in cuisine_mapping.items():
        if cuisine_key in user_lower:
            output = execute_tool("search_restaurants", {"cuisine": cuisine_value})
            return format_tool_output("search_restaurants", output)
    
    return "I can help you find restaurants. What type of cuisine would you like?"


def agent_reply(user_input, history):

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_input})

    try:
        response = call_llm(messages)
        choice = response.choices[0]
        msg = choice.message
    except BadRequestError as e:
        error_msg = str(e)
        if "tool_use_failed" in error_msg or "tool call validation failed" in error_msg:
            return handle_cuisine_request_fallback(user_input)
        else:
            return "I'm having trouble processing your request. Please try again."
    except Exception as e:
        return "I'm having trouble processing your request. Please try again."

    if msg.tool_calls:

        tool_call = msg.tool_calls[0]
        tool_name = tool_call.function.name
        raw_args = tool_call.function.arguments

        try:
            raw_args = raw_args.strip()
            raw_args = re.sub(r',\s*}', '}', raw_args)
            raw_args = re.sub(r',\s*]', ']', raw_args)
            args = json.loads(raw_args)
            
            args = {k: v for k, v in args.items() if v is not None}
            
            if tool_name in ["create_reservation", "check_availability", "cancel_reservation"]:
                if "restaurant_id" in args and isinstance(args["restaurant_id"], str):
                    args["restaurant_id"] = int(args["restaurant_id"])
                if "guests" in args and isinstance(args["guests"], str):
                    args["guests"] = int(args["guests"])
                if "reservation_id" in args and isinstance(args["reservation_id"], str):
                    args["reservation_id"] = int(args["reservation_id"])
            
            if tool_name == "search_restaurants":
                if "guests" in args and isinstance(args["guests"], str):
                    args["guests"] = int(args["guests"])

        except Exception as e:
            return "I couldn't process the booking details. Please repeat."

        output = execute_tool(tool_name, args)

        return clean_llm_output(format_tool_output(tool_name, output))

    content = msg.content or ""
    
    if any(tool_name in content for tool_name in ["search_restaurants", "create_reservation", "check_availability", "find_restaurant_by_name"]):
        
        if "search_restaurants" in content and "cuisine" in content:
            cuisine_match = re.search(r'"cuisine":\s*"([^"]+)"', content)
            if cuisine_match:
                cuisine = cuisine_match.group(1)
                output = execute_tool("search_restaurants", {"cuisine": cuisine})
                return format_tool_output("search_restaurants", output)
        
        if "find_restaurant_by_name" in content and "name" in content:
            name_match = re.search(r'"name":\s*"([^"]+)"', content)
            if name_match:
                name = name_match.group(1)
                output = execute_tool("find_restaurant_by_name", {"name": name})
                return format_tool_output("find_restaurant_by_name", output)
    
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
            
            for cuisine_key, cuisine_value in cuisine_mapping.items():
                if cuisine_key in restaurant_type:
                    output = execute_tool("search_restaurants", {"cuisine": cuisine_value, "guests": guests})
                    return format_tool_output("search_restaurants", output)
    
    clean = clean_llm_output(content)

    if not clean:
        return "I can help you book a restaurant. What cuisine would you like?"

    return clean
