"""
Template Validator Module
==========================

Validates template structure and content.
"""

from typing import Dict, Any


class TemplateValidationError(Exception):
    """Raised when template validation fails."""
    pass


class TemplateValidator:
    """Validates design template format and required fields."""
    
    @staticmethod
    def validate_template(template: Dict[str, Any]) -> None:
        """
        Validate template structure.
        
        Args:
            template: Template dictionary to validate
            
        Raises:
            TemplateValidationError: If template is invalid
        """
        required_sections = ["metadata", "typography", "colors", "layouts"]
        
        for section in required_sections:
            if section not in template:
                raise TemplateValidationError(f"Missing required section: {section}")
        
        # Validate typography
        typo = template["typography"]
        required_roles = ["title", "heading", "body"]
        for role in required_roles:
            if role not in typo:
                raise TemplateValidationError(f"Missing typography for role: {role}")
        
        # Validate colors
        colors = template["colors"]
        required_colors = ["primary", "secondary", "background", "text"]
        for color in required_colors:
            if color not in colors:
                raise TemplateValidationError(f"Missing color: {color}")
