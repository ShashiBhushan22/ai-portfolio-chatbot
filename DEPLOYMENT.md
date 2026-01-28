# Deploying the AI Portfolio Chatbot

## Option 1: Deploy to Render (Recommended - Free Tier Available)

### Step 1: Push to GitHub
```bash
cd /home/bhushan-arc/AI_Engineer/ai-portfolio-chatbot
git remote add origin https://github.com/ShashiBhushan22/ai-portfolio-chatbot.git
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to https://render.com and sign up/login
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: ai-portfolio-chatbot
   - **Root Directory**: backend
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variable:
   - `GROQ_API_KEY`: your-groq-api-key
6. Click "Create Web Service"

### Step 3: Get Your Backend URL
After deployment, you'll get a URL like: `https://ai-portfolio-chatbot.onrender.com`

---

## Option 2: Deploy to Railway (Alternative)

### Step 1: Push to GitHub (same as above)

### Step 2: Deploy on Railway
1. Go to https://railway.app and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your ai-portfolio-chatbot repository
4. Set Root Directory to `backend`
5. Add Environment Variable:
   - `GROQ_API_KEY`: your-groq-api-key
6. Railway will auto-detect Python and deploy

---

## After Deployment: Update Your Website

Once deployed, update the chat widget URL in your website:

### Edit `/home/bhushan-arc/AI_Engineer/website-repo/index.html`:
```javascript
ChatWidget.init({
    apiUrl: 'https://YOUR-ACTUAL-BACKEND-URL.onrender.com',  // Replace with your URL
    position: 'bottom-right',
    primaryColor: '#3b82f6',
    title: "Shashi's AI Assistant",
    subtitle: 'Ask me anything about Shashi!'
});
```

### Push website changes:
```bash
cd /home/bhushan-arc/AI_Engineer/website-repo
git add -A
git commit -m "Add AI chatbot widget"
git push origin main
```

---

## Testing Locally First

Before deploying, test locally:
```bash
# Terminal 1: Run backend
cd /home/bhushan-arc/AI_Engineer/ai-portfolio-chatbot/backend
source ../../.venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Open website
cd /home/bhushan-arc/AI_Engineer/website-repo
python3 -m http.server 3000
# Visit http://localhost:3000
```

For local testing, temporarily change apiUrl to `http://localhost:8000`

---

## CORS Configuration

The backend is already configured to accept requests from your website domain. After deployment, if you encounter CORS issues, update `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://shashibhushanjha.me",
        "http://localhost:3000",
        "https://your-render-url.onrender.com"
    ],
    # ... rest of config
)
```

---

## Environment Variables Required

| Variable | Description | Example |
|----------|-------------|---------|
| GROQ_API_KEY | Your Groq API key | gsk_xxxxx... |

---

## Troubleshooting

### Chatbot not responding?
1. Check browser console for errors
2. Verify backend URL is correct
3. Check Render/Railway logs for errors

### CORS errors?
1. Add your domain to allowed origins in main.py
2. Redeploy the backend

### Slow responses?
1. First request may be slow due to cold start (free tier)
2. Subsequent requests should be faster

---

## Summary of Files to Deploy

**Backend (to Render/Railway):**
- `/ai-portfolio-chatbot/backend/` - FastAPI application

**Website (to GitHub Pages or your hosting):**
- `/website-repo/index.html` - Updated with chatbot widget
- `/website-repo/chat-widget.js` - Chatbot JavaScript
- `/website-repo/chat-widget.css` - Chatbot styles
