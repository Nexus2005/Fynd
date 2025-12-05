import json
import requests
import streamlit as st

RAW_URL = "https://raw.githubusercontent.com/Nexus2005/Fynd/main/cloud_storage/reviews.json"
API_URL = "https://api.github.com/repos/Nexus2005/Fynd/contents/cloud_storage/reviews.json"

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")  # ADD THIS SECRET IN STREAMLIT

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}


def load_reviews():
    try:
        return requests.get(RAW_URL).json()
    except:
        return []


def save_reviews(data):
    # Encode data to base64 for GitHub API
    import base64
    content = base64.b64encode(json.dumps(data, indent=2).encode()).decode("utf-8")

    # Get SHA of existing file
    sha = requests.get(API_URL).json().get("sha")

    payload = {
        "message": "Update reviews.json",
        "content": content,
        "sha": sha
    }

    requests.put(API_URL, headers=headers, json=payload)


def add_review(entry):
    data = load_reviews()
    data.append(entry)
    save_reviews(data)
