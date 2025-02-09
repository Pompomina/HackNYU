from fastapi import FastAPI
from pydantic import BaseModel
import requests
import openai
from typing import List, Optional
from thefuzz import fuzz
import re

app = FastAPI()

# Replace with your OpenAI and Google API Keys
OPENAI_API_KEY = "sk-XXX"
YOUTUBE_API_KEY = "XXX"
GOOGLE_API_KEY = "XXX"
YELP_API_KEY = "XXX"

openai.api_key = OPENAI_API_KEY
video_url = ''

def extract_english(text):
    """Remove non-English characters from a restaurant name."""
    return re.sub(r'[^A-Za-z0-9\s]', '', text)


def search_yelp(dish, latitude, longitude):
    """Search Yelp API for restaurants serving a given dish."""
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {"Authorization": f"Bearer {YELP_API_KEY}"}
    params = {
        "term": dish,
        "latitude": latitude,
        "longitude": longitude,
        "categories": "restaurants",
        "limit": 10  # Increase results for better matching
    }

    response = requests.get(url, headers=headers, params=params).json()

    if "businesses" not in response:
        return {}

    yelp_data = {}
    for business in response["businesses"]:
        yelp_data[business["name"].lower()] = {
            "url": business["url"],
            "address": " ".join(business["location"].get("display_address", []))  # Convert address to string
        }

    return yelp_data



class DietRequest(BaseModel):
    preferences: List[str]
    goal: str
    allergies: List[str] = []
    available_ingredients: List[str] = []  # New field for fridge items
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    eat_location: str

def search_youtube(query):
    """Search YouTube and return a valid video link."""
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={YOUTUBE_API_KEY}&maxResults=1"
    response = requests.get(url).json()

    if "items" in response and response["items"]:
        video_id = response["items"][0]["id"]["videoId"]
        return f"https://www.youtube.com/watch?v={video_id}"
    return None
##


def generate_nutritional_data(dish_name):
    """Generate a short nutritional summary and nutrient breakdown for the dish."""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
    Provide the approximate nutritional breakdown for "{dish_name}" per 500 grams.
    Include:
    - Calories
    - Protein (grams)
    - Carbohydrates (grams)
    - Fat (grams)

    Respond in **JSON format**, example:
    {{
        "calories": 645,
        "protein": 49,
        "carbohydrates": 34,
        "fat": 34
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        nutrients = response.choices[0].message.content.strip()

        # Ensure the response is formatted correctly
        import json
        try:
            nutrient_data = json.loads(nutrients)
        except json.JSONDecodeError:
            return None  # Return None if parsing fails

        return nutrient_data

    except Exception as e:
        print(f"⚠️ Failed to generate nutrition data: {e}")
        return None

def generate_recommendation(preferences, goal, allergies, available_ingredients):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = f"""
        You are a professional nutritionist and meal planner. Based on the following dietary requirements, recommend three meal options (breakfast, lunch, and dinner) that can be made using the available ingredients. Each recommendation should be a **specific dish name only**, without numbering or extra text.

        - **Dietary Preferences:** {', '.join(preferences) if preferences else 'None'}
        - **Health Goal:** {goal}
        - **Allergens to Avoid:** {', '.join(allergies) if allergies else 'None'}
        - **Available Ingredients:** {', '.join(available_ingredients) if available_ingredients else 'None'}

        After listing the three meal names, provide a short **separate** paragraph with dietary advice. The advice should:
        1. Be relevant to the recommended meals.
        2. Highlight nutritional benefits or suggest improvements.
        3. Be no more than **two sentences**.

        ### **Response Format:**
        Provide exactly **three dish names**, one per line.
        Then, provide a short paragraph of dietary advice based on the selected meals. The advice should be:
        1. Specific to the recommended dishes.
        2. Focused on health benefits, possible improvements, or balance of nutrients.
        3. No more than **two sentences**.

        Example Response:
        1. Avocado Toast
        2. Grilled Chicken Salad
        3. Lentil Soup
        4. Advice: This meal plan is well-balanced, providing healthy fats, lean protein, and fiber. Consider adding more leafy greens for extra vitamins.
        """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )

        response_text = response.choices[0].message.content.strip().split("\n")

        # Extract dish names (first three lines) and advice (last line)
        dish_names = response_text[:3] if len(response_text) >= 3 else []
        advice_text = response_text[4] if len(response_text) > 4 else ""
        youtube_links = [search_youtube(dish) for dish in dish_names]
        nutrition_data = [generate_nutritional_data(dish) for dish in dish_names]

        return {
            "breakfast": {
                "dish": dish_names[0],
                "youtube_link": youtube_links[0],
                "nutrients": nutrition_data[0]
            } if dish_names else {},

            "lunch": {
                "dish": dish_names[1],
                "youtube_link": youtube_links[1],
                "nutrients": nutrition_data[1]
            } if len(dish_names) > 1 else {},

            "dinner": {
                "dish": dish_names[2],
                "youtube_link": youtube_links[2],
                "nutrients": nutrition_data[2]
            } if len(dish_names) > 2 else {},
            
            "advice": {"text": advice_text} if advice_text else {}  # Returns {} if no advice
        }

    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return {}
        

# ✅ Use OpenAI to recommend dish types for eating out
def recommend_dishes(preferences, goal, allergies):
    """Generate a list of dish types that align with the user's health goals and dietary restrictions."""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
        You are a professional nutritionist. Based on the user's preferences, health goal, and allergies, recommend three dish types that would be best suited when dining at a restaurant.

        - **Dietary Preferences:** {', '.join(preferences) if preferences else 'None'}
        - **Health Goal:** {goal}
        - **Allergens to Avoid:** {', '.join(allergies) if allergies else 'None'}

        Provide exactly **three dish types**, one per line (e.g., "Grilled Salmon", "Vegan Stir Fry", "Quinoa Salad").
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )

        dish_types = response.choices[0].message.content.strip().split("\n")
        return dish_types[:3]  # Return top 3 dish types

    except Exception as e:
        print(f"⚠️ OpenAI API call failed: {e}")
        return ["Healthy Salad", "Grilled Chicken", "Steamed Fish"]  # Default fallback



def get_city_name(latitude, longitude):
    """Get the city name from latitude and longitude using Google Geocoding API."""
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={GOOGLE_API_KEY}"
    response = requests.get(url).json()

    if "results" in response and response["results"]:
        for component in response["results"][0]["address_components"]:
            if "locality" in component["types"]:  # Look for city name
                return component["long_name"]

    return "Unknown Location"  # Fallback if geocoding fails

def search_restaurants(dish, latitude, longitude, radius=5000):
    """Search Google Places API for restaurants and generate Yelp search links dynamically."""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{latitude},{longitude}",
        "radius": radius,
        "keyword": dish,
        "type": "restaurant",
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params).json()
    
    if "results" not in response or not response["results"]:
        return []

    yelp_data = search_yelp(dish, latitude, longitude)
    city_name = get_city_name(latitude, longitude)  # Get dynamic city name

    restaurants = []
    for r in response["results"][:5]:  # Limit to top 5 results
        google_name = r["name"]
        google_address = r.get("vicinity", "")

        # Try to match Yelp data
        best_match = None
        best_score = 0

        for yelp_name, yelp_info in yelp_data.items():
            name_score = fuzz.ratio(google_name.lower(), yelp_name.lower())
            address_score = fuzz.partial_ratio(google_address.lower(), yelp_info["address"].lower())
            total_score = (name_score * 0.7) + (address_score * 0.3)  

            if total_score > best_score and total_score > 75:
                best_score = total_score
                best_match = yelp_name

        # Use the best-matched Yelp link if found, otherwise generate a Yelp search link
        if best_match:
            yelp_url = yelp_data[best_match]["url"]
        else:
            search_query = extract_english(google_name).replace(" ", "+")  # Keep only English characters
            yelp_url = f"https://www.yelp.com/search?find_desc={search_query}&find_loc={city_name}"


        restaurants.append({
            "name": google_name,
            "address": google_address,
            "rating": r.get("rating", "No rating"),
            "latitude": r["geometry"]["location"]["lat"],
            "longitude": r["geometry"]["location"]["lng"],
            "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{r['place_id']}",
            "yelp_url": yelp_url
        })

    return restaurants





# @app.post("/recommend")
# def recommend_diet(request: DietRequest):
#     recommendations = generate_recommendation(request.preferences, request.goal, request.allergies, request.available_ingredients)
#     return {"recommendations": recommendations}

# ✅ Handle API Requests
@app.post("/recommend")
def recommend_diet(request: DietRequest):
    if request.eat_location == "Outside":
        if request.latitude is None or request.longitude is None:
            return {"error": "Latitude and longitude are required for restaurant recommendations."}

        # Step 1: Get dish recommendations based on user preferences
        dish_types = recommend_dishes(request.preferences, request.goal, request.allergies)

        # Step 2: Search for nearby restaurants serving these dish types
        restaurants = []
        for dish in dish_types:
            restaurants.extend(search_restaurants(dish, request.latitude, request.longitude))

        return {"restaurants": restaurants}

    elif request.eat_location == "Home":
        recommendations = generate_recommendation(request.preferences, request.goal, request.allergies, request.available_ingredients)
        return {"recommendations": recommendations}
    else:
        return {"error": "Invalid choice. Use 'dine-in' or 'dine-out'."}

