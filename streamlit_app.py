import requests
import streamlit as st

st.set_page_config(page_title="Restaurant Recommender", page_icon="🍽️", layout="centered")
st.title("🍽️ AI Restaurant Recommender")
st.caption("Free deployable demo (Streamlit Cloud) with backend API integration")

backend_url = st.text_input("Backend API URL", value="http://127.0.0.1:8000")
with st.form("prefs"):
    user_id = st.text_input("User ID", value="user-001")
    location = st.text_input("Location", value="Delhi")
    budget = st.selectbox("Budget", ["low", "medium", "high"], index=1)
    cuisine = st.text_input("Cuisine", value="chinese")
    min_rating = st.slider("Min rating", 0.0, 5.0, 4.0, 0.1)
    optional = st.text_input("Optional preferences", value="quick service")
    top_n = st.slider("Top N", 1, 10, 5)
    submit = st.form_submit_button("Get Recommendations")

if submit:
    payload = {
        "user_id": user_id,
        "location": location,
        "budget": budget,
        "cuisine": cuisine,
        "min_rating": min_rating,
        "optional_preferences": [item.strip() for item in optional.split(",") if item.strip()],
        "top_n": top_n,
    }
    try:
        resp = requests.post(f"{backend_url}/recommendations", json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        st.success(
            f"{len(data['recommendations'])} recommendations | {data['meta']['processing_time_ms']} ms"
        )
        if data["meta"]["fallback_used"]:
            st.warning(data["meta"].get("fallback_reason", "Fallback used"))
        for item in data["recommendations"]:
            st.subheader(item["restaurant_name"])
            st.write(f"Cuisine: {item['cuisine']} | Rating: {item['rating']}")
            st.write(f"Cost for two: INR {item['estimated_cost']}")
            st.write(item["explanation"])
    except Exception as exc:
        st.error(f"Request failed: {exc}")
