<img width="964" alt="image" src="https://github.com/user-attachments/assets/a1650919-8ead-46fb-9dcc-0b13fdd5fe59" />

# 🥗 Diet Recommendation Web App

This is an advanced **Diet Recommendation Web App** built using **Streamlit** and **FastAPI**. The app provides personalized meal recommendations based on user preferences, goals, allergies, and available ingredients stored in a virtual "fridge." Additionally, it supports restaurant recommendations based on the user's location.

---

## 🌟 Features

### 1. **Personalized Meal Planning**
- Generate meal recommendations based on:
  - Dietary preferences
  - Health goals (e.g., Weight Loss, Muscle Gain)
  - Allergies
  - Ingredients available in your fridge
- Nutritional breakdown (calories, protein, carbs, fats) for recommended meals
- Embedded YouTube recipe videos for easy preparation

### 2. **Fridge Management**
- Add, remove, or clear ingredients in your virtual fridge.
- Save fridge data persistently in a local file (`fridge.json`).

### 3. **Restaurant Finder**
- Find restaurants near your location serving dishes aligned with your dietary preferences and health goals.
- View restaurant details, including:
  - Google Maps link
  - Yelp reviews and ratings
- Interactive map displaying nearby restaurants.

### 4. **Dynamic Nutritional Advice**
- Short dietary tips provided alongside recommendations.
- Advice tailored to selected meals for better health outcomes.

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/)
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **APIs Used**: if you want to run it, you can replace the API Key placeholder with your own
  - OpenAI GPT for generating meal and nutritional data
  - YouTube API for fetching recipe videos
  - Google Maps API for restaurant locations
  - Yelp API for restaurant reviews and details

---

## 🚀 How to Run the App

### Prerequisites
1. Python 3.8 or higher
2. Install required libraries:
   ```bash
   pip install -r requirements.txt

### Steps to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/Pompomina/HackNYU.git
   cd HackNYU

2. Start the backend (FastAPI):
   ```bash
   uvicorn demo:app --host 127.0.0.1 --port 8081 --reload

3. Start the frontend:
   ```bash
   streamlit run app.py

---

## 📝 Project Structure
```bash
diet-recommendation-app/
│
├── app.py               # Main Streamlit app
├── backend.py           # FastAPI backend
├── fridge.json          # Stores fridge items
├── requirements.txt     # Python dependencies
├── img/
│   └── Diet_logo.png    # App logo
├── pages/               # Optional additional pages for multi-page apps
└── README.md            # Project documentation



