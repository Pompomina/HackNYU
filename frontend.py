import streamlit as st
import requests
import json
import os
import openai

#tab config
st.set_page_config(
    page_title="Diet Recommendation",
    page_icon="🥗",
)

#TITLE config
# Inject custom CSS for font styles
st.markdown(
    """
    <style>
    .custom-title {
        font-size: 55px; /* Adjust font size */
        font-family: 'Impact', monospace; /* Change font family */
        color: #4CAF50; /* Change text color */
        font-weight: bold; /* Make text bold */
    }
    .custom-subtitle {
        font-size: 20px;
        font-family: 'Arial', sans-serif;
        color: #555555;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Create columns for layout
col1, col2 = st.columns([1, 3])  # Adjust column widths

with col1:
    st.image('img/Diet_logo.png', width=100)  # Adjust width as needed

with col2:
    st.markdown("<div class='custom-title'>Diet Recommendation</div>", unsafe_allow_html=True)

#


preferences = st.text_input("Enter your dietary preferences (comma-separated)")
goal = st.selectbox("Your health goal", ["Muscle gain", "Weight loss", "Maintain health"])
allergies = st.text_input("Enter your allergens (comma-separated)")

if st.button("Get Recommendation"):
    payload = {
        "preferences": preferences.split(",") if preferences else [],
        "goal": goal,
        "allergies": allergies.split(",") if allergies else []
    }
    
    try:
        response = requests.post("http://127.0.0.1:8000/recommend", json=payload)

        if response.status_code == 200:
            recommendations = response.json()["recommendations"]

            with st.expander("🍳 **Breakfast**"):
                st.write(recommendations.get("breakfast", "No recommendation."))

            with st.expander("🍱 **Lunch**"):
                st.write(recommendations.get("lunch", "No recommendation."))

            with st.expander("🍲 **Dinner**"):
                st.write(recommendations.get("dinner", "No recommendation."))

            with st.expander("⚠️ **Nutritional Advice**"):
                st.write(recommendations.get("advice", "No additional advice."))
        else:
            st.error("Failed to get recommendations. Please try again.")

    except requests.exceptions.ConnectionError:
        st.error("Backend server is not running. Start `demo.py` first.")

