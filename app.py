import streamlit as st
import requests
import geocoder
import json
import os
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static


API_URL = "http://127.0.0.1:8081"

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

# User Inputs
st.subheader("📝 Your Preferences")
preferences = st.text_input("Enter your dietary preferences (comma-separated)", placeholder="e.g., high protein, low carb")
goal = st.selectbox("Your Health Goal", ["Muscle Gain", "Weight Loss", "Maintain Health"])
allergies = st.text_input("Enter allergens (comma-separated)", placeholder="e.g., nuts, gluten")

eat_location = st.radio("Where would you like to eat?", ["Home", "Outside"], index=0)

if eat_location == "Home":
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
            st.success(f"✅ {food_item} removed from the fridge!")
    
    if fridge:
        st.write("### 🛒 Current Ingredients in Your Fridge:")
        st.write(", ".join(fridge))
    
    if st.button("🗑 Clear Fridge"):
        fridge = []
        save_fridge(fridge)
        st.success("❌ Fridge cleared!")

    st.markdown("---")
    
    # Handle Meal Recommendation
    if st.button("🔍 Generate Meal from Fridge"):
        payload = {
            "preferences": [p.strip() for p in preferences.split(",") if p.strip()],
            "goal": goal,
            "allergies": [a.strip() for a in allergies.split(",") if a.strip()],
            "available_ingredients": fridge,
            "eat_location": "Home"
        }
        response = requests.post(f"{API_URL}/recommend", json=payload)
        
        if response.status_code == 200:
            recommendations = response.json()["recommendations"]
            meals = {
                "Breakfast": recommendations.get("breakfast", {"dish": "No recommendation available", "youtube_link": ""}),
                "Lunch": recommendations.get("lunch", {"dish": "No recommendation available", "youtube_link": ""}),
                "Dinner": recommendations.get("dinner", {"dish": "No recommendation available", "youtube_link": ""})
            }
            advice = recommendations.get("advice", {}).get("text", "No additional advice available.")
            
            st.subheader("🍽 Recommended Meals")
            for meal, details in meals.items():
                with st.expander(f"🔹 {meal} Recommendation"):
                    st.markdown(f"**{details['dish']}**")
                    if details["youtube_link"]:
                        st.video(details["youtube_link"])
                    
                    if details.get("nutrients"):
                        nutrients = details["nutrients"]
                        calories = nutrients.pop("calories", None)
                        if calories:
                            st.markdown(f"**🔥 Calories: {calories} kcal**")
                        labels = list(nutrients.keys())
                        values = list(nutrients.values())
                        fig, ax = plt.subplots(figsize=(2, 2))
                        ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90, textprops={'fontsize': 8})
                        ax.axis("equal")
                        st.pyplot(fig)
                        st.info(
                            f"{details['dish']} contains approximately {calories} kcal, "
                            f"{nutrients['protein']}g of protein, {nutrients['carbohydrates']}g of carbs, "
                            f"and {nutrients['fat']}g of fat per 500g serving."
                        )
            st.subheader("⚠️ Nutritional Advice")
            st.markdown(advice)
        else:
            st.error("🚨 Failed to retrieve recommendations. Please try again.")

elif eat_location == "Outside":
    st.subheader("🍽️ Find Restaurants Nearby")

    g = geocoder.ip('me')
    location = g.latlng if g.latlng else None

    if location:
        latitude, longitude = location
        st.write(f"📍 **Detected Location:** ({latitude}, {longitude})")
    else:
        latitude = st.number_input("Enter your latitude:", value=40.730610)
        longitude = st.number_input("Enter your longitude:", value=-73.935242)
        st.warning("Could not determine location automatically. Please enter manually.")

    if st.button("📍 Find Restaurants"):
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "preferences": preferences.split(",") if preferences else [],
            "goal": goal,
            "allergies": allergies.split(",") if allergies else [],
            "eat_location": "Outside"
        }
        response = requests.post(f"{API_URL}/recommend", json=payload)

        if response.status_code == 200:
            restaurants = response.json()["restaurants"]
            st.subheader("🏨 Nearby Restaurants")

            if not restaurants:
                st.write("No restaurants found. Try adjusting search criteria.")
            else:
                # Create a map centered around user's location
                m = folium.Map(location=[latitude, longitude], zoom_start=14, tiles="cartodb positron")

                # Add a marker for the user's location
                folium.Marker(
                    location=[latitude, longitude],
                    popup="You are here 📍",
                    tooltip="Your Location",
                    icon=folium.Icon(color="blue", icon="home", prefix="fa")
                ).add_to(m)

                # Add restaurant markers
                for r in restaurants:
                    popup_content = f"""
                    <b>{r['name']}</b><br>
                    ⭐ Rating: {r['rating']}<br>
                    📍 {r['address']}<br>
                    <a href="{r['google_maps_url']}" target="_blank">View on Google Maps</a>
                    """
                    if "yelp.com/search" in r["yelp_url"]:
                        popup_content += f'<a href="{r["yelp_url"]}" target="_blank">Search on Yelp</a>'
                    else:
                        popup_content += f'<a href="{r["yelp_url"]}" target="_blank">View on Yelp</a>'
                    
                    folium.Marker(
                        location=[r["latitude"], r["longitude"]],
                        popup=folium.Popup(popup_content, max_width=300),
                        tooltip=r["name"],
                        icon=folium.Icon(color="red", icon="cutlery", prefix="fa")  # Custom icon color
                    ).add_to(m)

                    # st.markdown(f"**🍽 {r['name']}** - ⭐ {r['rating']}")
                    # st.markdown(f"📍 {r['address']}")
                    # st.markdown(f"[View on Google Maps]({r['google_maps_url']})")

                st.subheader("📍 Map View")
                folium_static(m)
        else:
            st.error("Failed to fetch restaurant data.")



