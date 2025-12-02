# Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place OAuth credentials
# Download client_secret.json from Google Cloud Console
# Copy to: credentials/client_secret.json
```

## First Use

```bash
# Run with any Google Slides URL
python -m presentation_design.main "YOUR_PRESENTATION_URL"

# Browser opens for authentication → Allow access
# Processing starts automatically
# New presentation link displayed
```

## Common Commands

```bash
# Use specific template
python -m presentation_design.main "URL" -t corporate_blue

# List available templates
python -m presentation_design.main --list-templates

# Use custom config
python -m presentation_design.main "URL" -c path/to/config.json
```

## Templates

- **default** - Simple black/white design
- **corporate_blue** - Professional blue theme

## Need Help?

- See [setup.md](setup.md) for detailed setup instructions
- See [README.md](README.md) for complete documentation
- Check `logs/` directory for error details
