import json
import requests
import streamlit as st
from datetime import datetime
import pandas as pd
import base64

RAW_URL = "https://raw.githubusercontent.com/Nexus2005/Fynd/main/cloud_storage/reviews.json"
API_URL = "https://api.github.com/repos/Nexus2005/Fynd/contents/cloud_storage/reviews.json"

GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}


class CloudStorage:
    def load_reviews(self):
        """Load review list from RAW GitHub JSON"""
        try:
            data = requests.get(RAW_URL).json()
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def save_reviews(self, data):
        """Write updated JSON to GitHub through API"""
        try:
            # Encode data to base64
            content = base64.b64encode(
                json.dumps(data, indent=2).encode()
            ).decode()

            # Get SHA of existing file
            existing = requests.get(API_URL, headers=headers).json()
            sha = existing.get("sha")

            payload = {
                "message": "Update reviews.json",
                "content": content,
                "sha": sha
            }

            requests.put(API_URL, headers=headers, json=payload)
            return True

        except Exception as e:
            print("SAVE ERROR:", e)
            return False

    def add_review(self, entry):
        """Append a new review"""
        reviews = self.load_reviews()
        reviews.append(entry)
        return self.save_reviews(reviews)

    def get_all_reviews(self):
        return self.load_reviews()

    def get_analytics(self):
        """Compute stats for admin dashboard"""
        reviews = self.load_reviews()
        if not reviews:
            return {
                "total_reviews": 0,
                "avg_rating": 0,
                "rating_distribution": {},
                "recent_reviews": []
            }

        df = pd.DataFrame(reviews)

        # Rating distribution
        dist = df["user_rating"].value_counts().to_dict()

        # Recent 20 reviews
        recent = df.tail(20).to_dict(orient="records")

        return {
            "total_reviews": len(df),
            "avg_rating": float(df["user_rating"].mean()),
            "rating_distribution": dist,
            "recent_reviews": recent
        }

    def export_to_csv(self, path):
        try:
            df = pd.DataFrame(self.load_reviews())
            df.to_csv(path, index=False)
            return True
        except:
            return False


# Global instance
def get_storage():
    return CloudStorage()
