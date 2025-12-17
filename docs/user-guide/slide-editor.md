# Slide Editor Guide

Complete guide to the interactive WYSIWYG slide editor.

---

## Overview

The Slide Editor is a powerful WYSIWYG (What You See Is What You Get) interface for editing presentation content before applying design templates.

**Key features:**
- Edit titles and text content
- Add and manage images
- Reorder slides
- Delete slides
- Real-time preview
- Configure presentation settings

---

## Accessing the Editor

The editor opens automatically after:
1. Submitting a presentation URL
2. Pasting text content
3. Successful content extraction

**Direct access:** `http://localhost:5000/editor/<job_id>`

---

## Editor Interface

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  AI Presentolog                    user@email.com  Logout│
├─────────────────────────────────────────────────────────┤
│  ← Back to Main                                          │
├─────────────────────────────────────────────────────────┤
│  Slide 1 of 5                           [+ Add Slide]   │
├───────────────────┬─────────────────────────────────────┤
│  [Slide 1]        │  Title: [________________]          │
│  [Slide 2]        │                                     │
│  [Slide 3]        │  Main Content:                      │
│  [Slide 4]        │  ┌──────────────────────────┐      │
│  [Slide 5]        │  │                          │      │
│                   │  │  [Edit area]             │      │
│                   │  │                          │      │
│                   │  └──────────────────────────┘      │
│                   │                                     │
│                   │  [ Upload Image ]  [ Add as BG ]   │
│                   │                                     │
│                   │  [Delete Slide]                     │
├───────────────────┴─────────────────────────────────────┤
│  Settings:                                               │
│  Template: [default ▼]  Color: [Blue ▼]  Font: [Arial ▼]│
│                                                          │
│  [Создать презентацию] (Create Presentation)            │
└─────────────────────────────────────────────────────────┘
```

---

## Editing Slides

### Edit Slide Title

1. **Locate** the "Title" field (large text box at top)
2. **Click** in the field
3. **Type** your new title
4. Changes save automatically

**Tips:**
- Keep titles concise (5-8 words)
- Use title case
- Avoid special characters

### Edit Main Content

1. **Locate** the "Main Content" text area
2. **Click** in the area
3. **Edit** text as needed

**Formatting options:**
- Plain text (recommended)
- Bullet points (use `-` or `*`)
- Numbered lists (use `1.`, `2.`, etc.)
- Line breaks (press Enter)

**Example:**
```
Main points:
- First important point
- Second key idea
- Third consideration

Action items:
1. Review the data
2. Make decision
3. Communicate results
```

### Content Types

The editor recognizes:
- **Regular text** - Paragraphs
- **Lists** - Bullets and numbered
- **Emphasis** - Bold/italic (if in original)
- **Headings** - Title vs. body text

---

## Working with Images

### Upload Image

1. **Click** "Upload Image" button
2. **Select** image file from computer
3. Image appears in slide content area

**Supported formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)

**Recommended:**
- Size: Under 5MB
- Resolution: 1920x1080 or smaller
- Aspect ratio: 16:9 for full slides

### Position Image

After upload:
1. Image appears in edit area
2. **Drag** to reposition
3. **Resize** using handles (if available)

### Background Image

To use image as slide background:

1. Upload image
2. **Click** "Add as Background" button
3. Image fills entire slide background

**Note:** Background images work best:
- High resolution
- Low contrast (for text readability)
- Relevant to slide content

### Remove Image

1. Select image in editor
2. Delete or click remove button
3. Image removed from slide

---

## Slide Management

### Navigate Slides

**Sidebar list:**
- Click any slide thumbnail to switch
- Current slide highlighted

**Keyboard shortcuts:**
- `←` Left arrow - Previous slide
- `→` Right arrow - Next slide
- `Home` - First slide
- `End` - Last slide

### Add New Slide

1. **Click** "+ Add Slide" button
2. New blank slide created
3. Appears at end of presentation

**Default structure:**
- Empty title
- Empty main content
- No images

### Reorder Slides

**Drag and Drop:**
1. Click and hold slide in sidebar
2. Drag to new position
3. Release to drop

**Alternative (some implementations):**
- Up/Down arrows next to slides
- Move to position input

### Delete Slide

1. **Navigate** to slide to delete
2. **Click** "Delete Slide" button
3. **Confirm** deletion (if prompted)

**Warning:** Deletion is immediate and cannot be undone in editor!

### Duplicate Slide (if available)

1. Navigate to slide
2. Click "Duplicate" button
3. Copy appears after current slide

---

## Presentation Settings

Located at bottom of editor:

### Template Selection

**Dropdown menu** with available templates:
- Default
- Corporate Blue
- (Custom templates if added)

**Changes:**
- Affects final generated presentation
- Does not change editor view
- Can be changed before each generation

### Color Scheme

**Options may include:**
- Blue
- Red
- Green
- Gray
- Custom

**Note:** Available colors depend on selected template

### Font Selection

**Common fonts:**
- Arial
- Calibri
- Times New Roman
- Georgia

**Recommendations:**
- Sans-serif (Arial, Calibri) for screens
- Serif (Times, Georgia) for print

### Other Settings (if available)

- Slide size (16:9, 4:3)
- Font size adjustments
- Spacing preferences

---

## Generating Presentation

### Ready to Generate

When satisfied with edits:

1. **Review** all slides one more time
2. **Configure** settings (template, colors, fonts)
3. **Click** "Создать презентацию" (Create Presentation)

### Generation Process

1. **Processing** - Creating new Google Slides presentation
2. **Applying** - Applying selected template
3. **Finalizing** - Saving to your Google Drive

**Wait time:** 10-60 seconds depending on:
- Number of slides
- Number of images
- Complexity of content

### Accessing Result

When complete:
- Link to new presentation appears
- Click link to open in Google Slides
- Presentation saved to your Google Drive

**Result:**
- New presentation with your content
- Template design applied
- Editable in Google Slides

---

## Tips & Best Practices

### Content Editing

✓ **DO:**
- Keep text concise
- Use bullet points for clarity
- Proofread before generating
- Test with one slide first

✗ **DON'T:**
- Overcrowd slides with text
- Use all caps (looks like shouting)
- Mix too many fonts/styles
- Forget to preview

### Images

✓ **DO:**
- Use high-quality images
- Choose relevant visuals
- Optimize file size
- Check licensing/permissions

✗ **DON'T:**
- Use blurry images
- Stretch/distort images
- Use copyrighted images without permission
- Upload huge files (slow upload)

### Slide Organization

✓ **DO:**
- Start with title slide
- Logical flow of content
- Group related topics
- End with summary/CTA

✗ **DON'T:**
- Random order
- Too many slides (aim for <20)
- Duplicate content
- Skip introduction slide

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+S` / `Cmd+S` | Save (auto-save already active) |
| `Ctrl+Z` / `Cmd+Z` | Undo (in text fields) |
| `Ctrl+Y` / `Cmd+Y` | Redo |
| `←` / `→` | Navigate slides |
| `Home` / `End` | First/Last slide |
| `Tab` | Move to next field |
| `Shift+Tab` | Move to previous field |
| `Esc` | Deselect/Cancel |

---

## Advanced Features

### Raw Text Mode

Some editors support raw text editing:
- Edit slide content as plain text
- Useful for bulk changes
- Preserves exact formatting

### Batch Operations

If available:
- Select multiple slides
- Apply changes to all
- Bulk delete/reorder

### Preview Mode

Toggle between:
- Edit mode (full controls)
- Preview mode (how it will look)

### Version History (Future)

Planned feature:
- Save different versions
- Restore previous state
- Compare changes

---

## Troubleshooting

### Can't Edit Text

**Problem:** Fields are not editable

**Solutions:**
- Click directly in field
- Check JavaScript is enabled
- Try different browser
- Refresh page

### Changes Not Saving

**Problem:** Edits disappear

**Solutions:**
- Don't close tab during editing
- Check session hasn't expired
- Verify database connection
- Check browser console for errors

### Images Not Uploading

**Problem:** Upload fails

**Causes:**
- File too large (>5MB)
- Unsupported format
- Network error
- Browser permissions

**Solutions:**
- Compress/resize image
- Convert to JPEG/PNG
- Check internet connection
- Allow file uploads in browser

### Slides Out of Order

**Problem:** Drag-and-drop not working

**Solutions:**
- Try manual reorder (arrows/numbers)
- Refresh and try again
- Use different browser
- Check mouse/trackpad

### Generation Fails

**Problem:** "Create Presentation" errors

**Solutions:**
- Check all required fields filled
- Verify internet connection
- Review logs for specific error
- Try with simpler content first

---

## Saving Your Work

### Auto-Save

Editor automatically saves:
- Every few seconds
- After each change
- To session database

**What's saved:**
- Slide content (titles, text)
- Slide order
- Images (references)
- Settings selections

### Manual Save

Not required (auto-save handles it), but you can:
- Navigate away and come back
- Job ID preserved
- Return via history

### Recovering Work

If browser closes:
1. Sign in again
2. Go to main page
3. Find job in history
4. Click "Edit" to resume

**Session duration:** 24 hours (default)

---

## Next Steps

After generating presentation:

1. **Open in Google Slides** - Make final adjustments
2. **Share** - With collaborators or viewers
3. **Present** - Use presentation mode
4. **Export** - PDF, PowerPoint, etc.

---

## Related Guides

- **[Web Interface](web-interface.md)** - Main application interface
- **[Templates](templates.md)** - Understanding design templates
- **[Troubleshooting](troubleshooting.md)** - Solve common issues

---

**Last Updated:** December 17, 2024
