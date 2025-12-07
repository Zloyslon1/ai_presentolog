# AI Presentolog - Deployment Guide

## Quick Deploy to Render.com

### Prerequisites
1. GitHub account with this repository
2. Render.com account (free tier available)
3. Google Cloud Project with Slides API enabled

### Step 1: Prepare Google API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Slides API
3. Create OAuth 2.0 credentials
4. Download `client_secret.json`
5. **IMPORTANT**: Keep credentials secure, don't commit to git

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml` configuration
5. Click "Create Web Service"

### Step 3: Upload Credentials to Render

**Option A: Environment Files (Recommended)**
1. In Render dashboard, go to your service
2. Navigate to "Environment" tab
3. Click "Add Secret File"
4. Name: `credentials/client_secret.json`
5. Paste contents of your `client_secret.json`

**Option B: Manual Upload (if needed)**
1. Use Render Shell to upload files
2. Or include in build command (less secure)

### Step 4: Set Environment Variables

In Render dashboard under "Environment":
```
FLASK_ENV=production
SECRET_KEY=<generate-random-secret-key>
```

### Step 5: Verify Deployment

1. Wait for build to complete
2. Open your app URL: `https://ai-presentolog.onrender.com`
3. Test with a sample Google Slides URL
4. Check logs for errors

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
export FLASK_ENV=development

# Run server
python web_app.py
```

## Database

- SQLite database stored in `db/presentation_jobs.db`
- Automatic initialization on startup
- Persistent storage for jobs and slides

## Troubleshooting

**Build fails:**
- Check `requirements.txt` has all dependencies
- Verify Python version (3.11)

**Authentication errors:**
- Ensure `client_secret.json` is uploaded correctly
- Check Google Cloud credentials are valid

**Database errors:**
- Render persistent disk enabled?
- Check write permissions on `db/` folder

## Configuration Files

- `render.yaml` - Render deployment config
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template
- `.gitignore` - Files excluded from git

## Support

For issues, check:
1. Render build logs
2. Application logs in Render dashboard
3. GitHub repository issues
