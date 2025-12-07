# Image Editing Implementation - Google Slides Style Interactive Controls

## Context

The slide editor web application (Flask backend, vanilla JavaScript frontend) currently supports basic image positioning through coordinate inputs and simple drag functionality. This design enhances the image manipulation system to provide a professional Google Slides-like experience with visual selection boundaries, resize handles, and interactive transformations.

## User Stories

**US-1: Visual Selection Feedback**
As a user, I want to click on an image in the slide preview and see a bounding box with corner and edge handles, so I can visually identify the selected image and understand how to manipulate it.

**US-2: Interactive Resize**
As a user, I want to drag the corner handles of a selected image to resize it while maintaining aspect ratio (when locked), so I can quickly adjust image dimensions without typing numbers.

**US-3: Free Positioning**
As a user, I want to drag an image anywhere on the slide canvas, so I can position it precisely where I need it visually rather than through coordinate inputs.

**US-4: Aspect Ratio Control**
As a user, I want to toggle aspect ratio locking and see it enforced during resize, so I can maintain image proportions or freely transform as needed.

**US-5: Multi-Image Management**
As a user, I want to select between multiple images on the same slide, with only the active image showing manipulation handles, so I can work with complex layouts without visual clutter.

---

## Technical Requirements

### Frontend Architecture

#### JavaScript Library Selection

**Recommended: Interact.js**

Rationale:
- Lightweight (no canvas overhead like Fabric.js or Konva.js)
- Works directly with DOM elements (maintains existing HTML structure)
- Built-in resize and drag modifiers
- Aspect ratio preservation support
- Touch-friendly (mobile compatibility)
- No dependencies
- Well-documented API

Alternative considerations:
- Fabric.js: Requires canvas rendering (breaks existing HTML-based preview)
- Konva.js: Canvas-based, adds complexity for text overlay
- Custom implementation: High development cost, cross-browser issues

**Decision: Use Interact.js for DOM-based manipulation**

#### Integration Points

**HTML Structure Enhancement**

Current preview structure:
```
<div id="slidePreview">
  <div id="previewImagesBackground"></div>
  <div class="text-content"></div>
  <div id="previewImagesForeground"></div>
</div>
```

Enhanced structure (no changes needed to existing DOM):
- Each `<img>` element in preview layers will become an Interact.js target
- Selection handles rendered as overlay divs
- Active image receives `selected` CSS class

**Interaction States**

Image element states:
- **Idle**: No visual indicators, pointer cursor on hover
- **Selected**: Bounding box with 8 resize handles visible
- **Dragging**: Move cursor, real-time position updates
- **Resizing**: Resize cursor, real-time dimension updates with aspect lock enforcement

**Event Flow**

1. User clicks image → Image becomes selected
2. Interact.js attaches drag/resize listeners
3. User drags image body → Position updates in real-time
4. User drags corner/edge handle → Size updates with aspect ratio enforcement
5. On interaction end → Data model updates, debounced save triggers

#### Functional Specifications

**Selection Management**

Behavior:
- Single selection model (one active image at a time)
- Click on image: Select it, deselect others
- Click on slide background: Deselect all
- Double-click on image: Open properties modal

**Drag Functionality**

Requirements:
- Constrain movement within slide preview bounds
- Update position coordinates in real-time
- Snap to grid (optional enhancement: 10px grid)
- Visual feedback during drag (cursor change)

Implementation approach:
- Use Interact.js `draggable()` API
- Set `restrict: { restriction: 'parent', elementRect: { left: 0, right: 1, top: 0, bottom: 1 } }`
- Update `image.position.x` and `image.position.y` during `onmove` event

**Resize Functionality**

Requirements:
- 8 resize handles: 4 corners + 4 edges
- Corner resize: Proportional scaling when aspect ratio locked
- Edge resize: Single-axis scaling (free transform mode only)
- Minimum size constraint: 20px × 20px
- Visual handle indicators (small squares, 8px × 8px)

Implementation approach:
- Use Interact.js `resizable()` API with `edges: { left: true, right: true, bottom: true, top: true }`
- Apply `modifiers: [interact.modifiers.aspectRatio()]` when aspect lock enabled
- Update `image.size.width` and `image.size.height` during `onresize` event

**Aspect Ratio Locking**

Mechanism:
- Per-image `aspectLocked` boolean property
- When locked: Interact.js aspectRatio modifier enforces original ratio
- When unlocked: Free transformation allowed
- Toggle via properties modal checkbox
- Visual indicator: Lock icon overlay on selected image

**Keyboard Shortcuts** (Optional Enhancement)

- **Delete**: Remove selected image
- **Escape**: Deselect current image
- **Arrow keys**: Nudge position by 1px (or 10px with Shift)

---

### Backend Requirements

#### Data Model Updates

**No changes required** to existing image data structure:

```
{
  id: string,
  url: string,
  position: {x: number, y: number},  // Already in pixels
  size: {width: number, height: number},  // Already in pixels
  layer: 'background' | 'foreground',
  aspectRatio: number,
  aspectLocked: boolean
}
```

The existing model already supports all required attributes.

#### API Endpoints

**No new endpoints required**

The current workflow already handles:
- Image data embedded in slide objects
- Batch save via `/process_slides` endpoint
- Position and size stored in pixels

#### Coordinate System

**Consistent units: Pixels**

- Frontend: Store and manipulate in pixels (relative to preview container)
- Backend: Convert pixels to EMU during Google Slides API call
- Existing `_pt_to_emu()` method handles conversion

**Scaling consideration**:
- Preview dimensions may differ from final slide size (1920×1080 default)
- Maintain aspect ratio mapping between preview and final output
- No change needed: existing implementation already handles this

#### Debounced Persistence

**Strategy**: Local updates + periodic save

Flow:
1. User drags/resizes image → Update in-memory slide data immediately
2. Visual preview updates in real-time
3. On interaction end (mouseup) → Trigger debounced save
4. Debounce delay: 500ms (avoid excessive saves during rapid adjustments)

Implementation:
- JavaScript debounce utility function
- Save to `slides[currentSlideIndex].images` array
- No server call until "Generate Presentation" clicked

---

## Implementation Plan

### Phase 1: Library Integration

**Step 1.1**: Add Interact.js to project

Method: CDN link in `base.html` or `slide_editor.html`
```
<script src="https://cdn.jsdelivr.net/npm/interactjs@1.10.19/dist/interact.min.js"></script>
```

**Step 1.2**: Create image manipulation module

Location: Inline `<script>` block in `slide_editor.html` after existing scripts

Structure:
- `initializeImageInteractions()` - Setup Interact.js on all image elements
- `selectImage(imageId)` - Handle selection state
- `deselectAllImages()` - Clear selection
- `updateImageTransform(imageId, transform)` - Apply drag/resize changes

### Phase 2: Selection System

**Step 2.1**: Implement selection visual feedback

Actions:
- Add CSS classes for selected state
- Create bounding box overlay element
- Render 8 resize handle elements positioned absolutely
- Append handles to selected image container

**Step 2.2**: Wire up selection events

Events:
- Click on image → Call `selectImage(imageId)`
- Click on slide background → Call `deselectAllImages()`
- Double-click on image → Open `editImage(imageId)` modal

### Phase 3: Drag Implementation

**Step 3.1**: Configure Interact.js draggable

Settings:
- Enable inertia for smooth movement
- Restrict to parent container bounds
- Disable text selection during drag

**Step 3.2**: Handle drag events

Event handlers:
- `onstart`: Set dragging cursor
- `onmove`: Update image position in DOM and data model
- `onend`: Trigger debounced save, reset cursor

### Phase 4: Resize Implementation

**Step 4.1**: Configure Interact.js resizable

Settings:
- Enable all edges for handle creation
- Set minimum size: 20×20px
- Apply aspect ratio modifier conditionally

**Step 4.2**: Handle resize events

Event handlers:
- `onstart`: Set resizing cursor based on edge
- `onresize`: Update image dimensions in DOM and data model
- `onend`: Recalculate aspect ratio, trigger debounced save

**Step 4.3**: Aspect ratio enforcement

Logic:
- Read `aspectLocked` from image data
- If locked: Add `interact.modifiers.aspectRatio({ ratio: image.aspectRatio })`
- If unlocked: Remove aspect ratio modifier
- Update modifier when lock toggled in properties modal

### Phase 5: Multi-Image Support

**Step 5.1**: Manage selection state

Data structure:
- Global variable: `let selectedImageId = null`
- On select: Store active image ID
- On deselect: Clear variable

**Step 5.2**: Re-initialize interactions on slide change

Trigger points:
- `loadSlide(index)` function
- After `renderPreviewImages()` function
- Call `initializeImageInteractions()` to attach Interact.js to new image elements

### Phase 6: Integration with Existing Features

**Step 6.1**: Sync with properties modal

Behavior:
- Opening modal for selected image: Pre-fill current position/size
- Saving modal: Update data model and re-render
- Call `initializeImageInteractions()` after render to reattach handlers

**Step 6.2**: Sync with drag-and-drop upload

Flow:
- Image dropped → Added to data model
- `renderPreviewImages()` called
- `initializeImageInteractions()` attaches Interact.js to new image
- New image automatically selectable

**Step 6.3**: Layer management compatibility

Consideration:
- Background and foreground images in separate containers
- Interact.js works independently on each container
- Selection spans both layers (only one image selected at a time)

### Phase 7: Debouncing and Performance

**Step 7.1**: Implement debounce utility

Function signature:
```
function debounce(func, delay)
```

Usage:
- Wrap slide data save in debounce wrapper
- Delay: 500ms after last interaction event
- Cancel pending save if new interaction starts

**Step 7.2**: Optimize rendering

Techniques:
- Use CSS transforms for position updates (GPU acceleration)
- Throttle drag event processing to 60fps
- Avoid unnecessary DOM queries (cache element references)

---

## UI/UX Design Specifications

### Visual Design

**Selection Bounding Box**

Appearance:
- Border: 2px solid blue (`#3B82F6`)
- Background: None (transparent)
- Padding: 2px around image (handle clearance)

**Resize Handles**

Appearance:
- Size: 8px × 8px squares
- Background: White with blue border
- Positioned on corners and edge midpoints
- Cursor changes based on handle direction:
  - Corner: `nwse-resize` or `nesw-resize`
  - Edge: `ew-resize` or `ns-resize`

**Cursors**

States:
- Idle image: `pointer`
- Dragging: `move`
- Resizing: Direction-specific resize cursor
- Hover over handle: Resize cursor preview

**Layer Indicators** (Optional Enhancement)

Visual cue:
- Small badge on selected image showing layer (BG/FG)
- Position: Top-right corner of bounding box
- Styling: Matches existing layer badges in image list

### Interaction Feedback

**During Drag**

Visual feedback:
- Semi-transparent overlay on slide (10% opacity)
- Real-time position coordinate display (tooltip near cursor)
- Snap indicators if grid snapping enabled

**During Resize**

Visual feedback:
- Real-time dimension display (width × height tooltip)
- Aspect ratio lock icon visible if enabled
- Handle being dragged highlights (darker blue)

**Error States**

Scenarios:
- Image too small: Handles turn red when reaching minimum size
- Out of bounds: Cannot drag beyond slide edges (hard constraint)
- Invalid aspect ratio: Visual warning if lock broken (should not occur with modifiers)

---

## Testing Strategy

### Functional Tests

**Selection Tests**
- Click image → Selection appears
- Click background → Selection clears
- Click different image → Selection moves
- Double-click → Modal opens

**Drag Tests**
- Drag to new position → Coordinates update
- Drag beyond left edge → Constrained to x=0
- Drag beyond right edge → Constrained to slide width
- Drag beyond top/bottom → Constrained to slide height

**Resize Tests**
- Drag corner with aspect lock ON → Proportional resize
- Drag corner with aspect lock OFF → Free resize
- Drag edge with aspect lock ON → Only allowed direction changes
- Resize below minimum → Constrained to 20×20px
- Resize beyond slide bounds → Image stays within preview

**Aspect Ratio Tests**
- Lock checkbox checked → Modifier applied
- Lock checkbox unchecked → Free transform allowed
- Resize corner with lock ON → Ratio maintained
- Toggle lock during resize → Behavior updates immediately

**Multi-Image Tests**
- Add 3 images to slide
- Select image 1 → Only image 1 shows handles
- Select image 2 → Image 1 handles disappear, image 2 shows handles
- Deselect all → No handles visible

**Persistence Tests**
- Drag image → Wait 500ms → Data model updated
- Resize image → Wait 500ms → Data model updated
- Rapid drag/resize → Only final state saved (debounce working)
- Switch slides → Changes persisted in previous slide

### Cross-Browser Compatibility

Target browsers:
- Chrome 90+ (primary)
- Firefox 88+
- Safari 14+
- Edge 90+

Testing focus:
- Interact.js compatibility (library handles most issues)
- CSS cursor support
- Transform performance
- Touch events (mobile/tablet)

### Performance Tests

Metrics:
- Drag latency: < 16ms per frame (60fps)
- Resize rendering: No visible lag
- Multiple images (10+ on slide): Smooth interactions
- Memory usage: No leaks after repeated interactions

### Edge Cases

Scenarios:
- Empty slide (no images): Selection system inactive
- Single pixel drag: Position updates correctly
- Extremely wide/tall images: Handles remain accessible
- Image with broken URL: Placeholder handles interaction
- Rapid slide switching: No orphaned event listeners

---

## Success Criteria

**Must Have**
- ✅ Users can click an image to see selection with resize handles
- ✅ Users can drag images freely within slide bounds
- ✅ Users can resize images using corner handles with aspect ratio lock
- ✅ Aspect ratio locking enforced during resize when enabled
- ✅ Only one image selected at a time
- ✅ Changes persist in slide data model
- ✅ Existing drag-and-drop upload workflow unaffected
- ✅ Properties modal syncs with interactive manipulation

**Should Have**
- ✅ Visual feedback during drag/resize (dimensions tooltip)
- ✅ Smooth 60fps interaction performance
- ✅ Edge resize handles for single-axis scaling (free mode)
- ✅ Minimum size constraint enforced (20×20px)
- ✅ Debounced save prevents excessive data updates

**Nice to Have**
- ⭕ Keyboard shortcuts (Delete, Arrow keys)
- ⭕ Grid snapping (10px intervals)
- ⭕ Rotation handles (future enhancement)
- ⭕ Multi-select with Shift+Click (future enhancement)
- ⭕ Undo/redo for transformations

---

## Deployment Considerations

### Dependencies

**External Library**
- Interact.js v1.10.19
- Delivery: CDN link (no npm install required)
- Fallback: Download and host locally if CDN unavailable

**No Backend Changes**
- Existing Flask endpoints handle image data
- Existing Google Slides API integration unchanged
- No database schema updates required

### Backward Compatibility

**Existing Features**
- Coordinate input fields: Still functional (sync with interactive values)
- Modal-based editing: Works alongside interactive manipulation
- Drag-and-drop upload: Unaffected
- Layer management: Compatible with new selection system

**Data Migration**
- No migration needed
- Existing slides with images work immediately
- Missing `aspectLocked` defaults to `true`

### Rollback Plan

If issues arise:
1. Remove Interact.js script tag
2. Interactive manipulation stops
3. Existing coordinate inputs continue working
4. No data loss (model unchanged)

---

## Security and Privacy

**Input Validation**

Constraints:
- Position coordinates: Must be within slide bounds (client-side validation)
- Dimensions: Minimum 20px, maximum slide dimensions
- Aspect ratio: Positive number only

**Data Sanitization**

No new risks:
- Image URLs already validated during upload
- Position/size values are numbers (no injection risk)
- No user-generated HTML in manipulation layer

**Third-Party Library**

Interact.js security:
- Open source, actively maintained
- No known vulnerabilities in v1.10.19
- Loaded from trusted CDN (jsDelivr)
- Subresource Integrity (SRI) hash recommended for production

---

## Future Enhancements

**Advanced Manipulation**
- Rotation control (circular handle)
- Flip horizontal/vertical buttons
- Crop tool integration

**Collaboration Features**
- Real-time cursor indicators for multi-user editing
- Lock mechanism to prevent simultaneous edits

**Accessibility**
- Keyboard-only navigation
- Screen reader announcements for position/size changes
- High contrast mode for selection indicators

**Performance Optimization**
- Virtual rendering for 50+ images per slide
- Web Worker for transform calculations
- Hardware acceleration hints

---

## Conclusion

This design implements a professional Google Slides-style image manipulation experience using Interact.js for interactive drag and resize functionality. The approach maintains the existing data model, requires no backend changes, and integrates seamlessly with current features. By leveraging a proven DOM-based library instead of building from scratch, the implementation achieves cross-browser compatibility, touch support, and production-ready performance with minimal development effort.

The single-responsibility focus on image manipulation keeps the design scoped and deliverable, while the architecture allows for future enhancements like rotation, cropping, and collaborative editing without major refactoring.
