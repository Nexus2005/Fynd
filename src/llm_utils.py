"""
LLM utilities for generating AI responses in the dashboards.
Uses Gemini 2.5 Flash for responses, summaries, and recommendations.
"""

import os
import google.generativeai as genai
from typing import Dict


# ---------- LLM INITIALIZATION ---------- #

def initialize_gemini():
    """Initialize Gemini API with the verified working model."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    genai.configure(api_key=api_key)

    # Use verified working model
    return genai.GenerativeModel("models/gemini-2.5-flash")


# ---------- PROMPT TEMPLATES ---------- #

USER_RESPONSE_PROMPT = """
You are responding to a Yelp review.

Rating: {rating} stars
Review: "{review_text}"

Write a short 2–3 sentence reply:
- thank them
- reflect their sentiment
- address concerns (if low rating)
- optionally invite them back
"""

SUMMARY_PROMPT = """
Summarize this Yelp review in 1–2 sentences.

Rating: {rating} stars
Review: "{review_text}"
"""

RECOMMENDATION_PROMPT = """
Based on this Yelp review, give ONE actionable improvement for the business.

Rating: {rating} stars
Review: "{review_text}"

Your answer must be a single clear recommendation.
"""


# ---------- LLM MANAGER ---------- #

class LLMManager:
    """Handles all LLM interactions for the dashboards."""

    def __init__(self):
        try:
            self.model = initialize_gemini()
        except Exception as e:
            print(f"[WARNING] LLM initialization failed: {e}")
            self.model = None

    def _safe_generate(self, prompt: str) -> str:
        """Internal function to safely call Gemini."""
        if not self.model:
            return "AI temporarily unavailable."

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[ERROR] LLM error: {e}")
            return "AI response failed."

    def generate_user_response(self, rating: int, review_text: str) -> str:
        prompt = USER_RESPONSE_PROMPT.format(
            rating=rating, review_text=review_text
        )
        return self._safe_generate(prompt)

    def generate_summary(self, rating: int, review_text: str) -> str:
        prompt = SUMMARY_PROMPT.format(
            rating=rating, review_text=review_text
        )
        return self._safe_generate(prompt)

    def generate_recommendation(self, rating: int, review_text: str) -> str:
        prompt = RECOMMENDATION_PROMPT.format(
            rating=rating, review_text=review_text
        )
        return self._safe_generate(prompt)

    def process_review(self, rating: int, review_text: str) -> Dict[str, str]:
        """Return all 3 outputs for dashboards."""
        return {
            "ai_response": self.generate_user_response(rating, review_text),
            "ai_summary": self.generate_summary(rating, review_text),
            "ai_recommended_action": self.generate_recommendation(rating, review_text),
        }


# Global instance
llm_manager = LLMManager()

def get_llm_manager():
    return llm_manager
