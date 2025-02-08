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
    response = requests.post("http://127.0.0.1:8081/recommend", json=payload)
    if response.status_code == 200:
        recommendations = response.json()["recommendations"]

        # ✅ Now we can safely use dictionary keys
        breakfast = recommendations.get("breakfast", {"dish": "No breakfast recommendation available.", "youtube_link": ""})
        lunch = recommendations.get("lunch", {"dish": "No lunch recommendation available.", "youtube_link": ""})
        dinner = recommendations.get("dinner", {"dish": "No dinner recommendation available.", "youtube_link": ""})
        advice = recommendations.get("advice", "No additional advice available.")

        formatted_output = f"""
        ### 🍽 **Recommended Meals**
        
        #### 🍳 **Breakfast**
        {breakfast["dish"]}  
        [Watch on YouTube]({breakfast["youtube_link"]})
        """
        st.markdown(formatted_output)
        if breakfast["youtube_link"]:
            st.video(breakfast["youtube_link"])
        
        formatted_output = f"""
        #### 🍱 **Lunch**
        {lunch["dish"]}  
        [Watch on YouTube]({lunch["youtube_link"]})
        """
        st.markdown(formatted_output)
        if lunch["youtube_link"]:
            st.video(lunch["youtube_link"])
        
        formatted_output = f"""
        #### 🍲 **Dinner**
        {dinner["dish"]}  
        [Watch on YouTube]({dinner["youtube_link"]})
        """
        st.markdown(formatted_output)
        if dinner["youtube_link"]:
            st.video(dinner["youtube_link"])
        
        formatted_output = f"""
        #### ⚠️ **Nutritional Advice**
        {advice}
        """
        st.markdown(formatted_output)
    else:
        st.error("Failed to get recommendation")