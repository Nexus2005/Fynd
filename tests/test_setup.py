"""
Test script to verify the project setup is working correctly.
Run this to check if all components are properly configured.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pandas: {e}")
        return False
    
    try:
        import streamlit as st
        print("✅ streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import streamlit: {e}")
        return False
    
    try:
        import google.generativeai as genai
        print("✅ google-generativeai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import google-generativeai: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ numpy imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import numpy: {e}")
        return False
    
    try:
        import matplotlib.pyplot as plt
        print("✅ matplotlib imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import matplotlib: {e}")
        return False
    
    return True

def test_storage():
    """Test storage utilities"""
    print("\n🔍 Testing storage utilities...")
    
    try:
        from src.storage_utils import get_storage
        storage = get_storage()
        
        # Test saving a review
        test_review = {
            'user_rating': 5,
            'user_review': 'Test review for setup verification',
            'ai_response': 'Test AI response',
            'ai_summary': 'Test summary',
            'ai_recommended_action': 'Test recommendation'
        }
        
        if storage.save_review(test_review):
            print("✅ Storage save test passed")
        else:
            print("❌ Storage save test failed")
            return False
        
        # Test retrieving reviews
        reviews = storage.get_all_reviews()
        if len(reviews) > 0:
            print("✅ Storage retrieval test passed")
        else:
            print("❌ Storage retrieval test failed")
            return False
        
        # Test analytics
        analytics = storage.get_analytics()
        if 'total_reviews' in analytics:
            print("✅ Analytics test passed")
        else:
            print("❌ Analytics test failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        return False

def test_llm():
    """Test LLM utilities (requires API key)"""
    print("\n🔍 Testing LLM utilities...")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  GEMINI_API_KEY not set, skipping LLM tests")
        return True  # Don't fail the overall test for missing API key
    
    try:
        from src.llm_utils import get_llm_manager
        llm = get_llm_manager()
        
        # Test response generation
        response = llm.generate_user_response(5, "Great service and amazing food!")
        if response and len(response) > 0:
            print("✅ LLM response generation test passed")
        else:
            print("❌ LLM response generation test failed")
            return False
        
        # Test summary generation
        summary = llm.generate_summary(5, "Great service and amazing food!")
        if summary and len(summary) > 0:
            print("✅ LLM summary generation test passed")
        else:
            print("❌ LLM summary generation test failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ LLM test failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'user_dashboard.py',
        'admin_dashboard.py',
        'src/storage_utils.py',
        'src/llm_utils.py',
        'prompts/prompt_templates.md',
        'requirements.txt',
        'README.md',
        'reviews.json'
    ]
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🧪 Yelp AI Intern Project - Setup Test\n")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("File Structure", test_file_structure),
        ("Storage", test_storage),
        ("LLM", test_llm)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Set your GEMINI_API_KEY environment variable")
        print("2. Run: streamlit run user_dashboard.py")
        print("3. Run: streamlit run admin_dashboard.py")
        print("4. Open notebooks/task1_rating_prediction.ipynb")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Check file permissions")
        print("3. Verify Python version (3.8+)")

if __name__ == "__main__":
    main()