"""
Presentation Builder Module
============================

Creates new Google Slides presentations with applied design.
"""

from typing import Dict, Any
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
    
    def _ensure_service(self) -> None:
        """Ensure Slides API service is initialized."""
        if self.slides_service is None:
            self.slides_service = self.oauth_manager.build_service('slides', 'v1')
    
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
