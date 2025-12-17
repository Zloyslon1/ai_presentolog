# AI Presentolog

**Automated Google Slides Presentation Designer with Interactive Editor**

AI Presentolog is a web-based tool that extracts content from Google Slides presentations (or raw text), provides an interactive WYSIWYG editor for customization, and generates beautifully designed presentations using professional templates.

---

## ✨ Key Features

- **🌐 Web Interface** - Easy-to-use Flask web application
- **🔐 Google OAuth Integration** - Secure multi-user authentication
- **📊 Multiple Input Methods**
  - Import from Google Slides URLs
  - Paste raw text content
- **✏️ Interactive WYSIWYG Editor**
  - Edit slide titles and content
  - Add and manage images
  - Reorder and delete slides
  - Real-time preview
- **🎨 Professional Templates** - Apply beautiful design templates
- **👥 Multi-User Support** - Each user has isolated sessions
- **💾 Job History** - Track and revisit previous presentations

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Google Cloud account** with:
  - Google Slides API enabled
  - Google Drive API enabled
  - OAuth 2.0 credentials configured

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_presentolog
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google OAuth credentials**
   - Follow the guide: [docs/getting-started/SETUP_OAUTH_GUIDE.md](docs/getting-started/SETUP_OAUTH_GUIDE.md)
   - Download `client_secret.json`
   - Place it in: `credentials/client_secret.json`

4. **Start the application**
   ```bash
   python web_app.py
   ```

5. **Open your browser**
   ```
   http://localhost:5000
   ```

6. **Sign in with Google** and start creating presentations!

---

## 📖 Documentation

### Getting Started
- **[Installation Guide](docs/getting-started/installation.md)** - Complete setup instructions
- **[Authentication Setup](docs/getting-started/authentication.md)** - OAuth and Service Account configuration
- **[Quick Start](docs/getting-started/quick-start.md)** - Get up and running in 5 minutes

### User Guide
- **[Web Interface](docs/user-guide/web-interface.md)** - Using the web application
- **[Slide Editor](docs/user-guide/slide-editor.md)** - Interactive editor features
- **[Templates](docs/user-guide/templates.md)** - Working with design templates
- **[Troubleshooting](docs/user-guide/troubleshooting.md)** - Common issues and solutions
- **[OAuth Guide](docs/user-guide/README_OAUTH.md)** - Detailed OAuth documentation

### Developer Guide
- **[Architecture](docs/developer-guide/architecture.md)** - System design and components
- **[API Reference](docs/developer-guide/api-reference.md)** - Python API documentation
- **[Template Development](docs/developer-guide/template-development.md)** - Creating custom templates
- **[Contributing](docs/developer-guide/contributing.md)** - Development guidelines

### Deployment
- **[Local Deployment](docs/deployment/local-deployment.md)** - Running locally
- **[Production](docs/deployment/production.md)** - Production deployment guide

---

## 🎯 How It Works

### Workflow

```
1. User Authentication
   ↓
2. Input Presentation (URL or Text)
   ↓
3. Content Extraction
   ↓
4. Interactive Editor
   - Edit titles & content
   - Add/manage images
   - Reorder slides
   ↓
5. Select Template
   ↓
6. Generate Styled Presentation
   ↓
7. Access via Google Slides
```

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  Flask Web App                       │
│              (web_app.py - Multi-user)              │
└─────────────────┬───────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐  ┌─────▼──────┐  ┌──▼────┐
│ OAuth │  │ Extraction │  │ Editor│
│Manager│  │   Engine   │  │  UI   │
└───┬───┘  └─────┬──────┘  └──┬────┘
    │            │             │
    └────────────┼─────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼────┐  ┌───▼────┐  ┌───▼─────┐
│Template│  │ Design │  │Presenta-│
│ System │  │Applica-│  │  tion   │
│        │  │  tor   │  │ Builder │
└────────┘  └────────┘  └─────────┘
```

**Core Components:**
- **Authentication Layer** - Google OAuth 2.0 with session management
- **Extraction Engine** - Parses Google Slides and raw text
- **Interactive Editor** - WYSIWYG editing interface
- **Template System** - JSON-based design templates
- **Design Applicator** - Applies templates to content
- **Presentation Builder** - Creates new Google Slides presentations

---

## 💻 Usage Examples

### Web Interface

1. **Sign in with Google**
2. **Choose input method:**
   - **URL**: Paste Google Slides link
   - **Text**: Paste raw presentation content
3. **Edit in the interactive editor:**
   - Modify titles and content
   - Upload and position images
   - Add or remove slides
4. **Configure settings** (template, colors, fonts)
5. **Generate presentation**
6. **Access your styled presentation in Google Slides**

### Python API

```python
from presentation_design.main import process_presentation

# Process a presentation programmatically
result = process_presentation(
    presentation_url="https://docs.google.com/presentation/d/YOUR_ID/edit",
    template_name="corporate_blue"
)

print(f"New presentation created: {result['presentation_url']}")
```

---

## 🗂️ Project Structure

```
ai_presentolog/
├── web_app.py                  # Flask web application (main entry point)
├── requirements.txt            # Python dependencies
│
├── presentation_design/        # Core Python modules
│   ├── auth/                  # OAuth and authentication
│   ├── extraction/            # Content extraction from Slides/text
│   ├── design/                # Design application logic
│   ├── generation/            # Presentation building
│   ├── templates/             # Template system
│   │   └── designs/          # JSON template files
│   └── utils/                 # Configuration, logging, utilities
│
├── templates/                  # Flask HTML templates (web UI)
│   ├── index.html             # Main page
│   ├── slide_editor.html      # Interactive editor
│   └── ...
│
├── docs/                       # Documentation
│   ├── getting-started/       # Setup and installation
│   ├── user-guide/            # User documentation
│   ├── developer-guide/       # Developer documentation
│   ├── deployment/            # Deployment guides
│   └── implementation-history/# Historical logs
│
├── tests/                      # Test files
│   ├── unit/                  # Unit tests
│   ├── debug/                 # Debug utilities
│   └── docs/                  # Test documentation
│
├── credentials/               # OAuth credentials (gitignored)
├── db/                        # SQLite database for sessions/jobs
├── logs/                      # Application logs
└── config/                    # Configuration files
```

---

## 🛠️ Technology Stack

- **Backend:** Python 3.8+, Flask
- **APIs:** Google Slides API, Google Drive API
- **Authentication:** Google OAuth 2.0
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **Templates:** JSON-based design templates

---

## 🔐 Security Features

- **OAuth 2.0 Authentication** - Secure Google account integration
- **Per-User Sessions** - Isolated user sessions in database
- **CSRF Protection** - OAuth state parameter validation
- **Credential Encryption** - Sensitive data encrypted in sessions
- **Session Management** - Automatic token refresh and expiration

---

## 🎨 Available Templates

- **Default** - Simple black and white design
- **Corporate Blue** - Professional blue color scheme

Create your own templates by following the [Template Development Guide](docs/developer-guide/template-development.md).

---

## 🧪 Testing

Run tests from the `tests/` directory:

```bash
# Run unit tests
python tests/unit/test_content_analyzer.py
python tests/unit/test_text_splitter.py

# Run debug utilities
python tests/debug/check_db.py
```

See [tests/README.md](tests/README.md) for more information.

---

## 🐛 Troubleshooting

### Common Issues

**OAuth Error: redirect_uri_mismatch**
- For Desktop app: This is normal during local development
- For Web app: Add `http://localhost:5000/auth/callback` to authorized redirect URIs

**Credentials File Not Found**
- Ensure `credentials/client_secret.json` exists
- Follow [SETUP_OAUTH_GUIDE.md](docs/getting-started/SETUP_OAUTH_GUIDE.md)

**Permission Denied on Presentation**
- Make sure presentation is accessible (shared with "Anyone with link")
- Or sign in with Google account that owns the presentation

**Session Expires Immediately**
- Set `SECRET_KEY` environment variable
- Enable cookies in browser
- Check for HTTPS/HTTP configuration issues

For more help, see the [Troubleshooting Guide](docs/user-guide/troubleshooting.md).

---

## 📊 Database

AI Presentolog uses SQLite for:
- **User Sessions** - OAuth credentials and session data
- **Job Tracking** - Presentation processing jobs and history
- **Multi-User Isolation** - Jobs are linked to user sessions

Database location: `db/presentation_jobs.db`

---

## 🚀 Deployment

### Local Development

```bash
# Set environment variables (optional)
export SECRET_KEY="your-secret-key"
export OAUTHLIB_INSECURE_TRANSPORT=1  # Development only!

# Run Flask application
python web_app.py
```

### Production

See [Production Deployment Guide](docs/deployment/production.md) for:
- HTTPS configuration
- Production web servers (Gunicorn, uWSGI)
- Security hardening
- Performance optimization
- Monitoring and logging

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/developer-guide/contributing.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

---

## 📝 License

Internal use only - AI Presentolog Team

---

## 📞 Support

- **Documentation:** [docs/](docs/)
- **Issues:** Check [Troubleshooting Guide](docs/user-guide/troubleshooting.md)
- **API Docs:** [Google Slides API](https://developers.google.com/slides/api)

---

## 🙏 Acknowledgments

- Google OAuth 2.0 and APIs
- Flask web framework
- All contributors to the project

---

**Last Updated:** December 17, 2024  
**Version:** 2.0.0  
**Status:** ✅ Production Ready
