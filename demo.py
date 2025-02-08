from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import streamlit as st
import requests
import openai
import json

app = FastAPI()

# Define request model
class DietRequest(BaseModel):
    preferences: List[str]  # Dietary preferences, e.g., ['low carb', 'vegetarian']
    goal: str  # Goal, e.g., 'muscle gain', 'weight loss'
    allergies: List[str] = []  # Allergens, e.g., ['peanuts', 'dairy']

# Replace with your OpenAI API Key
OPENAI_API_KEY = "OpenAI API KEY"
openai.api_key = OPENAI_API_KEY

def generate_recommendation(preferences, goal, allergies):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)  # ✅ Adapted for the new OpenAI SDK

    prompt = f"""
    You are a professional nutritionist. Based on the following information, provide meal recommendations in structured JSON format:
    - Dietary preferences: {', '.join(preferences) if preferences else 'None'}
    - Health goal: {goal}
    - Allergens: {', '.join(allergies) if allergies else 'None'}

    ### **Return JSON output only in this format** (no extra text):

    {{
      "breakfast": "A high-protein breakfast recommendation...",
      "lunch": "A balanced lunch recommendation...",
      "dinner": "A nutritious dinner recommendation...",
      "advice": "General nutritional advice..."
    }}

    Only return a JSON object **without additional explanation**.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional nutrition advisor"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )

        recommendation_text = response.choices[0].message.content
        print("DEBUG: Raw GPT Response:\n", recommendation_text)  # ✅ Debugging

        # ✅ Ensure GPT-4 output is correctly formatted as JSON
        recommendations = json.loads(recommendation_text)  

        if not isinstance(recommendations, dict):  # ✅ Extra safeguard
            raise ValueError("GPT response is not a valid dictionary.")

        return recommendations

    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return {"breakfast": "Error generating recommendation.", "lunch": "", "dinner": "", "advice": ""}

@app.post("/recommend")
def recommend_diet(request: DietRequest):
    recommendations = generate_recommendation(request.preferences, request.goal, request.allergies)
    return {"recommendations": recommendations}

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
    response = requests.post("http://127.0.0.1:8000/recommend", json=payload)
    if response.status_code == 200:
        recommendations = response.json()["recommendations"]

        if isinstance(recommendations, list):  # ✅ Convert list to dictionary if needed
            recommendations = json.loads(recommendations[0]) if recommendations else {}

        # ✅ Now we can safely use dictionary keys
        breakfast = recommendations.get("breakfast", "No breakfast recommendation available.")
        lunch = recommendations.get("lunch", "No lunch recommendation available.")
        dinner = recommendations.get("dinner", "No dinner recommendation available.")
        advice = recommendations.get("advice", "No additional advice available.")

        formatted_output = f"""
        ### 🍽 **Recommended Meals**
        
        #### 🍳 **Breakfast**
        {breakfast}

        #### 🍱 **Lunch**
        {lunch}

        #### 🍲 **Dinner**
        {dinner}

        #### ⚠️ **Nutritional Advice**
        {advice}
        """

        st.markdown(formatted_output)
    else:
        st.error("Failed to get recommendation")

# How to run:
# 1. Start the FastAPI server: uvicorn demo:app --reload
# 2. Run Streamlit: streamlit run filename.py
