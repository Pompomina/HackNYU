import streamlit as st
import requests
import json
import os

# Page Configuration
st.set_page_config(
    page_title="Diet Recommendation",
    page_icon="🥗",
    layout="wide"
)

# Load fridge data
FRIDGE_FILE = "fridge.json"

def load_fridge():
    if os.path.exists(FRIDGE_FILE):
        with open(FRIDGE_FILE, "r") as f:
            return json.load(f)
    return []

def save_fridge(fridge_items):
    with open(FRIDGE_FILE, "w") as f:
        json.dump(fridge_items, f)

fridge = load_fridge()

# Inject custom CSS for title styling
st.markdown("""
    <style>
    .custom-title {
        font-size: 50px;
        font-family: 'Impact', sans-serif;
        color: #4CAF50;
        font-weight: bold;
        text-align: center;
    }
    .custom-subtitle {
        font-size: 20px;
        font-family: 'Arial', sans-serif;
        color: #555555;
        text-align: center;
    }
    .recommend-container {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Layout - Header with Image and Title
col1, col2 = st.columns([1, 4])

with col1:
    st.image('img/Diet_logo.png', width=100)

with col2:
    st.markdown("<div class='custom-title'>Diet Recommendation</div>", unsafe_allow_html=True)
    st.markdown("<div class='custom-subtitle'>Personalized meal plans based on your available ingredients</div>", unsafe_allow_html=True)

st.markdown("---")

# Fridge Feature
st.subheader("🧊 Your Fridge")
food_item = st.text_input("Enter a food item to add to / remove from your fridge", placeholder="e.g., chicken, spinach, eggs")
if st.button("➕ Add Food to Fridge"):
    if food_item:
        new_items = [item.strip().lower() for item in food_item.split(",")]
        fridge.extend(new_items)
        save_fridge(fridge)
        st.success(f"✅ Added: {', '.join(new_items)} to the fridge!")


if st.button("➖ Remove Food from Fridge"):
    if food_item:
        fridge.remove(food_item.lower())
        save_fridge(fridge)
        st.success(f"✅ {food_item} remove from the fridge!")

if fridge:
    st.write("### 🛒 Current Ingredients in Your Fridge:")
    st.write(", ".join(fridge))

if st.button("🗑 Clear Fridge"):
    fridge = []
    save_fridge(fridge)
    st.success("❌ Fridge cleared!")

st.markdown("---")

# User Inputs
st.subheader("📝 Your Preferences")
preferences = st.text_input("Enter your dietary preferences (comma-separated)", placeholder="e.g., high protein, low carb")
goal = st.selectbox("Your Health Goal", ["Muscle Gain", "Weight Loss", "Maintain Health"])
allergies = st.text_input("Enter allergens (comma-separated)", placeholder="e.g., nuts, gluten")

# Handle button click
if st.button("🔍 Generate Meal from Fridge"):
    payload = {
        "preferences": [p.strip() for p in preferences.split(",") if p.strip()],
        "goal": goal,
        "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
        "available_ingredients": fridge
    }

    response = requests.post("http://127.0.0.1:8081/recommend", json=payload)

    if response.status_code == 200:
        recommendations = response.json()["recommendations"]

        # Extract recommendations safely
        meals = {
            "Breakfast": recommendations.get("breakfast", {"dish": "No recommendation available", "youtube_link": ""}),
            "Lunch": recommendations.get("lunch", {"dish": "No recommendation available", "youtube_link": ""}),
            "Dinner": recommendations.get("dinner", {"dish": "No recommendation available", "youtube_link": ""})
        }
        advice = recommendations.get("advice", "No additional advice available.")

        st.subheader("🍽 Recommended Meals")

        for meal, details in meals.items():
            with st.expander(f"🔹 {meal} Recommendation"):
                st.markdown(f"**{details['dish']}**")
                if details["youtube_link"]:
                    st.video(details["youtube_link"])

        # Display Nutritional Advice
        st.subheader("⚠️ Nutritional Advice")
        st.markdown(f"<div class='recommend-container'>{advice}</div>", unsafe_allow_html=True)

    else:
        st.error("🚨 Failed to retrieve recommendations. Please try again.")
