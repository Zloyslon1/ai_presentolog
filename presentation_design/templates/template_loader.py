"""
Template Loader Module
======================

Loads and manages design templates for presentations.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from .template_validator import TemplateValidator
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TemplateError(Exception):
    """Raised when template operations fail."""
    pass


class TemplateLoader:
    """
    Loads and caches design templates.
    
    Attributes:
        template_directory (Path): Directory containing template files
        templates_cache (Dict[str, Dict]): Cached loaded templates
    """
    
    def __init__(self, template_directory: str):
        """
        Initialize template loader.
        
        Args:
            template_directory: Path to templates directory
        """
        self.template_directory = Path(template_directory)
        self.templates_cache: Dict[str, Dict[str, Any]] = {}
        
        if not self.template_directory.exists():
            raise TemplateError(f"Template directory not found: {self.template_directory}")
    
    def load_template(self, template_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load template by name.
        
        Args:
            template_name: Name of template (without .json extension)
            use_cache: Whether to use cached template if available
            
        Returns:
            Template dictionary
            
        Raises:
            TemplateError: If template not found or invalid
        """
        # Check cache first
        if use_cache and template_name in self.templates_cache:
            logger.debug(f"Using cached template: {template_name}")
            return self.templates_cache[template_name]
        
        # Load from file
        template_path = self.template_directory / "designs" / f"{template_name}.json"
        
        if not template_path.exists():
            raise TemplateError(f"Template not found: {template_name}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # Validate template
            TemplateValidator.validate_template(template_data)
            
            # Cache template
            self.templates_cache[template_name] = template_data
            
            logger.info(f"Loaded template: {template_name}", operation="load_template")
            
            return template_data
            
        except json.JSONDecodeError as e:
            raise TemplateError(f"Invalid JSON in template {template_name}: {e}")
        except Exception as e:
            raise TemplateError(f"Failed to load template {template_name}: {e}")
    
    def list_templates(self) -> list:
        """
        List available template names.
        
        Returns:
            List of template names
        """
        designs_dir = self.template_directory / "designs"
        if not designs_dir.exists():
            return []
        
        templates = [f.stem for f in designs_dir.glob("*.json")]
        return templates
    
    def clear_cache(self) -> None:
        """Clear template cache."""
        self.templates_cache.clear()
        logger.debug("Template cache cleared")
