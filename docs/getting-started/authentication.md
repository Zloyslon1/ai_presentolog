# Authentication Guide

Understanding and configuring authentication for AI Presentolog.

---

## Overview

AI Presentolog supports two authentication methods:

1. **Google OAuth 2.0** (Required) - For user authentication and accessing user's presentations
2. **Service Account** (Optional) - For server-side access to public/shared presentations

---

## Google OAuth 2.0 Authentication

### What is OAuth?

OAuth 2.0 is an industry-standard protocol that allows AI Presentolog to access your Google Slides and Drive on your behalf, without ever seeing your password.

### Why OAuth?

- **Secure** - Application never sees your Google password
- **Controlled** - You choose what permissions to grant
- **Revocable** - You can revoke access anytime
- **Multi-User** - Each user authenticates with their own Google account

### Authentication Flow

```
1. User clicks "Sign in with Google"
   ↓
2. Redirected to Google OAuth consent screen
   ↓
3. User reviews requested permissions
   ↓
4. User grants access
   ↓
5. Google redirects back to AI Presentolog with authorization code
   ↓
6. Application exchanges code for access token
   ↓
7. Access token stored in encrypted session
   ↓
8. User authenticated ✓
```

### Requested Permissions (Scopes)

AI Presentolog requests the following permissions:

- `https://www.googleapis.com/auth/presentations` - Full access to Google Slides
  - **Why:** To read presentation content and create new presentations
  
- `https://www.googleapis.com/auth/drive` - Full access to Google Drive
  - **Why:** To read shared presentations and save new ones

### OAuth Setup

Detailed instructions: [SETUP_OAUTH_GUIDE.md](SETUP_OAUTH_GUIDE.md)

**Quick Summary:**

1. Create Google Cloud project
2. Enable Google Slides API and Google Drive API
3. Configure OAuth consent screen
4. Create OAuth credentials (Desktop app type)
5. Download `client_secret.json`
6. Place in `credentials/` directory

### First-Time Authorization

When you first sign in:

1. Click **"Sign in with Google"**
2. Select your Google account
3. Review requested permissions
4. Click **"Allow"**
5. You'll be redirected back to AI Presentolog

**Note:** You may see a warning "This app isn't verified" if your app is in testing mode. Click "Advanced" → "Go to AI Presentolog (unsafe)" to proceed.

### Token Management

**Access Tokens:**
- Short-lived (typically 1 hour)
- Used for API calls to Google
- Automatically refreshed by application

**Refresh Tokens:**
- Long-lived (until revoked)
- Used to get new access tokens
- Stored encrypted in session database

**Token Storage:**
- Tokens stored in Flask session (encrypted)
- Session data persisted to SQLite database
- Each user has isolated session

### Session Lifetime

- **Default:** 24 hours
- **Inactivity timeout:** No automatic timeout (configurable)
- **Manual logout:** Clears session immediately

### Revoking Access

To revoke AI Presentolog's access to your Google account:

1. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
2. Find "AI Presentolog"
3. Click **"Remove Access"**

Next time you sign in, you'll need to authorize again.

---

## Service Account Authentication (Optional)

### What is a Service Account?

A Service Account is a special Google account used for server-to-server authentication, not tied to a specific user.

### When to Use Service Account?

Use Service Account when:
- You want server-side access to public presentations
- You don't want to require user OAuth for every request
- You're accessing presentations shared with the service account

**Note:** Service Account can only access:
- Public presentations (shared with "Anyone with link")
- Presentations explicitly shared with the service account email

### Service Account vs OAuth

| Feature | OAuth 2.0 | Service Account |
|---------|-----------|-----------------|
| User authentication | ✓ Yes | ✗ No |
| Access user's presentations | ✓ Yes | ✗ No |
| Access public presentations | ✓ Yes | ✓ Yes |
| Server-side access | ✗ No | ✓ Yes |
| Multi-user support | ✓ Yes | ✗ No |
| Requires user login | ✓ Yes | ✗ No |

### Service Account Setup

Detailed instructions: [SETUP_SERVICE_ACCOUNT.md](SETUP_SERVICE_ACCOUNT.md)

**Quick Summary:**

1. In Google Cloud Console, go to IAM & Admin → Service Accounts
2. Create service account
3. Create key (JSON format)
4. Download `service_account.json`
5. Place in `credentials/` directory
6. Enable Google Slides API and Drive API for the project

### Using Service Account

When Service Account is configured:

1. Application tries OAuth first (if user is signed in)
2. Falls back to Service Account if OAuth fails
3. Service Account can access public/shared presentations

**Sharing presentations with Service Account:**

1. Open the presentation in Google Slides
2. Click **"Share"**
3. Add the service account email (found in `service_account.json`)
4. Grant **"Viewer"** permission
5. Click **"Send"**

---

## Security Best Practices

### OAuth Security

**Do:**
- ✓ Keep `client_secret.json` secure (never commit to git)
- ✓ Use HTTPS in production
- ✓ Set strong `SECRET_KEY` for session encryption
- ✓ Review granted permissions periodically
- ✓ Revoke access when no longer needed

**Don't:**
- ✗ Share `client_secret.json` publicly
- ✗ Use `OAUTHLIB_INSECURE_TRANSPORT=1` in production
- ✗ Store tokens in plaintext
- ✗ Grant more permissions than needed

### Service Account Security

**Do:**
- ✓ Keep `service_account.json` secure (never commit to git)
- ✓ Limit service account permissions
- ✓ Rotate keys periodically
- ✓ Monitor service account usage

**Don't:**
- ✗ Share service account key publicly
- ✗ Grant unnecessary API permissions
- ✗ Use service account for user-specific data

### Session Security

**Implemented:**
- ✓ Session encryption with SECRET_KEY
- ✓ CSRF protection (OAuth state parameter)
- ✓ Per-user session isolation
- ✓ Secure token storage in database

**Production Recommendations:**
- Set strong, random `SECRET_KEY`
- Use HTTPS only (disable OAUTHLIB_INSECURE_TRANSPORT)
- Implement session timeout
- Add rate limiting
- Enable audit logging

---

## Troubleshooting Authentication

### OAuth Errors

**Error: redirect_uri_mismatch**

**Cause:** OAuth redirect URI doesn't match Google Cloud Console configuration

**Solution:**
- For Desktop app: This warning is normal, click through
- For Web app: Add `http://localhost:5000/auth/callback` to authorized redirect URIs

**Error: access_denied**

**Cause:** User denied permission or consent screen not configured

**Solution:**
- Click "Allow" when authorizing
- Verify OAuth consent screen is configured
- Check app is in "Testing" or "Production" mode
- Verify user is added as test user (if in testing mode)

**Error: invalid_client**

**Cause:** `client_secret.json` is invalid or not found

**Solution:**
- Verify file exists: `credentials/client_secret.json`
- Check file is valid JSON
- Re-download from Google Cloud Console
- Ensure OAuth client is for "Desktop app" type

**Error: Token has been expired or revoked**

**Cause:** Access token expired and refresh failed

**Solution:**
- Sign out and sign in again
- Check internet connection
- Verify OAuth client is still active in Google Cloud Console
- Delete session and re-authorize

### Service Account Errors

**Error: Permission denied (403)**

**Cause:** Service account doesn't have access to presentation

**Solution:**
- Make presentation public ("Anyone with link" can view)
- Or share presentation with service account email
- Verify APIs are enabled for the project

**Error: Service account file not found**

**Cause:** `service_account.json` not in credentials directory

**Solution:**
- Download key from Google Cloud Console
- Place in `credentials/service_account.json`
- Verify filename is exact

### Session Issues

**Problem: Keep getting logged out**

**Possible causes:**
- Session timeout configured too short
- Browser blocking cookies
- SECRET_KEY not set or changing

**Solution:**
- Set `SECRET_KEY` environment variable
- Enable cookies in browser
- Check browser privacy settings
- Verify database permissions

**Problem: Can't access other users' jobs**

**This is expected behavior!** 

Each user has isolated sessions. Jobs are linked to the user who created them.

---

## Multi-User Support

AI Presentolog fully supports multiple concurrent users:

### How It Works

1. Each user signs in with their own Google account
2. User session stored in database with unique session_id
3. All jobs/presentations linked to session_id
4. Complete isolation between users

### Session Database

**Table: user_sessions**
- `session_id` - Unique session identifier
- `user_email` - User's Google email
- `credentials_json` - Encrypted OAuth tokens
- `created_at` - Session creation timestamp
- `last_used_at` - Last activity timestamp
- `expires_at` - Session expiration time

**Table: jobs**
- `session_id` - Links job to user session
- Other job metadata

### Testing Multi-User

To test with multiple users:

1. Open application in different browsers (Chrome, Firefox, etc.)
2. Sign in with different Google accounts in each
3. Each user will see only their own jobs
4. Sessions are completely isolated

---

## Environment Variables

### Development

```bash
# Windows (PowerShell)
$env:SECRET_KEY = "dev-secret-key-change-in-production"
$env:OAUTHLIB_INSECURE_TRANSPORT = "1"

# macOS/Linux
export SECRET_KEY="dev-secret-key-change-in-production"
export OAUTHLIB_INSECURE_TRANSPORT=1
```

### Production

```bash
# Generate strong random key
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# Set in production
export SECRET_KEY="<generated-key-here>"
# Remove OAUTHLIB_INSECURE_TRANSPORT completely
```

---

## Testing Authentication

### Test OAuth Flow

1. Start application: `python web_app.py`
2. Open: http://localhost:5000
3. Click "Sign in with Google"
4. Authorize application
5. Verify redirect back to main page
6. Check user email displayed in navigation

### Test Session Persistence

1. Sign in
2. Close browser
3. Reopen browser
4. Visit http://localhost:5000
5. Should still be signed in (if session not expired)

### Test Logout

1. Sign in
2. Click "Logout"
3. Verify redirected to login page
4. Try accessing protected page
5. Should redirect to login

---

## Additional Resources

- **[OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)**
- **[Google Slides API](https://developers.google.com/slides/api)**
- **[Google Drive API](https://developers.google.com/drive/api)**
- **[Service Accounts](https://cloud.google.com/iam/docs/service-accounts)**

---

**Last Updated:** December 17, 2024
