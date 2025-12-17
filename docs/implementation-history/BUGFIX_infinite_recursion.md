# Bug Fix: Infinite Recursion in saveCurrentSlide

## Issue
```
Uncaught RangeError: Maximum call stack size exceeded
    at saveCurrentSlide (slide_editor?job_id=1c6b4632:2034:5)
```

## Root Cause
Attempted to "override" the `saveCurrentSlide` function by storing a reference and redefining it:

```javascript
// WRONG - Creates infinite recursion
const originalSaveCurrentSlide = saveCurrentSlide;
function saveCurrentSlide() {
    originalSaveCurrentSlide();  // This actually calls the NEW function, not the old one!
    triggerAutoSave();
}
```

The problem: In JavaScript, when you redefine a function in the same scope, the `const originalSaveCurrentSlide` reference captures the function *name*, not the function *value*. When the name is redefined, both references point to the new function, creating infinite recursion.

## Solution
Instead of trying to override the function, simply add the auto-save trigger directly to the original function:

```javascript
function saveCurrentSlide() {
    
    // Persist to localStorage
    saveSlides();
    
    // Trigger backend auto-save
    triggerAutoSave();
}
```

Also removed the duplicate override attempt in the `addNewSlide()` and `deleteCurrentSlide()` helper functions since they now call the updated `saveCurrentSlide()`.

## Changes Made
1. **Removed**: Lines 1989-1994 (the faulty override code)
2. **Added**: `triggerAutoSave()` call to original `saveCurrentSlide()` function
3. **Simplified**: Helper functions now rely on updated `saveCurrentSlide()`

## Files Modified
- `templates/slide_editor.html` (removed 7 lines, added 3 lines)

## Testing
- ✅ Page loads without stack overflow
- ✅ Slide editing works normally
- ✅ Auto-save triggers correctly
- ✅ No infinite recursion

## Lesson Learned
When you need to extend a function's behavior:
1. **Best**: Modify the original function directly
2. **Alternative**: Use proper closure pattern or wrapper with different name
3. **Never**: Try to "override" by redefining in the same scope
