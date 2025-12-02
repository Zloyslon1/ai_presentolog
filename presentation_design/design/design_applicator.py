"""
Design Applicator Module
=========================

Applies design templates to extracted presentation content.
"""

from typing import Dict, Any
from .layout_engine import LayoutEngine
from ..extraction.content_analyzer import ContentAnalyzer
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DesignApplicator:
    """
    Applies design templates to presentation content.
    
    Transforms extracted presentation data by applying typography,
    colors, and layout from a template.
    """
    
    def __init__(self, template: Dict[str, Any]):
        """
        Initialize design applicator with template.
        
        Args:
            template: Loaded design template dictionary
        """
        self.template = template
    
    def apply_design(self, presentation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply design to complete presentation.
        
        Args:
            presentation_data: Parsed presentation data
            
        Returns:
            Designed presentation specification
        """
        designed = {
            'presentation_id': presentation_data.get('presentation_id'),
            'title': presentation_data.get('title'),
            'template_name': self.template['metadata']['name'],
            'slides': []
        }
        
        for slide in presentation_data.get('slides', []):
            designed_slide = self._apply_to_slide(slide)
            designed['slides'].append(designed_slide)
        
        logger.info(
            f"Applied design template '{self.template['metadata']['name']}' to {len(designed['slides'])} slides",
            operation="apply_design",
            template=self.template['metadata']['name']
        )
        
        return designed
    
    def _apply_to_slide(self, slide: Dict[str, Any]) -> Dict[str, Any]:
        """Apply design to individual slide."""
        designed_slide = {
            'index': slide.get('index'),
            'slide_id': slide.get('slide_id'),
            'layout_type': slide.get('layout_type'),
            'background_color': self.template['colors']['background'],
            'elements': []
        }
        
        for element in slide.get('elements', []):
            # Process element with structured content handling
            designed_elements = self._apply_to_element(element, slide['layout_type'])
            
            # _apply_to_element now returns a list (for split lists)
            if isinstance(designed_elements, list):
                designed_slide['elements'].extend(designed_elements)
            else:
                designed_slide['elements'].append(designed_elements)
        
        return designed_slide
    
    def _apply_to_element(self, element: Dict[str, Any], slide_layout: str) -> Any:
        """
        Apply design to individual element.
        
        Returns either a single designed element or a list of elements
        (when splitting structured content like lists).
        """
        role = element.get('role', 'body').lower()
        
        # Get typography for role
        typography = self.template['typography'].get(role, self.template['typography']['body'])
        
        # Get color for role
        color_map = {
            'title': 'primary',
            'subtitle': 'secondary',
            'heading': 'primary',
            'body': 'text',
            'footer': 'text_light'
        }
        color_key = color_map.get(role, 'text')
        color = self.template['colors'][color_key]
        
        # Check if element has structured content (lists)
        text_analysis = element.get('text_analysis', {})
        content_type = text_analysis.get('content_type', 'plain')
        
        # Handle structured content (lists)
        if content_type in ['numbered_list', 'bullet_list']:
            return self._handle_list_element(
                element, 
                text_analysis, 
                typography, 
                color, 
                slide_layout
            )
        
        # Handle plain content
        formatted_content = element['content'].strip()
        
        # Create designed element
        designed_element = {
            'content': formatted_content,
            'role': element['role'],
            'font_family': typography['font_family'],
            'font_size': typography['font_size'],
            'font_weight': typography['font_weight'],
            'line_height': typography['line_height'],
            'color': color,
            'original_position': element.get('position', {}),
            'content_type': content_type
        }
        
        # Apply layout
        designed_element = LayoutEngine.apply_layout(designed_element, self.template, slide_layout)
        
        return designed_element
    
    def _handle_list_element(
        self, 
        element: Dict[str, Any], 
        text_analysis: Dict[str, Any],
        typography: Dict[str, Any],
        color: str,
        slide_layout: str
    ) -> Dict[str, Any]:
        """
        Handle list elements with proper formatting.
        
        Returns a single element with properly formatted list content.
        """
        items = text_analysis.get('items', [])
        content_type = text_analysis.get('content_type')
        
        # Format list with consistent markers
        formatted_content = ContentAnalyzer.format_list_items(items, content_type)
        
        # Use slightly smaller font for lists
        list_typography = typography.copy()
        if element.get('role', '').upper() != 'TITLE':
            list_typography['font_size'] = max(14, typography['font_size'] - 2)
        
        designed_element = {
            'content': formatted_content,
            'role': element['role'],
            'font_family': list_typography['font_family'],
            'font_size': list_typography['font_size'],
            'font_weight': list_typography['font_weight'],
            'line_height': list_typography.get('line_height', 1.6),  # More spacing for lists
            'color': color,
            'original_position': element.get('position', {}),
            'content_type': content_type,
            'is_list': True
        }
        
        # Apply layout with list-specific positioning
        designed_element = LayoutEngine.apply_layout(designed_element, self.template, slide_layout)
        
        return designed_element
