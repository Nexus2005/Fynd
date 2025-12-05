# Deployment Guide

This guide provides detailed instructions for deploying the Yelp AI Intern project to various cloud platforms.

## 🚀 Quick Deployment Options

### Option 1: Streamlit Cloud (Recommended)

#### Step 1: Prepare Your Repository

```bash
# Ensure your project structure is correct
tree -I '__pycache__|*.pyc|.git'

# Should show:
# .
# ├── user_dashboard.py
# ├── admin_dashboard.py
# ├── requirements.txt
# ├── src/
# │   ├── storage_utils.py
# │   └── llm_utils.py
# └── ...
```

#### Step 2: Deploy User Dashboard

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Configure:
   - **Repository**: Select your GitHub repo
   - **Branch**: main (or your branch)
   - **Main file path**: `user_dashboard.py`
   - **App URL**: Choose a unique name

5. Add environment variable:
   - Key: `GEMINI_API_KEY`
   - Value: Your actual Gemini API key

6. Click "Deploy"

#### Step 3: Deploy Admin Dashboard

1. Create another app in Streamlit Cloud
2. Use same repository
3. Configure:
   - **Main file path**: `admin_dashboard.py`
   - **App URL**: Choose different name (e.g., `your-app-admin`)

4. Add same `GEMINI_API_KEY` environment variable
5. Deploy

#### Step 4: Access Your Apps

- User Dashboard: `https://your-app-name.streamlit.app`
- Admin Dashboard: `https://your-app-admin.streamlit.app`

### Option 2: HuggingFace Spaces

#### Step 1: Create Combined App

Create `app.py` that combines both dashboards:

```python
import streamlit as st
from src.storage_utils import get_storage
from src.llm_utils import get_llm_manager

# Page config
st.set_page_config(page_title="Yelp AI Review System", layout="wide")

# Initialize services
storage = get_storage()
llm = get_llm_manager()

# Create tabs
tab1, tab2 = st.tabs(["User Dashboard", "Admin Dashboard"])

with tab1:
    # User dashboard content
    st.title("🌟 User Dashboard")
    # ... rest of user dashboard code

with tab2:
    # Admin dashboard content
    st.title("📊 Admin Dashboard")
    # ... rest of admin dashboard code
```

#### Step 2: Create Space Structure

```
space/
├── app.py
├── requirements.txt
├── src/
│   ├── storage_utils.py
│   └── llm_utils.py
└── README.md
```

#### Step 3: Deploy to HuggingFace

1. Create account on [huggingface.co](https://huggingface.co)
2. Create new Space:
   - Choose "Streamlit" as SDK
   - Set repository name
   - Make it public or private

3. Push your code:
```bash
git clone https://huggingface.co/spaces/your-username/your-space-name
cd your-space-name
cp -r /path/to/your/project/* .
git add .
git commit -m "Initial commit"
git push
```

4. Add secret:
   - Go to Space Settings
   - Add `GEMINI_API_KEY` as secret

### Option 3: Render (Alternative)

#### Step 1: Create Render Configuration

Create `render.yaml`:
```yaml
services:
  - type: web
    name: user-dashboard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run user_dashboard.py --server.port=$PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false

  - type: web
    name: admin-dashboard
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run admin_dashboard.py --server.port=$PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false
```

#### Step 2: Deploy

1. Connect GitHub repository to Render
2. Select `render.yaml` configuration
3. Add environment variable
4. Deploy both services

## 🔧 Environment Configuration

### Required Environment Variables

```bash
# Core
GEMINI_API_KEY=your-actual-api-key

# Optional
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

### Platform-Specific Instructions

#### Streamlit Cloud
- Add variables in "Settings" → "Secrets"
- Format: Key-value pairs

#### HuggingFace Spaces
- Add in "Settings" → "Secrets"
- Automatically injected as environment variables

#### Render
- Add in "Environment" tab
- Supports both plain text and secret types

## 📊 Monitoring and Maintenance

### Health Checks

Create `health_check.py`:
```python
import requests
import sys

def check_app_health(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {url} is healthy")
            return True
        else:
            print(f"❌ {url} returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {url} error: {e}")
        return False

if __name__ == "__main__":
    user_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8501"
    admin_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8502"
    
    print("🔍 Health Check Results:")
    check_app_health(user_url)
    check_app_health(admin_url)
```

### Performance Monitoring

Add to your Streamlit apps:
```python
import time

# Track response times
start_time = time.time()
# ... your code ...
response_time = time.time() - start_time

# Log slow operations
if response_time > 5:  # 5 seconds
    print(f"⚠️ Slow operation: {response_time:.2f}s")
```

### Error Tracking

```python
import traceback

def log_error(error):
    error_details = {
        'error': str(error),
        'traceback': traceback.format_exc(),
        'timestamp': datetime.now().isoformat()
    }
    
    # Log to file or external service
    with open('errors.log', 'a') as f:
        f.write(json.dumps(error_details) + '\n')
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python tests/test_setup.py
    
    - name: Deploy to Streamlit Cloud
      run: |
        # This would trigger Streamlit Cloud deployment
        echo "Deployment triggered"
```

## 🛡️ Security Best Practices

### API Key Management

1. **Never commit API keys to git**
   ```bash
   echo "*.env" >> .gitignore
   echo "**/secrets.env" >> .gitignore
   ```

2. **Use environment variables**
   ```python
   import os
   API_KEY = os.getenv('GEMINI_API_KEY')
   if not API_KEY:
       raise ValueError("API key not found")
   ```

3. **Rotate keys regularly**
   - Set calendar reminders
   - Update in all deployed environments
   - Test after rotation

### Data Protection

```python
# Sanitize user inputs
def sanitize_input(text):
    # Remove potential harmful content
    return text.strip()[:1000]  # Limit length

# Secure file operations
import fcntl
import os

def secure_write(filename, data):
    with open(filename, 'w') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(data, f)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

## 📈 Scaling Considerations

### Database Migration

When JSON storage becomes insufficient:

```python
# SQLite upgrade example
import sqlite3

def migrate_to_sqlite():
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY,
            user_rating INTEGER,
            user_review TEXT,
            ai_response TEXT,
            ai_summary TEXT,
            ai_recommended_action TEXT,
            timestamp TEXT
        )
    ''')
    
    # Migrate existing data
    with open('reviews.json', 'r') as f:
        reviews = json.load(f)
    
    for review in reviews:
        cursor.execute('''
            INSERT INTO reviews VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            review.get('id'),
            review.get('user_rating'),
            review.get('user_review'),
            review.get('ai_response'),
            review.get('ai_summary'),
            review.get('ai_recommended_action'),
            review.get('timestamp')
        ))
    
    conn.commit()
    conn.close()
```

### Load Balancing

For high-traffic deployments:

```yaml
# docker-compose.yml
version: '3.8'
services:
  user-app:
    build: .
    ports:
      - "8501"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    deploy:
      replicas: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - user-app
```

## 🆘 Troubleshooting

### Common Issues

1. **App won't start**
   ```bash
   # Check logs
   streamlit logs
   
   # Verify dependencies
   pip list | grep streamlit
   ```

2. **API key not working**
   ```python
   # Test API key
   import os
   print(os.getenv('GEMINI_API_KEY'))
   
   # Test API connection
   import google.generativeai as genai
   genai.configure(api_key='your-key')
   model = genai.GenerativeModel('gemini-1.5-pro')
   response = model.generate_content("Hello")
   print(response.text)
   ```

3. **Storage file issues**
   ```bash
   # Check permissions
   ls -la reviews.json
   
   # Test write access
   python -c "import json; json.dump([], open('test.json', 'w'))"
   ```

### Getting Help

1. Check application logs
2. Verify environment variables
3. Test individual components
4. Review platform documentation

## 📚 Additional Resources

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-cloud)
- [HuggingFace Spaces Guide](https://huggingface.co/docs/hub/spaces)
- [Render Deployment Docs](https://render.com/docs)
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)

---

**Good luck with your deployment! 🚀**