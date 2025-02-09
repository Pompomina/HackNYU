# 🥗 Diet Recommendation Web App

This is a **Diet Recommendation Web App** built using **Streamlit** and **FastAPI**. The app provides personalized meal recommendations based on user preferences, goals, allergies, and available ingredients stored in a virtual "fridge." 

## 🌟 Features
- **Fridge Management**:
  - Add ingredients to a virtual fridge.
  - Remove ingredients from the fridge.
  - Store and persist fridge items in a local JSON file.
- **Personalized Meal Recommendations**:
  - Generate meal recommendations based on dietary preferences, health goals, and allergens.
  - Only suggest recipes that can be made with ingredients in the fridge.
- **YouTube Integration**:
  - Embedded YouTube videos for recommended recipes.
- **Modern UI**:
  - Built with Streamlit for a clean and responsive design.
- **FastAPI Backend**:
  - Uses OpenAI's GPT API to generate meal recommendations dynamically.

---

## 🛠️ Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **APIs Used**:
  - OpenAI API for generating meal ideas.
  - YouTube API for fetching recipe videos.

---

## 🚀 How to Run the App
### Prerequisites
1. Python 3.8 or higher
2. Install required libraries:
   ```bash
   pip install -r requirements.txt
