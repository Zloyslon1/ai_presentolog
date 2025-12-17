# Templates Guide

Working with design templates in AI Presentolog.

---

## What Are Templates?

Templates are JSON-based design definitions that control the visual appearance of your presentations:

- **Colors** - Brand colors and themes
- **Typography** - Fonts, sizes, and styles
- **Layouts** - Slide structure and element positioning
- **Styles** - Text formatting and emphasis

Templates transform content-focused slides into professionally designed presentations while preserving your content.

---

## Available Templates

### Default Template

**Description:** Simple, clean black and white design

**Best for:**
- Academic presentations
- Minimalist style
- Text-heavy content
- Print-friendly slides

**Colors:**
- Primary: Black (#000000)
- Secondary: White (#FFFFFF)
- Accent: Dark Gray (#333333)

**File:** `presentation_design/templates/designs/default.json`

### Corporate Blue Template

**Description:** Professional blue color scheme

**Best for:**
- Business presentations
- Corporate communications
- Professional settings
- Client presentations

**Colors:**
- Primary: Blue (#1E3A8A)
- Secondary: Light Blue (#DBEAFE)
- Accent: Gold (#F59E0B)

**File:** `presentation_design/templates/designs/corporate_blue.json`

---

## Using Templates

### In Web Interface

1. **After extraction**, open the interactive editor
2. **Edit your slides** as needed
3. **Configure settings** at the bottom:
   - Select **Template** from dropdown
   - Choose color scheme (if applicable)
   - Select font preferences
4. **Click "Создать презентацию"** (Create Presentation)
5. Template applied automatically

### In Python API

```python
from presentation_design.main import process_presentation

result = process_presentation(
    presentation_url="https://docs.google.com/presentation/d/YOUR_ID/edit",
    template_name="corporate_blue"  # or "default"
)
```

### List Available Templates

```bash
python -m presentation_design.main --list-templates
```

Output:
```
Available templates:
  - default
  - corporate_blue
```

---

## Template Components

### 1. Metadata

Basic template information:

```json
{
  "metadata": {
    "name": "Template Name",
    "version": "1.0",
    "description": "Template description",
    "author": "Author Name"
  }
}
```

### 2. Colors

Color palette definition:

```json
{
  "colors": {
    "primary": "#1E3A8A",
    "secondary": "#DBEAFE",
    "accent": "#F59E0B",
    "background": "#FFFFFF",
    "text": "#000000"
  }
}
```

**Color roles:**
- `primary` - Main brand color (headings, important elements)
- `secondary` - Supporting color (backgrounds, accents)
- `accent` - Highlight color (call-to-actions, emphasis)
- `background` - Slide background
- `text` - Main text color

### 3. Typography

Font and text styling:

```json
{
  "typography": {
    "title": {
      "font": "Arial",
      "size": 44,
      "bold": true,
      "color": "primary"
    },
    "heading": {
      "font": "Arial",
      "size": 32,
      "bold": true,
      "color": "primary"
    },
    "body": {
      "font": "Arial",
      "size": 18,
      "bold": false,
      "color": "text"
    }
  }
}
```

**Typography roles:**
- `title` - Presentation title (title slide)
- `heading` - Slide titles
- `body` - Main content text
- `caption` - Small text, footnotes

### 4. Layouts

Slide structure definitions:

```json
{
  "layouts": {
    "title_slide": {
      "type": "title",
      "elements": {
        "title": {"position": "center", "size": "large"},
        "subtitle": {"position": "below_title", "size": "medium"}
      }
    },
    "content_slide": {
      "type": "content",
      "elements": {
        "title": {"position": "top", "size": "medium"},
        "body": {"position": "main", "size": "normal"}
      }
    }
  }
}
```

---

## Choosing a Template

### Considerations

**1. Purpose:**
- Academic → Default
- Business → Corporate Blue
- Creative → (Create custom)

**2. Audience:**
- Formal → Corporate Blue
- Casual → Default
- Mixed → Default

**3. Content Type:**
- Text-heavy → Default (better readability)
- Visual-heavy → Corporate Blue (more visual interest)
- Data-focused → Either works

**4. Brand Guidelines:**
- Match company colors → Create custom template
- No specific branding → Use default templates

### Switching Templates

You can try different templates:

1. Generate presentation with Template A
2. If not satisfied, go back to editor
3. Change template to Template B
4. Generate again
5. Compare results

**Note:** Each generation creates a new presentation in Google Slides

---

## Template Features

### Color Adaptation

Templates intelligently apply colors:
- Headings use primary color
- Body text uses text color
- Backgrounds use background color
- Accents highlight important items

### Font Consistency

All fonts are consistent within template:
- Professional appearance
- Easy to read
- Print-friendly

### Responsive Layouts

Layouts adapt to content:
- Short titles → Larger text
- Long titles → Adjusted sizing
- Lists → Proper spacing
- Images → Optimal positioning

---

## Creating Custom Templates

Want to create your own template?

See: **[Template Development Guide](../developer-guide/template-development.md)**

**Quick steps:**

1. Copy existing template JSON file
2. Modify colors, fonts, and layouts
3. Save with new name in `presentation_design/templates/designs/`
4. Validate with template validator
5. Use in presentations

---

## Template Best Practices

### DO:

✓ Choose template based on audience and purpose  
✓ Keep colors consistent with brand (if applicable)  
✓ Use readable fonts (Arial, Calibri, etc.)  
✓ Test template with sample content first  
✓ Consider accessibility (color contrast)

### DON'T:

✗ Mix multiple templates in one presentation  
✗ Use too many colors  
✗ Choose decorative fonts for body text  
✗ Sacrifice readability for aesthetics  
✗ Ignore brand guidelines

---

## Troubleshooting Templates

### Template Not Found

**Error:** `Template 'xyz' not found`

**Solution:**
1. Check template name spelling
2. List available templates:
   ```bash
   python -m presentation_design.main --list-templates
   ```
3. Verify template file exists in designs folder

### Template Loading Error

**Error:** Invalid JSON or validation error

**Solution:**
1. Open template file in text editor
2. Validate JSON syntax (use online validator)
3. Check all required fields are present
4. Compare with working template

### Colors Not Applied

**Problem:** Presentation doesn't use template colors

**Causes:**
- Template color definitions incorrect
- Original presentation has manual color overrides
- Template application failed

**Solutions:**
1. Check template color hex codes are valid
2. Review logs for errors
3. Try with different template
4. Create new presentation instead of modifying existing

---

## Advanced Usage

### Template Inheritance

Currently not supported, but planned for future versions.

### Dynamic Templates

Templates are static JSON files. For dynamic templates (e.g., based on user input), modify template JSON programmatically before processing.

### Template Validation

Validate template before use:

```python
from presentation_design.templates.template_validator import TemplateValidator

validator = TemplateValidator()
is_valid = validator.validate_template("path/to/template.json")
```

---

## Next Steps

- **[Web Interface Guide](web-interface.md)** - Using templates in web UI
- **[Template Development](../developer-guide/template-development.md)** - Create custom templates
- **[Slide Editor](slide-editor.md)** - Edit content before applying template

---

**Last Updated:** December 17, 2024
