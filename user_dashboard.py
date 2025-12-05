"""
User Dashboard - Streamlit App
Allows users to submit reviews and receive AI-generated responses
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from storage_utils import get_storage
from llm_utils import get_llm_manager

# Page configuration
st.set_page_config(
    page_title="Yelp Review Assistant",
    page_icon="⭐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize services
storage = get_storage()
llm = get_llm_manager()

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        background-color: #FF6B6B;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 2rem;
        font-size: 1rem;
    }
    .stButton > button:hover {
        background-color: #FF5252;
    }
    .ai-response {
        background-color: #F0F8FF;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    .rating-select {
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.title("🌟 Yelp Review Assistant")
st.markdown("*Share your experience and get instant AI-powered insights!*")

# Create two columns for better layout
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Your Rating")
    rating = st.selectbox(
        "Select your rating:",
        options=[5, 4, 3, 2, 1],
        format_func=lambda x: f"{'⭐' * x} {x} stars",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("### Your Review")
    review_text = st.text_area(
        "Write your review:",
        placeholder="Tell us about your experience...",
        height=150,
        label_visibility="collapsed"
    )

# Submit button
if st.button("🚀 Submit Review", type="primary"):
    if review_text.strip():
        with st.spinner("🤖 AI is analyzing your review..."):
            # Process with LLM
            ai_results = llm.process_review(rating, review_text)
            
            # Save to storage
            review_data = {
                'user_rating': rating,
                'user_review': review_text,
                'ai_response': ai_results['ai_response'],
                'ai_summary': ai_results['ai_summary'],
                'ai_recommended_action': ai_results['ai_recommended_action']
            }
            
            if storage.save_review(review_data):
                st.success("✅ Review submitted successfully!")
                
                # Display AI response
                st.markdown("### 🤖 AI Response")
                st.markdown(f"<div class='ai-response'>{ai_results['ai_response']}</div>", 
                           unsafe_allow_html=True)
                
                # Show additional insights in expander
                with st.expander("📊 View AI Analysis"):
                    st.markdown("**Summary:**")
                    st.write(ai_results['ai_summary'])
                    
                    st.markdown("**Recommended Action:**")
                    st.write(ai_results['ai_recommended_action'])
            else:
                st.error("❌ Failed to save review. Please try again.")
    else:
        st.warning("⚠️ Please write a review before submitting.")

# Sidebar with information
with st.sidebar:
    st.markdown("## 📱 About")
    st.info(
        "This AI-powered assistant helps you get the most out of your Yelp reviews. "
        "Submit your rating and review to receive instant AI-generated insights and recommendations."
    )
    
    st.markdown("## 🎯 Features")
    st.markdown("- ⭐ Rate your experience (1-5 stars)")
    st.markdown("- 📝 Write detailed reviews")
    st.markdown("- 🤖 Get AI-powered responses")
    st.markdown("- 📊 Receive business insights")
    st.markdown("- 💡 Actionable recommendations")
    
    # Show total reviews
    analytics = storage.get_analytics()
    st.markdown("## 📈 Stats")
    st.metric("Total Reviews", analytics['total_reviews'])
    if analytics['avg_rating'] > 0:
        st.metric("Average Rating", f"{analytics['avg_rating']:.1f} ⭐")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Powered by Gemini AI | Built with Streamlit</div>",
    unsafe_allow_html=True
)