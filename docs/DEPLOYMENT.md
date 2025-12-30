# CampusShield AI - Deployment Guide

Complete step-by-step deployment guide for Render (Backend) and Vercel (Frontend).

---

## 📋 Prerequisites

- GitHub repository with your code
- Render account (free tier available)
- Vercel account (free tier available)
- API keys for your chosen LLM provider (OpenAI, Groq, or Gemini)

---

## 🚀 Part 1: Backend Deployment (Render)

### Step 1: Create Render Service

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository: `Campus-Shield--AI`

### Step 2: Configure Build Settings

**Service Name:** `campusshield-ai-backend`

**Build Command:**
```bash
pip install -r Backend/requirements.txt
```

**Start Command:**
```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

**Note:** Render automatically sets `$PORT` environment variable.

### Step 3: Environment Variables

Add these environment variables in Render Dashboard → Environment:

```bash
# Database
DATABASE_URL=postgresql://user:pass@hostname:5432/dbname
# (Render provides PostgreSQL - use the internal database URL)

# Security
CS_SECRET_KEY=your-super-secret-key-change-this-in-production
CS_DEBUG=False

# CORS (replace with your frontend URL after deploying)
CS_CORS_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:3000

# LLM Provider (choose one)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# OR use Groq:
# LLM_PROVIDER=groq
# GROQ_API_KEY=your-groq-api-key
# GROQ_MODEL=llama-3.1-8b-instant

# OR use Gemini:
# LLM_PROVIDER=gemini
# GEMINI_API_KEY=your-gemini-api-key
# GEMINI_MODEL=gemini-1.5-flash
```

### Step 4: PostgreSQL Database (Render)

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Service Name: `campusshield-db`
3. Plan: **Free** (or paid for production)
4. Copy the **Internal Database URL** and paste it into `DATABASE_URL`
5. (Optional) Copy the **External Database URL** for local development

### Step 5: Initialize Database

After deployment, run database migrations:

1. SSH into your Render service (or use Render Shell)
2. Or add a one-time script:

```bash
cd /opt/render/project/src
python -m Backend.app.scripts.init_db
```

Or create an admin user:
```bash
python Backend/app/scripts/create_admin.py
```

### Step 6: WebSocket Support

Render supports WebSocket by default for Web Services. Ensure your WebSocket endpoint is at `/ws/alerts` (already configured).

### Step 7: Health Checks

Render automatically checks `/health` endpoint. This is already implemented in `Backend/app/main.py`.

### Step 8: Deploy

Click **"Create Web Service"** and wait for deployment.

**Your backend URL will be:** `https://campusshield-ai-backend.onrender.com`

---

## 🌐 Part 2: Frontend Deployment (Vercel)

### Step 1: Create Vercel Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository: `Campus-Shield--AI`
4. Root Directory: **`dashboard`**

### Step 2: Configure Build Settings

**Framework Preset:** Create React App (detected automatically)

**Build Command:**
```bash
npm install && npm run build
```

**Output Directory:**
```
build
```

**Install Command:**
```bash
npm install
```

### Step 3: Environment Variables

Add in Vercel Dashboard → Settings → Environment Variables:

```bash
REACT_APP_API_URL=https://campusshield-ai-backend.onrender.com
```

**Important:** Replace with your actual Render backend URL.

### Step 4: Deploy

Click **"Deploy"** and wait for build completion.

**Your frontend URL will be:** `https://your-project-name.vercel.app`

---

## 🔄 Part 3: Update CORS After Deployment

After frontend is deployed, update backend CORS:

1. Go to Render Dashboard → Your Backend Service → Environment
2. Update `CS_CORS_ORIGINS`:
   ```
   https://your-project-name.vercel.app,https://your-project-name-git-main.vercel.app
   ```
3. Save and redeploy backend

---

## ✅ Post-Deployment Checklist

### Backend (Render)

- [ ] Health endpoint responds: `https://your-backend.onrender.com/health`
- [ ] API docs accessible (dev only): `https://your-backend.onrender.com/docs`
- [ ] Database initialized with tables
- [ ] Admin user created (optional)
- [ ] LLM API key configured and working
- [ ] WebSocket endpoint functional: `wss://your-backend.onrender.com/ws/alerts`

### Frontend (Vercel)

- [ ] Dashboard loads: `https://your-frontend.vercel.app`
- [ ] API connection working (check browser console)
- [ ] Health check successful
- [ ] Can fetch incidents/alerts
- [ ] AI Assistant page loads and connects to backend

---

## 🔧 Common Issues & Fixes

### Issue 1: Backend Returns 500 on Startup

**Cause:** Missing environment variables or database connection.

**Fix:**
- Check all environment variables are set
- Verify `DATABASE_URL` is correct
- Check Render logs for detailed error

### Issue 2: CORS Errors in Browser

**Cause:** Frontend URL not in `CS_CORS_ORIGINS`.

**Fix:**
- Add your Vercel URL to `CS_CORS_ORIGINS` in Render
- Include both `your-app.vercel.app` and `your-app-git-*.vercel.app`
- Redeploy backend

### Issue 3: LLM Features Not Working

**Cause:** Missing or invalid API key.

**Fix:**
- Verify `OPENAI_API_KEY` (or `GROQ_API_KEY` / `GEMINI_API_KEY`) is set
- Check API key is valid and has credits
- Check backend logs for LLM errors

### Issue 4: Database Connection Failed

**Cause:** Wrong `DATABASE_URL` or database not provisioned.

**Fix:**
- Use **Internal Database URL** from Render (starts with `postgresql://`)
- Ensure PostgreSQL service is running
- Check database credentials

### Issue 5: Build Fails on Render

**Cause:** Missing dependencies or wrong build command.

**Fix:**
- Ensure `Backend/requirements.txt` exists and is up-to-date
- Check Render build logs for specific package errors
- Verify Python version (Render uses Python 3.11 by default)

### Issue 6: Frontend Build Fails on Vercel

**Cause:** Missing environment variable or build error.

**Fix:**
- Ensure `REACT_APP_API_URL` is set
- Check Vercel build logs
- Verify `package.json` is in `dashboard/` folder
- Ensure Node.js version compatibility (≥18.0.0)

---

## 🔒 Security Best Practices

1. **Never commit API keys to Git**
   - Use environment variables only
   - Add `.env` to `.gitignore`

2. **Use Strong Secret Keys**
   - Generate with: `openssl rand -hex 32`
   - Store in Render environment variables

3. **Enable HTTPS Only**
   - Render and Vercel enforce HTTPS automatically

4. **Limit CORS Origins**
   - Only include your production frontend URLs
   - Remove localhost in production

5. **Database Security**
   - Use connection pooling
   - Never expose database URL publicly
   - Use Render's internal database URL

6. **API Rate Limiting** (Future Enhancement)
   - Implement rate limiting for public endpoints
   - Use Render's rate limiting features

---

## 📊 Monitoring & Logs

### Render Logs
- View in Render Dashboard → Your Service → Logs
- Real-time logs available
- Download logs for analysis

### Vercel Logs
- View in Vercel Dashboard → Your Project → Deployments → Logs
- Function logs available for serverless functions

### Health Monitoring
- Set up uptime monitoring (UptimeRobot, Pingdom)
- Monitor `/health` endpoint
- Alert on failures

---

## 🚀 Scaling Strategy

### Render (Backend)

1. **Upgrade Plan:**
   - Free tier: 512MB RAM, 0.1 CPU
   - Starter: $7/month - 512MB RAM
   - Standard: $25/month - 2GB RAM (recommended for production)

2. **Database Scaling:**
   - Free tier: 90 days retention
   - Paid: Automatic backups, longer retention

3. **Horizontal Scaling:**
   - Render supports multiple instances
   - Load balancing handled automatically

### Vercel (Frontend)

1. **Free Tier:**
   - 100GB bandwidth/month
   - Unlimited deployments
   - Automatic HTTPS

2. **Pro Tier ($20/month):**
   - Unlimited bandwidth
   - Team collaboration
   - Advanced analytics

---

## 📝 Environment Variables Summary

### Backend (Render)

```bash
DATABASE_URL=postgresql://...
CS_SECRET_KEY=...
CS_DEBUG=False
CS_CORS_ORIGINS=https://your-frontend.vercel.app
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

### Frontend (Vercel)

```bash
REACT_APP_API_URL=https://your-backend.onrender.com
```

---

## 🎯 Final Production Checklist

- [ ] Backend deployed on Render with PostgreSQL
- [ ] Frontend deployed on Vercel
- [ ] All environment variables configured
- [ ] CORS configured correctly
- [ ] Database initialized
- [ ] Admin user created (if needed)
- [ ] LLM API keys working
- [ ] Health endpoints responding
- [ ] WebSocket connections working
- [ ] SSL/HTTPS enabled (automatic)
- [ ] Monitoring setup
- [ ] Error logging configured
- [ ] Documentation updated

---

## 📞 Support

- **Render Support:** [render.com/docs](https://render.com/docs)
- **Vercel Support:** [vercel.com/docs](https://vercel.com/docs)
- **Project Issues:** GitHub Issues in your repository

---

**Last Updated:** January 2025

