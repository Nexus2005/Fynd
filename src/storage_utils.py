import json
import requests
import streamlit as st
from datetime import datetime
import pandas as pd
import base64

# ----------------------------
# GitHub Storage Configuration
# ----------------------------
GITHUB_REPO = "Nexus2005/Fynd"
FILE_PATH = "reviews.json"

RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{FILE_PATH}"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")  # MUST be added in Streamlit secrets

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


class CloudStorage:

    # ----------------------------
    # Load reviews from GitHub raw
    # ----------------------------
    def load_reviews(self):
        try:
            r = requests.get(RAW_URL)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return []

    # ----------------------------
    # Save reviews back to GitHub
    # ----------------------------
    def save_reviews(self, data):
        try:
            # Encode to base64
            encoded = base64.b64encode(
                json.dumps(data, indent=2).encode()
            ).decode()

            # Get SHA
            sha_info = requests.get(API_URL, headers=HEADERS).json()
            sha = sha_info.get("sha")

            payload = {
                "message": "Update reviews.json",
                "content": encoded,
                "sha": sha
            }

            resp = requests.put(API_URL, headers=HEADERS, json=payload)
            return resp.status_code in (200, 201)

        except Exception as e:
            print("SAVE ERROR:", e)
            return False

    # ----------------------------
    # Add one review
    # ----------------------------
    def add_review(self, entry):
        data = self.load_reviews()
        data.append(entry)
        return self.save_reviews(data)

    # ----------------------------
    # Get all
    # ----------------------------
    def get_all_reviews(self):
        return self.load_reviews()

    # ----------------------------
    # Dashboard analytics
    # ----------------------------
    def get_analytics(self):
        reviews = self.load_reviews()
        if not reviews:
            return {
                "total_reviews": 0,
                "avg_rating": 0,
                "rating_distribution": {},
                "recent_reviews": []
            }

        total = len(reviews)
        avg = sum(r["user_rating"] for r in reviews) / total

        dist = {}
        for r in reviews:
            dist[r["user_rating"]] = dist.get(r["user_rating"], 0) + 1

        recent = reviews[-20:]

        return {
            "total_reviews": total,
            "avg_rating": avg,
            "rating_distribution": dist,
            "recent_reviews": recent
        }

    # ----------------------------
    # Export CSV
    # ----------------------------
    def export_to_csv(self, filename):
        try:
            df = pd.DataFrame(self.load_reviews())
            df.to_csv(filename, index=False)
            return True
        except:
            return False


# Global instance
def get_storage():
    return CloudStorage()
