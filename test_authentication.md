# Authentication Testing Guide

## Prerequisites

Before testing, ensure you have:
1. ✅ Google Cloud Console OAuth configured
2. ✅ `credentials/client_secret.json` file in place
3. ✅ Flask server running

## Test Phase 1: Basic Authentication Flow

### Test 1.1: Initial Access (Unauthenticated User)

**Steps:**
1. Clear browser cookies/cache or use incognito mode
2. Navigate to `http://localhost:5000`

**Expected Result:**
- ✅ Redirected to `/login` page
- ✅ See "AI Presentolog" login page
- ✅ See "Sign in with Google" button

**Status:** [ ] Pass [ ] Fail

---

### Test 1.2: Google OAuth Flow

**Steps:**
1. From login page, click "Sign in with Google" button
2. Select/enter Google account credentials
3. Grant requested permissions

**Expected Result:**
- ✅ Redirected to Google consent screen
- ✅ Permissions listed:
  - View and manage Google Slides presentations
  - View files in Google Drive
- ✅ After granting, redirected back to application
- ✅ Land on home page (`/`)

**Status:** [ ] Pass [ ] Fail

---

### Test 1.3: Session Persistence

**Steps:**
1. After successful login, note the user email in navigation bar
2. Reload the page (F5)
3. Navigate to different pages (/history)
4. Return to home page

**Expected Result:**
- ✅ User email remains visible in navigation bar
- ✅ No re-authentication required
- ✅ All pages load without redirect to login

**Status:** [ ] Pass [ ] Fail

---

### Test 1.4: User Email Display

**Steps:**
1. While logged in, check the navigation bar

**Expected Result:**
- ✅ Navigation bar shows: `👤 your.email@gmail.com`
- ✅ "Logout" button visible next to email

**Status:** [ ] Pass [ ] Fail

---

### Test 1.5: Presentation Processing with User Credentials

**Steps:**
1. On home page, enter a Google Slides URL
2. Click "📝 Открыть редактор"
3. Wait for extraction to complete

**Expected Result:**
- ✅ Extraction starts successfully
- ✅ No authentication errors
- ✅ Presentation extracted using YOUR Google account credentials
- ✅ Can access slides in editor

**Status:** [ ] Pass [ ] Fail

**Test Data:**
- Presentation URL used: ___________________________
- Extraction time: _______ seconds
- Number of slides extracted: _______

---

### Test 1.6: Logout Functionality

**Steps:**
1. Click "Logout" button in navigation bar
2. Observe result

**Expected Result:**
- ✅ Redirected to `/login` page
- ✅ Session cleared (no user email in navigation)
- ✅ Attempting to access `/` redirects to login

**Status:** [ ] Pass [ ] Fail

---

### Test 1.7: Re-login After Logout

**Steps:**
1. After logout, click "Sign in with Google" again
2. Select same Google account

**Expected Result:**
- ✅ Successfully re-authenticated
- ✅ Redirected to home page
- ✅ User email displayed again

**Status:** [ ] Pass [ ] Fail

---

## Test Phase 2: Token Refresh (Advanced)

### Test 2.1: Session Expiry Handling

**Note:** This test requires waiting or manually expiring the token.

**Steps:**
1. Log in successfully
2. Wait for access token to expire (typically 1 hour)
   - OR: Manually delete access token from session (developer tools)
3. Try to process a presentation

**Expected Result:**
- ✅ System automatically refreshes token
- ✅ No visible interruption to user
- ✅ Processing continues successfully
- OR (if refresh token expired):
- ✅ Redirected to login with clear message

**Status:** [ ] Pass [ ] Fail [ ] Skipped (requires long wait)

---

## Test Phase 3: Error Handling

### Test 3.1: OAuth Cancellation

**Steps:**
1. Logout
2. Click "Sign in with Google"
3. On Google consent screen, click "Cancel" or back button

**Expected Result:**
- ✅ Redirected to error page or login page
- ✅ Clear error message displayed
- ✅ Option to try again

**Status:** [ ] Pass [ ] Fail

---

### Test 3.2: Permission Denial

**Steps:**
1. Logout
2. Click "Sign in with Google"
3. On consent screen, try to deny permissions (if possible)

**Expected Result:**
- ✅ Error page shown
- ✅ Message: "Authentication failed"
- ✅ "Try Again" button available

**Status:** [ ] Pass [ ] Fail

---

### Test 3.3: Invalid Session Access

**Steps:**
1. Log in successfully
2. Open browser developer tools
3. Manually clear cookies
4. Try to access `/slide_editor?job_id=test`

**Expected Result:**
- ✅ Redirected to `/login`
- ✅ Original URL saved for post-login redirect
- ✅ After login, redirected back to intended page

**Status:** [ ] Pass [ ] Fail

---

## Test Results Summary

| Test | Status | Notes |
|------|--------|-------|
| 1.1 Initial Access | [ ] | |
| 1.2 OAuth Flow | [ ] | |
| 1.3 Session Persistence | [ ] | |
| 1.4 User Email Display | [ ] | |
| 1.5 Presentation Processing | [ ] | |
| 1.6 Logout | [ ] | |
| 1.7 Re-login | [ ] | |
| 2.1 Token Refresh | [ ] | |
| 3.1 OAuth Cancellation | [ ] | |
| 3.2 Permission Denial | [ ] | |
| 3.3 Invalid Session | [ ] | |

---

## Troubleshooting Common Issues

### Issue: Redirect URI Mismatch

**Symptom:** Error: "redirect_uri_mismatch"

**Solution:**
1. Check Google Cloud Console → OAuth 2.0 Client IDs
2. Ensure redirect URI exactly matches: `http://localhost:5000/auth/callback`
3. No trailing slashes, exact match required

---

### Issue: Credentials Not Found

**Symptom:** Error: "Client secrets file not found"

**Solution:**
1. Verify file exists: `credentials/client_secret.json`
2. Check file permissions (readable)
3. Verify JSON format is valid

---

### Issue: Session Expires Immediately

**Symptom:** Keep getting redirected to login after authenticating

**Solution:**
1. Check `SECRET_KEY` is set in environment or web_app.py
2. Ensure cookies are enabled in browser
3. Check for HTTPS/HTTP mismatch

---

### Issue: Database Errors

**Symptom:** Errors about missing tables or columns

**Solution:**
1. Delete database: `rm db/presentation_jobs.db`
2. Restart server (will recreate database with new schema)

---

## Sign-off

**Tester Name:** _________________________

**Test Date:** _________________________

**Overall Result:** [ ] All Pass [ ] Some Failed

**Notes:**
_________________________________________________________
_________________________________________________________
_________________________________________________________
