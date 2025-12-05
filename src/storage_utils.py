import json
import requests
import streamlit as st
from datetime import datetime
import os

# ---------- CONFIG ---------- #

RAW_URL = "https://raw.githubusercontent.com/Nexus2005/Fynd/main/cloud_storage/reviews.json"
API_URL = "https://api.github.com/repos/Nexus2005/Fynd/contents/cloud_storage/reviews.json"

# Secret from Streamlit Cloud
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

# Local fallback file (for offline/local use)
LOCAL_FILE = "reviews.json"


# ---------- STORAGE CLASS ---------- #

class Storage:
    def __init__(self):
        self.use_github = GITHUB_TOKEN is not None
        if self.use_github:
            print("Using GitHub cloud storage")
        else:
            print("Using LOCAL storage (GitHub token missing!)")

    # ----------------- LOAD REVIEWS ----------------- #
    def load_reviews(self):
        # Cloud mode
        if self.use_github:
            try:
                resp = requests.get(RAW_URL)
                if resp.status_code == 200:
                    return resp.json()
            except:
                pass

        # Local fallback
        if os.path.exists(LOCAL_FILE):
            with open(LOCAL_FILE, "r") as f:
                return json.load(f)

        return []

    # ----------------- SAVE REVIEWS ----------------- #
    def save_reviews(self, reviews):
        # Cloud mode
        if self.use_github:
            try:
                import base64

                content = base64.b64encode(
                    json.dumps(reviews, indent=2).encode()
                ).decode()

                # Fetch current SHA
                sha_resp = requests.get(API_URL)
                sha = sha_resp.json().get("sha", None)

                payload = {
                    "message": "Update reviews.json",
                    "content": content,
                    "sha": sha
                }

                headers = {
                    "Authorization": f"Bearer {GITHUB_TOKEN}",
                    "Content-Type": "application/json"
                }

                requests.put(API_URL, json=payload, headers=headers)
                return
            except Exception as e:
                print("GitHub save failed:", e)

        # Local fallback
        with open(LOCAL_FILE, "w") as f:
            json.dump(reviews, f, indent=2)

    # ----------------- ADD REVIEW ----------------- #
    def add_review(self, user_rating, user_review, ai_summary, ai_recommended_action, ai_response):
        reviews = self.load_reviews()

        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_rating": user_rating,
            "user_review": user_review,
            "ai_summary": ai_summary,
            "ai_recommended_action": ai_recommended_action,
            "ai_response": ai_response
        }

        reviews.append(entry)
        self.save_reviews(reviews)

    # ----------------- EXPORT CSV ----------------- #
    def export_to_csv(self, filename):
        try:
            import pandas as pd
            data = self.load_reviews()
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            return True
        except:
            return False

    # ----------------- ANALYTICS ----------------- #
    def get_analytics(self):
        data = self.load_reviews()

        if not data:
            return {
                "total_reviews": 0,
                "avg_rating": 0,
                "rating_distribution": {},
                "recent_reviews": []
            }

        import pandas as pd

        df = pd.DataFrame(data)

        return {
            "total_reviews": len(df),
            "avg_rating": df["user_rating"].mean(),
            "rating_distribution": df["user_rating"].value_counts().to_dict(),
            "recent_reviews": df.tail(20).to_dict(orient="records")
        }

    # ----------------- GET ALL REVIEWS ----------------- #
    def get_all_reviews(self):
        return self.load_reviews()


# GLOBAL INSTANCE
storage = Storage()

def get_storage():
    return storage
