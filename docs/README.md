# Automated Presentation Design System

## Phase 1: Core Design Engine

A Python-based system for automatically extracting content from Google Slides presentations, applying professional design templates, and generating styled presentations.

## Features

- **OAuth 2.0 Authentication**: Secure Google API access with token management
- **Content Extraction**: Parse presentation structure and text from Google Slides
- **Template System**: JSON-based design templates with typography, colors, and layouts
- **Design Application**: Apply templates to preserve content while enhancing visual design
- **Presentation Generation**: Create new Google Slides presentations with applied designs
- **Error Handling**: Comprehensive logging and retry logic for API operations

## Project Structure

```
presentation_design/
├── auth/                   # Authentication and credentials management
├── extraction/             # Content extraction from Google Slides
├── templates/              # Template management and validation
│   └── designs/           # Design template files (JSON)
├── design/                 # Design application logic
├── generation/             # Presentation building
└── utils/                  # Configuration, logging, retry logic

config/                     # Configuration files
credentials/                # OAuth credentials (gitignored)
logs/                       # Application logs
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Cloud project with Slides API enabled
- OAuth 2.0 credentials from Google Cloud Console

### Setup Steps

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Google Cloud:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google Slides API and Google Drive API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download credentials as `client_secret.json`

3. **Place credentials:**
   ```bash
   mkdir -p credentials
   # Copy your downloaded client_secret.json to credentials/
   ```

4. **Verify configuration:**
   - Review `config/config.json`
   - Adjust paths and settings as needed

## Usage

### Command Line

**Process a presentation:**
```bash
python -m presentation_design.main <presentation_url> -t corporate_blue
```

**List available templates:**
```bash
python -m presentation_design.main --list-templates
```

**Specify custom configuration:**
```bash
python -m presentation_design.main <presentation_url> -c path/to/config.json
```

### Python API

```python
from presentation_design.main import process_presentation

result = process_presentation(
    presentation_url="https://docs.google.com/presentation/d/YOUR_ID/edit",
    template_name="corporate_blue"
)

print(f"New presentation: {result['presentation_url']}")
```

## Configuration

Edit `config/config.json` to customize:

- **Authentication**: OAuth credentials paths and scopes
- **Templates**: Template directory and default template
- **Processing**: Retry counts and timeouts
- **Logging**: Log level, format, and retention

## Templates

Templates are JSON files in `presentation_design/templates/designs/`.

**Available templates:**
- `default` - Simple black and white template
- `corporate_blue` - Professional blue color scheme

**Create custom templates:**
See `docs/template_guide.md` for template structure documentation.

## Authentication Flow

On first run:
1. Application opens browser for Google OAuth consent
2. Grant access to Google Slides and Drive
3. Credentials saved to `credentials/token.json`
4. Subsequent runs use saved credentials

To re-authenticate:
```bash
# Delete token file and run again
rm credentials/token.json
```

## Logging

Logs are written to `logs/` directory:
- JSON format for automated processing
- Console output for real-time monitoring
- Automatic daily rotation
- 30-day retention (configurable)

## Troubleshooting

**Authentication errors:**
- Verify `client_secret.json` is valid
- Check API is enabled in Google Cloud Console
- Delete `credentials/token.json` and re-authenticate

**API quota exceeded:**
- System will automatically retry after quota resets
- Consider requesting quota increase in Google Cloud Console

**Template not found:**
- Verify template name matches file in `templates/designs/`
- Use `--list-templates` to see available templates

## Phase 2 (Planned)

Future enhancements:
- Google Sheets monitoring for automated processing
- Workflow orchestration and status tracking
- Google Drive upload and organization
- Email notifications
- Scheduled processing

## Contributing

This is an internal tool. For issues or enhancements, contact the development team.

## License

Internal use only - AI Presentolog Team
