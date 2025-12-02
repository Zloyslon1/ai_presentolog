# Local Testing Guide

## How to Check Your Work on Local Machine

Since this is a Python-based Google Slides processor (not a web app), testing is done through command-line tools and scripts.

## Quick Test (Without Google Credentials)

### 1. Run Local Test Script

```powershell
# Install dependencies first
pip install -r requirements.txt

# Run the test script
python test_local.py
```

**Expected output:**
- ✅ Module Imports - All Python modules load correctly
- ✅ Configuration - Config file loads and validates
- ✅ Template System - Templates load successfully
- ✅ Logging System - Logs are created
- ⚠️ OAuth Credentials - Will fail until you set up Google credentials

### 2. List Available Templates

```powershell
python -m presentation_design.main --list-templates
```

**Expected output:**
```
Available templates:
  - corporate_blue
  - default
```

### 3. Check File Structure

Verify all files were created:

```powershell
# Check main package exists
dir presentation_design

# Check templates exist
dir presentation_design\templates\designs

# Check configuration
type config\config.json

# Check documentation
dir docs
```

## Full Test (With Google Credentials)

### Step 1: Set Up Google Cloud OAuth

1. **Go to**: https://console.cloud.google.com/
2. **Create Project**: "Presentation Design System"
3. **Enable APIs**:
   - Google Slides API
   - Google Drive API
4. **Create Credentials**:
   - APIs & Services → Credentials
   - CREATE CREDENTIALS → OAuth client ID
   - Application type: Desktop app
   - Download JSON file

5. **Place Credentials**:
   ```powershell
   # Create credentials directory
   mkdir credentials -Force
   
   # Copy downloaded file and rename
   copy Downloads\client_secret_*.json credentials\client_secret.json
   ```

### Step 2: Create Test Presentation

1. Go to Google Slides: https://docs.google.com/presentation/
2. Create new presentation
3. Add 2-3 slides with some text
4. Copy the URL (looks like: `https://docs.google.com/presentation/d/LONG_ID/edit`)

### Step 3: Run Full Test

```powershell
# Process your test presentation
python -m presentation_design.main "YOUR_PRESENTATION_URL" -t corporate_blue
```

**First Run - Authentication Flow:**
1. Browser window opens automatically
2. Sign in to Google account
3. Review permissions requested
4. Click "Allow"
5. Browser shows success message
6. Return to terminal - processing starts

**Expected output:**
```
✓ Presentation designed successfully!
  Title: Your Presentation Title (Designed)
  URL: https://docs.google.com/presentation/d/NEW_ID/edit
```

### Step 4: Verify Result

1. Click the URL from output
2. Check that new presentation has:
   - Same content as original
   - Applied design template (colors, fonts)
   - Professional styling

## Testing Individual Components

### Test Configuration

```powershell
python -c "from presentation_design.utils.config import get_config; config = get_config(); print('Config OK:', config)"
```

### Test Template Loading

```powershell
python -c "from presentation_design.templates.template_loader import TemplateLoader; loader = TemplateLoader('presentation_design/templates'); print('Templates:', loader.list_templates())"
```

### Test Logger

```powershell
python -c "from presentation_design.utils.logger import get_logger; logger = get_logger('test'); logger.info('Test message'); print('Check logs/ directory')"
```

## Checking Logs

All operations are logged to the `logs/` directory:

```powershell
# View latest log file
type logs\presentation_design.log

# Or in PowerShell:
Get-Content logs\presentation_design.log -Tail 50
```

**Log format:** JSON for easy parsing
```json
{"timestamp": "2024-01-15T10:30:00Z", "level": "INFO", "message": "Operation completed"}
```

## Common Test Scenarios

### Scenario 1: Test Different Templates

```powershell
# Test with default template
python -m presentation_design.main "URL" -t default

# Test with corporate_blue template
python -m presentation_design.main "URL" -t corporate_blue
```

### Scenario 2: Test Error Handling

```powershell
# Test with invalid URL (should show error)
python -m presentation_design.main "invalid-url"

# Test with non-existent template (should use fallback)
python -m presentation_design.main "URL" -t nonexistent
```

### Scenario 3: Test Python API

Create a test file `test_api.py`:

```python
from presentation_design.main import process_presentation

# Test processing
try:
    result = process_presentation(
        presentation_url="YOUR_URL_HERE",
        template_name="corporate_blue"
    )
    print(f"Success! New presentation: {result['presentation_url']}")
except Exception as e:
    print(f"Error: {e}")
```

Run it:
```powershell
python test_api.py
```

## Troubleshooting Local Tests

### Issue: Module not found

**Solution:**
```powershell
# Ensure you're in the project directory
cd C:\Users\Zloyslon\Desktop\Projects\ai_presentolog

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Configuration error

**Solution:**
```powershell
# Check config file exists
type config\config.json

# Validate JSON syntax
python -c "import json; json.load(open('config/config.json')); print('Config valid')"
```

### Issue: Template not found

**Solution:**
```powershell
# List templates
python -m presentation_design.main --list-templates

# Check template files exist
dir presentation_design\templates\designs\*.json
```

### Issue: OAuth errors

**Solution:**
```powershell
# Delete existing token and re-authenticate
Remove-Item credentials\token.json -ErrorAction SilentlyContinue

# Run again to trigger new auth flow
python -m presentation_design.main "URL"
```

## What "Works Locally" Means

✅ **Code Quality:**
- All modules import without errors
- No syntax errors
- Configuration loads correctly
- Templates validate successfully

✅ **Functionality:**
- Can list templates
- Can load and validate templates
- Logging system works
- Configuration system works
- Error handling functions properly

✅ **Integration (with credentials):**
- OAuth authentication succeeds
- Can connect to Google Slides API
- Can extract presentation content
- Can apply design templates
- Can create new presentations

## Next Steps After Local Testing

Once everything works locally:

1. **Version Control**: Commit code (without credentials!)
2. **Documentation**: Update README with findings
3. **Deployment**: Deploy to server/cloud if needed
4. **Phase 2**: Begin Phase 2 implementation (Google Sheets integration)

## Summary

Unlike a Rails web app with `rails server`, this Python system is tested via:
- **Command-line interface** for processing presentations
- **Test scripts** for component validation  
- **Direct Google API calls** for end-to-end testing
- **Log files** for operation verification

The system is working correctly when:
- `test_local.py` shows all tests passing (except OAuth before setup)
- Templates can be listed
- Presentations can be processed with real Google credentials
- Logs show successful operations
