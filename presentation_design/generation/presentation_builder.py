"""
Presentation Builder Module
============================

Creates new Google Slides presentations with applied design.
"""

from typing import Dict, Any
import base64
import io
from ..auth.oauth_manager import OAuthManager
from ..utils.logger import get_logger
from ..utils.retry import retry_on_network_error

logger = get_logger(__name__)


class BuilderError(Exception):
    """Raised when presentation building fails."""
    pass


class PresentationBuilder:
    """
    Builds Google Slides presentations from designed specification.
    
    Creates new presentations via Google Slides API with
    formatted text, colors, and layouts.
    """
    
    def __init__(self, oauth_manager: OAuthManager):
        """Initialize presentation builder."""
        self.oauth_manager = oauth_manager
        self.slides_service = None
        self.drive_service = None
    
    def _ensure_service(self) -> None:
        """Ensure Slides API service is initialized."""
        if self.slides_service is None:
            self.slides_service = self.oauth_manager.build_service('slides', 'v1')
    
    def _ensure_drive_service(self) -> None:
        """Ensure Drive API service is initialized."""
        if self.drive_service is None:
            self.drive_service = self.oauth_manager.build_service('drive', 'v3')
    
    @retry_on_network_error()
    def build_simple_presentation(self, slides_data: list, title: str = "New Presentation", settings: dict = None) -> Dict[str, Any]:
        """
        Build new presentation with advanced formatting options.
        Supports custom fonts, text positioning, images, tables, and arrows.
        
        Args:
            slides_data: List of slides with 'title', 'mainText', and optional advanced features
            title: Presentation title
            settings: Presentation-level settings (orientation, default font, etc.)
            
        Returns:
            Dictionary with presentation_id and presentation_url
        """
        try:
            self._ensure_service()
            
            # Parse settings
            if settings is None:
                settings = {}
            
            page_orientation = settings.get('pageOrientation', '16:9')
            
            # Define page size based on aspect ratio
            # Google Slides uses EMU (English Metric Units)
            # 1 inch = 914400 EMU, standard slide is 10" x 7.5" for 4:3
            page_sizes = {
                '16:9': {'width': 9144000, 'height': 5143500},  # 10" x 5.625"
                '4:3': {'width': 9144000, 'height': 6858000},   # 10" x 7.5"
                '1:1': {'width': 6858000, 'height': 6858000},   # 7.5" x 7.5"
                '9:16': {'width': 5143500, 'height': 9144000},  # 5.625" x 10"
                # Legacy support
                'horizontal': {'width': 9144000, 'height': 5143500},
                'vertical': {'width': 5143500, 'height': 9144000}
            }
            
            size = page_sizes.get(page_orientation, page_sizes['16:9'])
            page_size = {
                'width': {'magnitude': size['width'], 'unit': 'EMU'},
                'height': {'magnitude': size['height'], 'unit': 'EMU'}
            }
            
            # Create blank presentation with custom page size
            presentation = self.slides_service.presentations().create(
                body={
                    'title': title,
                    'pageSize': page_size
                }
            ).execute()
            
            presentation_id = presentation['presentationId']
            
            logger.info(
                f"Created presentation: {title} ({page_orientation})",
                operation="build_simple_presentation",
                presentation_id=presentation_id
            )
            
            # Get the created presentation to get actual slide IDs
            presentation = self.slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            # Create additional slides if needed
            requests = []
            slide_count = len(slides_data)
            
            for idx in range(1, slide_count):
                requests.append({
                    'createSlide': {
                        'insertionIndex': idx
                    }
                })
            
            # Execute slide creation first
            if requests:
                self.slides_service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body={'requests': requests}
                ).execute()
                
                # Refresh presentation to get new slide IDs
                presentation = self.slides_service.presentations().get(
                    presentationId=presentation_id
                ).execute()
            
            # Now add content to each slide
            requests = []
            actual_slides = presentation.get('slides', [])
            
            for idx, slide_data in enumerate(slides_data):
                if idx < len(actual_slides):
                    actual_slide_id = actual_slides[idx]['objectId']
                    
                    # Delete default layout elements (title/body placeholders)
                    slide = actual_slides[idx]
                    for element in slide.get('pageElements', []):
                        requests.append({
                            'deleteObject': {
                                'objectId': element['objectId']
                            }
                        })
            
            # Execute deletions
            if requests:
                self.slides_service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body={'requests': requests}
                ).execute()
                requests = []
            
            # Add content with advanced features
            for idx, slide_data in enumerate(slides_data):
                if idx < len(actual_slides):
                    actual_slide_id = actual_slides[idx]['objectId']
                    slide_requests = self._build_advanced_slide_content(
                        slide_data, actual_slide_id, idx, settings
                    )
                    requests.extend(slide_requests)
            
            # Apply all content updates in batch
            if requests:
                # Split into batches if too large (max 500 requests per batch)
                batch_size = 500
                for i in range(0, len(requests), batch_size):
                    batch = requests[i:i + batch_size]
                    self.slides_service.presentations().batchUpdate(
                        presentationId=presentation_id,
                        body={'requests': batch}
                    ).execute()
            
            presentation_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
            
            logger.info(
                f"Presentation built successfully",
                operation="build_simple_presentation",
                presentation_id=presentation_id,
                url=presentation_url
            )
            
            return {
                'presentation_id': presentation_id,
                'presentation_url': presentation_url,
                'title': title
            }
            
        except Exception as e:
            logger.error(
                f"Failed to build presentation: {e}",
                operation="build_simple_presentation",
                exc_info=True
            )
            raise BuilderError(f"Failed to build presentation: {e}") from e
    
    def _build_plain_slide_content(self, slide_data: Dict[str, Any], slide_id: str, index: int) -> list:
        """
        Generate batch update requests for PLAIN TEXT slide content.
        NO formatting, NO colors, NO backgrounds - just raw text.
        
        Args:
            slide_data: Slide with 'title' and 'mainText' fields
            slide_id: Actual slide ID in the presentation
            index: Slide index
            
        Returns:
            List of batch update requests
        """
        requests = []
        
        title = slide_data.get('title', '').strip()
        main_text = slide_data.get('mainText', '').strip()
        
        element_count = 0
        
        # Add title if present
        if title:
            element_id = f"plain_title_{index}_{element_count}"
            element_count += 1
            
            # Create title text box (top of slide)
            requests.append({
                'createShape': {
                    'objectId': element_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': 8000000, 'unit': 'EMU'},  # ~630 PT
                            'height': {'magnitude': 1000000, 'unit': 'EMU'}  # ~80 PT
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': 635000,  # ~50 PT from left
                            'translateY': 635000,  # ~50 PT from top
                            'unit': 'EMU'
                        }
                    }
                }
            })
            
            # Insert title text
            requests.append({
                'insertText': {
                    'objectId': element_id,
                    'text': title,
                    'insertionIndex': 0
                }
            })
        
        # Add main text if present
        if main_text:
            element_id = f"plain_text_{index}_{element_count}"
            element_count += 1
            
            # Calculate Y position (below title or at top if no title)
            y_position = 1905000 if title else 635000  # ~150 PT or ~50 PT
            
            # Create main text box
            requests.append({
                'createShape': {
                    'objectId': element_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': 8000000, 'unit': 'EMU'},  # ~630 PT
                            'height': {'magnitude': 4500000, 'unit': 'EMU'}  # ~355 PT
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': 635000,  # ~50 PT from left
                            'translateY': y_position,
                            'unit': 'EMU'
                        }
                    }
                }
            })
            
            # Insert main text
            requests.append({
                'insertText': {
                    'objectId': element_id,
                    'text': main_text,
                    'insertionIndex': 0
                }
            })
        
        return requests
    
    @retry_on_network_error()
    def build_presentation(self, designed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build new presentation from designed specification.
        
        Args:
            designed_data: Designed presentation specification
            
        Returns:
            Dictionary with presentation_id and presentation_url
        """
        try:
            self._ensure_service()
            
            # Create blank presentation
            title = f"{designed_data.get('title', 'Untitled')} (Designed)"
            presentation = self.slides_service.presentations().create(
                body={'title': title}
            ).execute()
            
            presentation_id = presentation['presentationId']
            
            logger.info(
                f"Created presentation: {title}",
                operation="build_presentation",
                presentation_id=presentation_id
            )
            
            # Get the created presentation to get actual slide IDs
            presentation = self.slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            # Build slides
            requests = []
            slide_count = len(designed_data.get('slides', []))
            
            # Create additional slides if needed
            for idx in range(1, slide_count):
                requests.append({
                    'createSlide': {
                        'insertionIndex': idx
                    }
                })
            
            # Execute slide creation first
            if requests:
                self.slides_service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body={'requests': requests}
                ).execute()
                
                # Refresh presentation to get new slide IDs
                presentation = self.slides_service.presentations().get(
                    presentationId=presentation_id
                ).execute()
            
            # Now build content for each slide
            requests = []
            actual_slides = presentation.get('slides', [])
            
            for idx, slide_data in enumerate(designed_data.get('slides', [])):
                if idx < len(actual_slides):
                    actual_slide_id = actual_slides[idx]['objectId']
                    slide_requests = self._build_slide_content(
                        slide_data, actual_slide_id, idx
                    )
                    requests.extend(slide_requests)
            
            # Apply all content updates in batch
            if requests:
                self.slides_service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body={'requests': requests}
                ).execute()
            
            presentation_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
            
            logger.info(
                f"Presentation built successfully",
                operation="build_presentation",
                presentation_id=presentation_id,
                url=presentation_url
            )
            
            return {
                'presentation_id': presentation_id,
                'presentation_url': presentation_url,
                'title': title
            }
            
        except Exception as e:
            logger.error(
                f"Failed to build presentation: {e}",
                operation="build_presentation",
                exc_info=True
            )
            raise BuilderError(f"Failed to build presentation: {e}") from e
    
    @retry_on_network_error()
    def update_presentation(self, presentation_id: str, designed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing presentation with new designed content.
        
        Args:
            presentation_id: ID of existing presentation to update
            designed_data: Designed presentation specification
            
        Returns:
            Dictionary with presentation_id and presentation_url
        """
        try:
            self._ensure_service()
            
            logger.info(
                f"Updating presentation: {presentation_id}",
                operation="update_presentation",
                presentation_id=presentation_id
            )
            
            # Get current presentation
            presentation = self.slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            existing_slides = presentation.get('slides', [])
            needed_slides = len(designed_data.get('slides', []))
            
            requests = []
            
            # Delete all existing slides except the first one
            for idx in range(len(existing_slides) - 1, 0, -1):
                requests.append({
                    'deleteObject': {
                        'objectId': existing_slides[idx]['objectId']
                    }
                })
            
            # Execute deletions
            if requests:
                self.slides_service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body={'requests': requests}
                ).execute()
                requests = []
            
            # Create new slides if needed
            for idx in range(1, needed_slides):
                requests.append({
                    'createSlide': {
                        'insertionIndex': idx
                    }
                })
            
            # Execute slide creation
            if requests:
                self.slides_service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body={'requests': requests}
                ).execute()
                requests = []
                
                # Refresh to get new slide IDs
                presentation = self.slides_service.presentations().get(
                    presentationId=presentation_id
                ).execute()
            
            # Clear all content from first slide and rebuild
            actual_slides = presentation.get('slides', [])
            
            # Delete all page elements from all slides
            for slide in actual_slides:
                for element in slide.get('pageElements', []):
                    requests.append({
                        'deleteObject': {
                            'objectId': element['objectId']
                        }
                    })
            
            # Execute deletions
            if requests:
                self.slides_service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body={'requests': requests}
                ).execute()
                requests = []
            
            # Now build content for each slide
            for idx, slide_data in enumerate(designed_data.get('slides', [])):
                if idx < len(actual_slides):
                    actual_slide_id = actual_slides[idx]['objectId']
                    slide_requests = self._build_slide_content(
                        slide_data, actual_slide_id, idx
                    )
                    requests.extend(slide_requests)
            
            # Apply all content updates in batch
            if requests:
                self.slides_service.presentations().batchUpdate(
                    presentationId=presentation_id,
                    body={'requests': requests}
                ).execute()
            
            presentation_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
            
            logger.info(
                f"Presentation updated successfully",
                operation="update_presentation",
                presentation_id=presentation_id,
                url=presentation_url
            )
            
            return {
                'presentation_id': presentation_id,
                'presentation_url': presentation_url,
                'title': presentation.get('title', 'Updated Presentation')
            }
            
        except Exception as e:
            logger.error(
                f"Failed to update presentation: {e}",
                operation="update_presentation",
                exc_info=True
            )
            raise BuilderError(f"Failed to update presentation: {e}") from e
    
    def _build_slide_content(self, slide_data: Dict[str, Any], slide_id: str, index: int) -> list:
        """
        Generate batch update requests for slide content.
        
        Args:
            slide_data: Designed slide specification
            slide_id: Actual slide ID in the new presentation
            index: Slide index
            
        Returns:
            List of batch update requests
        """
        requests = []
        
        # Apply slide background color
        background_color = slide_data.get('background_color', '#FFFFFF')
        requests.append({
            'updatePageProperties': {
                'objectId': slide_id,
                'pageProperties': {
                    'pageBackgroundFill': {
                        'solidFill': {
                            'color': {
                                'rgbColor': self._hex_to_rgb(background_color)
                            }
                        }
                    }
                },
                'fields': 'pageBackgroundFill'
            }
        })
        
        # Add text elements to the slide
        element_count = 0
        for element in slide_data.get('elements', []):
            content = element.get('content', '').strip()
            if not content:
                continue
                
            element_id = f"element_{index}_{element_count}"
            element_count += 1
            
            role = element.get('role', 'BODY')
            role_upper = role.upper()  # Normalize for comparison
            font_size = element.get('font_size', 18)
            font_family = element.get('font_family', 'Arial')
            color = element.get('color', '#000000')
            
            # Log title elements for debugging
            if role_upper in ['TITLE', 'SUBTITLE']:
                logger.info(
                    f"Processing {role_upper}: font_size={font_size}, color={color}, content={content[:50]}",
                    operation="_build_slide_content"
                )
            
            # Get position from styled_position or use default
            styled_pos = element.get('styled_position', {})
            
            # Convert PT to EMU (1 PT = 12700 EMU)
            x_pt = styled_pos.get('x', 50 + (element_count * 20))
            y_pt = styled_pos.get('y', 100 + (element_count * 80))
            width_pt = styled_pos.get('width', 600)
            height_pt = styled_pos.get('height', 60)
            
            # Convert to EMU
            x_emu = int(x_pt * 12700)
            y_emu = int(y_pt * 12700)
            width_emu = int(width_pt * 12700)
            height_emu = int(height_pt * 12700)
            
            # Create text box
            requests.append({
                'createShape': {
                    'objectId': element_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': width_emu, 'unit': 'EMU'},
                            'height': {'magnitude': height_emu, 'unit': 'EMU'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': x_emu,
                            'translateY': y_emu,
                            'unit': 'EMU'
                        }
                    }
                }
            })
            
            # Insert text
            requests.append({
                'insertText': {
                    'objectId': element_id,
                    'text': content,
                    'insertionIndex': 0
                }
            })
            
            # Apply comprehensive text styling to all text
            requests.append({
                'updateTextStyle': {
                    'objectId': element_id,
                    'textRange': {
                        'type': 'ALL'
                    },
                    'style': {
                        'fontSize': {
                            'magnitude': font_size,
                            'unit': 'PT'
                        },
                        'fontFamily': font_family,
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': self._hex_to_rgb(color)
                            }
                        },
                        'bold': role_upper in ['TITLE', 'SUBTITLE', 'HEADING'],
                        'weightedFontFamily': {
                            'fontFamily': font_family,
                            'weight': 700 if role_upper in ['TITLE', 'SUBTITLE', 'HEADING'] else 400
                        }
                    },
                    'fields': 'fontSize,fontFamily,foregroundColor,bold,weightedFontFamily'
                }
            })
            
            # Apply list formatting if this is a list element
            if element.get('is_list'):
                content_type = element.get('content_type', '')
                requests.extend(
                    self._apply_list_formatting(element_id, content, content_type)
                )
            
            # Center align titles and subtitles
            if role_upper in ['TITLE', 'SUBTITLE']:
                requests.append({
                    'updateParagraphStyle': {
                        'objectId': element_id,
                        'textRange': {
                            'type': 'ALL'
                        },
                        'style': {
                            'alignment': 'CENTER',
                            'spaceAbove': {'magnitude': 10, 'unit': 'PT'},
                            'spaceBelow': {'magnitude': 10, 'unit': 'PT'}
                        },
                        'fields': 'alignment,spaceAbove,spaceBelow'
                    }
                })
        
        return requests
    
    def _apply_list_formatting(self, element_id: str, content: str, content_type: str) -> list:
        """
        Apply bullet or numbered list formatting to text.
        
        Args:
            element_id: Text box element ID
            content: Text content with list items
            content_type: 'numbered_list' or 'bullet_list'
            
        Returns:
            List of formatting requests
        """
        requests = []
        
        # Split content into lines to identify list items
        lines = content.split('\n')
        current_index = 0
        
        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            
            if line.strip():
                # Apply bullet/number formatting to this line
                glyph = 'NUMBERED' if content_type == 'numbered_list' else 'BULLET_DISC_CIRCLE_SQUARE'
                
                # Update paragraph style for list
                requests.append({
                    'createParagraphBullets': {
                        'objectId': element_id,
                        'textRange': {
                            'type': 'FIXED_RANGE',
                            'startIndex': current_index,
                            'endIndex': current_index + len(line)
                        },
                        'bulletPreset': glyph
                    }
                })
                
                # Add indentation
                requests.append({
                    'updateParagraphStyle': {
                        'objectId': element_id,
                        'textRange': {
                            'type': 'FIXED_RANGE',
                            'startIndex': current_index,
                            'endIndex': current_index + len(line)
                        },
                        'style': {
                            'indentStart': {'magnitude': 20, 'unit': 'PT'},
                            'indentFirstLine': {'magnitude': 0, 'unit': 'PT'},
                            'spaceAbove': {'magnitude': 4, 'unit': 'PT'},
                            'spaceBelow': {'magnitude': 4, 'unit': 'PT'}
                        },
                        'fields': 'indentStart,indentFirstLine,spaceAbove,spaceBelow'
                    }
                })
            
            current_index += line_length
        
        return requests
    
    def _hex_to_rgb(self, hex_color: str) -> Dict[str, float]:
        """
        Convert hex color to RGB format for Google Slides API.
        
        Args:
            hex_color: Color in hex format (e.g., '#1A237E')
            
        Returns:
            RGB color dict with values 0-1
        """
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return {'red': r, 'green': g, 'blue': b}
    
    def _pt_to_emu(self, pt: float) -> int:
        """
        Convert points to EMU (English Metric Units).
        
        Args:
            pt: Value in points
            
        Returns:
            Value in EMU
        """
        return int(pt * 12700)
    
    def _html_to_plain_text(self, html_text: str) -> str:
        """
        Convert HTML from contenteditable to plain text.
        Removes HTML tags while preserving text content and line breaks.
        
        Args:
            html_text: HTML string from contenteditable editor
            
        Returns:
            Plain text without HTML tags
        """
        import re
        from html import unescape
        
        # Replace <br> and </div><div> with newlines before removing tags
        text = re.sub(r'<br\s*/?>', '\n', html_text)
        text = re.sub(r'</div><div>', '\n', text)
        text = re.sub(r'</p><p>', '\n\n', text)
        
        # Convert list items to bullet points (handle </li> before <li>)
        text = re.sub(r'</li>\s*<li[^>]*>', '\n• ', text)  # Between items
        text = re.sub(r'<li[^>]*>', '• ', text)  # First item
        text = re.sub(r'</li>', '', text)  # Remove closing tags
        
        # Remove all remaining HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities
        text = unescape(text)
        
        # Clean up multiple newlines and spaces
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 2 newlines
        text = re.sub(r' +', ' ', text)  # Multiple spaces to single
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def _build_advanced_slide_content(self, slide_data: Dict[str, Any], slide_id: str, index: int, settings: dict) -> list:
        """
        Generate batch update requests for slide with plain text content.
        NO colors, NO backgrounds - just clean text positioning.
        
        Args:
            slide_data: Slide with title, mainText, and optional images/tables/arrows
            slide_id: Actual slide ID in the presentation
            index: Slide index
            settings: Presentation-level settings
            
        Returns:
            List of batch update requests
        """
        requests = []
        
        # Apply background if specified
        background = slide_data.get('background', {})
        bg_type = background.get('type', 'none')
        
        if bg_type == 'solid' or bg_type == 'gradient':
            # Use solid color for both solid and gradient (Google Slides doesn't support gradients)
            color = background.get('color', '#FFFFFF')
            requests.append({
                'updatePageProperties': {
                    'objectId': slide_id,
                    'pageProperties': {
                        'pageBackgroundFill': {
                            'solidFill': {
                                'color': {
                                    'rgbColor': self._hex_to_rgb(color)
                                }
                            }
                        }
                    },
                    'fields': 'pageBackgroundFill'
                }
            })
        
        title = slide_data.get('title', '').strip()
        main_text = slide_data.get('mainText', '').strip()
        
        # Parse HTML from contenteditable if present
        if main_text and ('<' in main_text):
            main_text = self._html_to_plain_text(main_text)
        
        font_family = slide_data.get('fontFamily', settings.get('defaultFont', 'Arial'))
        title_size = slide_data.get('titleSize', 44)
        text_size = slide_data.get('textSize', 18)
        text_color = slide_data.get('textColor', '#000000')
        
        # Get text positioning
        text_position = slide_data.get('textPosition', settings.get('defaultTextPosition', {}))
        vertical = text_position.get('vertical', 'top')
        horizontal = text_position.get('horizontal', 'left')
        
        # Calculate positions
        vertical_positions = {'top': 635000, 'center': 3200000, 'bottom': 5715000}
        horizontal_positions = {'left': 635000, 'center': 1905000, 'right': 3175000}
        
        y_title = vertical_positions.get(vertical, 635000)
        x_pos = horizontal_positions.get(horizontal, 635000)
        
        element_count = 0
        
        # Add title if present
        if title:
            element_id = f"title_{index}_{element_count}"
            element_count += 1
            
            # Create title text box
            requests.append({
                'createShape': {
                    'objectId': element_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': self._pt_to_emu(600), 'unit': 'EMU'},
                            'height': {'magnitude': self._pt_to_emu(80), 'unit': 'EMU'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': x_pos,
                            'translateY': y_title,
                            'unit': 'EMU'
                        }
                    }
                }
            })
            
            # Insert title text
            requests.append({
                'insertText': {
                    'objectId': element_id,
                    'text': title,
                    'insertionIndex': 0
                }
            })
            
            # Apply ONLY font family and size - NO colors, NO bold
            requests.append({
                'updateTextStyle': {
                    'objectId': element_id,
                    'textRange': {'type': 'ALL'},
                    'style': {
                        'fontSize': {'magnitude': title_size, 'unit': 'PT'},
                        'fontFamily': font_family,
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': self._hex_to_rgb(text_color)
                            }
                        }
                    },
                    'fields': 'fontSize,fontFamily,foregroundColor'
                }
            })
            
            # Apply alignment
            alignment = 'START' if horizontal == 'left' else ('CENTER' if horizontal == 'center' else 'END')
            requests.append({
                'updateParagraphStyle': {
                    'objectId': element_id,
                    'textRange': {'type': 'ALL'},
                    'style': {'alignment': alignment},
                    'fields': 'alignment'
                }
            })
            
            # Apply vertical alignment via contentAlignment
            vertical_alignment_map = {
                'top': 'TOP',
                'center': 'MIDDLE',
                'bottom': 'BOTTOM'
            }
            content_alignment = vertical_alignment_map.get(vertical, 'TOP')
            requests.append({
                'updateShapeProperties': {
                    'objectId': element_id,
                    'shapeProperties': {
                        'contentAlignment': content_alignment
                    },
                    'fields': 'contentAlignment'
                }
            })
        
        # Add main text if present
        if main_text:
            element_id = f"text_{index}_{element_count}"
            element_count += 1
            
            # Calculate Y position (below title or at position if no title)
            y_text = y_title + self._pt_to_emu(100) if title else y_title
            
            # Create main text box
            requests.append({
                'createShape': {
                    'objectId': element_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': self._pt_to_emu(600), 'unit': 'EMU'},
                            'height': {'magnitude': self._pt_to_emu(300), 'unit': 'EMU'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': x_pos,
                            'translateY': y_text,
                            'unit': 'EMU'
                        }
                    }
                }
            })
            
            # Insert main text
            requests.append({
                'insertText': {
                    'objectId': element_id,
                    'text': main_text,
                    'insertionIndex': 0
                }
            })
            
            # Apply ONLY font family and size - NO colors
            requests.append({
                'updateTextStyle': {
                    'objectId': element_id,
                    'textRange': {'type': 'ALL'},
                    'style': {
                        'fontSize': {'magnitude': text_size, 'unit': 'PT'},
                        'fontFamily': font_family,
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': self._hex_to_rgb(text_color)
                            }
                        }
                    },
                    'fields': 'fontSize,fontFamily,foregroundColor'
                }
            })
            
            # Apply alignment
            alignment = 'START' if horizontal == 'left' else ('CENTER' if horizontal == 'center' else 'END')
            requests.append({
                'updateParagraphStyle': {
                    'objectId': element_id,
                    'textRange': {'type': 'ALL'},
                    'style': {'alignment': alignment},
                    'fields': 'alignment'
                }
            })
            
            # Apply vertical alignment via contentAlignment
            vertical_alignment_map = {
                'top': 'TOP',
                'center': 'MIDDLE',
                'bottom': 'BOTTOM'
            }
            content_alignment = vertical_alignment_map.get(vertical, 'TOP')
            requests.append({
                'updateShapeProperties': {
                    'objectId': element_id,
                    'shapeProperties': {
                        'contentAlignment': content_alignment
                    },
                    'fields': 'contentAlignment'
                }
            })
        
        # Separate images by layer
        all_images = slide_data.get('images', [])
        background_images = [img for img in all_images if img.get('layer') != 'foreground']
        foreground_images = [img for img in all_images if img.get('layer') == 'foreground']
        
        # Add background images first (behind text)
        for img_idx, image in enumerate(background_images):
            requests.extend(self._add_image(slide_id, image, f"bg_{img_idx}"))
        
        # Text is already added above, so foreground images come after
        # Add foreground images last (in front of text)
        for img_idx, image in enumerate(foreground_images):
            requests.extend(self._add_image(slide_id, image, f"fg_{img_idx}"))
        
        # Add tables
        for tbl_idx, table in enumerate(slide_data.get('tables', [])):
            requests.extend(self._add_table(slide_id, table, tbl_idx))
        
        # Add arrows
        for arr_idx, arrow in enumerate(slide_data.get('arrows', [])):
            requests.extend(self._add_arrow(slide_id, arrow, arr_idx))
        
        # Add accent boxes
        for box_idx, box in enumerate(slide_data.get('accentBoxes', [])):
            requests.extend(self._add_accent_box(slide_id, box, box_idx))
        
        return requests
    
    def _upload_image_to_drive(self, data_url: str, file_name: str = "slide_image.png") -> str:
        """
        Upload base64-encoded data URL image to Google Drive and return public URL.
        
        Args:
            data_url: Data URL string (e.g., "data:image/png;base64,...")
            file_name: Name for the uploaded file
            
        Returns:
            Public URL to the uploaded image on Google Drive
            
        Raises:
            BuilderError: If upload fails
        """
        try:
            self._ensure_drive_service()
            
            # Parse data URL to extract MIME type and base64 data
            if not data_url.startswith('data:'):
                raise BuilderError(f"Invalid data URL format")
            
            # Split: data:image/png;base64,iVBORw0KG...
            header, encoded_data = data_url.split(',', 1)
            mime_type = header.split(';')[0].split(':')[1]  # Extract 'image/png'
            
            # Decode base64 to binary
            image_data = base64.b64decode(encoded_data)
            
            # Determine file extension from MIME type
            extension_map = {
                'image/png': '.png',
                'image/jpeg': '.jpg',
                'image/jpg': '.jpg',
                'image/gif': '.gif',
                'image/webp': '.webp'
            }
            extension = extension_map.get(mime_type, '.png')
            
            # Ensure file name has correct extension
            if not file_name.endswith(extension):
                file_name = f"{file_name}{extension}"
            
            # Create file metadata
            file_metadata = {
                'name': file_name,
                'mimeType': mime_type
            }
            
            # Upload to Drive using media upload
            from googleapiclient.http import MediaIoBaseUpload
            media = MediaIoBaseUpload(
                io.BytesIO(image_data),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,webViewLink,webContentLink'
            ).execute()
            
            file_id = file.get('id')
            
            # Make file publicly accessible
            self.drive_service.permissions().create(
                fileId=file_id,
                body={
                    'type': 'anyone',
                    'role': 'reader'
                }
            ).execute()
            
            # Return direct download link (works with Google Slides API)
            public_url = f"https://drive.google.com/uc?export=view&id={file_id}"
            
            logger.info(
                f"Uploaded image to Google Drive",
                operation="upload_image_to_drive",
                file_id=file_id,
                file_name=file_name,
                size_bytes=len(image_data)
            )
            
            return public_url
            
        except Exception as e:
            logger.error(
                f"Failed to upload image to Drive: {e}",
                operation="upload_image_to_drive",
                exc_info=True
            )
            raise BuilderError(f"Failed to upload image to Drive: {e}") from e
    
    def _add_image(self, slide_id: str, image_data: dict, index) -> list:
        """
        Generate batch requests for image insertion.
        Automatically uploads data URLs to Google Drive to bypass 2KB limit.
        
        Args:
            slide_id: Target slide object ID
            image_data: {url, position, size, layer}
            index: Image index for unique ID generation (can be int or str)
            
        Returns:
            List of batch update requests
        """
        requests = []
        
        image_id = f"img_{slide_id}_{index}"
        url = image_data.get('url')
        position = image_data.get('position', {'x': 100, 'y': 100})
        size = image_data.get('size', {'width': 200, 'height': 150})
        
        if not url:
            return requests
        
        # If URL is a data URL, upload to Google Drive first
        # This bypasses the 2KB URL limit in Google Slides API
        if url.startswith('data:'):
            logger.info(
                f"Detected data URL for image {image_id}, uploading to Drive",
                operation="add_image",
                data_url_length=len(url)
            )
            
            # Generate unique file name
            file_name = f"slide_{slide_id}_image_{index}"
            url = self._upload_image_to_drive(url, file_name)
            
            logger.info(
                f"Image uploaded, using Drive URL",
                operation="add_image",
                drive_url=url
            )
        
        requests.append({
            'createImage': {
                'objectId': image_id,
                'url': url,
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': self._pt_to_emu(size['width']), 'unit': 'EMU'},
                        'height': {'magnitude': self._pt_to_emu(size['height']), 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': self._pt_to_emu(position['x']),
                        'translateY': self._pt_to_emu(position['y']),
                        'unit': 'EMU'
                    }
                }
            }
        })
        
        return requests
    
    def _add_table(self, slide_id: str, table_data: dict, index: int) -> list:
        """
        Generate batch requests for table creation.
        
        Args:
            slide_id: Target slide object ID
            table_data: {rows, columns, position, size, cellData}
            index: Table index for unique ID generation
            
        Returns:
            List of batch update requests
        """
        requests = []
        
        table_id = f"tbl_{slide_id}_{index}"
        rows = table_data.get('rows', 3)
        columns = table_data.get('columns', 3)
        position = table_data.get('position', {'x': 50, 'y': 200})
        size = table_data.get('size', {'width': 500, 'height': 200})
        cell_data = table_data.get('cellData', {})
        
        requests.append({
            'createTable': {
                'objectId': table_id,
                'rows': rows,
                'columns': columns,
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': self._pt_to_emu(size['width']), 'unit': 'EMU'},
                        'height': {'magnitude': self._pt_to_emu(size['height']), 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': self._pt_to_emu(position['x']),
                        'translateY': self._pt_to_emu(position['y']),
                        'unit': 'EMU'
                    }
                }
            }
        })
        
        # Add cell text if provided
        for cell_key, cell_text in cell_data.items():
            if '_' in cell_key:
                row_idx, col_idx = map(int, cell_key.split('_'))
                requests.append({
                    'insertText': {
                        'objectId': table_id,
                        'text': cell_text,
                        'cellLocation': {
                            'rowIndex': row_idx,
                            'columnIndex': col_idx
                        }
                    }
                })
        
        return requests
    
    def _add_arrow(self, slide_id: str, arrow_data: dict, index: int) -> list:
        """
        Generate batch requests for arrow/connector shape.
        
        Args:
            slide_id: Target slide object ID
            arrow_data: {type, startPoint, endPoint, color, strokeWidth}
            index: Arrow index for unique ID generation
            
        Returns:
            List of batch update requests
        """
        requests = []
        
        arrow_id = f"arr_{slide_id}_{index}"
        arrow_type = arrow_data.get('type', 'straight')
        start_point = arrow_data.get('startPoint', {'x': 100, 'y': 150})
        end_point = arrow_data.get('endPoint', {'x': 300, 'y': 150})
        color = arrow_data.get('color', '#000000')
        stroke_width = arrow_data.get('strokeWidth', 2)
        
        # Map arrow type to Google Slides shape type
        shape_type_map = {
            'straight': 'STRAIGHT_CONNECTOR_1',
            'bent': 'BENT_CONNECTOR_2',
            'curved': 'CURVED_CONNECTOR_3'
        }
        shape_type = shape_type_map.get(arrow_type, 'STRAIGHT_CONNECTOR_1')
        
        # Calculate length and position
        width = end_point['x'] - start_point['x']
        height = end_point['y'] - start_point['y']
        
        requests.append({
            'createShape': {
                'objectId': arrow_id,
                'shapeType': shape_type,
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': self._pt_to_emu(abs(width)), 'unit': 'EMU'},
                        'height': {'magnitude': self._pt_to_emu(abs(height)), 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1 if width >= 0 else -1,
                        'scaleY': 1 if height >= 0 else -1,
                        'translateX': self._pt_to_emu(start_point['x']),
                        'translateY': self._pt_to_emu(start_point['y']),
                        'unit': 'EMU'
                    }
                }
            }
        })
        
        # Apply arrow styling
        requests.append({
            'updateShapeProperties': {
                'objectId': arrow_id,
                'shapeProperties': {
                    'outline': {
                        'outlineFill': {
                            'solidFill': {
                                'color': {
                                    'rgbColor': self._hex_to_rgb(color)
                                }
                            }
                        },
                        'weight': {'magnitude': stroke_width, 'unit': 'PT'}
                    }
                },
                'fields': 'outline'
            }
        })
        
        return requests
    
    def _add_accent_box(self, slide_id: str, box_data: dict, index: int) -> list:
        """
        Generate batch requests for accent box (highlighted rectangle with text).
        
        Args:
            slide_id: Target slide object ID
            box_data: {text, position, size, backgroundColor, borderColor, borderWidth, textColor, fontSize}
            index: Box index for unique ID generation
            
        Returns:
            List of batch update requests
        """
        requests = []
        
        box_id = f"accent_{slide_id}_{index}"
        text = box_data.get('text', '')
        position = box_data.get('position', {'x': 50, 'y': 200})
        size = box_data.get('size', {'width': 300, 'height': 100})
        bg_color = box_data.get('backgroundColor', '#E0E7FF')
        border_color = box_data.get('borderColor', '#4F46E5')
        border_width = box_data.get('borderWidth', 2)
        text_color = box_data.get('textColor', '#1E1B4B')
        font_size = box_data.get('fontSize', 14)
        
        # Create rounded rectangle shape
        requests.append({
            'createShape': {
                'objectId': box_id,
                'shapeType': 'ROUND_RECTANGLE',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': self._pt_to_emu(size['width']), 'unit': 'EMU'},
                        'height': {'magnitude': self._pt_to_emu(size['height']), 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': self._pt_to_emu(position['x']),
                        'translateY': self._pt_to_emu(position['y']),
                        'unit': 'EMU'
                    }
                }
            }
        })
        
        # Apply background and border styling
        requests.append({
            'updateShapeProperties': {
                'objectId': box_id,
                'shapeProperties': {
                    'shapeBackgroundFill': {
                        'solidFill': {
                            'color': {'rgbColor': self._hex_to_rgb(bg_color)}
                        }
                    },
                    'outline': {
                        'outlineFill': {
                            'solidFill': {
                                'color': {'rgbColor': self._hex_to_rgb(border_color)}
                            }
                        },
                        'weight': {'magnitude': border_width, 'unit': 'PT'}
                    }
                },
                'fields': 'shapeBackgroundFill,outline'
            }
        })
        
        # Add text content if provided
        if text:
            requests.append({
                'insertText': {
                    'objectId': box_id,
                    'text': text,
                    'insertionIndex': 0
                }
            })
            
            # Style the text
            requests.append({
                'updateTextStyle': {
                    'objectId': box_id,
                    'textRange': {'type': 'ALL'},
                    'style': {
                        'fontSize': {'magnitude': font_size, 'unit': 'PT'},
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': self._hex_to_rgb(text_color)
                            }
                        }
                    },
                    'fields': 'fontSize,foregroundColor'
                }
            })
            
            # Center align text in box
            requests.append({
                'updateParagraphStyle': {
                    'objectId': box_id,
                    'textRange': {'type': 'ALL'},
                    'style': {'alignment': 'CENTER'},
                    'fields': 'alignment'
                }
            })
        
        return requests
