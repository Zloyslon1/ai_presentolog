# Slide Editor Enhancement Design

## Overview

This design outlines the enhancement of the existing slide editor with advanced formatting capabilities including page orientation selection, extended font library, independent image placement, table and arrow drawing tools, and flexible text positioning controls.

## Objectives

Enable users to create richly formatted presentations directly within the editor by providing professional design tools comparable to native Google Slides capabilities, while maintaining the current plain-text workflow as the default option.

## Context

### Current System State

- **Frontend**: Flask application serving Jinja2 templates with Vanilla JavaScript
- **Editor Location**: `/slide_editor` route rendered via `templates/slide_editor.html`
- **Backend Processing**: `web_app.py` handles extraction and generation workflows
- **Presentation Generation**: `PresentationBuilder` in `presentation_design/generation/presentation_builder.py`
- **Google Slides API**: OAuth 2.0 authenticated integration
- **Current Workflow**: Extract → Edit plain text → Generate plain presentation

### Technical Stack

- Python 3.12 with Flask 3.0+
- Frontend: HTML, JavaScript (Vanilla), Tailwind CSS v4, Flowbite 4.0.1
- API: Google Slides API v1
- Coordinates System: EMU (English Metric Units) where 1 PT = 12700 EMU

## Requirements

### 1. Page Orientation Selection

**Purpose**: Allow users to create presentations in horizontal (16:9) or vertical (9:16) aspect ratios.

**User Interface**:
- Control panel location: Right panel (existing "Info Panel" section)
- Control type: Dropdown or toggle switch
- Options:
  - "Горизонтальный (16:9)" - Horizontal/Landscape
  - "Вертикальный (9:16)" - Vertical/Portrait
- Default: Horizontal (16:9)

**Behavior**:
- Orientation selection updates slide preview aspect ratio immediately
- Preview container CSS: `style="aspect-ratio: 16/9"` or `style="aspect-ratio: 9/16"`
- Setting applies to entire presentation (global setting)
- Persists across editor sessions via localStorage

**Google Slides API Integration**:
- Apply during presentation creation via `presentations().create()` method
- Use `pageSize` property with custom dimensions:
  - Horizontal: `{width: {magnitude: 9144000, unit: 'EMU'}, height: {magnitude: 5143500, unit: 'EMU'}}`
  - Vertical: `{width: {magnitude: 5143500, unit: 'EMU'}, height: {magnitude: 9144000, unit: 'EMU'}}`

**Data Structure**:
```
presentationSettings: {
  pageOrientation: 'horizontal' | 'vertical',
  pageSize: {
    width: {magnitude: number, unit: 'EMU'},
    height: {magnitude: number, unit: 'EMU'}
  }
}
```

### 2. Extended Font Selection

**Purpose**: Expand font choices beyond system defaults to include Google Fonts available in Google Slides.

**Current State**: Arial default font only

**User Interface**:
- Control panel location: Right panel below existing size controls
- Control type: Dropdown menu with font preview
- Label: "Шрифт" (Font)
- Per-slide setting with "Apply to All" option

**Font Library**:

System Fonts:
- Arial (default)
- Times New Roman
- Calibri
- Georgia

Google Fonts:
- Roboto
- Open Sans
- Lato
- Montserrat
- Oswald
- Raleway

**Behavior**:
- Font selection updates preview immediately
- Font family stored per slide in slide data structure
- "Apply to All" button propagates font choice to all slides

**Google Slides API Integration**:
- Apply via `updateTextStyle` request with `fontFamily` field
- Text range: `{type: 'ALL'}` to affect entire text box
- Request structure:
```
{
  updateTextStyle: {
    objectId: elementId,
    textRange: {type: 'ALL'},
    style: {
      fontFamily: selectedFont,
      weightedFontFamily: {
        fontFamily: selectedFont,
        weight: 400
      }
    },
    fields: 'fontFamily,weightedFontFamily'
  }
}
```

**Data Structure**:
```
slideData: {
  title: string,
  mainText: string,
  secondaryText: string,
  fontFamily: string,
  titleSize: number,
  textSize: number
}
```

### 3. Independent Image Placement

**Purpose**: Enable users to insert images as overlay elements independent of background layer.

**User Interface**:
- Control location: Center panel below text editors
- Button: "➕ Добавить изображение"
- Image source options:
  - Upload from local file
  - Enter image URL
- Positioning method: Drag-and-drop within preview OR coordinate inputs (x, y, width, height)
- Image list: Display added images with delete/reposition controls

**Behavior**:
- Images layer above background but can be positioned freely
- Multiple images supported per slide
- Preview shows images in approximate positions
- Images do not affect text box layout

**Google Slides API Integration**:
- Use `createImage` request in batch update
- Request structure:
```
{
  createImage: {
    url: imageUrl,
    elementProperties: {
      pageObjectId: slideId,
      size: {
        width: {magnitude: widthEMU, unit: 'EMU'},
        height: {magnitude: heightEMU, unit: 'EMU'}
      },
      transform: {
        scaleX: 1,
        scaleY: 1,
        translateX: xEMU,
        translateY: yEMU,
        unit: 'EMU'
      }
    }
  }
}
```

**Constraints**:
- Image URL must be publicly accessible or uploaded to Google Drive
- Supported formats: PNG, JPG, GIF
- Maximum recommended dimensions: 1920x1080 pixels

**Data Structure**:
```
slideData: {
  ...existingFields,
  images: [
    {
      id: uniqueId,
      url: string,
      position: {x: number, y: number},
      size: {width: number, height: number}
    }
  ]
}
```

### 4. Table Drawing Support

**Purpose**: Insert editable tables for structured data presentation.

**User Interface**:
- Control location: Center panel below image button
- Button: "📊 Добавить таблицу"
- Table configuration modal:
  - Rows count (input, range 1-10)
  - Columns count (input, range 1-8)
  - Position controls (x, y)
  - Size controls (width, height)
- Table list: Display added tables with edit/delete controls

**Behavior**:
- Tables created with empty cells
- Cell text editable after creation (requires refresh or advanced interface)
- Tables positioned via coordinates
- Preview shows table outline and dimensions

**Google Slides API Integration**:
- Use `createTable` request in batch update
- Request structure:
```
{
  createTable: {
    rows: rowCount,
    columns: columnCount,
    elementProperties: {
      pageObjectId: slideId,
      size: {
        width: {magnitude: widthEMU, unit: 'EMU'},
        height: {magnitude: heightEMU, unit: 'EMU'}
      },
      transform: {
        scaleX: 1,
        scaleY: 1,
        translateX: xEMU,
        translateY: yEMU,
        unit: 'EMU'
      }
    }
  }
}
```

- Cell text editing via `insertText` with `tableCellLocation`:
```
{
  insertText: {
    objectId: tableId,
    text: cellContent,
    cellLocation: {
      rowIndex: row,
      columnIndex: column
    }
  }
}
```

**Data Structure**:
```
slideData: {
  ...existingFields,
  tables: [
    {
      id: uniqueId,
      rows: number,
      columns: number,
      position: {x: number, y: number},
      size: {width: number, height: number},
      cellData: {
        [rowIndex_columnIndex]: string
      }
    }
  ]
}
```

### 5. Arrow Drawing Support

**Purpose**: Add directional arrows for visual flow and emphasis.

**User Interface**:
- Control location: Center panel next to table button
- Button: "➡️ Добавить стрелку"
- Arrow configuration:
  - Arrow type: Straight, bent, curved
  - Start point (x, y)
  - End point (x, y)
  - Color picker
  - Stroke width
- Arrow list: Display added arrows with edit/delete controls

**Behavior**:
- Arrows rendered as connector shapes
- Interactive positioning via drag endpoints in preview
- Preview shows arrow path and style

**Google Slides API Integration**:
- Use `createShape` request with connector shape types
- Shape types:
  - `STRAIGHT_CONNECTOR_1` - Simple straight arrow
  - `BENT_CONNECTOR_2` - Single bend arrow
  - `CURVED_CONNECTOR_3` - Curved arrow
- Request structure:
```
{
  createShape: {
    objectId: arrowId,
    shapeType: 'STRAIGHT_CONNECTOR_1',
    elementProperties: {
      pageObjectId: slideId,
      size: {
        width: {magnitude: lengthEMU, unit: 'EMU'},
        height: {magnitude: 0, unit: 'EMU'}
      },
      transform: {
        scaleX: 1,
        scaleY: 1,
        translateX: startXEMU,
        translateY: startYEMU,
        unit: 'EMU'
      }
    }
  }
}
```

- Styling via `updateShapeProperties`:
```
{
  updateShapeProperties: {
    objectId: arrowId,
    shapeProperties: {
      outline: {
        outlineFill: {
          solidFill: {
            color: {rgbColor: colorRGB}
          }
        },
        weight: {magnitude: strokeWidth, unit: 'PT'}
      }
    },
    fields: 'outline'
  }
}
```

**Data Structure**:
```
slideData: {
  ...existingFields,
  arrows: [
    {
      id: uniqueId,
      type: 'straight' | 'bent' | 'curved',
      startPoint: {x: number, y: number},
      endPoint: {x: number, y: number},
      color: string,
      strokeWidth: number
    }
  ]
}
```

### 6. Text Positioning Controls

**Purpose**: Provide precise control over text block placement with preset alignments.

**User Interface**:
- Control location: Right panel below font selection
- Label: "Позиционирование текста"
- Vertical alignment buttons:
  - "Сверху" (Top)
  - "По центру" (Center)
  - "Снизу" (Bottom)
- Horizontal alignment buttons:
  - "Слева" (Left)
  - "По центру" (Center)
  - "Справа" (Right)
- Per-slide setting

**Behavior**:
- Alignment buttons update preview text position immediately
- Both title and main text use same alignment
- Default: Top + Left alignment

**Position Mapping (EMU coordinates)**:

Vertical:
- Top: `translateY = 635000` (~50 PT from top)
- Center: `translateY = 3200000` (~252 PT, mid-slide)
- Bottom: `translateY = 5715000` (~450 PT from top)

Horizontal:
- Left: `translateX = 635000` (~50 PT from left)
- Center: `translateX = 1905000` (~150 PT, centered for 600 PT width)
- Right: `translateX = 3175000` (~250 PT from left, right-aligned)

**Google Slides API Integration**:
- Apply via `updateParagraphStyle` for text alignment within box
- Box positioning via `transform` property during `createShape`
- Alignment request:
```
{
  updateParagraphStyle: {
    objectId: elementId,
    textRange: {type: 'ALL'},
    style: {
      alignment: 'START' | 'CENTER' | 'END'
    },
    fields: 'alignment'
  }
}
```

**Data Structure**:
```
slideData: {
  ...existingFields,
  textPosition: {
    vertical: 'top' | 'center' | 'bottom',
    horizontal: 'left' | 'center' | 'right'
  }
}
```

### 7. Settings Persistence

**Purpose**: Preserve user preferences across sessions and presentations.

**Scope**:
- Per-presentation settings (tied to job ID)
- Global default settings

**Settings to Persist**:
```
presentationSettings: {
  background: {
    color: string,
    imageUrl: string | null
  },
  defaultFont: string,
  defaultFontSize: number,
  pageOrientation: 'horizontal' | 'vertical',
  defaultTextPosition: {
    vertical: 'top' | 'center' | 'bottom',
    horizontal: 'left' | 'center' | 'right'
  }
}
```

**Storage Mechanism**:
- Browser localStorage with key: `presentation_settings_{jobId}`
- JSON serialization
- Load on editor initialization
- Save on setting change (debounced)

**JavaScript Implementation Pattern**:
```javascript
// Save settings
function saveSettings() {
  const settings = {
    background: {...},
    defaultFont: document.getElementById('fontSelect').value,
    defaultFontSize: parseInt(document.getElementById('textSize').value),
    pageOrientation: document.getElementById('orientationSelect').value,
    defaultTextPosition: {...}
  };
  
  localStorage.setItem(
    'presentation_settings_' + jobId, 
    JSON.stringify(settings)
  );
}

// Load settings
function loadSettings() {
  const stored = localStorage.getItem('presentation_settings_' + jobId);
  if (stored) {
    const settings = JSON.parse(stored);
    // Apply settings to UI controls
  }
}
```

**Default Behavior**:
- New slides inherit current settings
- Settings reset button restores system defaults
- Settings export/import for template reuse (future enhancement)

## Implementation Strategy

### Phase 1: Core UI Controls
- Add orientation selector to right panel
- Add font dropdown with preview
- Add text positioning controls
- Implement settings persistence
- Update preview rendering

### Phase 2: Image Placement
- Add image upload/URL input UI
- Implement image list management
- Add drag-and-drop positioning
- Integrate with PresentationBuilder

### Phase 3: Table Support
- Add table configuration modal
- Implement table creation UI
- Add cell editing interface
- Integrate with Google Slides API

### Phase 4: Arrow Drawing
- Add arrow type selector
- Implement endpoint positioning UI
- Add styling controls (color, width)
- Integrate with Google Slides API

### Phase 5: Backend Integration
- Extend `process_slides_in_background` to accept new parameters
- Modify `PresentationBuilder.build_simple_presentation` to apply advanced settings
- Add helper methods: `_add_image`, `_add_table`, `_add_arrow`
- Update batch request generation

## File Modifications

### templates/slide_editor.html
**Additions Required**:
- Font selection dropdown in right panel
- Page orientation selector
- Text positioning button grid
- Image management section with upload/URL input
- Table configuration modal
- Arrow configuration controls
- Settings persistence JavaScript functions

**JavaScript Functions to Add**:
- `applyPageOrientation()`
- `changeFontFamily()`
- `changeTextPosition(vertical, horizontal)`
- `addImage(source, url)`
- `removeImage(imageId)`
- `addTable(rows, columns)`
- `editTableCell(tableId, row, col, text)`
- `addArrow(type, start, end, style)`
- `saveSettings()` / `loadSettings()`
- `updatePreviewWithImages()` / `updatePreviewWithTables()` / `updatePreviewWithArrows()`

**Updated `generatePresentation()` Function**:
- Serialize extended slide data including images, tables, arrows
- Include presentation-level settings (orientation, default font)
- Send via POST to `/process_slides`

### web_app.py
**Route Modification**: `/process_slides`
- Accept additional JSON fields:
  - `pageOrientation`
  - `defaultFont`
  - `images` array
  - `tables` array
  - `arrows` array

**Function Update**: `process_slides_in_background`
- Extract new parameters from request data
- Pass to `PresentationBuilder` methods

### presentation_design/generation/presentation_builder.py
**New Methods to Add**:

```
_add_image(self, slide_id: str, image_data: dict, index: int) -> list
```
**Purpose**: Generate batch requests for image insertion
**Parameters**: 
- slide_id: Target slide object ID
- image_data: {url, position, size}
- index: Image index for unique ID generation
**Returns**: List of batch update requests

```
_add_table(self, slide_id: str, table_data: dict, index: int) -> list
```
**Purpose**: Generate batch requests for table creation
**Parameters**:
- slide_id: Target slide object ID
- table_data: {rows, columns, position, size, cellData}
- index: Table index for unique ID generation
**Returns**: List of batch update requests

```
_add_arrow(self, slide_id: str, arrow_data: dict, index: int) -> list
```
**Purpose**: Generate batch requests for arrow/connector shape
**Parameters**:
- slide_id: Target slide object ID
- arrow_data: {type, startPoint, endPoint, color, strokeWidth}
- index: Arrow index for unique ID generation
**Returns**: List of batch update requests

**Method Modification**: `build_simple_presentation`
- Accept presentation-level settings parameter
- Apply page size based on orientation
- Iterate through slides and call helper methods for images, tables, arrows
- Apply default font and positioning to text elements

**Coordinate Conversion Utility**:
```
_pt_to_emu(self, pt: float) -> int
```
**Purpose**: Convert points to EMU
**Formula**: `EMU = PT * 12700`

## Data Flow

### User Interaction Flow
1. User selects page orientation → Updates preview aspect ratio + stores in settings
2. User selects font → Updates preview font + stores in slide data
3. User adds image → Shows in image list + renders in preview
4. User adds table/arrow → Shows in element list + renders in preview
5. User adjusts text position → Updates preview layout
6. User clicks "Создать презентацию" → Serializes all data → POST to `/process_slides`

### Backend Processing Flow
1. Flask receives enhanced slide data via `/process_slides`
2. `process_slides_in_background` extracts settings and element data
3. `PresentationBuilder.build_simple_presentation` receives full specification
4. For each slide:
   - Create text boxes with applied font, size, position
   - Call `_add_image` for each image
   - Call `_add_table` for each table
   - Call `_add_arrow` for each arrow
5. Batch all requests per slide
6. Execute via `presentations().batchUpdate()`
7. Return presentation ID and URL

## API Request Batching Strategy

To comply with Google Slides API quotas and minimize latency:

### Batching Rules
- Group all requests per slide into single batch
- Maximum 500 requests per batch (API limit)
- Order of operations within batch:
  1. Slide background updates
  2. Text box creation
  3. Text insertion
  4. Text styling
  5. Image creation
  6. Table creation
  7. Arrow/shape creation

### Batch Size Management
- Count requests before execution
- Split into multiple batches if exceeding 500
- Execute batches sequentially with error handling

### Example Batch Structure
```
{
  requests: [
    // Background
    {updatePageProperties: {...}},
    
    // Text elements
    {createShape: {...}},
    {insertText: {...}},
    {updateTextStyle: {...}},
    
    // Images
    {createImage: {...}},
    {createImage: {...}},
    
    // Tables
    {createTable: {...}},
    {insertText: {cellLocation: {...}}},
    
    // Arrows
    {createShape: {...}},
    {updateShapeProperties: {...}}
  ]
}
```

## Testing Requirements

### Functional Tests
- Font changes persist across slides when applied individually
- "Apply to All" propagates settings correctly
- Images do not overlap or interfere with text boxes
- Tables are created with correct dimensions and cell structure
- Arrow positioning accurately reflects start/end coordinates
- Settings save/load correctly via localStorage
- Portrait mode renders with correct aspect ratio in Google Slides
- Page orientation affects all slides uniformly

### Edge Cases
- Empty slides (no text, only images/tables)
- Maximum element count per slide (performance)
- Very long table cell content (overflow handling)
- Invalid image URLs (error handling)
- Concurrent setting changes (race conditions)
- Browser without localStorage support (graceful degradation)

### Integration Tests
- End-to-end: Extract → Edit → Generate with advanced features
- API quota handling with large presentations (50+ slides)
- OAuth token refresh during long operations
- Network error recovery during batch updates

## Constraints and Limitations

### Technical Constraints
- All coordinates must be in EMU (1 PT = 12700 EMU)
- Google Slides API batch limit: 500 requests
- Image URLs must be publicly accessible
- Font availability depends on Google Slides font library
- Preview rendering is approximate (actual positions may vary slightly)

### User Experience Constraints
- Maintain 1:1 text extraction from source presentations (existing requirement)
- Plain text presentation option remains available
- Do not break existing editor workflows
- Preview updates should be near-instantaneous (<100ms)

### API Constraints
- OAuth token valid for limited time (refresh required)
- API quota: 300 requests per minute per user
- Image file size limits enforced by Google

## Success Criteria

- Users can create presentations with custom fonts in under 2 minutes
- Image placement workflow requires no more than 3 clicks per image
- Table creation supports up to 10x8 cells without performance degradation
- Settings persistence works across browser sessions 100% of the time
- Portrait presentations render correctly in Google Slides without manual adjustment
- All advanced features work with existing plain-text workflow without conflicts

## Future Enhancements (Out of Scope)

- Shape library beyond arrows (rectangles, circles, callouts)
- Background image upload and positioning
- Text box rotation and layering
- Animation and transition settings
- Master slide templates
- Collaborative editing
- Undo/redo functionality in editor
- Rich text formatting within editor (bold, italic, colors)
