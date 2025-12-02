# Setup Guide

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Internet**: Stable connection for Google API access
- **Google Account**: With access to Google Slides

## Detailed Setup Instructions

### 1. Python Environment

**Verify Python installation:**
```bash
python --version
# Should show 3.8 or higher
```

**Create virtual environment (recommended):**
```bash
# Navigate to project directory
cd ai_presentolog

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `google-api-python-client` - Google API access
- `google-auth-oauthlib` - OAuth authentication
- `google-auth` - Authentication helpers
- `requests` - HTTP library

### 3. Google Cloud Setup

**3.1. Create Google Cloud Project:**

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: "Presentation Design System"
4. Click "Create"

**3.2. Enable APIs:**

1. In Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Slides API" → Enable
3. Search for "Google Drive API" → Enable

**3.3. Create OAuth Credentials:**

1. Go to "APIs & Services" → "Credentials"
2. Click "+ CREATE CREDENTIALS" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: Internal (if in organization) or External
   - App name: "Presentation Design System"
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue" through remaining steps
4. Back to create credentials:
   - Application type: "Desktop app"
   - Name: "Presentation Design Desktop"
   - Click "Create"
5. Download credentials:
   - Click download icon next to created credential
   - Save as `client_secret.json`

**3.4. Place credentials:**

```bash
# Create credentials directory if not exists
mkdir credentials

# Move downloaded file
# On Windows:
move Downloads\client_secret*.json credentials\client_secret.json
# On macOS/Linux:
mv ~/Downloads/client_secret*.json credentials/client_secret.json
```

### 4. Configuration

**Review configuration file:**
```bash
# Open config/config.json in text editor
# Verify paths match your setup
```

**Key configuration parameters:**
- `client_secrets_path`: Path to OAuth credentials
- `token_path`: Where to store access tokens
- `template_directory`: Location of design templates
- `log_level`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

### 5. First Run - Authentication

**Run with test presentation:**
```bash
python -m presentation_design.main "YOUR_PRESENTATION_URL"
```

**Authentication flow:**
1. Browser window opens automatically
2. Select your Google account
3. Review permissions requested
4. Click "Allow"
5. Browser shows success message
6. Return to terminal - processing begins

**Note:** Token is saved to `credentials/token.json` for future use.

### 6. Verify Installation

**List available templates:**
```bash
python -m presentation_design.main --list-templates
```

Expected output:
```
Available templates:
  - default
  - corporate_blue
```

### 7. Test Processing

**Create test presentation:**
1. Create simple Google Slides presentation
2. Add a few slides with text
3. Copy the presentation URL

**Process test presentation:**
```bash
python -m presentation_design.main "YOUR_TEST_URL" -t corporate_blue
```

**Verify result:**
- New presentation link displayed in terminal
- Open link to view designed presentation
- Check that design template applied correctly

## Common Setup Issues

### Issue: Module not found errors

**Solution:**
```bash
# Ensure you're in project directory
cd ai_presentolog

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: OAuth errors during authentication

**Solutions:**
1. Verify APIs are enabled in Google Cloud Console
2. Check `client_secret.json` is valid JSON
3. Ensure OAuth consent screen is configured
4. Delete `credentials/token.json` and try again

### Issue: Permission denied errors

**Solutions:**
```bash
# On Windows, run as administrator
# On macOS/Linux, check file permissions:
chmod 600 credentials/client_secret.json
chmod 700 credentials/
```

### Issue: Template not found

**Solutions:**
- Verify template files exist in `presentation_design/templates/designs/`
- Check template name spelling
- Use `--list-templates` to see available options

## Development Setup

**For development and testing:**

```bash
# Install in development mode
pip install -e .

# Run tests (when available)
python -m pytest tests/
```

## Next Steps

- Review [README.md](README.md) for usage instructions
- Create custom templates (see template documentation)
- Configure for your organization's needs
- Test with various presentation types

## Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review error messages carefully
3. Verify Google Cloud Console configuration
4. Contact development team for assistance
