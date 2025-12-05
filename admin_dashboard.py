"""
Admin Dashboard - Streamlit App
View all submissions, analytics, and manage reviews
"""

import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json  # REQUIRED

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from storage_utils import get_storage

# Page configuration
st.set_page_config(
    page_title="Admin Dashboard - Yelp Reviews",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize storage
storage = get_storage()

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
    }
    .review-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e1e5e9;
        margin-bottom: 1rem;
    }
    .rating-stars {
        color: #ffc107;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("📊 Admin Dashboard - Yelp Review Analytics")

# Get analytics
analytics = storage.get_analytics()

# ----------- OVERVIEW CARDS ------------
st.markdown("## 📈 Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>Total Reviews</h3>
        <h2>{analytics['total_reviews']}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    avg_rating = f"{analytics['avg_rating']:.1f}" if analytics['avg_rating'] > 0 else "N/A"
    st.markdown(f"""
    <div class="metric-card">
        <h3>Average Rating</h3>
        <h2>{avg_rating} ⭐</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    five_star_pct = (
        f"{(analytics['rating_distribution'].get(5, 0) / analytics['total_reviews'] * 100):.1f}%"
        if analytics['total_reviews'] > 0 else "0%"
    )
    st.markdown(f"""
    <div class="metric-card">
        <h3>5-Star Reviews</h3>
        <h2>{five_star_pct}</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    low_rating_count = sum(analytics['rating_distribution'].get(i, 0) for i in [1, 2])
    st.markdown(f"""
    <div class="metric-card">
        <h3>Low Ratings (1–2⭐)</h3>
        <h2>{low_rating_count}</h2>
    </div>
    """, unsafe_allow_html=True)

# ----------- ANALYTICS CHARTS ------------
if analytics['total_reviews'] > 0:
    st.markdown("## 📊 Analytics")

    col1, col2 = st.columns(2)

    # Rating distribution
    with col1:
        ratings_data = [
            {'Rating': f'{i}⭐', 'Count': analytics['rating_distribution'].get(i, 0)}
            for i in range(1, 6)
        ]
        df_ratings = pd.DataFrame(ratings_data)

        fig1 = px.bar(
            df_ratings, x='Rating', y='Count',
            title='Rating Distribution',
            color='Rating',
            color_discrete_map={
                '1⭐': '#dc3545', '2⭐': '#fd7e14', '3⭐': '#ffc107',
                '4⭐': '#20c997', '5⭐': '#198754'
            }
        )
        fig1.update_layout(showlegend=False)
        st.plotly_chart(fig1, width="stretch")

    # Recent activity graph
    with col2:
        if analytics['recent_reviews']:
            recent_df = pd.DataFrame(analytics['recent_reviews'])
            recent_df['timestamp'] = pd.to_datetime(recent_df['timestamp'])
            recent_df = recent_df.sort_values('timestamp')

            fig2 = go.Figure()

            for rating in range(1, 6):
                data = recent_df[recent_df['user_rating'] == rating]
                if not data.empty:
                    fig2.add_trace(go.Scatter(
                        x=data['timestamp'],
                        y=data['user_rating'],
                        mode='markers',
                        name=f'{rating}⭐',
                        marker=dict(size=10)
                    ))

            fig2.update_layout(
                title='Recent Review Activity',
                xaxis_title='Time',
                yaxis_title='Rating',
                yaxis=dict(tickmode='linear', tick0=1, dtick=1)
            )

            st.plotly_chart(fig2, width="stretch")

# ----------- REVIEW LIST ------------
st.markdown("## 📝 All Reviews")

all_reviews = storage.get_all_reviews()

if all_reviews:
    reviews_df = pd.DataFrame(all_reviews)

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        rating_filter = st.selectbox(
            "Filter by Rating:",
            options=["All"] + list(range(1, 6)),
            format_func=lambda x: f"{x}⭐" if x != "All" else "All Ratings"
        )

    with col2:
        search_term = st.text_input("Search reviews:", placeholder="Enter keyword...")

    with col3:
        show_ai_content = st.checkbox("Show AI Analysis", value=False)

    # Apply filters
    filtered_reviews = reviews_df.copy()

    if rating_filter != "All":
        filtered_reviews = filtered_reviews[filtered_reviews['user_rating'] == rating_filter]

    if search_term:
        filtered_reviews = filtered_reviews[
            filtered_reviews['user_review'].str.contains(search_term, case=False, na=False) |
            filtered_reviews['ai_summary'].str.contains(search_term, case=False, na=False)
        ]

    st.info(f"Showing {len(filtered_reviews)} of {len(reviews_df)} reviews")

    # Display each review card
    for idx, review in filtered_reviews.iterrows():
        st.markdown(f"""
        <div class="review-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div class="rating-stars">{'⭐' * review['user_rating']}</div>
                <div style="color: #666; font-size: 0.9rem;">{review.get('timestamp', 'N/A')[:10]}</div>
            </div>
            <p><strong>Review:</strong> {review['user_review']}</p>
        </div>
        """, unsafe_allow_html=True)

        if show_ai_content:
            colA, colB = st.columns(2)
            with colA:
                st.markdown("**AI Summary:**")
                st.write(review['ai_summary'])
            with colB:
                st.markdown("**Recommended Action:**")
                st.write(review['ai_recommended_action'])

            st.markdown("**AI Response:**")
            st.info(review['ai_response'])

        st.markdown("---")

    # ----------- EXPORT SECTION ------------
    st.subheader("📤 Export Data")
    col1, col2 = st.columns(2)

    # CSV Export
    with col1:
        if st.button("Export to CSV"):
            csv_path = "yelp_reviews_export.csv"
            if storage.export_to_csv(csv_path):
                with open(csv_path, "rb") as f:
                    st.download_button(
                        label="Download CSV",
                        data=f.read(),
                        file_name="yelp_reviews_export.csv",
                        mime="text/csv"
                    )
                st.success("✅ CSV export ready!")
            else:
                st.error("❌ Failed to export CSV.")

    # JSON Export
    with col2:
        if st.button("Export to JSON"):
            json_data = json.dumps(all_reviews, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="yelp_reviews_export.json",
                mime="application/json"
            )
            st.success("✅ JSON export ready!")

else:
    st.warning("No reviews found. Use the User Dashboard to submit reviews!")

# Footer
st.markdown("---")
st.markdown("<center style='color:#666;'>End of Dashboard</center>", unsafe_allow_html=True)
