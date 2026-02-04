# Render Deployment Guide

## Deploy to Render

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure as follows:

### Build Settings
- **Name**: `aai-risk-api` (or your choice)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: `Server`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Important Notes
- The `runtime.txt` file forces Python 3.11 (required for pandas compatibility)
- Port is set via `$PORT` environment variable (Render provides this)
- Free tier sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds

6. Click "Create Web Service"
7. Wait for deployment (3-5 minutes)
8. Copy your service URL (e.g., `https://aai-risk-api.onrender.com`)
9. Update `Client/.env.production`:
   ```
   VITE_API_BASE_URL=https://aai-risk-api.onrender.com
   ```

## Test Your Deployment

```bash
curl https://YOUR-SERVICE-URL.onrender.com/health
curl https://YOUR-SERVICE-URL.onrender.com/models
```

## Common Issues

### Build fails with pandas compilation error
- Ensure `runtime.txt` contains `3.11`
- Clear build cache in Render dashboard
- Redeploy

### Port binding error
- Make sure Start Command uses `$PORT`: `--port $PORT`

### CORS errors from frontend
- Backend CORS is configured for `*`, should work
- Check browser console for actual error
