# 🚀 CampusCompanion Deployment - Quick Start

## ✅ What's Done
- ✅ Project pushed to GitHub: https://github.com/NiharikaAdigoppula/Campuscompanion-VU
- ✅ All 1,980 commits with full history
- ✅ MongoDB Atlas configured and connected
- ✅ All API keys configured (GEMINI_API_KEY, JWT_SECRET)

---

## 📋 What You Need to Do

### 🎯 STEP 1: Deploy Frontend on Vercel (5 mins)
**Go to**: https://vercel.com/new

1. **Sign in** with GitHub
2. **Select** Campuscompanion-VU repository
3. **Root Directory**: `frontend/`
4. **Click Deploy**
5. **Get URL** → Save it (e.g., `https://campuscompanion-vu.vercel.app`)

---

### 🎯 STEP 2: Deploy Backend on Render (5 mins)
**Go to**: https://render.com

1. **Sign in** with GitHub
2. **New Web Service** → Select Campuscompanion-VU
3. **Fill in**:
   - Name: `campus-companion-backend`
   - Environment: `Node`
   - Build: `npm install`
   - Start: `npm start`

4. **Add Environment Variables**:
   ```
   MONGODB_URI = mongodb+srv://campusadmin:Niharika1234@cluster0.3c4ud6.mongodb.net/campus-companion?retryWrites=true&w=majority&appName=Cluster0
   JWT_SECRET = campus-companion-super-secret-key-2025-niharika-project-xyz789
   GEMINI_API_KEY = AIzaSyCM96WJhe2J9IGqOis01srq8jemIGki-qg
   NODE_ENV = production
   PORT = 5000
   ```

5. **Click Deploy**
6. **Get URL** → Save it (e.g., `https://campus-companion-backend.onrender.com`)

---

### 🎯 STEP 3: Link Frontend & Backend (2 mins)

**In Vercel**:
- Go to project → Settings → Environment Variables
- Add/Update: `REACT_APP_API_URL = https://campus-companion-backend.onrender.com`
- Save (auto-redeploys)

**In Render**:
- Go to backend service → Environment
- Add/Update: `FRONTEND_URL = https://campuscompanion-vu.vercel.app`
- Save (auto-redeploys)

---

### 🎯 STEP 4 (Optional): Deploy Python AI on Render

Same as backend but:
- Name: `campus-companion-python-ai`
- Environment: `Python 3.11`
- Build: `pip install -r python-ai-service/requirements.txt`
- Start: `cd python-ai-service && python main.py`
- Port: `8000`

---

## 🧪 Verify Everything Works

### Test Backend
```bash
curl https://campus-companion-backend.onrender.com/api/health
```
Should return: `{"status":"ok","message":"CampusCompanion API is running"}`

### Test Frontend
Open in browser: `https://campuscompanion-vu.vercel.app`
- Should load your React app
- Login should work
- Features should connect to backend

### Test Python AI (if deployed)
```bash
curl https://campus-companion-python-ai.onrender.com/health
```
Should return: `{"status":"healthy","database":"connected",...}`

---

## 📚 Full Guides Available

1. **VERCEL_RENDER_DEPLOYMENT_GUIDE.md** - Complete step-by-step with screenshots
2. **DEPLOYMENT_GUIDE.md** - Detailed troubleshooting
3. **DEPLOYMENT_CHECKLIST.md** - Quick reference

---

## 🎯 Final Architecture

```
You (Browser)
    ↓
Vercel (Frontend - React)
    ↓
Render (Backend - Node.js)
    ↓
MongoDB Atlas (Database)
    
Optional:
Render (Python AI - FastAPI)
    ↓
MongoDB Atlas (Shared DB)
```

---

## 📊 Summary

| Component | Service | Status |
|-----------|---------|--------|
| Frontend | Vercel | ⏳ Ready to deploy |
| Backend | Render | ⏳ Ready to deploy |
| Python AI | Render | ⏳ Optional |
| Database | MongoDB Atlas | ✅ Configured |

---

## 🚀 Ready? Start Here:
1. Go to https://vercel.com/new
2. Go to https://render.com
3. Link the URLs between them
4. Test!

**Estimated total time: 15-20 minutes** ⏱️

Need help? Check the detailed guides! 📖
