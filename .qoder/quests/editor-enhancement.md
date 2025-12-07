# Editor Enhancement Design

## Overview

Enhancement of the slide editor to include missing formatting and styling features for a complete presentation editing experience. This design addresses seven distinct feature areas identified in the current editor implementation.

## Background

The current editor supports basic text editing, custom fonts, font sizes, images, and page orientation. However, critical formatting features are missing or non-functional including tables, background styling, text formatting, lists, accent boxes, text alignment, and font color.

## Objectives

Implement seven feature sets to provide comprehensive slide editing capabilities:

1. Fix table functionality
2. Add slide background selection
3. Enable text formatting controls
4. Support bulleted and numbered lists  
5. Add accent box elements
6. Fix text alignment
7. Add font color selection

## Feature Requirements

### 1. Table Functionality

#### Current State
- UI modal exists for table creation
- Tables are not persisted to slide data
- Backend method exists but is not invoked
- No cell editing capability

#### Requirements
- Table creation with configurable rows and columns
- Cell content editing interface
- Position and size controls
- Data persistence in slide structure
- Preview rendering on slide canvas
- Backend generation via Google Slides API

#### Data Structure
```
{
  id: string (unique identifier)
  rows: number (1-10)
  columns: number (1-8)
  position: { x: number, y: number }
  size: { width: number, height: number }
  cellData: object (key format: "row_col", value: cell text)
}
```

#### Interactions
- Modal workflow: Configure dimensions → Position table → Edit cells → Save
- Cell editor: Grid interface with input fields for each cell
- Preview: Visual table representation on slide canvas
- List management: Display added tables with edit and delete actions

### 2. Slide Background Selection

#### Requirements
- Three background types: none (white), solid color, gradient
- Color picker for solid backgrounds
- Dual color picker for gradients with direction selection
- Real-time preview update
- Persistence per slide
- Backend application via Google Slides API

#### Background Types

| Type | Parameters | Preview Behavior |
|------|-----------|-----------------|
| None | Default white | White background |
| Solid | Single color value | Apply solid color |
| Gradient | Color1, Color2, Direction | Linear gradient (horizontal, vertical, diagonal) |

#### Constraints
- Google Slides API limitation: Native gradient support unavailable
- Gradient implementation approach: Solid color fallback or image-based gradient

#### Data Structure
```
{
  type: string (none, solid, gradient)
  color: string (hex value for solid)
  gradient: {
    color1: string (hex)
    color2: string (hex)
    direction: string (to right, to bottom, to bottom right)
  }
}
```

### 3. Text Formatting Controls

#### Requirements
- Bold, italic, and underline formatting
- Markdown-style markers in text
- Toolbar buttons for applying formatting
- Selection-based formatting application
- Parse and render formatting in backend

#### Formatting Markers

| Style | Marker | Example |
|-------|--------|---------|
| Bold | \*\*text\*\* | \*\*Important\*\* |
| Italic | \*text\* | \*Emphasis\* |
| Underline | \_\_text\_\_ | \_\_Underlined\_\_ |

#### Workflow
1. User selects text in textarea
2. Clicks formatting button
3. Markers wrap selected text
4. Preview updates with styled text
5. Backend parses markers during generation
6. Google Slides API applies formatting segments

#### Backend Processing
- Parse text into segments with formatting flags
- Each segment contains: text content, bold flag, italic flag, underline flag
- Apply formatting per segment via API text style requests

### 4. List Support

#### Current State
- List markers detected in preview rendering
- Backend list formatting method exists but underutilized
- No toolbar integration for list insertion

#### Requirements
- Bulleted list insertion
- Numbered list insertion
- Toolbar buttons for list markers
- Line-based marker insertion
- Backend formatting via Google Slides API

#### List Markers

| Type | Marker | Example |
|------|--------|---------|
| Bullet | • or - | • First item |
| Numbered | 1. | 1. First step |

#### Workflow
- User positions cursor in textarea
- Clicks list button
- Marker inserted at line start
- Preview renders list formatting
- Backend applies Google Slides list formatting

### 5. Accent Box Elements

#### Requirements
- Rectangular highlight boxes with text
- Configurable background and border colors
- Position and size controls
- Text content input
- Corner radius styling
- Layer rendering with other elements

#### Use Cases
- Callout boxes for key information
- Highlighted notes
- Visual emphasis areas
- Sectioned content

#### Data Structure
```
{
  id: string (unique identifier)
  text: string (box content)
  position: { x: number, y: number }
  size: { width: number, height: number }
  backgroundColor: string (hex)
  borderColor: string (hex)
  borderWidth: number (points)
  borderRadius: number (corner rounding)
  textColor: string (hex)
  fontSize: number (points)
}
```

#### Rendering Strategy
- Backend creates rounded rectangle shape
- Applies fill and border styling
- Inserts text content
- Positions on slide canvas

### 6. Text Alignment Fix

#### Current State
- UI buttons exist for vertical and horizontal alignment
- Preview reflects alignment changes
- Backend does not apply alignment to generated slides

#### Requirements
- Vertical alignment: top, center, bottom
- Horizontal alignment: left, center, right
- Apply to text boxes during generation
- Use Google Slides API content alignment properties

#### Alignment Mapping

| Direction | Values | API Property |
|-----------|--------|--------------|
| Vertical | top, center, bottom | contentAlignment: TOP, MIDDLE, BOTTOM |
| Horizontal | left, center, right | alignment: START, CENTER, END |

#### Implementation Strategy
- Store alignment preferences in slide data
- During text box creation, apply shape properties
- Set contentAlignment for vertical positioning
- Set paragraph alignment for horizontal positioning

### 7. Font Color Selection

#### Requirements
- Color picker input for text color
- Hex value text input for precision
- Synchronization between picker and hex input
- Preview update on color change
- Apply to all text elements in slide
- Backend rendering via text style API

#### UI Components
- Color input (visual picker)
- Text input (hex value)
- Bidirectional sync on change

#### Data Flow
1. User selects color via picker or enters hex
2. Input values sync automatically
3. Preview text updates to show color
4. Color value stored in slide data
5. Backend applies foregroundColor to text elements

#### Default Behavior
- Default color: black (#000000)
- Apply consistently across title, main text, secondary text
- Allow per-slide customization

## Data Schema Integration

### Enhanced Slide Data Structure

```
{
  // Existing fields
  title: string
  mainText: string
  secondaryText: string
  fontFamily: string
  titleSize: number
  textSize: number
  
  // Enhanced fields
  textColor: string (hex value)
  textPosition: {
    vertical: string (top, center, bottom)
    horizontal: string (left, center, right)
  }
  background: {
    type: string (none, solid, gradient)
    color: string (hex for solid)
    gradient: { color1: string, color2: string, direction: string }
  }
  
  // Element collections
  images: array
  tables: array (enhanced with cell editing)
  arrows: array
  accentBoxes: array (new)
}
```

## Frontend Implementation Strategy

### UI Component Organization

| Area | Components |
|------|-----------|
| Settings Panel | Background selector, color pickers, alignment buttons |
| Text Editor | Formatting toolbar (B/I/U, lists) above textareas |
| Element Tools | Table, arrow, accent box modals |
| Preview Canvas | Real-time rendering with all elements |

### Modal Workflows

**Table Modal:**
- Step 1: Configure rows, columns, position, size
- Step 2: Launch cell editor grid
- Step 3: Input cell contents
- Step 4: Save and render preview

**Accent Box Modal:**
- Configure text content
- Select background and border colors
- Set position and size
- Save and render preview

### Preview Rendering Logic

#### Rendering Order (Z-index layers)
1. Background (solid/gradient)
2. Background images (z-index: 10)
3. Accent boxes (z-index: 15)
4. Text elements (z-index: 20)
5. Tables (z-index: 25)
6. Foreground images (z-index: 30)
7. Arrows (z-index: 35)

#### Text Formatting in Preview
- Parse markdown markers (bold, italic, underline)
- Render as HTML with appropriate tags
- Maintain line breaks and structure
- Apply list styling for bullet/numbered markers

## Backend Implementation Strategy

### API Request Generation

#### Background Application
- Use updatePageProperties request
- Set pageBackgroundFill with solidFill
- Gradient fallback: Use solid color (first gradient color)

#### Text Formatting
- Parse text into formatted segments
- Create separate updateTextStyle requests per segment
- Apply bold, italic, underline flags
- Maintain text range indices

#### Alignment Application
- Apply updateShapeProperties for vertical alignment (contentAlignment)
- Apply updateParagraphStyle for horizontal alignment
- Execute after text box creation

#### Accent Box Creation
- Create rounded rectangle shape (createShape with ROUND_RECTANGLE)
- Apply fill and border (updateShapeProperties)
- Insert text content (insertText)
- Style text (updateTextStyle)

#### Table Generation
- Use existing table creation method
- Populate cells with data from cellData object
- Apply default styling (borders, padding)

### Batch Request Optimization

- Group related operations
- Maintain request order dependencies
- Respect 500 request limit per batch
- Split large operations into multiple batches

### EMU Conversion Utilities

| Unit | Conversion | Usage |
|------|-----------|-------|
| Points to EMU | PT × 12700 | Position, size values |
| Hex to RGB | Parse and normalize to 0-1 | Color values |
| Percentage to float | Divide by 100 | Opacity values |

## Implementation Priority

### Priority Levels

| Priority | Features | Rationale |
|----------|----------|-----------|
| High | Font color, solid background, text alignment | Essential formatting controls |
| Medium | Tables, text formatting (B/I/U), lists | Common content needs |
| Low | Accent boxes, gradients | Enhancement features |

### Recommended Implementation Order

1. Font color selection (simple, high impact)
2. Solid background (straightforward API usage)
3. Text alignment fix (corrects existing UI)
4. Table functionality (complex but UI exists)
5. Text formatting (requires parsing logic)
6. List support (builds on text formatting)
7. Accent boxes (new element type)

## Testing Strategy

### Test Coverage Areas

#### Unit Testing
- Text parsing for formatting markers
- Color conversion functions
- EMU conversion utilities
- Data structure validation

#### Integration Testing
- Modal workflows (open, configure, save, close)
- Preview rendering accuracy
- Data persistence to slide structure
- Backend API request generation

#### End-to-End Testing
- Complete slide editing workflow
- Presentation generation with all features
- Google Slides API interaction
- Multi-slide consistency

### Test Scenarios

**Per Feature:**
1. Create element via UI
2. Verify preview rendering
3. Verify data persistence
4. Generate presentation
5. Validate output in Google Slides

**Cross-Feature:**
- Multiple elements on single slide
- Formatting with images and tables
- Background with foreground content
- Complex text with multiple formatting styles

## Technical Constraints

### Google Slides API Limitations

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| No native gradients | Cannot apply gradient backgrounds directly | Use solid color fallback |
| 500 requests per batch | Large presentations may exceed limit | Split into multiple batches |
| Text formatting granularity | Marker parsing required | Implement robust parser |

### Browser Compatibility
- Color input support (modern browsers only)
- Drag-and-drop for images (existing implementation)
- Preview rendering performance with many elements

### Performance Considerations
- Real-time preview updates on text input
- Debounce preview rendering for large text blocks
- Optimize batch request generation
- Lazy load Google Fonts in preview

## User Experience Guidelines

### Discoverability
- Clear visual indicators for formatting buttons
- Tooltips on all control elements
- Preview updates provide immediate feedback
- Contextual help in info panel

### Consistency
- Uniform modal design patterns
- Consistent color picker interfaces
- Standard button layouts and colors
- Predictable save/cancel behaviors

### Error Handling
- Validate inputs before saving
- Warn on unsupported gradient usage
- Handle API request failures gracefully
- Preserve data on errors

## Documentation Requirements

### User-Facing
- Feature descriptions in help panel
- Keyboard shortcuts for formatting
- Best practices for element usage
- Limitations and workarounds

### Developer-Facing
- API request examples for each feature
- Data structure schemas
- Extension points for new element types
- Backend parsing logic documentation

## Future Enhancement Opportunities

### Beyond Current Scope
- Custom gradient via background image upload
- Advanced table styling (cell colors, borders)
- Text box rotation and transformations
- Shape library (circles, polygons, etc.)
- Multi-select and bulk operations
- Template saving and loading
- Collaboration features

### Scalability Considerations
- Modular element rendering system
- Plugin architecture for new element types
- Centralized formatting parser
- Theme and style presets
