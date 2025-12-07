# Image Upload Solution for Google Slides API 2KB URL Limit

## Problem
When creating presentations with images, the Google Slides API has a strict 2KB limit on URLs in the `createImage` request. Base64-encoded data URLs typically exceed this limit, causing the following error:

```
Invalid requests[X].createImage: The URL must be 2K bytes or less.
```

## Solution
Automatically upload large image data URLs to Google Drive and use the public Drive URLs instead. This approach:

1. **Detects data URLs** - Identifies when an image URL starts with `data:`
2. **Uploads to Drive** - Converts base64 to binary and uploads to Google Drive
3. **Makes public** - Sets Drive file permissions to "anyone with link can view"
4. **Returns short URL** - Uses Drive's direct view URL format (much shorter than 2KB)

## Implementation Details

### Modified Files
- **`presentation_builder.py`** - Added Drive upload functionality

### New Methods

#### `_upload_image_to_drive(data_url, file_name)`
Uploads a base64-encoded data URL to Google Drive:
- Parses data URL to extract MIME type and binary data
- Uploads to Drive with proper MIME type
- Sets public permissions
- Returns short Drive URL: `https://drive.google.com/uc?export=view&id={file_id}`

#### Modified `_add_image(slide_id, image_data, index)`
Now automatically detects and handles data URLs:
```python
if url.startswith('data:'):
    # Upload to Drive instead of using data URL directly
    file_name = f"slide_{slide_id}_image_{index}"
    url = self._upload_image_to_drive(url, file_name)
```

### Configuration
The Google Drive API scope was already included in `config/config.json`:
```json
"scopes": [
  "https://www.googleapis.com/auth/presentations",
  "https://www.googleapis.com/auth/drive.file"
]
```

### Supported Image Formats
- PNG (image/png)
- JPEG (image/jpeg, image/jpg)
- GIF (image/gif)
- WebP (image/webp)

## Benefits

1. **Transparent handling** - Users don't need to change how they add images
2. **No size limits** - Drive handles large images without issues
3. **Persistent URLs** - Drive URLs remain valid permanently
4. **Better performance** - Shorter URLs reduce batch request size
5. **Logging** - Full tracking of uploads in logs

## Usage

No changes required in client code! The system automatically:
- Detects when an image is a data URL
- Uploads it to Google Drive
- Uses the Drive URL in the presentation

Example from slide editor:
```javascript
// Add image with data URL (as before)
currentSlide.images.push({
    url: "data:image/png;base64,iVBORw0KG...",  // Long data URL
    position: {x: 100, y: 100},
    size: {width: 200, height: 150}
});

// System automatically uploads to Drive before creating presentation
```

## Logging

The system logs all image uploads:
```
INFO: Detected data URL for image img_slide_1_0, uploading to Drive
INFO: Uploaded image to Google Drive (file_id: 1abc..., size: 45123 bytes)
INFO: Image uploaded, using Drive URL
```

## Error Handling

If Drive upload fails:
- Detailed error logged with stack trace
- Raises `BuilderError` with descriptive message
- Prevents presentation creation with broken images

## Performance Considerations

- Each image upload is a separate API call
- Multiple images are uploaded sequentially
- Consider rate limits for presentations with many images
- Drive API quota: 1,000,000,000 queries per day (more than sufficient)

## Future Enhancements

Potential improvements:
1. **Parallel uploads** - Upload multiple images concurrently
2. **Caching** - Reuse uploaded images if content matches
3. **Compression** - Reduce image file size before upload
4. **Folder organization** - Group presentation images in Drive folders
5. **Cleanup** - Option to delete temporary Drive files after presentation creation

## Date Implemented
December 7, 2025
