# Web Interface Guide

Complete guide to using the AI Presentolog web interface.

---

## Overview

AI Presentolog provides a modern, user-friendly web interface for processing presentations. This guide covers all features and workflows.

---

## Accessing the Application

### Local Development

```bash
python web_app.py
```

Open browser: **http://localhost:5000**

### Production

Access via your deployed URL (e.g., `https://yourserver.com`)

---

## Authentication

### Sign In

1. Visit application URL
2. Click **"Sign in with Google"** button
3. Select your Google account
4. Review and grant permissions
5. Click **"Allow"**
6. Redirected to main interface

### Session Status

- **Logged in:** Your email appears in navigation bar
- **Session duration:** 24 hours (by default)
- **Auto-refresh:** Access tokens refreshed automatically

### Sign Out

1. Click **"Logout"** in navigation bar
2. Session cleared immediately
3. Redirected to login page

---

## Main Interface

### Layout

```
┌─────────────────────────────────────────────────┐
│  AI Presentolog         user@email.com  Logout  │ ← Navigation Bar
├─────────────────────────────────────────────────┤
│                                                 │
│  [  URL Import  ] [ Text Input ]               │ ← Input Tabs
│                                                 │
│  ┌──────────────────────────────────────────┐ │
│  │ Paste Google Slides URL or text content  │ │ ← Input Area
│  │                                          │ │
│  └──────────────────────────────────────────┘ │
│                                                 │
│          [ 📝 Открыть редактор ]               │ ← Process Button
│                                                 │
├─────────────────────────────────────────────────┤
│  Recent Jobs:                                   │ ← Job History
│  ┌─────────────────────────────────────────┐  │
│  │ Job #abc123 - Status: completed         │  │
│  └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Navigation Bar

**Elements:**
- **AI Presentolog** logo (home link)
- **User email** - Shows logged-in user
- **Logout** button - Sign out

---

## Input Methods

### Method 1: URL Import

**Use when:** You have an existing Google Slides presentation

**Steps:**

1. Click **"URL"** tab (default)

2. Get presentation URL:
   - Open presentation in Google Slides
   - Copy URL from browser address bar
   - Format: `https://docs.google.com/presentation/d/[ID]/edit`

3. Paste URL in input field

4. Click **"📝 Открыть редактор"** (Open Editor)

**Requirements:**
- Must be signed in with Google
- Presentation must be:
  - Owned by you, OR
  - Shared with you, OR
  - Public ("Anyone with link")

### Method 2: Text Input

**Use when:** You have text content to convert to slides

**Steps:**

1. Click **"Текст"** (Text) tab

2. Paste or type content in text area

**Supported formats:**

**Simple format:**
```
Presentation Title

# Slide 1 Title
Main content for slide 1
- Bullet point 1
- Bullet point 2

# Slide 2 Title
Content for slide 2
```

**Markdown-like format:**
```
# Main Title

## First Slide
Content here

## Second Slide
More content
- List item
- Another item
```

3. Click **"📝 Открыть редактор"**

**Text parsing features:**
- Automatic slide detection
- Heading recognition
- Bullet list formatting
- Emphasis detection (bold, italic)

---

## Processing Status

### Extraction Status Page

After submitting, you'll see the status page:

```
Extracting presentation...
Status: extracting
Created: 2024-12-17 14:30:22
```

**Status indicators:**

- **extracting** - Reading presentation content
- **parsing** - Processing text input
- **completed** - Ready for editing
- **error** - Something went wrong

### Auto-refresh

Page automatically checks status every 2 seconds until complete.

### Error Handling

If extraction fails, you'll see:
- Error message
- Possible causes
- Suggested solutions

**Common errors:**
- Permission denied - Share presentation or sign in with correct account
- Invalid URL - Check URL format
- Network error - Check internet connection

---

## Job Management

### Job History

Recent jobs displayed on main page:

**Information shown:**
- Job ID (unique identifier)
- Presentation URL or "Text input"
- Status (extracting, completed, error)
- Created timestamp
- Generated presentation link (if completed)

### Accessing Jobs

**From main page:**
- Click job ID to view details
- Click "Open Editor" to edit slides
- Click generated presentation link to view result

**Direct access:**
- URL format: `http://localhost:5000/status/<job_id>`

### Job Isolation

**Multi-user support:**
- Each user sees only their own jobs
- Jobs are linked to user session
- Complete data isolation

---

## Interactive Editor

Detailed guide: [slide-editor.md](slide-editor.md)

**Quick overview:**

After extraction completes, you're redirected to the interactive editor where you can:

- Edit slide titles and content
- Add and position images
- Reorder slides
- Delete slides
- Configure presentation settings
- Select design template
- Generate final presentation

---

## Features

### Multi-Tab Input

- **URL tab** - Import from Google Slides
- **Text tab** - Paste text content
- Switch between tabs anytime
- Input cleared when switching

### Real-Time Updates

- Job status updates automatically
- No page refresh needed
- Visual feedback for all actions

### Session Persistence

- Stay signed in between visits
- Jobs saved to database
- History preserved across sessions

### Mobile Responsive

- Works on desktop and mobile
- Touch-friendly interface
- Responsive layout

---

## Keyboard Shortcuts

**Main Interface:**
- `Ctrl+V` / `Cmd+V` - Paste URL or text
- `Enter` - Submit form (when focused)
- `Tab` - Switch between fields

**Navigation:**
- Browser back button returns to main page from editor

---

## Tips & Best Practices

### URL Import

✓ **Do:**
- Copy full URL including `/edit`
- Ensure you have access before importing
- Use presentations with consistent formatting

✗ **Don't:**
- Use shortened URLs (expand them first)
- Import presentations you don't have access to
- Submit incomplete URLs

### Text Input

✓ **Do:**
- Use clear heading markers (`#` or `##`)
- Structure content logically
- Include whitespace between slides
- Use bullet points for lists

✗ **Don't:**
- Mix multiple formatting styles
- Use overly complex formatting
- Paste raw data without structure

### Job Management

✓ **Do:**
- Use descriptive presentation titles
- Keep track of important jobs
- Clean up old test jobs periodically

✗ **Don't:**
- Create duplicate jobs unnecessarily
- Leave sensitive content in jobs
- Share job IDs with others

---

## Troubleshooting

### Can't Sign In

**Problem:** OAuth flow fails

**Solutions:**
- Clear browser cookies
- Try incognito/private mode
- Check credentials file exists
- Review OAuth consent screen setup

### Extraction Fails

**Problem:** "Permission denied" error

**Solutions:**
- Sign in with account that owns presentation
- Make presentation public ("Anyone with link")
- Share presentation with your Google account
- Check presentation URL is correct

### Jobs Not Showing

**Problem:** Can't see previously created jobs

**Possible causes:**
- Different user account
- Session expired
- Database issue

**Solutions:**
- Sign in with same Google account
- Check browser console for errors
- Verify database file exists

### Slow Extraction

**Problem:** Takes too long to extract

**Causes:**
- Large presentation (many slides)
- Complex content (many images)
- Network latency

**Normal times:**
- Small (1-5 slides): 5-10 seconds
- Medium (6-20 slides): 10-30 seconds
- Large (20+ slides): 30-60 seconds

---

## Advanced Features

### Service Account Mode

If Service Account is configured:

- Application tries OAuth first
- Falls back to Service Account for public presentations
- Transparent to user

### Debug Mode

Available in development:

```bash
# Enable debug mode
export FLASK_DEBUG=1
python web_app.py
```

**Features:**
- Detailed error messages
- Auto-reload on code changes
- Interactive debugger

---

## API Access

For programmatic access, use the Python API instead of web interface.

See: [API Reference](../developer-guide/api-reference.md)

---

## Next Steps

- **[Slide Editor Guide](slide-editor.md)** - Learn editor features
- **[Templates Guide](templates.md)** - Work with design templates
- **[Troubleshooting](troubleshooting.md)** - Solve common issues

---

**Last Updated:** December 17, 2024
# Web Interface Guide

Complete guide to using the AI Presentolog web interface.

---

## Overview

AI Presentolog provides a modern, user-friendly web interface for processing presentations. This guide covers all features and workflows.

---

## Accessing the Application

### Local Development

```bash
python web_app.py
```

Open browser: **http://localhost:5000**

### Production

Access via your deployed URL (e.g., `https://yourserver.com`)

---

## Authentication

### Sign In

1. Visit application URL
2. Click **"Sign in with Google"** button
3. Select your Google account
4. Review and grant permissions
5. Click **"Allow"**
6. Redirected to main interface

### Session Status

- **Logged in:** Your email appears in navigation bar
- **Session duration:** 24 hours (by default)
- **Auto-refresh:** Access tokens refreshed automatically

### Sign Out

1. Click **"Logout"** in navigation bar
2. Session cleared immediately
3. Redirected to login page

---

## Main Interface

### Layout

```
┌─────────────────────────────────────────────────┐
│  AI Presentolog         user@email.com  Logout  │ ← Navigation Bar
├─────────────────────────────────────────────────┤
│                                                 │
│  [  URL Import  ] [ Text Input ]               │ ← Input Tabs
│                                                 │
│  ┌──────────────────────────────────────────┐ │
│  │ Paste Google Slides URL or text content  │ │ ← Input Area
│  │                                          │ │
│  └──────────────────────────────────────────┘ │
│                                                 │
│          [ 📝 Открыть редактор ]               │ ← Process Button
│                                                 │
├─────────────────────────────────────────────────┤
│  Recent Jobs:                                   │ ← Job History
│  ┌─────────────────────────────────────────┐  │
│  │ Job #abc123 - Status: completed         │  │
│  └─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Navigation Bar

**Elements:**
- **AI Presentolog** logo (home link)
- **User email** - Shows logged-in user
- **Logout** button - Sign out

---

## Input Methods

### Method 1: URL Import

**Use when:** You have an existing Google Slides presentation

**Steps:**

1. Click **"URL"** tab (default)

2. Get presentation URL:
   - Open presentation in Google Slides
   - Copy URL from browser address bar
   - Format: `https://docs.google.com/presentation/d/[ID]/edit`

3. Paste URL in input field

4. Click **"📝 Открыть редактор"** (Open Editor)

**Requirements:**
- Must be signed in with Google
- Presentation must be:
  - Owned by you, OR
  - Shared with you, OR
  - Public ("Anyone with link")

### Method 2: Text Input

**Use when:** You have text content to convert to slides

**Steps:**

1. Click **"Текст"** (Text) tab

2. Paste or type content in text area

**Supported formats:**

**Simple format:**
```
Presentation Title

# Slide 1 Title
Main content for slide 1
- Bullet point 1
- Bullet point 2

# Slide 2 Title
Content for slide 2
```

**Markdown-like format:**
```
# Main Title

## First Slide
Content here

## Second Slide
More content
- List item
- Another item
```

3. Click **"📝 Открыть редактор"**

**Text parsing features:**
- Automatic slide detection
- Heading recognition
- Bullet list formatting
- Emphasis detection (bold, italic)

---

## Processing Status

### Extraction Status Page

After submitting, you'll see the status page:

```
Extracting presentation...
Status: extracting
Created: 2024-12-17 14:30:22
```

**Status indicators:**

- **extracting** - Reading presentation content
- **parsing** - Processing text input
- **completed** - Ready for editing
- **error** - Something went wrong

### Auto-refresh

Page automatically checks status every 2 seconds until complete.

### Error Handling

If extraction fails, you'll see:
- Error message
- Possible causes
- Suggested solutions

**Common errors:**
- Permission denied - Share presentation or sign in with correct account
- Invalid URL - Check URL format
- Network error - Check internet connection

---

## Job Management

### Job History

Recent jobs displayed on main page:

**Information shown:**
- Job ID (unique identifier)
- Presentation URL or "Text input"
- Status (extracting, completed, error)
- Created timestamp
- Generated presentation link (if completed)

### Accessing Jobs

**From main page:**
- Click job ID to view details
- Click "Open Editor" to edit slides
- Click generated presentation link to view result

**Direct access:**
- URL format: `http://localhost:5000/status/<job_id>`

### Job Isolation

**Multi-user support:**
- Each user sees only their own jobs
- Jobs are linked to user session
- Complete data isolation

---

## Interactive Editor

Detailed guide: [slide-editor.md](slide-editor.md)

**Quick overview:**

After extraction completes, you're redirected to the interactive editor where you can:

- Edit slide titles and content
- Add and position images
- Reorder slides
- Delete slides
- Configure presentation settings
- Select design template
- Generate final presentation

---

## Features

### Multi-Tab Input

- **URL tab** - Import from Google Slides
- **Text tab** - Paste text content
- Switch between tabs anytime
- Input cleared when switching

### Real-Time Updates

- Job status updates automatically
- No page refresh needed
- Visual feedback for all actions

### Session Persistence

- Stay signed in between visits
- Jobs saved to database
- History preserved across sessions

### Mobile Responsive

- Works on desktop and mobile
- Touch-friendly interface
- Responsive layout

---

## Keyboard Shortcuts

**Main Interface:**
- `Ctrl+V` / `Cmd+V` - Paste URL or text
- `Enter` - Submit form (when focused)
- `Tab` - Switch between fields

**Navigation:**
- Browser back button returns to main page from editor

---

## Tips & Best Practices

### URL Import

✓ **Do:**
- Copy full URL including `/edit`
- Ensure you have access before importing
- Use presentations with consistent formatting

✗ **Don't:**
- Use shortened URLs (expand them first)
- Import presentations you don't have access to
- Submit incomplete URLs

### Text Input

✓ **Do:**
- Use clear heading markers (`#` or `##`)
- Structure content logically
- Include whitespace between slides
- Use bullet points for lists

✗ **Don't:**
- Mix multiple formatting styles
- Use overly complex formatting
- Paste raw data without structure

### Job Management

✓ **Do:**
- Use descriptive presentation titles
- Keep track of important jobs
- Clean up old test jobs periodically

✗ **Don't:**
- Create duplicate jobs unnecessarily
- Leave sensitive content in jobs
- Share job IDs with others

---

## Troubleshooting

### Can't Sign In

**Problem:** OAuth flow fails

**Solutions:**
- Clear browser cookies
- Try incognito/private mode
- Check credentials file exists
- Review OAuth consent screen setup

### Extraction Fails

**Problem:** "Permission denied" error

**Solutions:**
- Sign in with account that owns presentation
- Make presentation public ("Anyone with link")
- Share presentation with your Google account
- Check presentation URL is correct

### Jobs Not Showing

**Problem:** Can't see previously created jobs

**Possible causes:**
- Different user account
- Session expired
- Database issue

**Solutions:**
- Sign in with same Google account
- Check browser console for errors
- Verify database file exists

### Slow Extraction

**Problem:** Takes too long to extract

**Causes:**
- Large presentation (many slides)
- Complex content (many images)
- Network latency

**Normal times:**
- Small (1-5 slides): 5-10 seconds
- Medium (6-20 slides): 10-30 seconds
- Large (20+ slides): 30-60 seconds

---

## Advanced Features

### Service Account Mode

If Service Account is configured:

- Application tries OAuth first
- Falls back to Service Account for public presentations
- Transparent to user

### Debug Mode

Available in development:

```bash
# Enable debug mode
export FLASK_DEBUG=1
python web_app.py
```

**Features:**
- Detailed error messages
- Auto-reload on code changes
- Interactive debugger

---

## API Access

For programmatic access, use the Python API instead of web interface.

See: [API Reference](../developer-guide/api-reference.md)

---

## Next Steps

- **[Slide Editor Guide](slide-editor.md)** - Learn editor features
- **[Templates Guide](templates.md)** - Work with design templates
- **[Troubleshooting](troubleshooting.md)** - Solve common issues

---

**Last Updated:** December 17, 2024
