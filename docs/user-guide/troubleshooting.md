# Troubleshooting Guide

Common issues and solutions for AI Presentolog.

---

## Installation Issues

### Python Not Found

**Error:** `python: command not found` or `'python' is not recognized`

**Solution:**
```bash
# Try python3
python3 --version

# Or install Python from python.org
# Windows: Make sure "Add Python to PATH" is checked
```

### Dependencies Won't Install

**Error:** Various package installation errors

**Solutions:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt

# If still fails, try one package at a time
pip install flask
pip install google-auth
# etc.
```

### Permission Errors

**Error:** `Permission denied` during installation

**Solutions:**
```bash
# Use user install (recommended)
pip install --user -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## Authentication Issues

### OAuth redirect_uri_mismatch

**Error:** `Error 400: redirect_uri_mismatch`

**For Desktop App (Development):**
- This is normal! Click "Advanced" → "Go to AI Presentolog"
- OAuth Desktop apps use local redirect URI

**For Web App (Production):**
1. Go to Google Cloud Console
2. APIs & Services → Credentials
3. Edit your OAuth client
4. Add authorized redirect URI: `https://yourdomain.com/auth/callback`

### Client Secrets Not Found

**Error:** `Client secrets file not found: credentials/client_secret.json`

**Solution:**
1. Check file exists:
   ```bash
   ls credentials/client_secret.json  # macOS/Linux
   dir credentials\client_secret.json  # Windows
   ```

2. If missing:
   - Download from Google Cloud Console
   - Save as `client_secret.json`
   - Place in `credentials/` directory

3. Verify file content:
   - Open in text editor
   - Should be valid JSON
   - Should contain `client_id`, `client_secret`

### Access Denied

**Error:** User clicked "Deny" or permissions not granted

**Solution:**
1. Try signing in again
2. Click "Allow" when prompted
3. If app shows as "unsafe":
   - Click "Advanced"
   - Click "Go to AI Presentolog (unsafe)"
   - This is safe for your own app

4. If still denied:
   - Go to https://myaccount.google.com/permissions
   - Remove "AI Presentolog"
   - Try authorizing again

### Token Expired

**Error:** `Token has been expired or revoked`

**Solution:**
```bash
# Simple: Sign out and sign in again
# Or delete session from database

# Check session in database
python tests/debug/check_db.py
```

---

## Extraction Issues

### Permission Denied (403)

**Error:** Can't access presentation

**Causes & Solutions:**

**1. Private presentation:**
- Share presentation with your Google account
- OR make it public ("Anyone with link")

**2. Wrong account:**
- Sign in with account that owns presentation
- Check email shown in navigation bar

**3. Service Account (if configured):**
- Share presentation with service account email
- OR make presentation public

### Invalid URL

**Error:** `Invalid Google Slides URL format`

**Solution:**
- Use full URL: `https://docs.google.com/presentation/d/[ID]/edit`
- Not shortened URLs
- Not view-only links

**Valid formats:**
```
https://docs.google.com/presentation/d/1ABC...XYZ/edit
https://docs.google.com/presentation/d/1ABC...XYZ/edit#slide=id.p
```

### Presentation Not Found (404)

**Error:** Presentation doesn't exist

**Solution:**
- Verify URL is correct
- Check presentation wasn't deleted
- Ensure you have access to view it
- Try opening URL in browser first

### Network Timeout

**Error:** Request timed out

**Causes:**
- Large presentation
- Slow internet connection
- Google API rate limit

**Solutions:**
- Wait and try again
- Check internet connection
- For large presentations, try smaller batches
- Check Google API quotas in Cloud Console

---

## Editor Issues

### Editor Won't Load

**Problem:** Blank page or error after extraction

**Solutions:**
1. Check browser console (F12)
2. Verify JavaScript is enabled
3. Try different browser
4. Clear browser cache

### Can't Edit Text

**Problem:** Text fields not editable

**Solutions:**
- Click directly in text area
- Check browser compatibility
- Try refreshing page
- Verify JavaScript enabled

### Images Not Uploading

**Problem:** Image upload fails

**Causes & Solutions:**

**1. File too large:**
- Resize image before uploading
- Maximum recommended: 5MB

**2. Unsupported format:**
- Use JPEG, PNG, or GIF
- Convert other formats first

**3. Network error:**
- Check internet connection
- Try again

### Changes Not Saving

**Problem:** Edits disappear or don't persist

**Solutions:**
1. Don't close tab during editing
2. Check session hasn't expired
3. Verify database is writable
4. Check browser local storage

---

## Generation Issues

### Presentation Generation Fails

**Error:** Can't create new presentation

**Causes & Solutions:**

**1. API quota exceeded:**
- Wait for quota reset (usually next day)
- Check quotas in Google Cloud Console
- Request quota increase if needed

**2. Permission error:**
- Re-authorize application
- Check token isn't expired
- Sign out and sign in again

**3. Template error:**
- Try different template
- Check template file is valid
- Review logs for specific error

### Generated Presentation Empty

**Problem:** New presentation created but has no content

**Possible causes:**
- Slides were empty in editor
- Template application failed
- API error during creation

**Solutions:**
1. Check original slides had content
2. Review application logs
3. Try simpler template (default)
4. Regenerate presentation

---

## Session Issues

### Keep Getting Logged Out

**Problem:** Session expires too quickly

**Solutions:**
1. Set SECRET_KEY environment variable:
   ```bash
   export SECRET_KEY="your-random-secret-key"
   ```

2. Enable cookies in browser

3. Check session timeout config

4. Verify database permissions

### Can't See Previous Jobs

**Problem:** Job history is empty

**Causes:**
- Signed in with different account
- Session expired and cleared
- Database issue

**Solutions:**
1. Sign in with same Google account used before
2. Check database file exists:
   ```bash
   ls db/presentation_jobs.db
   ```

3. Verify database integrity:
   ```bash
   python tests/debug/check_db.py
   ```

### Jobs Belong to Another User

**This is expected!** Jobs are isolated by user session. You can only see jobs you created.

---

## Database Issues

### Database File Not Found

**Error:** Can't find or create database

**Solution:**
```bash
# Create db directory
mkdir db

# Run application (will create database)
python web_app.py
```

### Database Locked

**Error:** `database is locked`

**Causes:**
- Another process using database
- Previous process didn't close properly

**Solutions:**
```bash
# Find processes using database
# Windows
handle db\presentation_jobs.db

# macOS/Linux
lsof | grep presentation_jobs.db

# Kill the process or restart application
```

### Corrupt Database

**Error:** Database errors or invalid data

**Solution:**
```bash
# Backup current database
cp db/presentation_jobs.db db/presentation_jobs.db.backup

# Delete and recreate
rm db/presentation_jobs.db
python web_app.py
# Database will be recreated
```

**Note:** This deletes all jobs and sessions!

---

## Performance Issues

### Slow Application

**Causes & Solutions:**

**1. Large database:**
```bash
# Clean up old jobs
python tests/debug/check_db.py --cleanup --days 30
```

**2. Many concurrent users:**
- Consider production WSGI server (Gunicorn)
- Scale horizontally
- Optimize database queries

**3. Network latency:**
- Check internet speed
- Try at different time
- Consider caching

### High Memory Usage

**Causes:**
- Processing large presentations
- Many images
- Memory leak (rare)

**Solutions:**
- Restart application periodically
- Process presentations in batches
- Monitor with system tools
- Report persistent issues

---

## Browser-Specific Issues

### Chrome

**Issue:** Session cookies blocked

**Solution:** Check Settings → Privacy → Cookies → Allow all cookies (for localhost)

### Firefox

**Issue:** OAuth popup blocked

**Solution:** Allow popups for localhost in browser settings

### Safari

**Issue:** Intelligent Tracking Prevention blocks OAuth

**Solution:** Disable ITP for localhost or use different browser for development

---

## Production Issues

### HTTPS Required

**Error:** OAuth only works with HTTPS

**Solution:**
1. Configure SSL certificate
2. Use reverse proxy (nginx, Apache)
3. Remove `OAUTHLIB_INSECURE_TRANSPORT` variable
4. See [Production Guide](../deployment/production.md)

### Port Already in Use

**Error:** `Address already in use: Port 5000`

**Solutions:**
```bash
# Find process using port
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9

# Or use different port
python web_app.py --port 8080
```

---

## Logs and Debugging

### View Application Logs

```bash
# Tail logs in real-time
# Windows
Get-Content logs\app.log -Wait -Tail 50

# macOS/Linux
tail -f logs/app.log
```

### Enable Debug Mode

```bash
export FLASK_DEBUG=1
python web_app.py
```

**Features:**
- Detailed error messages
- Stack traces
- Interactive debugger
- Auto-reload

**Warning:** Never use debug mode in production!

### Check Database

```bash
python tests/debug/check_db.py
```

Shows:
- Number of sessions
- Number of jobs
- Recent activity
- Database size

---

## Getting Help

If issues persist:

1. **Check Documentation:**
   - [Installation Guide](../getting-started/installation.md)
   - [Authentication Guide](../getting-started/authentication.md)
   - [Web Interface Guide](web-interface.md)

2. **Review Logs:**
   - Application logs in `logs/`
   - Browser console (F12)
   - System logs

3. **Test Systematically:**
   - Isolate the problem
   - Try minimal example
   - Document steps to reproduce

4. **External Resources:**
   - [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
   - [Google Slides API](https://developers.google.com/slides/api)
   - [Flask Documentation](https://flask.palletsprojects.com/)

---

## Common Error Messages

### "NoneType object has no attribute"

**Cause:** Missing or invalid data

**Solution:** Check that all required fields are filled and valid

### "ConnectionError"

**Cause:** No internet connection

**Solution:** Check network connection and try again

### "JSONDecodeError"

**Cause:** Invalid JSON in configuration or response

**Solution:** Verify JSON files are valid (use JSON validator)

### "ImportError: No module named"

**Cause:** Missing Python package

**Solution:**
```bash
pip install <missing-package>
# Or reinstall all
pip install -r requirements.txt
```

---

**Last Updated:** December 17, 2024
# Troubleshooting Guide

Common issues and solutions for AI Presentolog.

---

## Installation Issues

### Python Not Found

**Error:** `python: command not found` or `'python' is not recognized`

**Solution:**
```bash
# Try python3
python3 --version

# Or install Python from python.org
# Windows: Make sure "Add Python to PATH" is checked
```

### Dependencies Won't Install

**Error:** Various package installation errors

**Solutions:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt

# If still fails, try one package at a time
pip install flask
pip install google-auth
# etc.
```

### Permission Errors

**Error:** `Permission denied` during installation

**Solutions:**
```bash
# Use user install (recommended)
pip install --user -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## Authentication Issues

### OAuth redirect_uri_mismatch

**Error:** `Error 400: redirect_uri_mismatch`

**For Desktop App (Development):**
- This is normal! Click "Advanced" → "Go to AI Presentolog"
- OAuth Desktop apps use local redirect URI

**For Web App (Production):**
1. Go to Google Cloud Console
2. APIs & Services → Credentials
3. Edit your OAuth client
4. Add authorized redirect URI: `https://yourdomain.com/auth/callback`

### Client Secrets Not Found

**Error:** `Client secrets file not found: credentials/client_secret.json`

**Solution:**
1. Check file exists:
   ```bash
   ls credentials/client_secret.json  # macOS/Linux
   dir credentials\client_secret.json  # Windows
   ```

2. If missing:
   - Download from Google Cloud Console
   - Save as `client_secret.json`
   - Place in `credentials/` directory

3. Verify file content:
   - Open in text editor
   - Should be valid JSON
   - Should contain `client_id`, `client_secret`

### Access Denied

**Error:** User clicked "Deny" or permissions not granted

**Solution:**
1. Try signing in again
2. Click "Allow" when prompted
3. If app shows as "unsafe":
   - Click "Advanced"
   - Click "Go to AI Presentolog (unsafe)"
   - This is safe for your own app

4. If still denied:
   - Go to https://myaccount.google.com/permissions
   - Remove "AI Presentolog"
   - Try authorizing again

### Token Expired

**Error:** `Token has been expired or revoked`

**Solution:**
```bash
# Simple: Sign out and sign in again
# Or delete session from database

# Check session in database
python tests/debug/check_db.py
```

---

## Extraction Issues

### Permission Denied (403)

**Error:** Can't access presentation

**Causes & Solutions:**

**1. Private presentation:**
- Share presentation with your Google account
- OR make it public ("Anyone with link")

**2. Wrong account:**
- Sign in with account that owns presentation
- Check email shown in navigation bar

**3. Service Account (if configured):**
- Share presentation with service account email
- OR make presentation public

### Invalid URL

**Error:** `Invalid Google Slides URL format`

**Solution:**
- Use full URL: `https://docs.google.com/presentation/d/[ID]/edit`
- Not shortened URLs
- Not view-only links

**Valid formats:**
```
https://docs.google.com/presentation/d/1ABC...XYZ/edit
https://docs.google.com/presentation/d/1ABC...XYZ/edit#slide=id.p
```

### Presentation Not Found (404)

**Error:** Presentation doesn't exist

**Solution:**
- Verify URL is correct
- Check presentation wasn't deleted
- Ensure you have access to view it
- Try opening URL in browser first

### Network Timeout

**Error:** Request timed out

**Causes:**
- Large presentation
- Slow internet connection
- Google API rate limit

**Solutions:**
- Wait and try again
- Check internet connection
- For large presentations, try smaller batches
- Check Google API quotas in Cloud Console

---

## Editor Issues

### Editor Won't Load

**Problem:** Blank page or error after extraction

**Solutions:**
1. Check browser console (F12)
2. Verify JavaScript is enabled
3. Try different browser
4. Clear browser cache

### Can't Edit Text

**Problem:** Text fields not editable

**Solutions:**
- Click directly in text area
- Check browser compatibility
- Try refreshing page
- Verify JavaScript enabled

### Images Not Uploading

**Problem:** Image upload fails

**Causes & Solutions:**

**1. File too large:**
- Resize image before uploading
- Maximum recommended: 5MB

**2. Unsupported format:**
- Use JPEG, PNG, or GIF
- Convert other formats first

**3. Network error:**
- Check internet connection
- Try again

### Changes Not Saving

**Problem:** Edits disappear or don't persist

**Solutions:**
1. Don't close tab during editing
2. Check session hasn't expired
3. Verify database is writable
4. Check browser local storage

---

## Generation Issues

### Presentation Generation Fails

**Error:** Can't create new presentation

**Causes & Solutions:**

**1. API quota exceeded:**
- Wait for quota reset (usually next day)
- Check quotas in Google Cloud Console
- Request quota increase if needed

**2. Permission error:**
- Re-authorize application
- Check token isn't expired
- Sign out and sign in again

**3. Template error:**
- Try different template
- Check template file is valid
- Review logs for specific error

### Generated Presentation Empty

**Problem:** New presentation created but has no content

**Possible causes:**
- Slides were empty in editor
- Template application failed
- API error during creation

**Solutions:**
1. Check original slides had content
2. Review application logs
3. Try simpler template (default)
4. Regenerate presentation

---

## Session Issues

### Keep Getting Logged Out

**Problem:** Session expires too quickly

**Solutions:**
1. Set SECRET_KEY environment variable:
   ```bash
   export SECRET_KEY="your-random-secret-key"
   ```

2. Enable cookies in browser

3. Check session timeout config

4. Verify database permissions

### Can't See Previous Jobs

**Problem:** Job history is empty

**Causes:**
- Signed in with different account
- Session expired and cleared
- Database issue

**Solutions:**
1. Sign in with same Google account used before
2. Check database file exists:
   ```bash
   ls db/presentation_jobs.db
   ```

3. Verify database integrity:
   ```bash
   python tests/debug/check_db.py
   ```

### Jobs Belong to Another User

**This is expected!** Jobs are isolated by user session. You can only see jobs you created.

---

## Database Issues

### Database File Not Found

**Error:** Can't find or create database

**Solution:**
```bash
# Create db directory
mkdir db

# Run application (will create database)
python web_app.py
```

### Database Locked

**Error:** `database is locked`

**Causes:**
- Another process using database
- Previous process didn't close properly

**Solutions:**
```bash
# Find processes using database
# Windows
handle db\presentation_jobs.db

# macOS/Linux
lsof | grep presentation_jobs.db

# Kill the process or restart application
```

### Corrupt Database

**Error:** Database errors or invalid data

**Solution:**
```bash
# Backup current database
cp db/presentation_jobs.db db/presentation_jobs.db.backup

# Delete and recreate
rm db/presentation_jobs.db
python web_app.py
# Database will be recreated
```

**Note:** This deletes all jobs and sessions!

---

## Performance Issues

### Slow Application

**Causes & Solutions:**

**1. Large database:**
```bash
# Clean up old jobs
python tests/debug/check_db.py --cleanup --days 30
```

**2. Many concurrent users:**
- Consider production WSGI server (Gunicorn)
- Scale horizontally
- Optimize database queries

**3. Network latency:**
- Check internet speed
- Try at different time
- Consider caching

### High Memory Usage

**Causes:**
- Processing large presentations
- Many images
- Memory leak (rare)

**Solutions:**
- Restart application periodically
- Process presentations in batches
- Monitor with system tools
- Report persistent issues

---

## Browser-Specific Issues

### Chrome

**Issue:** Session cookies blocked

**Solution:** Check Settings → Privacy → Cookies → Allow all cookies (for localhost)

### Firefox

**Issue:** OAuth popup blocked

**Solution:** Allow popups for localhost in browser settings

### Safari

**Issue:** Intelligent Tracking Prevention blocks OAuth

**Solution:** Disable ITP for localhost or use different browser for development

---

## Production Issues

### HTTPS Required

**Error:** OAuth only works with HTTPS

**Solution:**
1. Configure SSL certificate
2. Use reverse proxy (nginx, Apache)
3. Remove `OAUTHLIB_INSECURE_TRANSPORT` variable
4. See [Production Guide](../deployment/production.md)

### Port Already in Use

**Error:** `Address already in use: Port 5000`

**Solutions:**
```bash
# Find process using port
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9

# Or use different port
python web_app.py --port 8080
```

---

## Logs and Debugging

### View Application Logs

```bash
# Tail logs in real-time
# Windows
Get-Content logs\app.log -Wait -Tail 50

# macOS/Linux
tail -f logs/app.log
```

### Enable Debug Mode

```bash
export FLASK_DEBUG=1
python web_app.py
```

**Features:**
- Detailed error messages
- Stack traces
- Interactive debugger
- Auto-reload

**Warning:** Never use debug mode in production!

### Check Database

```bash
python tests/debug/check_db.py
```

Shows:
- Number of sessions
- Number of jobs
- Recent activity
- Database size

---

## Getting Help

If issues persist:

1. **Check Documentation:**
   - [Installation Guide](../getting-started/installation.md)
   - [Authentication Guide](../getting-started/authentication.md)
   - [Web Interface Guide](web-interface.md)

2. **Review Logs:**
   - Application logs in `logs/`
   - Browser console (F12)
   - System logs

3. **Test Systematically:**
   - Isolate the problem
   - Try minimal example
   - Document steps to reproduce

4. **External Resources:**
   - [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
   - [Google Slides API](https://developers.google.com/slides/api)
   - [Flask Documentation](https://flask.palletsprojects.com/)

---

## Common Error Messages

### "NoneType object has no attribute"

**Cause:** Missing or invalid data

**Solution:** Check that all required fields are filled and valid

### "ConnectionError"

**Cause:** No internet connection

**Solution:** Check network connection and try again

### "JSONDecodeError"

**Cause:** Invalid JSON in configuration or response

**Solution:** Verify JSON files are valid (use JSON validator)

### "ImportError: No module named"

**Cause:** Missing Python package

**Solution:**
```bash
pip install <missing-package>
# Or reinstall all
pip install -r requirements.txt
```

---

**Last Updated:** December 17, 2024
