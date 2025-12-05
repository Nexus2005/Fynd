"""
Admin Dashboard - Streamlit App
View all submissions, analytics, and manage reviews
"""

import streamlit as st
import sys
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add src path
sys.path.append(str(Path(__file__).parent / "src"))

from storage_utils import get_storage

st.set_page_config(
    page_title="Admin Dashboard - Yelp Reviews",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

storage = get_storage()

# Style
st.markdown("""
<style>
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

st.title("📊 Admin Dashboard - Yelp Review Analytics")

analytics = storage.get_analytics()

# ---------------- OVERVIEW ----------------
st.markdown("## 📈 Overview")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class='metric-card'>
        <h3>Total Reviews</h3>
        <h2>{analytics['total_reviews']}</h2>
    </div>
    """, unsafe_allow_html=True)

with c2:
    avg = f"{analytics['avg_rating']:.1f}" if analytics['avg_rating'] else "N/A"
    st.markdown(f"""
    <div class='metric-card'>
        <h3>Average Rating</h3>
        <h2>{avg} ⭐</h2>
    </div>
    """, unsafe_allow_html=True)

with c3:
    if analytics['total_reviews']:
        pct = f"{analytics['rating_distribution'].get(5, 0) / analytics['total_reviews'] * 100:.1f}%"
    else:
        pct = "0%"
    st.markdown(f"""
    <div class='metric-card'>
        <h3>5-Star Reviews</h3>
        <h2>{pct}</h2>
    </div>
    """, unsafe_allow_html=True)

with c4:
    low = analytics['rating_distribution'].get(1, 0) + analytics['rating_distribution'].get(2, 0)
    st.markdown(f"""
    <div class='metric-card'>
        <h3>Low Ratings (1–2⭐)</h3>
        <h2>{low}</h2>
    </div>
    """, unsafe_allow_html=True)


# ---------------- ANALYTICS CHARTS ----------------
if analytics['total_reviews'] > 0:
    st.markdown("## 📊 Analytics")

    c1, c2 = st.columns(2)

    # Rating distribution
    with c1:
        data = [{'Rating': f"{i}⭐", 'Count': analytics['rating_distribution'].get(i, 0)} for i in range(1, 6)]
        df = pd.DataFrame(data)
        fig = px.bar(df, x="Rating", y="Count", title="Rating Distribution")
        st.plotly_chart(fig, width="stretch")

    # Recent activity
    with c2:
        recent = pd.DataFrame(analytics["recent_reviews"])

        if not recent.empty:
            # FIX: Prevent crash on invalid/empty timestamps
            recent["timestamp"] = pd.to_datetime(recent["timestamp"], errors="coerce")
            recent = recent.dropna(subset=["timestamp"])
            recent = recent.sort_values("timestamp")

            if not recent.empty:
                fig2 = px.scatter(
                    recent,
                    x="timestamp",
                    y="user_rating",
                    title="Recent Review Activity",
                )
                st.plotly_chart(fig2, width="stretch")


# ---------------- REVIEW LIST ----------------
st.markdown("## 📝 All Reviews")

reviews = storage.get_all_reviews()

if reviews:
    df = pd.DataFrame(reviews)

    f1, f2, f3 = st.columns(3)

    with f1:
        rating_filter = st.selectbox("Filter by Rating", ["All"] + list(range(1, 6)))

    with f2:
        search = st.text_input("Search reviews")

    with f3:
        show_ai = st.checkbox("Show AI Analysis")

    filtered = df.copy()

    if rating_filter != "All":
        filtered = filtered[filtered["user_rating"] == rating_filter]

    if search:
        filtered = filtered[
            filtered["user_review"].str.contains(search, case=False, na=False)
            | filtered["ai_summary"].str.contains(search, case=False, na=False)
        ]

    st.info(f"Showing {len(filtered)} of {len(df)} reviews")

    for _, review in filtered.iterrows():
        st.markdown(f"""
        <div class='review-card'>
            <div style='display:flex; justify-content:space-between;'>
                <div class='rating-stars'>{'⭐' * review['user_rating']}</div>
                <div style='color:#666'>{review.get('timestamp', '')[:10]}</div>
            </div>
            <p><b>Review:</b> {review['user_review']}</p>
        </div>
        """, unsafe_allow_html=True)

        if show_ai:
            st.write("**AI Summary:**", review["ai_summary"])
            st.write("**Recommended Action:**", review["ai_recommended_action"])
            st.info(review["ai_response"])

        st.markdown("---")

    # -------- EXPORTS ----------
    st.subheader("📤 Export Data")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Export CSV"):
            path = "export.csv"
            if storage.export_to_csv(path):
                with open(path, "rb") as f:
                    st.download_button("Download CSV", f.read(), "yelp_reviews.csv", "text/csv")
                st.success("Ready!")
            else:
                st.error("Failed.")

    with c2:
        if st.button("Export JSON"):
            j = json.dumps(reviews, indent=2)
            st.download_button("Download JSON", j, "yelp_reviews.json")
else:
    st.warning("No reviews found.")

st.markdown("---")
st.markdown("<center style='color:#666;'>End of Dashboard</center>", unsafe_allow_html=True)
