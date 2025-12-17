# Installation Guide

Complete step-by-step guide to install and configure AI Presentolog.

---

## System Requirements

### Operating System
- **Windows** 10 or later
- **macOS** 10.14 or later
- **Linux** (Ubuntu 18.04+, Debian 10+, or equivalent)

### Software Prerequisites
- **Python 3.8 or higher** ([Download Python](https://www.python.org/downloads/))
- **pip** (Python package manager - included with Python)
- **Git** (optional, for cloning repository)
- **Web browser** (Chrome, Firefox, Safari, or Edge)

### Google Cloud Requirements
- **Google Cloud account** (free tier available)
- **Google Cloud project** with:
  - Google Slides API enabled
  - Google Drive API enabled
  - OAuth 2.0 credentials configured

---

## Step 1: Get the Code

### Option A: Clone with Git
```bash
git clone <repository-url>
cd ai_presentolog
```

### Option B: Download ZIP
1. Download the repository as ZIP
2. Extract to your desired location
3. Open terminal/command prompt in that directory

---

## Step 2: Install Python Dependencies

### Check Python Version
```bash
python --version
# Should show Python 3.8 or higher
```

If Python is not installed or version is too old:
- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **macOS:** Use Homebrew: `brew install python3`
- **Linux:** `sudo apt install python3 python3-pip`

### Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected packages:**
- Flask - Web framework
- google-auth - Google authentication
- google-auth-oauthlib - OAuth flow
- google-auth-httplib2 - HTTP library
- google-api-python-client - Google APIs
- Additional dependencies listed in requirements.txt

### Verify Installation
```bash
python -c "import flask; import google.auth; print('Dependencies installed successfully!')"
```

---

## Step 3: Create Directory Structure

Create required directories:

```bash
# On Windows (PowerShell)
New-Item -ItemType Directory -Force -Path credentials, db, logs

# On macOS/Linux
mkdir -p credentials db logs
```

**Directory purposes:**
- `credentials/` - OAuth credentials (gitignored for security)
- `db/` - SQLite database files
- `logs/` - Application log files

---

## Step 4: Set Up Google Cloud Project

### 4.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: **"AI Presentolog"**
4. Click **"Create"**
5. Wait for project creation (may take a few seconds)

### 4.2 Enable Required APIs

1. In Google Cloud Console, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Slides API"**
   - Click on it
   - Click **"Enable"**
3. Search for **"Google Drive API"**
   - Click on it
   - Click **"Enable"**

### 4.3 Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** user type
3. Click **"Create"**
4. Fill in required information:
   - **App name:** AI Presentolog
   - **User support email:** Your email
   - **Developer contact:** Your email
5. Click **"Save and Continue"**
6. On **"Scopes"** page, click **"Save and Continue"** (we'll add scopes via code)
7. On **"Test users"** page:
   - Click **"Add Users"**
   - Add your Google email address
   - Add any other users who will test the app
8. Click **"Save and Continue"**
9. Review and click **"Back to Dashboard"**

### 4.4 Create OAuth Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Select **Application type:** "Desktop app"
4. **Name:** "AI Presentolog Desktop Client"
5. Click **"Create"**
6. In the popup:
   - Click **"Download JSON"**
   - Save the file as `client_secret.json`

### 4.5 Place Credentials File

Move the downloaded file:

```bash
# Move to credentials directory
# Windows (PowerShell)
Move-Item ~/Downloads/client_secret*.json credentials/client_secret.json

# macOS/Linux
mv ~/Downloads/client_secret*.json credentials/client_secret.json
```

**Verify:**
```bash
# Check file exists
# Windows
Test-Path credentials/client_secret.json

# macOS/Linux
ls credentials/client_secret.json
```

---

## Step 5: Configure Application

### Configuration File

The application uses `config/config.json` for settings. Default configuration should work for most setups.

**Optional:** Review and customize:
```bash
# View configuration
cat config/config.json
```

**Key settings:**
- `authentication.scopes` - Google API permissions
- `logging.level` - Log verbosity (INFO, DEBUG, WARNING, ERROR)
- `templates.default_template` - Default design template

### Environment Variables (Optional)

For enhanced security, set environment variables:

```bash
# Windows (PowerShell)
$env:SECRET_KEY = "your-random-secret-key-here"
$env:OAUTHLIB_INSECURE_TRANSPORT = "1"  # Development only!

# macOS/Linux (bash/zsh)
export SECRET_KEY="your-random-secret-key-here"
export OAUTHLIB_INSECURE_TRANSPORT=1  # Development only!
```

**Variables:**
- `SECRET_KEY` - Flask session encryption key (generate random string)
- `OAUTHLIB_INSECURE_TRANSPORT` - Allow HTTP for local development (remove in production!)

---

## Step 6: Initialize Database

The database will be created automatically on first run, but you can verify:

```bash
# Run the application briefly
python web_app.py
# Press Ctrl+C after you see "Running on http://localhost:5000"
```

**Verify database created:**
```bash
# Windows
Test-Path db/presentation_jobs.db

# macOS/Linux
ls db/presentation_jobs.db
```

---

## Step 7: Verify Installation

### Run Test Script (Optional)

```bash
python tests/unit/test_local.py
```

This verifies:
- Python dependencies
- Configuration files
- Template system
- Logging setup

### Start Application

```bash
python web_app.py
```

**Expected output:**
```
Database initialized at db/presentation_jobs.db
✓ Service Account loaded: <email> (if configured)
 * Running on http://localhost:5000
 * Debug mode: off
```

### Test in Browser

1. Open browser: http://localhost:5000
2. You should see the AI Presentolog login page
3. Try clicking **"Sign in with Google"**
4. Authorize the application
5. You should be redirected to the main interface

---

## Installation Verification Checklist

- [ ] Python 3.8+ installed and accessible
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Directory structure created (`credentials/`, `db/`, `logs/`)
- [ ] Google Cloud project created
- [ ] Google Slides API enabled
- [ ] Google Drive API enabled
- [ ] OAuth consent screen configured
- [ ] OAuth credentials created and downloaded
- [ ] `credentials/client_secret.json` file placed correctly
- [ ] Application starts without errors
- [ ] Can access http://localhost:5000 in browser
- [ ] OAuth flow works (sign in with Google)

---

## Troubleshooting

### "Python not found" or "python: command not found"

**Solution:**
- Install Python from [python.org](https://www.python.org/downloads/)
- On Windows: Make sure "Add Python to PATH" is checked during installation
- Try `python3` instead of `python`

### "pip: command not found"

**Solution:**
```bash
# Windows
python -m pip install -r requirements.txt

# macOS/Linux
python3 -m pip install -r requirements.txt
```

### "Module not found" errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### OAuth credentials not found

**Error:** `Client secrets file not found: credentials/client_secret.json`

**Solution:**
1. Verify file exists: `ls credentials/` (macOS/Linux) or `dir credentials\` (Windows)
2. Check filename is exactly `client_secret.json`
3. Verify file is valid JSON (open in text editor)
4. Re-download from Google Cloud Console if needed

### Port 5000 already in use

**Error:** `Address already in use`

**Solution:**
```bash
# Find and kill process using port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9

# Or run on different port
python web_app.py --port 5001
```

### Permission errors on database

**Error:** `Permission denied: db/presentation_jobs.db`

**Solution:**
```bash
# Fix permissions (macOS/Linux)
chmod 755 db
chmod 644 db/*.db

# Windows: Run PowerShell as Administrator
icacls db /grant Everyone:F /T
```

---

## Next Steps

Once installation is complete:

1. **[Set up Authentication](authentication.md)** - Configure OAuth in detail
2. **[Quick Start Guide](quick-start.md)** - Process your first presentation
3. **[Web Interface Guide](../user-guide/web-interface.md)** - Learn the features

---

## Optional: Service Account Setup

For server-side access to public presentations (advanced):

See [SETUP_SERVICE_ACCOUNT.md](SETUP_SERVICE_ACCOUNT.md) for instructions.

---

**Installation Support:**
- For common issues, see [Troubleshooting Guide](../user-guide/troubleshooting.md)
- For Google Cloud issues, see [Google Cloud Documentation](https://cloud.google.com/docs)

**Last Updated:** December 17, 2024
# Installation Guide

Complete step-by-step guide to install and configure AI Presentolog.

---

## System Requirements

### Operating System
- **Windows** 10 or later
- **macOS** 10.14 or later
- **Linux** (Ubuntu 18.04+, Debian 10+, or equivalent)

### Software Prerequisites
- **Python 3.8 or higher** ([Download Python](https://www.python.org/downloads/))
- **pip** (Python package manager - included with Python)
- **Git** (optional, for cloning repository)
- **Web browser** (Chrome, Firefox, Safari, or Edge)

### Google Cloud Requirements
- **Google Cloud account** (free tier available)
- **Google Cloud project** with:
  - Google Slides API enabled
  - Google Drive API enabled
  - OAuth 2.0 credentials configured

---

## Step 1: Get the Code

### Option A: Clone with Git
```bash
git clone <repository-url>
cd ai_presentolog
```

### Option B: Download ZIP
1. Download the repository as ZIP
2. Extract to your desired location
3. Open terminal/command prompt in that directory

---

## Step 2: Install Python Dependencies

### Check Python Version
```bash
python --version
# Should show Python 3.8 or higher
```

If Python is not installed or version is too old:
- **Windows:** Download from [python.org](https://www.python.org/downloads/)
- **macOS:** Use Homebrew: `brew install python3`
- **Linux:** `sudo apt install python3 python3-pip`

### Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected packages:**
- Flask - Web framework
- google-auth - Google authentication
- google-auth-oauthlib - OAuth flow
- google-auth-httplib2 - HTTP library
- google-api-python-client - Google APIs
- Additional dependencies listed in requirements.txt

### Verify Installation
```bash
python -c "import flask; import google.auth; print('Dependencies installed successfully!')"
```

---

## Step 3: Create Directory Structure

Create required directories:

```bash
# On Windows (PowerShell)
New-Item -ItemType Directory -Force -Path credentials, db, logs

# On macOS/Linux
mkdir -p credentials db logs
```

**Directory purposes:**
- `credentials/` - OAuth credentials (gitignored for security)
- `db/` - SQLite database files
- `logs/` - Application log files

---

## Step 4: Set Up Google Cloud Project

### 4.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: **"AI Presentolog"**
4. Click **"Create"**
5. Wait for project creation (may take a few seconds)

### 4.2 Enable Required APIs

1. In Google Cloud Console, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Slides API"**
   - Click on it
   - Click **"Enable"**
3. Search for **"Google Drive API"**
   - Click on it
   - Click **"Enable"**

### 4.3 Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** user type
3. Click **"Create"**
4. Fill in required information:
   - **App name:** AI Presentolog
   - **User support email:** Your email
   - **Developer contact:** Your email
5. Click **"Save and Continue"**
6. On **"Scopes"** page, click **"Save and Continue"** (we'll add scopes via code)
7. On **"Test users"** page:
   - Click **"Add Users"**
   - Add your Google email address
   - Add any other users who will test the app
8. Click **"Save and Continue"**
9. Review and click **"Back to Dashboard"**

### 4.4 Create OAuth Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Select **Application type:** "Desktop app"
4. **Name:** "AI Presentolog Desktop Client"
5. Click **"Create"**
6. In the popup:
   - Click **"Download JSON"**
   - Save the file as `client_secret.json`

### 4.5 Place Credentials File

Move the downloaded file:

```bash
# Move to credentials directory
# Windows (PowerShell)
Move-Item ~/Downloads/client_secret*.json credentials/client_secret.json

# macOS/Linux
mv ~/Downloads/client_secret*.json credentials/client_secret.json
```

**Verify:**
```bash
# Check file exists
# Windows
Test-Path credentials/client_secret.json

# macOS/Linux
ls credentials/client_secret.json
```

---

## Step 5: Configure Application

### Configuration File

The application uses `config/config.json` for settings. Default configuration should work for most setups.

**Optional:** Review and customize:
```bash
# View configuration
cat config/config.json
```

**Key settings:**
- `authentication.scopes` - Google API permissions
- `logging.level` - Log verbosity (INFO, DEBUG, WARNING, ERROR)
- `templates.default_template` - Default design template

### Environment Variables (Optional)

For enhanced security, set environment variables:

```bash
# Windows (PowerShell)
$env:SECRET_KEY = "your-random-secret-key-here"
$env:OAUTHLIB_INSECURE_TRANSPORT = "1"  # Development only!

# macOS/Linux (bash/zsh)
export SECRET_KEY="your-random-secret-key-here"
export OAUTHLIB_INSECURE_TRANSPORT=1  # Development only!
```

**Variables:**
- `SECRET_KEY` - Flask session encryption key (generate random string)
- `OAUTHLIB_INSECURE_TRANSPORT` - Allow HTTP for local development (remove in production!)

---

## Step 6: Initialize Database

The database will be created automatically on first run, but you can verify:

```bash
# Run the application briefly
python web_app.py
# Press Ctrl+C after you see "Running on http://localhost:5000"
```

**Verify database created:**
```bash
# Windows
Test-Path db/presentation_jobs.db

# macOS/Linux
ls db/presentation_jobs.db
```

---

## Step 7: Verify Installation

### Run Test Script (Optional)

```bash
python tests/unit/test_local.py
```

This verifies:
- Python dependencies
- Configuration files
- Template system
- Logging setup

### Start Application

```bash
python web_app.py
```

**Expected output:**
```
Database initialized at db/presentation_jobs.db
✓ Service Account loaded: <email> (if configured)
 * Running on http://localhost:5000
 * Debug mode: off
```

### Test in Browser

1. Open browser: http://localhost:5000
2. You should see the AI Presentolog login page
3. Try clicking **"Sign in with Google"**
4. Authorize the application
5. You should be redirected to the main interface

---

## Installation Verification Checklist

- [ ] Python 3.8+ installed and accessible
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Directory structure created (`credentials/`, `db/`, `logs/`)
- [ ] Google Cloud project created
- [ ] Google Slides API enabled
- [ ] Google Drive API enabled
- [ ] OAuth consent screen configured
- [ ] OAuth credentials created and downloaded
- [ ] `credentials/client_secret.json` file placed correctly
- [ ] Application starts without errors
- [ ] Can access http://localhost:5000 in browser
- [ ] OAuth flow works (sign in with Google)

---

## Troubleshooting

### "Python not found" or "python: command not found"

**Solution:**
- Install Python from [python.org](https://www.python.org/downloads/)
- On Windows: Make sure "Add Python to PATH" is checked during installation
- Try `python3` instead of `python`

### "pip: command not found"

**Solution:**
```bash
# Windows
python -m pip install -r requirements.txt

# macOS/Linux
python3 -m pip install -r requirements.txt
```

### "Module not found" errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### OAuth credentials not found

**Error:** `Client secrets file not found: credentials/client_secret.json`

**Solution:**
1. Verify file exists: `ls credentials/` (macOS/Linux) or `dir credentials\` (Windows)
2. Check filename is exactly `client_secret.json`
3. Verify file is valid JSON (open in text editor)
4. Re-download from Google Cloud Console if needed

### Port 5000 already in use

**Error:** `Address already in use`

**Solution:**
```bash
# Find and kill process using port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9

# Or run on different port
python web_app.py --port 5001
```

### Permission errors on database

**Error:** `Permission denied: db/presentation_jobs.db`

**Solution:**
```bash
# Fix permissions (macOS/Linux)
chmod 755 db
chmod 644 db/*.db

# Windows: Run PowerShell as Administrator
icacls db /grant Everyone:F /T
```

---

## Next Steps

Once installation is complete:

1. **[Set up Authentication](authentication.md)** - Configure OAuth in detail
2. **[Quick Start Guide](quick-start.md)** - Process your first presentation
3. **[Web Interface Guide](../user-guide/web-interface.md)** - Learn the features

---

## Optional: Service Account Setup

For server-side access to public presentations (advanced):

See [SETUP_SERVICE_ACCOUNT.md](SETUP_SERVICE_ACCOUNT.md) for instructions.

---

**Installation Support:**
- For common issues, see [Troubleshooting Guide](../user-guide/troubleshooting.md)
- For Google Cloud issues, see [Google Cloud Documentation](https://cloud.google.com/docs)

**Last Updated:** December 17, 2024
