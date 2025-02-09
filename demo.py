from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import requests
import openai

app = FastAPI()

# Replace with your OpenAI and Google API Keys
OPENAI_API_KEY = "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"
YOUTUBE_API_KEY = "AIzaSyDnif_YQGkT6Sr-2bYNWSOaf4JsPULUXi0"

openai.api_key = OPENAI_API_KEY
video_url = ''

class DietRequest(BaseModel):
    preferences: List[str]
    goal: str
    allergies: List[str] = []
    available_ingredients: List[str] = []  # New field for fridge items

def search_youtube(query):
    """Search YouTube and return a valid video link."""
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={YOUTUBE_API_KEY}&maxResults=1"
    response = requests.get(url).json()

    if "items" in response and response["items"]:
        video_id = response["items"][0]["id"]["videoId"]
        return f"https://www.youtube.com/watch?v={video_id}"
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
            max_tokens=150
        )

        response_text = response.choices[0].message.content.strip().split("\n")

        # Extract dish names (first three lines) and advice (last line)
        dish_names = response_text[:3] if len(response_text) >= 3 else []
        advice_text = response_text[4] if len(response_text) > 4 else ""
        youtube_links = [search_youtube(dish) for dish in dish_names]

        return {
            "breakfast": {"dish": dish_names[0], "youtube_link": youtube_links[0]} if dish_names else {},
            "lunch": {"dish": dish_names[1], "youtube_link": youtube_links[1]} if len(dish_names) > 1 else {},
            "dinner": {"dish": dish_names[2], "youtube_link": youtube_links[2]} if len(dish_names) > 2 else {},
            "advice": {"text": advice_text} if advice_text else {}  # Returns {} if no advice
        }

    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return {}


@app.post("/recommend")
def recommend_diet(request: DietRequest):
    recommendations = generate_recommendation(request.preferences, request.goal, request.allergies, request.available_ingredients)
    return {"recommendations": recommendations}
