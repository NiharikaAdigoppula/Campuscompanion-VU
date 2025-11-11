# Complete Deployment Guide - Vercel & Render

## 🎯 Overview
- **Frontend**: React app → Vercel
- **Backend**: Node.js API → Render
- **Database**: MongoDB Atlas (already configured)
- **Python AI Service**: FastAPI → Render (optional)

---

# PART 1: Deploy Frontend on Vercel ✨

## Step 1: Create Vercel Account
1. Go to **https://vercel.com**
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"**
4. Authorize Vercel to access your GitHub account
5. Complete signup

## Step 2: Import Your Project
1. Click **"Add New"** (top right)
2. Select **"Project"**
3. You'll see a list of your GitHub repositories
4. Find and click on **"Campuscompanion-VU"**
5. Click **"Import"**

## Step 3: Configure Build Settings
Vercel should auto-detect these, but verify:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Create React App |
| **Root Directory** | `frontend/` |
| **Build Command** | `npm run build` |
| **Output Directory** | `build` |
| **Install Command** | `npm install` |

If these aren't auto-filled:
- Click **"Edit"** next to "Configure Project"
- Manually enter the values above

## Step 4: Add Environment Variables
Before deploying, add the environment variable:

1. Scroll to **"Environment Variables"** section
2. Click **"Add"**
3. Fill in:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: `https://campus-companion-backend.onrender.com` (we'll get this from Render)
   - **Environments**: Select all (Production, Preview, Development)
4. Click **"Add"**

**⚠️ NOTE**: We'll update this URL after deploying the backend on Render.

For now, you can use a placeholder or skip this step and add it after Render deployment.

## Step 5: Deploy
1. Click **"Deploy"**
2. Wait 2-3 minutes for the build to complete
3. Once complete, you'll get a URL like: `https://campuscompanion-vu.vercel.app`
4. **Save this URL** - you'll need it for backend configuration

## Step 6: Verify Frontend
1. Click the deployment URL
2. Your React app should load
3. If you see errors in the browser console about API, that's normal (backend not deployed yet)

---

# PART 2: Deploy Backend on Render 🔧

## Step 1: Create Render Account
1. Go to **https://render.com**
2. Click **"Get Started"**
3. Choose **"Sign Up with GitHub"**
4. Authorize Render to access your GitHub
5. Complete signup

## Step 2: Create Web Service
1. Click **"New +"** (top right)
2. Select **"Web Service"**
3. A list of your GitHub repositories will appear
4. Find **"Campuscompanion-VU"** and click **"Connect"**

## Step 3: Configure Service
Fill in the configuration form:

| Field | Value |
|-------|-------|
| **Name** | `campus-companion-backend` |
| **Environment** | `Node` |
| **Build Command** | `npm install` |
| **Start Command** | `npm start` |
| **Instance Type** | `Free` (or upgrade if needed) |

## Step 4: Add Environment Variables
Click **"Add Environment Variable"** and add each one:

### Variable 1: MongoDB URI
- **Key**: `MONGODB_URI`
- **Value**: `mongodb+srv://campusadmin:Niharika1234@cluster0.3c4ud6.mongodb.net/campus-companion?retryWrites=true&w=majority&appName=Cluster0`

### Variable 2: JWT Secret
- **Key**: `JWT_SECRET`
- **Value**: `campus-companion-super-secret-key-2025-niharika-project-xyz789`

### Variable 3: Gemini API Key
- **Key**: `GEMINI_API_KEY`
- **Value**: `AIzaSyCM96WJhe2J9IGqOis01srq8jemIGki-qg`

### Variable 4: Environment
- **Key**: `NODE_ENV`
- **Value**: `production`

### Variable 5: Port
- **Key**: `PORT`
- **Value**: `5000`

### Variable 6: Frontend URL (add after Vercel deployment)
- **Key**: `FRONTEND_URL`
- **Value**: `https://YOUR-VERCEL-URL.vercel.app` (we'll add this later)

## Step 5: Deploy
1. Click **"Create Web Service"**
2. Render will start building (check logs for progress)
3. Build typically takes 3-5 minutes
4. Once complete, you'll get a URL like: `https://campus-companion-backend.onrender.com`
5. **Save this URL** - it's your backend API

## Step 6: Verify Backend
```bash
# Test the API health endpoint
curl https://campus-companion-backend.onrender.com/api/health
```

Expected response:
```json
{
  "status": "ok",
  "message": "CampusCompanion API is running"
}
```

---

# PART 3: Update Vercel with Backend URL 🔗

Now that you have both URLs, connect them:

## Step 1: Get Both URLs
- **Vercel Frontend**: `https://campuscompanion-vu.vercel.app` (or your domain)
- **Render Backend**: `https://campus-companion-backend.onrender.com` (or your domain)

## Step 2: Update Vercel Environment Variable
1. Go to **Vercel Dashboard**
2. Select your **campuscompanion-vu** project
3. Go to **Settings** → **Environment Variables**
4. Find or add `REACT_APP_API_URL`
5. Set the value to: `https://campus-companion-backend.onrender.com`
6. Click **"Save"**
7. Vercel will automatically redeploy

## Step 3: Update Render Backend URL
1. Go to **Render Dashboard**
2. Select **campus-companion-backend** service
3. Go to **Environment** tab
4. Find or add `FRONTEND_URL`
5. Set the value to: `https://campuscompanion-vu.vercel.app`
6. Click **"Save"**
7. Render will automatically redeploy

---

# PART 4: Deploy Python AI Service (Optional) 🤖

## Step 1: Create Web Service on Render
1. In **Render Dashboard**, click **"New +"** → **"Web Service"**
2. Connect **Campuscompanion-VU** repository
3. Fill in:

| Field | Value |
|-------|-------|
| **Name** | `campus-companion-python-ai` |
| **Environment** | `Python 3.11` |
| **Build Command** | `pip install -r python-ai-service/requirements.txt` |
| **Start Command** | `cd python-ai-service && python main.py` |

## Step 2: Add Environment Variables
Add these variables:

### Variable 1: MongoDB URI
- **Key**: `MONGODB_URI`
- **Value**: `mongodb+srv://campusadmin:Niharika1234@cluster0.3c4ud6.mongodb.net/campus-companion?retryWrites=true&w=majority&appName=Cluster0`

### Variable 2: Gemini API Key
- **Key**: `GEMINI_API_KEY`
- **Value**: `AIzaSyCM96WJhe2J9IGqOis01srq8jemIGki-qg`

### Variable 3: Python Port
- **Key**: `PYTHON_AI_PORT`
- **Value**: `8000`

## Step 3: Deploy
1. Click **"Create Web Service"**
2. Wait for build to complete
3. You'll get a URL like: `https://campus-companion-python-ai.onrender.com`

## Step 4: Verify Python Service
```bash
curl https://campus-companion-python-ai.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "agents": {"student_planner": "active", ...},
  "chatbot": "active",
  "voice_assistant": "active"
}
```

---

# PART 5: Final Verification ✅

## Test All Services

### 1. Test Backend API
```bash
curl https://campus-companion-backend.onrender.com/api/health
```

### 2. Test Frontend
Open in browser: `https://campuscompanion-vu.vercel.app`
- Should load without errors
- Check browser console (F12) for any API errors

### 3. Test Python Service (if deployed)
```bash
curl https://campus-companion-python-ai.onrender.com/health
```

## Test Full Integration
1. Go to frontend URL
2. Try to login (use any credentials, backend will validate)
3. Try any agentic AI feature (Study Planner, etc.)
4. Should work without errors

---

# 📊 Final Architecture

```
┌─────────────────────┐
│  Vercel Frontend    │
│ campuscompanion-vu  │
│  (React App)        │
└──────────┬──────────┘
           │
           ▼ (REACT_APP_API_URL)
┌─────────────────────┐
│   Render Backend    │
│ campus-companion    │
│ (Node.js + Express) │
└──────────┬──────────┘
           │
           ├──▶ MongoDB Atlas (Shared DB)
           │
           └──▶ Render Python AI (Optional)
                (FastAPI agents)
```

---

# 🆘 Troubleshooting

## Frontend Shows "Cannot Connect to API"
1. Check `REACT_APP_API_URL` is set correctly in Vercel
2. Verify backend URL is accessible:
   ```bash
   curl https://campus-companion-backend.onrender.com/api/health
   ```
3. Check browser console (F12) for exact error
4. CORS might be blocked - check backend logs

## Backend Won't Start
1. Check **Render Dashboard** → **Logs** for error messages
2. Common issues:
   - Missing environment variables
   - MongoDB connection string is wrong
   - Node modules not installed
3. Try redeploying: Click **"Manual Deploy"** → **"Deploy latest commit"**

## Python Service Won't Start
1. Check **Render Dashboard** → **Logs** for error messages
2. Ensure all Python dependencies are installed
3. Check `PYTHON_AI_PORT=8000` is set
4. Verify MongoDB connection string

## Database Connection Issues
1. Go to **MongoDB Atlas** dashboard
2. Check **Network Access** (IP Whitelist)
3. Render servers should be whitelisted (usually 0.0.0.0/0 for public databases)
4. Verify connection string has correct username and password

---

# 🎯 Summary

| Service | URL | Status |
|---------|-----|--------|
| Frontend (Vercel) | https://campuscompanion-vu.vercel.app | ⏳ Deploy now |
| Backend (Render) | https://campus-companion-backend.onrender.com | ⏳ Deploy now |
| Python AI (Render) | https://campus-companion-python-ai.onrender.com | ⏳ Optional |
| Database (MongoDB Atlas) | mongodb+srv://... | ✅ Already configured |

---

# 🚀 Next Steps

1. **Deploy Frontend on Vercel** (follow PART 1)
2. **Deploy Backend on Render** (follow PART 2)
3. **Update URLs** in both services (follow PART 3)
4. **Deploy Python AI** (optional, follow PART 4)
5. **Test everything** (follow PART 5)

Ready to deploy? Let me know if you hit any issues! 💪
