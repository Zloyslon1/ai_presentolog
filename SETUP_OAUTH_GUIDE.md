# Google OAuth Setup Guide

## Step-by-Step Instructions for Configuring Google Cloud Console

This guide will help you set up Google OAuth for the AI Presentolog application.

---

## Prerequisites

- Google account (any Gmail account)
- 10-15 minutes of time
- Access to https://console.cloud.google.com

---

## Part 1: Create a Google Cloud Project

### Step 1: Go to Google Cloud Console

1. Open your browser
2. Navigate to: https://console.cloud.google.com
3. Sign in with your Google account

### Step 2: Create New Project

1. Click the project dropdown at the top of the page
   - Look for: "Select a project" or current project name
2. Click "**NEW PROJECT**" button
3. Fill in project details:
   - **Project name**: `AI Presentolog`
   - **Organization**: Leave as-is (No organization)
   - **Location**: Leave as-is
4. Click "**CREATE**"
5. Wait for project creation (takes ~30 seconds)
6. Select your new project from the dropdown

---

## Part 2: Enable Required APIs

### Step 3: Enable Google Slides API

1. In the left sidebar, go to: **APIs & Services** > **Library**
2. In the search box, type: `Google Slides API`
3. Click on "**Google Slides API**"
4. Click "**ENABLE**" button
5. Wait for activation (~10 seconds)

### Step 4: Enable Google Drive API

1. Click "**< Go back to Library**" (or navigate back to Library)
2. In the search box, type: `Google Drive API`
3. Click on "**Google Drive API**"
4. Click "**ENABLE**" button
5. Wait for activation

---

## Part 3: Configure OAuth Consent Screen

### Step 5: Set Up Consent Screen

1. In left sidebar, go to: **APIs & Services** > **OAuth consent screen**
2. Choose user type:
   - **External** (if you're an individual user)
   - **Internal** (if you're part of a Google Workspace organization)
3. Click "**CREATE**"

### Step 6: Fill OAuth Consent Screen Information

**App information:**
- **App name**: `AI Presentolog`
- **User support email**: Your email address (select from dropdown)
- **App logo**: (Optional - skip for now)

**App domain:**
- **Application home page**: `http://localhost:5000` (for development)
- **Application privacy policy**: (Optional - skip for now)
- **Application terms of service**: (Optional - skip for now)

**Authorized domains:**
- Leave empty for local development
- For production, add your domain (e.g., `yourdomain.com`)

**Developer contact information:**
- **Email addresses**: Your email address

4. Click "**SAVE AND CONTINUE**"

### Step 7: Configure Scopes

1. Click "**ADD OR REMOVE SCOPES**"
2. In the filter box, search for: `presentations`
3. Select these scopes:
   - ✅ `https://www.googleapis.com/auth/presentations`
   - ✅ `https://www.googleapis.com/auth/presentations.readonly`
4. In the filter box, search for: `drive`
5. Select this scope:
   - ✅ `https://www.googleapis.com/auth/drive.readonly`
6. Click "**UPDATE**"
7. Scroll down and click "**SAVE AND CONTINUE**"

### Step 8: Add Test Users (For External Type Only)

If you selected "External" user type:

1. Click "**+ ADD USERS**"
2. Enter your email address (and any other testers)
3. Click "**ADD**"
4. Click "**SAVE AND CONTINUE**"

### Step 9: Review and Finish

1. Review your consent screen configuration
2. Click "**BACK TO DASHBOARD**"

---

## Part 4: Create OAuth Credentials

### Step 10: Create OAuth Client ID

1. In left sidebar, go to: **APIs & Services** > **Credentials**
2. Click "**+ CREATE CREDENTIALS**" at the top
3. Select "**OAuth client ID**"

### Step 11: Configure OAuth Client

1. **Application type**: Select "**Desktop app**"
   - Note: We use "Desktop app" for local development
   - For production web app, use "Web application"

2. **Name**: `AI Presentolog Desktop Client`

3. Click "**CREATE**"

### Step 12: Download Credentials

1. A popup appears: "OAuth client created"
2. Click "**DOWNLOAD JSON**" button
3. Save the file to your Downloads folder
   - Filename will be something like: `client_secret_123456789.apps.googleusercontent.com.json`

4. **IMPORTANT**: Click "OK" to close the popup

---

## Part 5: Install Credentials in Your Application

### Step 13: Rename and Move Credentials File

**On Windows:**
```powershell
# Open PowerShell in project directory
cd C:\Users\Zloyslon\Desktop\Projects\ai_presentolog

# Create credentials directory if it doesn't exist
New-Item -ItemType Directory -Force -Path credentials

# Move and rename the file (adjust the source path to match your download)
Move-Item "$env:USERPROFILE\Downloads\client_secret_*.json" "credentials\client_secret.json"
```

**On macOS/Linux:**
```bash
# Navigate to project directory
cd ~/Desktop/Projects/ai_presentolog

# Create credentials directory
mkdir -p credentials

# Move and rename the file
mv ~/Downloads/client_secret_*.json credentials/client_secret.json
```

### Step 14: Verify File Placement

Check that the file exists:

**Windows:**
```powershell
Test-Path "credentials\client_secret.json"
# Should output: True
```

**macOS/Linux:**
```bash
ls -la credentials/client_secret.json
# Should show the file
```

---

## Part 6: Update Redirect URIs (For Production)

**Note:** This step is only needed for production deployment. Skip for local development.

### For Web Application (Production)

1. Go back to **APIs & Services** > **Credentials**
2. Click "**+ CREATE CREDENTIALS**" again
3. Select "**OAuth client ID**"
4. Choose "**Web application**"
5. **Name**: `AI Presentolog Web Client`
6. **Authorized redirect URIs**: Click "**+ ADD URI**"
   - Add: `https://yourdomain.com/auth/callback`
   - Replace `yourdomain.com` with your actual domain
7. Click "**CREATE**"
8. Download this JSON as well and save as `client_secret_web.json`

---

## Part 7: Verify Configuration

### Step 15: Check Client Secret Contents

Open `credentials/client_secret.json` and verify it looks like this:

```json
{
  "installed": {
    "client_id": "123456789-abcdefg.apps.googleusercontent.com",
    "project_id": "ai-presentolog-12345",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-AbCdEfGhIjKlMnOpQrStUvWx",
    "redirect_uris": ["http://localhost"]
  }
}
```

**Important fields:**
- ✅ `client_id` should end with `.apps.googleusercontent.com`
- ✅ `client_secret` should start with `GOCSPX-`
- ✅ File should be valid JSON

### Step 16: Test the Application

1. Start the Flask application:
   ```bash
   python web_app.py
   ```

2. Open browser: `http://localhost:5000`

3. You should be redirected to `/login`

4. Click "Sign in with Google"

5. **Expected flow:**
   - Redirected to Google sign-in
   - Select your Google account
   - See consent screen: "AI Presentolog wants to access your Google Account"
   - See requested permissions:
     - ✅ View and manage your Google Slides presentations
     - ✅ See, edit, create, and delete only the specific Google Drive files you use with this app
   - Click "Allow"
   - Redirected back to application home page
   - See your email in navigation bar

6. **Success!** ✅ OAuth is configured correctly

---

## Troubleshooting

### Issue 1: "redirect_uri_mismatch" Error

**Symptom:**
```
Error 400: redirect_uri_mismatch
The redirect URI in the request, http://localhost:5000/auth/callback, does not match...
```

**Solution:**
1. For Desktop app type, this is normal - the redirect happens internally
2. If using Web application type, add `http://localhost:5000/auth/callback` to Authorized redirect URIs
3. Make sure there are NO trailing slashes

### Issue 2: "Access Denied" or "Unauthorized" Error

**Symptom:**
```
Error: Access denied. Please ensure you've granted the required permissions.
```

**Solution:**
1. Go to https://myaccount.google.com/permissions
2. Find "AI Presentolog"
3. Click "Remove access"
4. Try signing in again and grant all permissions

### Issue 3: File Not Found Error

**Symptom:**
```
Client secrets file not found: credentials/client_secret.json
```

**Solution:**
1. Check file exists: `ls credentials/client_secret.json`
2. Check file permissions: Should be readable
3. Verify path is correct relative to web_app.py

### Issue 4: Invalid Client Error

**Symptom:**
```
Error: invalid_client
The OAuth client was not found.
```

**Solution:**
1. Re-download credentials from Google Cloud Console
2. Make sure you copied the entire JSON file
3. Verify JSON is valid (no syntax errors)

### Issue 5: Consent Screen Not Configured

**Symptom:**
```
Error: invalid_request
The OAuth consent screen is not configured correctly.
```

**Solution:**
1. Go to **OAuth consent screen** in Google Cloud Console
2. Complete all required fields
3. Add test users (for External type)
4. Publish app (or keep in testing mode)

---

## Security Notes

### For Development
- ✅ Client secret file is gitignored
- ✅ Never commit `client_secret.json` to version control
- ✅ `OAUTHLIB_INSECURE_TRANSPORT=1` allows HTTP (local only!)

### For Production
- ⚠️ Remove `OAUTHLIB_INSECURE_TRANSPORT=1` environment variable
- ⚠️ Use HTTPS only
- ⚠️ Create separate OAuth client for web application
- ⚠️ Rotate client secret regularly
- ⚠️ Monitor OAuth consent screen for abuse
- ⚠️ Implement rate limiting on auth endpoints

---

## Next Steps

After OAuth is configured:

1. ✅ Test authentication flow (see `test_authentication.md`)
2. ✅ Test multi-user scenarios (see `test_multiuser.md`)
3. ✅ Configure SECRET_KEY for session encryption
4. ✅ Set up production environment with HTTPS
5. ✅ Implement additional security measures

---

## Quick Reference

**Google Cloud Console:** https://console.cloud.google.com

**Project Name:** AI Presentolog

**Required APIs:**
- Google Slides API
- Google Drive API

**OAuth Scopes:**
- `https://www.googleapis.com/auth/presentations`
- `https://www.googleapis.com/auth/presentations.readonly`
- `https://www.googleapis.com/auth/drive.readonly`

**Credentials File:** `credentials/client_secret.json`

**Redirect URI (development):** `http://localhost:5000/auth/callback`

---

## Support Resources

**Google OAuth Documentation:**
- https://developers.google.com/identity/protocols/oauth2
- https://developers.google.com/workspace/guides/create-credentials

**Slides API Documentation:**
- https://developers.google.com/slides/api/guides/overview

**Common OAuth Errors:**
- https://developers.google.com/identity/protocols/oauth2/web-server#errors

---

**Setup Date:** _________________________

**Configured By:** _________________________

**Status:** [ ] Complete [ ] In Progress [ ] Need Help
