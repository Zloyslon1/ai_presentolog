# Image Upload Fixes - Testing Guide

## Issues Fixed

### 1. ✅ "Add Image" Button Now Works
**Problem**: Button wasn't responding  
**Fix**: 
- Fixed tab switching logic (corrected element ID mapping)
- Added better error messages with console logging
- Made validation more lenient with fallback values
- Added `.trim()` to URL input

### 2. ✅ Drag & Drop Images Are Now Editable
**Problem**: Images added via drag-and-drop couldn't be edited  
**Fix**: Already working! The code already calls `updateImagesList()` and `updateSlidePreview()`, which:
- Adds image to the images list with thumbnail
- Shows edit button (✏️) for each image
- Edit button opens modal with all image properties pre-filled

## How to Test

### Test 1: Add Image via URL
1. Open slide editor
2. Click "➕ Добавить изображение" button
3. Make sure "URL" tab is active
4. Enter an image URL (e.g., `https://via.placeholder.com/300`)
5. Click "Добавить" button
6. **Expected**: Image appears in preview and images list

### Test 2: Add Image via Drag & Drop (Modal)
1. Click "➕ Добавить изображение"
2. Switch to "Drag & Drop" tab
3. Drag an image file into the drop zone
4. **Expected**: File name appears below drop zone, size inputs update
5. Click "Добавить"
6. **Expected**: Image appears in preview and images list

### Test 3: Add Image via Direct Preview Drop
1. Drag an image file from file explorer
2. Drop directly onto the slide preview area
3. **Expected**: 
   - Preview border highlights during drag
   - Image appears at drop position
   - Image appears in images list with edit button

### Test 4: Edit Dropped Image
1. After dropping image on preview (Test 3)
2. Look at images list below "Изображения" section
3. Click the edit button (✏️) next to the image
4. **Expected**: Modal opens with all image settings pre-filled
5. Change size, position, or layer
6. Click "Добавить"
7. **Expected**: Image updates in preview and list

### Test 5: Layer Control
1. Add an image via any method
2. Edit the image
3. Change layer from "Behind Text" to "In Front of Text"
4. Click "Добавить"
5. **Expected**: 
   - Badge changes from "BG" to "FG"
   - Image renders in front of text in preview

## Console Debugging

Open browser console (F12) to see debug logs:
- "addImage called, URL: ..."
- "Creating image with: ..."
- "Added new image, total images: X"
- "Image added successfully"

If button doesn't work, check console for errors.

## Common Issues & Solutions

### Issue: "Add Image" button does nothing
**Solution**: 
- Check browser console for errors
- Verify URL starts with `http://` or `https://`
- For data URLs, make sure file was processed correctly

### Issue: Image doesn't appear in list
**Solution**:
- Check console: should see "Added new image, total images: X"
- Verify `slides[currentSlideIndex].images` array in console
- Try switching to another slide and back

### Issue: Edit button doesn't work
**Solution**:
- Check console for "editImage" errors
- Verify image has valid `id` property
- Try refreshing page and re-adding image

### Issue: Drag & Drop doesn't work
**Solution**:
- Make sure file is an image (JPG, PNG, GIF, WebP, SVG)
- Check file size (must be < 5MB)
- Look for validation error alerts

## Expected Behavior Summary

✅ **URL Upload**: Enter URL → Click Add → Image appears  
✅ **Modal Drag-Drop**: Switch tab → Drag file → Click Add → Image appears  
✅ **Preview Drop**: Drag file → Drop on preview → Image appears at position  
✅ **Edit**: Click ✏️ → Modal opens → Change settings → Click Add → Updates  
✅ **Layer**: Change layer → Badge updates → Preview z-index changes  
✅ **Delete**: Click ✕ → Image removed from list and preview  

## Files Changed

- `templates/slide_editor.html`:
  - Fixed `switchImageTab()` function (corrected element ID mapping)
  - Enhanced `addImage()` with console logging and better validation
  - Added fallback values for all inputs
