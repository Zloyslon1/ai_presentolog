"""
Content Parser Module
=====================

Analyzes extracted presentation content to identify structural roles
and hierarchy of text elements.
"""

from typing import Dict, Any, List
from ..utils.logger import get_logger
from .content_analyzer import ContentAnalyzer
from .text_splitter import TextSplitter

logger = get_logger(__name__)


class ContentParser:
    """
    Parses presentation content to identify structural roles.
    
    Determines whether text elements are titles, headings, body text,
    or footer elements based on position, size, and context.
    """
    
    @staticmethod
    def parse_presentation(presentation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse complete presentation structure.
        
        Args:
            presentation_data: Raw presentation data from Slides API
            
        Returns:
            Parsed presentation with identified roles
        """
        parsed = {
            'presentation_id': presentation_data.get('presentationId'),
            'title': presentation_data.get('title'),
            'slides': []
        }
        
        slides = presentation_data.get('slides', [])
        
        for idx, slide in enumerate(slides):
            parsed_slide = ContentParser.parse_slide(slide, idx)
            parsed['slides'].append(parsed_slide)
        
        logger.info(
            f"Parsed presentation with {len(parsed['slides'])} slides",
            operation="parse_presentation",
            presentation_id=parsed['presentation_id']
        )
        
        return parsed
    
    @staticmethod
    def parse_slide(slide_data: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Parse individual slide to identify element roles.
        
        Args:
            slide_data: Raw slide data from API
            index: Slide position index
            
        Returns:
            Parsed slide with element roles
        """
        parsed_slide = {
            'index': index,
            'slide_id': slide_data.get('objectId'),
            'layout_type': ContentParser._determine_layout_type(slide_data, index),
            'elements': []
        }
        
        # NEW APPROACH: Extract ALL text from slide first
        all_text = ContentParser._extract_all_slide_text(slide_data)
        
        if all_text:
            # Split text into logical components
            components = TextSplitter.split_slide_text(all_text, index)
            
            # Convert components to elements
            for comp in components:
                element = {
                    'type': 'TEXT',
                    'content': comp['content'],
                    'role': comp['role'],
                    'position': {},  # Will be set by layout engine
                    'size': {},
                }
                
                # Add list metadata if present
                if comp.get('is_list'):
                    element['text_analysis'] = {
                        'content_type': comp.get('content_type'),
                        'items': comp.get('items', []),
                        'has_emphasis': False,
                        'is_title_case': False,
                        'original_text': comp['content']
                    }
                else:
                    # Analyze non-list content
                    element['text_analysis'] = ContentAnalyzer.analyze_text_structure(
                        comp['content']
                    )
                
                parsed_slide['elements'].append(element)
        
        logger.info(
            f"Parsed slide {index} with {len(parsed_slide['elements'])} components",
            operation="parse_slide"
        )
        
        return parsed_slide
    
    @staticmethod
    def _extract_all_slide_text(slide_data: Dict[str, Any]) -> str:
        """Extract all text from slide as a single string."""
        page_elements = slide_data.get('pageElements', [])
        text_parts = []
        
        for element in page_elements:
            if 'shape' in element:
                shape = element['shape']
                if 'text' in shape:
                    text = ContentParser._extract_text(shape['text'])
                    if text.strip():
                        text_parts.append(text.strip())
        
        return '\n'.join(text_parts)
    
    @staticmethod
    def extract_raw_slide_elements(slide_data: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Extract raw text elements from slide without any structural analysis.
        
        This method preserves original text exactly as it appears in the source
        Google Slides presentation, without applying TextSplitter or ContentAnalyzer.
        
        Args:
            slide_data: Raw slide data from Google Slides API
            index: Slide position index
            
        Returns:
            Dict with slide metadata and raw_elements list
        """
        raw_slide = {
            'index': index,
            'slide_id': slide_data.get('objectId'),
            'raw_elements': []
        }
        
        page_elements = slide_data.get('pageElements', [])
        
        for element in page_elements:
            # Only process shapes with text
            if 'shape' not in element:
                continue
                
            shape = element['shape']
            if 'text' not in shape:
                continue
            
            # Extract text content (preserve exact formatting)
            text_content = ContentParser._extract_text(shape['text'])
            
            if not text_content.strip():
                continue
            
            # Get placeholder type (if exists)
            placeholder = shape.get('placeholder', {})
            placeholder_type = placeholder.get('type', '')
            
            # Get position for ordering
            transform = element.get('transform', {})
            position_y = transform.get('translateY', 0)
            position_x = transform.get('translateX', 0)
            
            raw_element = {
                'type': 'TEXT',
                'content': text_content,
                'objectId': element.get('objectId', ''),
                'position_y': position_y,
                'position_x': position_x,
                'placeholder_type': placeholder_type
            }
            
            raw_slide['raw_elements'].append(raw_element)
        
        # Sort by vertical position (top to bottom), then horizontal (left to right)
        raw_slide['raw_elements'].sort(key=lambda e: (e['position_y'], e['position_x']))
        
        logger.info(
            f"Extracted {len(raw_slide['raw_elements'])} raw elements from slide {index}",
            operation="extract_raw_slide_elements"
        )
        
        return raw_slide
    
    @staticmethod
    def _determine_layout_type(slide_data: Dict[str, Any], index: int) -> str:
        """Determine slide layout type based on position and content."""
        # First slide is typically title slide
        if index == 0:
            return 'TITLE'
        
        # Check if slide has specific layout properties
        layout_properties = slide_data.get('slideProperties', {})
        layout_object_id = layout_properties.get('layoutObjectId', '')
        
        # Try to infer from layout name
        if 'title' in layout_object_id.lower():
            return 'TITLE'
        elif 'section' in layout_object_id.lower():
            return 'SECTION'
        
        return 'CONTENT'
    
    @staticmethod
    def parse_element(element_data: Dict[str, Any], slide_layout: str) -> Dict[str, Any]:
        """
        Parse individual page element.
        
        Args:
            element_data: Raw element data
            slide_layout: Parent slide layout type
            
        Returns:
            Parsed element or None if not a text element
        """
        # Only process text elements
        if 'shape' not in element_data:
            return None
        
        shape = element_data['shape']
        if 'text' not in shape:
            return None
        
        # Extract text content
        text_content = ContentParser._extract_text(shape['text'])
        
        if not text_content.strip():
            return None
        
        # Determine role based on placeholder type or position
        role = ContentParser._determine_role(element_data, slide_layout)
        
        # Extract transform properties for position
        transform = element_data.get('transform', {})
        
        parsed_element = {
            'type': 'TEXT',
            'content': text_content,
            'role': role,
            'position': {
                'translateX': transform.get('translateX', 0),
                'translateY': transform.get('translateY', 0),
                'scaleX': transform.get('scaleX', 1),
                'scaleY': transform.get('scaleY', 1),
            },
            'size': element_data.get('size', {}),
            'original_data': element_data
        }
        
        return parsed_element
    
    @staticmethod
    def _extract_text(text_data: Dict[str, Any]) -> str:
        """Extract plain text from text run structure."""
        text_elements = text_data.get('textElements', [])
        text_parts = []
        
        for elem in text_elements:
            if 'textRun' in elem:
                content = elem['textRun'].get('content', '')
                text_parts.append(content)
        
        return ''.join(text_parts)
    
    @staticmethod
    def _determine_role(element_data: Dict[str, Any], slide_layout: str) -> str:
        """
        Determine structural role of text element.
        
        Returns:
            One of: TITLE, SUBTITLE, HEADING, BODY, FOOTER
        """
        shape = element_data.get('shape', {})
        placeholder = shape.get('placeholder', {})
        placeholder_type = placeholder.get('type', '')
        
        # Check placeholder type first
        if placeholder_type == 'TITLE' or placeholder_type == 'CENTERED_TITLE':
            return 'TITLE'
        elif placeholder_type == 'SUBTITLE':
            return 'SUBTITLE'
        elif placeholder_type == 'BODY':
            return 'BODY'
        
        # Infer from slide layout
        if slide_layout == 'TITLE':
            # On title slides, first is title, second is subtitle
            return 'TITLE'  # Could be refined based on position
        
        # Check position (footer is at bottom)
        transform = element_data.get('transform', {})
        y_position = transform.get('translateY', 0)
        
        # If very low on slide, likely footer
        if y_position > 4000000:  # EMUs - approximate bottom position
            return 'FOOTER'
        
        # Default to body
        return 'BODY'
