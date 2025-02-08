from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import requests
import openai

app = FastAPI()

# Replace with your OpenAI and Google API Keys
OPENAI_API_KEY = "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"
YOUTUBE_API_KEY = "AIzaSyBHxuNGuV6aApcXwvkTEm7nxDwDXlRB4Yg"

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
    return "No valid YouTube link found."

def generate_recommendation(preferences, goal, allergies, available_ingredients):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
    You are a professional nutritionist. Based on the following information, provide meal recommendations:

    - Dietary preferences: {', '.join(preferences) if preferences else 'None'}
    - Health goal: {goal}
    - Allergens: {', '.join(allergies) if allergies else 'None'}
    - Available ingredients: {', '.join(available_ingredients) if available_ingredients else 'None'}

    Only recommend meals that **can be made using the available ingredients**. Provide specific dish names only.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )

        dish_names = response.choices[0].message.content.strip().split("\n")
        print(response)
        print("dish_names")

        return {
            "breakfast": {"dish": dish_names[0], "youtube_link": search_youtube(dish_names[0])} if dish_names else {},
            "lunch": {"dish": dish_names[1], "youtube_link": search_youtube(dish_names[1])} if len(dish_names) > 1 else {},
            "dinner": {"dish": dish_names[2], "youtube_link": search_youtube(dish_names[2])} if len(dish_names) > 2 else {},
            "advice": "Stay hydrated and eat balanced meals."
        }

    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return {}

@app.post("/recommend")
def recommend_diet(request: DietRequest):
    recommendations = generate_recommendation(request.preferences, request.goal, request.allergies, request.available_ingredients)
    return {"recommendations": recommendations}
