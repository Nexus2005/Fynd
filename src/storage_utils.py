"""
Shared storage utilities for Task 2 dashboards.
Both user and admin dashboards use this for reading/writing review data.
"""

import json
import csv
import os
from typing import Dict, List, Any
from datetime import datetime
import pandas as pd

class ReviewStorage:
    """Handles all storage operations for reviews"""
    
    def __init__(self, storage_path: str = "reviews.json"):
        self.storage_path = storage_path
        self.ensure_storage_exists()
    
    def ensure_storage_exists(self):
        """Create storage file if it doesn't exist"""
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump([], f)
    
    def save_review(self, review_data: Dict[str, Any]) -> bool:
        """
        Save a new review to storage
        
        Args:
            review_data: Dictionary containing:
                - user_rating: int (1-5)
                - user_review: str
                - ai_response: str
                - ai_summary: str
                - ai_recommended_action: str
                - timestamp: str (ISO format)
        
        Returns:
            bool: Success status
        """
        try:
            # Load existing reviews
            with open(self.storage_path, 'r') as f:
                reviews = json.load(f)
            
            # Add metadata
            review_data['id'] = len(reviews) + 1
            review_data['timestamp'] = datetime.now().isoformat()
            
            # Append new review
            reviews.append(review_data)
            
            # Save back to file
            with open(self.storage_path, 'w') as f:
                json.dump(reviews, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving review: {e}")
            return False
    
    def get_all_reviews(self) -> List[Dict[str, Any]]:
        """Get all reviews from storage"""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading reviews: {e}")
            return []
    
    def get_reviews_dataframe(self) -> pd.DataFrame:
        """Get all reviews as a pandas DataFrame"""
        reviews = self.get_all_reviews()
        return pd.DataFrame(reviews)
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get basic analytics from reviews"""
        df = self.get_reviews_dataframe()
        
        if df.empty:
            return {
                'total_reviews': 0,
                'avg_rating': 0,
                'rating_distribution': {},
                'recent_reviews': []
            }
        
        # Rating distribution
        rating_dist = df['user_rating'].value_counts().sort_index().to_dict()
        
        # Ensure all ratings 1-5 are present
        for i in range(1, 6):
            if i not in rating_dist:
                rating_dist[i] = 0
        
        return {
            'total_reviews': len(df),
            'avg_rating': df['user_rating'].mean(),
            'rating_distribution': rating_dist,
            'recent_reviews': df.tail(10).to_dict('records')
        }
    
    def export_to_csv(self, csv_path: str) -> bool:
        """Export reviews to CSV format"""
        try:
            df = self.get_reviews_dataframe()
            df.to_csv(csv_path, index=False)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

# Global storage instance
storage = ReviewStorage()

def get_storage() -> ReviewStorage:
    """Get the global storage instance"""
    return storage