# Full-Screen Editor Layout Enhancement

## Objective

Transform the slide editor to utilize the full browser viewport while maintaining fixed-width sidebars for slides and settings panels, with intelligent font scaling based on the preview window dimensions.

## Current State Analysis

### Existing Layout Structure
- Three-column grid layout using Tailwind's 12-column system:
  - Left panel (Slides): `col-span-2` (2/12 width)
  - Center panel (Editor): `col-span-8` (8/12 width)
  - Right panel (Settings): `col-span-2` (2/12 width)
- Container wrapper: `mx-auto px-4` (centered with padding)
- Preview canvas: Fixed aspect ratio (16:9 or 9:16) with relative sizing

### Current Constraints
- Editor is centered with horizontal padding, not utilizing full viewport width
- Font sizes are absolute pixel values (e.g., `text-3xl`, `44px` for titles)
- No responsive scaling based on preview canvas dimensions

## Design Requirements

### 1. Full-Screen Layout
The editor interface must expand to utilize the entire browser viewport width and height.

**Layout Transformation:**
- Remove container horizontal centering and padding constraints
- Maintain three-panel structure with new sizing strategy:
  - Left panel (Slides): Fixed pixel width
  - Right panel (Settings): Fixed pixel width
  - Center panel (Editor): Flexible width filling remaining space

**Panel Sizing Strategy:**
| Panel | Current | New Approach |
|-------|---------|--------------|
| Slides (Left) | col-span-2 (16.67%) | Fixed width (e.g., 280px) |
| Settings (Right) | col-span-2 (16.67%) | Fixed width (e.g., 280px) |
| Editor (Center) | col-span-8 (66.67%) | Flexible (calc(100vw - 560px - gaps)) |

### 2. Fixed Sidebar Dimensions
Both the Slides list and Settings panels must maintain consistent, comfortable widths regardless of viewport size.

**Recommended Dimensions:**
- Minimum width: 240px (prevents cramping on smaller screens)
- Optimal width: 280px (balances readability and space efficiency)
- Maximum width: 320px (prevents excessive space on large monitors)

**Responsive Behavior:**
- Sidebars retain fixed pixel width at all viewport sizes
- Vertical scrolling enabled when content exceeds viewport height
- No horizontal scrolling within sidebars

### 3. Responsive Font Scaling

Font sizes for preview elements must dynamically adjust based on the preview canvas dimensions to maintain visual consistency.

**Scaling Strategy:**

The preview canvas size varies based on:
- Viewport dimensions (full-screen mode)
- Orientation setting (16:9 vs 9:16)
- Browser window dimensions

**Scaling Formula Approach:**

Calculate scale factor based on preview canvas width:
```
scaleFactor = (currentPreviewWidth / baselinePreviewWidth)
```

Where:
- `baselinePreviewWidth`: Reference width at which default font sizes are optimal (e.g., 800px)
- `currentPreviewWidth`: Actual rendered width of the preview canvas

**Scaled Font Calculations:**

| Element | Base Size (PT) | Scaling Application |
|---------|----------------|---------------------|
| Title | User-selected (24-60 PT) | baseSize × scaleFactor |
| Main Text | User-selected (12-32 PT) | baseSize × scaleFactor |
| Secondary Text | Derived from main text | mainTextSize × 0.7 × scaleFactor |

**Constraints:**
- Minimum scaled size: 10px (readability threshold)
- Maximum scaled size: 120px (prevents overflow on ultra-wide displays)
- Re-calculate on window resize events
- Re-calculate on orientation change

**Font Size Persistence:**
- Store user-selected base font sizes (in PT) unchanged
- Apply scaling only for preview rendering
- Actual presentation generation uses base sizes

### 4. Preview Canvas Behavior

**Sizing Logic:**
- Horizontal orientation (16:9):
  - Width: Fill available center panel width (minus padding)
  - Height: Auto-calculated via aspect ratio
  - Max-height constraint: Prevent vertical overflow
  
- Vertical orientation (9:16):
  - Height: Fill available viewport height (minus header/controls)
  - Width: Auto-calculated via aspect ratio
  - Center horizontally within available space

**Aspect Ratio Maintenance:**
- Use CSS `aspect-ratio` property for automatic dimension calculation
- Fallback strategy for older browsers (manual calculation via JavaScript)

## Implementation Approach

### Layout Structure Changes

**Container Modification:**
Transform the main container from centered with padding to full-viewport utilization.

Current structure:
```
<div class="mx-auto px-4">
  <div class="grid grid-cols-12 gap-6">
    ...
  </div>
</div>
```

New structure concept:
- Remove `mx-auto` (horizontal centering)
- Remove `px-4` (horizontal padding)
- Apply full-width container styling
- Implement CSS Grid or Flexbox for three-panel layout with fixed-flexible-fixed pattern

**Grid Layout Configuration:**
Replace Tailwind's fractional column system with explicit width definitions:
- Use CSS Grid with `grid-template-columns`
- Pattern: `[fixed-width] [1fr] [fixed-width]`
- Apply gap spacing between panels

### Responsive Scaling Logic

**Scale Factor Calculation:**

Monitor preview canvas dimensions via:
- ResizeObserver API (modern approach)
- Window resize event listener (fallback)

Trigger re-calculation when:
- Window resizes
- Orientation changes (via `applyPageOrientation()`)
- Sidebar panels toggle (if implemented in future)

**Font Size Application:**

Modify `updatePreviewStyles()` function to:
1. Retrieve user-selected base font sizes
2. Calculate current preview canvas width
3. Compute scale factor
4. Apply scaled sizes to preview elements
5. Clamp results within min/max bounds

**Update Trigger Points:**
- Initial page load
- Window resize (debounced to avoid performance issues)
- Slide navigation
- Font size slider adjustments
- Orientation toggle

### Viewport Height Utilization

**Header and Controls:**
- Calculate fixed height of top header section
- Calculate fixed height of slide controls within editor panel
- Reserve space for modals and tooltips (z-index layering)

**Available Height Calculation:**
```
availableHeight = viewportHeight - headerHeight - controlsHeight - gaps
```

**Panel Height Allocation:**
- Sidebars: `height: calc(100vh - headerHeight - margins)`
- Center panel: Same calculation
- Preview canvas: Constrained by aspect ratio and available space

### Performance Considerations

**Debouncing Resize Events:**
Prevent excessive re-calculations during window resize by implementing debounce mechanism:
- Debounce delay: 150-200ms (balance responsiveness and performance)
- Cancel pending calculations on rapid successive events

**Scaling Calculation Optimization:**
- Cache baseline dimensions to avoid repeated DOM queries
- Use CSS transforms for scaling where possible (hardware-accelerated)
- Limit precision of calculated values (e.g., round to nearest 0.1px)

## User Experience Impact

### Visual Consistency
- Preview canvas fills available space efficiently
- Text remains proportionally sized relative to canvas
- No jarring size jumps during window resize (smooth transitions)

### Workflow Preservation
- Slides list maintains comfortable width for thumbnail previews
- Settings panel retains adequate space for all controls
- Editor panel maximizes preview size for detailed editing

### Responsive Behavior
| Viewport Width | Behavior |
|----------------|----------|
| < 1024px | Consider stacked layout (out of scope - mobile optimization) |
| 1024px - 1440px | Standard three-panel with minimal sidebar widths |
| 1440px - 1920px | Optimal experience with 280px sidebars |
| > 1920px | Ultra-wide support - preview scales proportionally |

## Edge Cases and Constraints

### Minimum Viewport Requirements
- Minimum supported width: 1024px (below this, layout may degrade)
- Minimum supported height: 600px (prevents vertical cramping)
- Below minimums: Display warning message or force scrollbars

### Aspect Ratio Conflicts
When vertical orientation (9:16) is selected on a short viewport:
- Prioritize height constraint to prevent content overflow
- Allow horizontal scrolling if preview exceeds center panel width
- Provide visual indicator when preview is cropped/scrolled

### Font Scaling Limits
Prevent unreadable or oversized text:
- Enforce minimum 10px for all text elements
- Enforce maximum 120px for title elements
- Disable scaling if user explicitly sets fixed sizes (future enhancement)

### Browser Compatibility
- Modern browsers: Use ResizeObserver for efficient dimension tracking
- Legacy browsers (IE11, older Edge): Fallback to window resize events
- CSS aspect-ratio property not supported: JavaScript-based dimension calculation

## Interaction with Existing Features

### Page Orientation Toggle
The `applyPageOrientation()` function must trigger font scaling recalculation:
- Orientation change modifies preview dimensions significantly
- Scale factor must be recomputed immediately after orientation change
- Smooth transition animation between orientations (optional enhancement)

### Font Size Controls
User adjustments via sliders should:
1. Update base font size values (persist to data model)
2. Trigger scaling recalculation
3. Apply scaled result to preview
4. No change to generation logic (uses base values)

### Sidebar Interactions
- Slides list scrolling should not affect layout calculations
- Settings panel controls remain accessible at all viewport sizes
- Modals (image, table, arrow) overlay entire viewport

### Image, Table, and Arrow Positioning
Coordinate systems for positioned elements:
- Continue using absolute pixel positioning relative to preview canvas
- Coordinates remain independent of scaling
- Visual representation scales with preview canvas
- Actual generation uses stored pixel coordinates

## Testing Scenarios

### Functional Testing
1. Verify full-screen layout at various viewport sizes (1024px, 1366px, 1920px, 2560px)
2. Confirm sidebar widths remain fixed during resize
3. Validate font scaling maintains readability across all viewport sizes
4. Test orientation toggle triggers appropriate scaling updates
5. Verify window resize debouncing prevents performance degradation

### Visual Regression Testing
1. Compare preview rendering at different viewport sizes with generated slides
2. Ensure text wrapping behavior is consistent
3. Validate image/table/arrow positioning accuracy
4. Check modal dialogs remain centered and accessible

### Edge Case Testing
1. Ultra-wide monitors (3440x1440, 21:9 aspect ratio)
2. Vertical monitors (portrait mode, 1080x1920)
3. Minimum supported viewport (1024x600)
4. Rapid window resize operations
5. Orientation switching under constrained viewport

### Cross-Browser Testing
| Browser | Version | Focus Areas |
|---------|---------|-------------|
| Chrome | Latest | ResizeObserver, CSS Grid, aspect-ratio |
| Firefox | Latest | Scaling calculations, flexbox fallback |
| Safari | Latest | CSS aspect-ratio polyfill, font rendering |
| Edge | Latest | Performance optimization validation |

## Success Criteria

1. Editor utilizes full browser viewport width and height without scrollbars (except for overflow content)
2. Slides and Settings panels maintain fixed, comfortable widths (280px ± 40px range)
3. Preview canvas scales to fill available center panel space while maintaining aspect ratio
4. Font sizes scale proportionally to preview canvas dimensions
5. Text remains readable at all tested viewport sizes (no smaller than 10px, no larger than 120px)
6. Window resize operations complete smoothly within 200ms (debounced)
7. Existing functionality (save, orientation toggle, element positioning) remains unaffected
8. Generated presentations use unscaled base font sizes (no change to output)

## Out of Scope

The following enhancements are intentionally excluded from this design:

- Mobile responsive layout (viewport < 1024px)
- Sidebar collapse/expand toggle controls
- User-configurable sidebar widths
- Full-screen mode toggle (F11 browser feature sufficient)
- Multi-monitor support optimizations
- Custom scaling factor override controls
- Saved viewport preferences per user
- Zoom in/out controls for preview canvas
