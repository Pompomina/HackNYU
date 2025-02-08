from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from streamlit_player import st_player
import streamlit as st
import requests
import openai
import json


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

def search_youtube(query):
    """Search YouTube and return a valid video link."""
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={YOUTUBE_API_KEY}&maxResults=1"
    response = requests.get(url).json()

    if "items" in response and response["items"]:
        video_id = response["items"][0]["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        return f"https://www.youtube.com/watch?v={video_id}"
    return "No valid YouTube link found."

def generate_recommendation(preferences, goal, allergies):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
    You are a professional nutritionist. Based on the following information, provide meal recommendations:

    - Dietary preferences: {', '.join(preferences) if preferences else 'None'}
    - Health goal: {goal}
    - Allergens: {', '.join(allergies) if allergies else 'None'}

    Provide specific dish names only (e.g., "Grilled Chicken Salad", "Vegan Tofu Stir-Fry"), without additional descriptions.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )

        dish_names = response.choices[0].message.content.strip().split("\n")

        breakfast_dish = dish_names[0] if len(dish_names) > 0 else "Oatmeal with Fruits"
        lunch_dish = dish_names[1] if len(dish_names) > 1 else "Grilled Chicken Salad"
        dinner_dish = dish_names[2] if len(dish_names) > 2 else "Vegan Tofu Stir-Fry"

        return {
            "breakfast": {"dish": breakfast_dish, "youtube_link": search_youtube(breakfast_dish)},
            "lunch": {"dish": lunch_dish, "youtube_link": search_youtube(lunch_dish)},
            "dinner": {"dish": dinner_dish, "youtube_link": search_youtube(dinner_dish)},
            "advice": "Stay hydrated and eat balanced meals."
        }

    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return {
            "breakfast": {"dish": "Error generating recommendation.", "youtube_link": ""},
            "lunch": {"dish": "", "youtube_link": ""},
            "dinner": {"dish": "", "youtube_link": ""},
            "advice": ""
        }

@app.post("/recommend")
def recommend_diet(request: DietRequest):
    recommendations = generate_recommendation(request.preferences, request.goal, request.allergies)
    return {"recommendations": recommendations}

<<<<<<< HEAD
# How to run:
# 1. Start the FastAPI server: uvicorn demo:app --reload
# 2. Run Streamlit: streamlit run filename.py
=======
# Streamlit UI
st.title("Diet Recommendation System")

preferences = st.text_input("Enter your dietary preferences (comma-separated)")
goal = st.selectbox("Your health goal", ["Muscle gain", "Weight loss", "Maintain health"])
allergies = st.text_input("Enter your allergens (comma-separated)")

if st.button("Get Recommendation"):
    payload = {
        "preferences": preferences.split(",") if preferences else [],
        "goal": goal,
        "allergies": allergies.split(",") if allergies else []
    }
    response = requests.post("http://127.0.0.1:8082/recommend", json=payload)
    if response.status_code == 200:
        recommendations = response.json()["recommendations"]

        breakfast = recommendations.get("breakfast", {"dish": "No breakfast recommendation available.", "youtube_link": ""})
        lunch = recommendations.get("lunch", {"dish": "No lunch recommendation available.", "youtube_link": ""})
        dinner = recommendations.get("dinner", {"dish": "No dinner recommendation available.", "youtube_link": ""})
        advice = recommendations.get("advice", "No additional advice available.")

        formatted_output = f"""
        ### 🍽 **Recommended Meals**
        
        #### 🍳 **Breakfast**
        {breakfast["dish"]}  
        [Watch on YouTube]({breakfast["youtube_link"]})

        #### 🍱 **Lunch**
        {lunch["dish"]}  
        [Watch on YouTube]({lunch["youtube_link"]})

        #### 🍲 **Dinner**
        {dinner["dish"]}  
        [Watch on YouTube]({dinner["youtube_link"]})

        #### ⚠️ **Nutritional Advice**
        {advice}
        """

        st.markdown(formatted_output)
    else:
        st.error("Failed to get recommendation")
if video_url:
    st_player(video_url)
>>>>>>> 352d309 (add new)
