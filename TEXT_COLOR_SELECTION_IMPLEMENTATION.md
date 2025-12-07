# Text Color Selection for Selected Text Implementation

## Date
December 7, 2025

## Overview
Implemented per-selection text color formatting in the WYSIWYG editor. Users can now select text and apply color using a color picker in the formatting toolbar, similar to how Bold/Italic/Underline work.

## Implementation Details

### Frontend Changes (slide_editor.html)

#### 1. Added Color Picker to Formatting Toolbar
**Location:** Lines 295-304

Added a color input element to the formatting toolbar, positioned between the text formatting buttons (B/I/U) and the list buttons:

```html
<div class="flex gap-1 mb-2 border-b pb-2 bg-gray-50 p-2 rounded-t items-center">
    <button type="button" onclick="formatText('bold')">B</button>
    <button type="button" onclick="formatText('italic')">I</button>
    <button type="button" onclick="formatText('underline')">U</button>
    <span class="border-l mx-2"></span>
    
    <!-- NEW: Text color picker -->
    <div class="flex items-center gap-1">
        <label class="text-xs text-gray-600">Цвет:</label>
        <input type="color" id="selectionTextColor" value="#000000" 
               class="h-8 w-10 rounded border cursor-pointer" 
               onchange="applyTextColor()" 
               title="Цвет текста">
    </div>
    
    <span class="border-l mx-2"></span>
    <button type="button" onclick="formatText('insertUnorderedList')">• Список</button>
    <!-- ... -->
</div>
```

#### 2. Implemented applyTextColor() Function
**Location:** Lines 1779-1789

New function that applies the selected color to the currently selected text using the browser's `document.execCommand('foreColor')` API:

```javascript
function applyTextColor() {
    const color = document.getElementById('selectionTextColor').value;
    const editor = document.getElementById('mainTextInput');
    editor.focus();
    
    // Apply color to selected text using foreColor command
    document.execCommand('foreColor', false, color);
    
    // Update preview
    updateSlidePreview();
}
```

## User Experience

### How It Works

1. **User selects text** in the contenteditable editor
2. **User picks a color** from the color picker in the toolbar
3. **Color is applied immediately** to the selected text (or at cursor position if no selection)
4. **Preview updates** in real-time showing the colored text
5. **Color is preserved** in the HTML when saving

### Visual Appearance

The color picker appears in the formatting toolbar with:
- Small label "Цвет:" (Color)
- Compact color input (8px height, 10px width)
- Rounded border with cursor pointer
- Tooltip: "Цвет текста" (Text color)

### Key Features

✅ **Selection-based**: Works on selected text only, not entire slide
✅ **WYSIWYG**: Immediate visual feedback in editor and preview
✅ **Integrated**: Seamlessly integrated with other formatting tools
✅ **Persistent**: Colors preserved in slide data (HTML format)
✅ **Intuitive**: Follows familiar text editor paradigms

## Technical Details

### HTML Output Format

When a user applies color, the browser generates HTML like:
```html
<font color="#ff0000">Red text</font>
```

Or in some browsers:
```html
<span style="color: rgb(255, 0, 0);">Red text</span>
```

### Data Storage

Colors are stored as part of the HTML in the slide's `mainText` field:
```javascript
slides[currentSlideIndex].mainText = '<div>Normal text <font color="#ff0000">red text</font> more text</div>';
```

### Preview Rendering

The preview displays the HTML directly, showing colored text:
```javascript
document.getElementById('previewMain').innerHTML = mainTextEditor.innerHTML;
```

### Backend Conversion

When generating the presentation, the backend:
1. Detects HTML in `mainText` field
2. Calls `_html_to_plain_text()` to convert to plain text
3. **Note:** Current implementation strips color information and converts to plain text
4. Future enhancement could parse color tags and apply via Google Slides API `updateTextStyle` with text ranges

## Differences from Global Text Color

| Feature | Selection Text Color | Global Text Color (Settings Panel) |
|---------|---------------------|-----------------------------------|
| **Location** | Formatting toolbar | Settings panel (right side) |
| **Scope** | Selected text only | Entire slide text |
| **Method** | `document.execCommand('foreColor')` | CSS `style.color` |
| **Persistence** | Stored in HTML | Stored in slide settings |
| **Use Case** | Highlighting specific words/phrases | Overall slide text color theme |

## Limitations

1. **Backend Processing**: Current implementation converts HTML to plain text, losing color information in final presentation
2. **No Keyboard Shortcut**: Unlike Bold (Ctrl+B), color doesn't have a keyboard shortcut
3. **Google Slides API**: Applying per-character colors requires complex text range formatting in backend

## Future Enhancements

### Option 1: Parse HTML Colors (Advanced)
Enhance `_html_to_plain_text()` to:
1. Extract color information from HTML tags
2. Build a character-to-color mapping
3. Apply colors using Google Slides API `updateTextStyle` with specific text ranges

Example:
```python
def _parse_html_with_colors(self, html_text: str) -> dict:
    """
    Returns: {
        'text': 'plain text',
        'formatting': [
            {'start': 0, 'end': 10, 'color': '#FF0000'},
            {'start': 15, 'end': 20, 'bold': True}
        ]
    }
    """
```

### Option 2: Keep Current Behavior (Simple)
- Colors visible in editor and preview
- Converted to plain text in final presentation
- User informed that colors are for preview only

## Testing

### Manual Test Cases

1. ✅ Select text and apply color → Text changes color
2. ✅ Click color picker without selection → Color applies at cursor
3. ✅ Apply multiple different colors → Each preserves independently
4. ✅ Mix with bold/italic → All formatting works together
5. ✅ Switch slides → Colors preserved when returning
6. ✅ Preview shows colors → Real-time update works

## Compatibility

- **Browser Support**: Chrome, Firefox, Edge (modern browsers with contenteditable support)
- **Existing Features**: Compatible with all existing formatting (bold, italic, underline, lists)
- **Backward Compatible**: Old slides without colors continue to work

## Conclusion

The per-selection text color feature successfully extends the WYSIWYG editor with color formatting capabilities. Users can now apply colors to specific text selections using an intuitive color picker in the formatting toolbar, with immediate visual feedback in both the editor and preview.

The implementation follows the established pattern of using `document.execCommand` for rich text editing, maintaining consistency with other formatting features like bold, italic, and underline.
