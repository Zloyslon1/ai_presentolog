# Bug Fix: defaultTextPosition Undefined Error

## Issue
```
Uncaught TypeError: Cannot read properties of undefined (reading 'vertical')
at updatePreviewStyles (slide_editor?job_id=1c6b4632:972:63)
```

## Root Cause
When loading presentation settings from the backend, the `presentationSettings` object could be replaced with incomplete data that doesn't include the `defaultTextPosition` property. This caused multiple functions to fail when trying to access `presentationSettings.defaultTextPosition.vertical` and `.horizontal`.

## Functions Affected
1. `updatePreviewStyles()` - Line 930
2. `saveCurrentSlide()` - Lines 746-747
3. `applyToAll()` - Line 977
4. `initializeSlideData()` - Line 1078

## Solution

### 1. Fixed Backend Data Loading
In `loadFromBackend()` function, changed from direct assignment to safe merging:

**Before:**
```javascript
if (data.settings) {
    presentationSettings = data.settings;
}
```

**After:**
```javascript
if (data.settings) {
    // Merge settings while preserving default structure
    presentationSettings = {
        pageOrientation: data.settings.pageOrientation || 'horizontal',
        defaultFont: data.settings.defaultFont || 'Arial',
        defaultFontSize: data.settings.defaultFontSize || 18,
        defaultTextPosition: {
            vertical: data.settings.defaultTextPosition?.vertical || 'top',
            horizontal: data.settings.defaultTextPosition?.horizontal || 'left'
        }
    };
}
```

### 2. Added Safety Checks in All Accessing Functions

Added defensive initialization before accessing `defaultTextPosition`:

```javascript
// Ensure defaultTextPosition exists
if (!presentationSettings.defaultTextPosition) {
    presentationSettings.defaultTextPosition = {
        vertical: 'top',
        horizontal: 'left'
    };
}
```

This was added to:
- `updatePreviewStyles()`
- `saveCurrentSlide()`
- `applyToAll()`
- `initializeSlideData()`

## Testing
- ✅ Page loads without errors
- ✅ Settings properly merged from backend
- ✅ Text positioning works correctly
- ✅ All slide operations function normally

## Files Modified
- `templates/slide_editor.html` (42 lines added across 5 functions)

## Prevention
The fix ensures that `presentationSettings.defaultTextPosition` always exists with valid default values, preventing similar errors in the future.
