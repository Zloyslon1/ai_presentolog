"""
Layout Engine Module
====================

Calculates element positions and sizes based on template layout rules.
"""

from typing import Dict, Any


class LayoutEngine:
    """Applies layout rules to position elements on slides."""
    
    @staticmethod
    def apply_layout(element: Dict[str, Any], template: Dict[str, Any], slide_layout: str) -> Dict[str, Any]:
        """
        Apply template layout to element.
        
        Args:
            element: Parsed element with role
            template: Design template
            slide_layout: Slide layout type (TITLE, CONTENT, etc.)
            
        Returns:
            Element with updated position based on template
        """
        role = element.get('role', 'body').lower()
        layouts = template.get('layouts', {})
        
        # Determine which layout to use
        layout_key = 'title_slide' if slide_layout == 'TITLE' else 'content_slide'
        layout = layouts.get(layout_key, {})
        
        # Map role to position key
        position_key = f"{role}_position"
        if position_key not in layout:
            position_key = "body_position"  # Fallback
        
        new_position = layout.get(position_key, element.get('position', {}))
        
        # Update element position
        element['styled_position'] = new_position
        
        return element
