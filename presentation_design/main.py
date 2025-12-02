"""
Automated Presentation Design System - Main Entry Point
========================================================

Phase 1: Core Design Engine

This module provides the main interface for processing presentations.
"""

import sys
import argparse
from pathlib import Path

from presentation_design.utils.config import get_config
from presentation_design.utils.logger import get_logger, setup_logging_from_config
from presentation_design.auth.oauth_manager import OAuthManager
from presentation_design.extraction.slides_extractor import SlidesExtractor
from presentation_design.templates.template_loader import TemplateLoader
from presentation_design.design.design_applicator import DesignApplicator
from presentation_design.generation.presentation_builder import PresentationBuilder

logger = get_logger(__name__)


def process_presentation(
    presentation_url: str,
    template_name: str = "default",
    config_path: str = None
) -> dict:
    """
    Process a presentation with design template.
    
    Args:
        presentation_url: Google Slides URL or presentation ID
        template_name: Name of template to apply
        config_path: Optional path to configuration file
        
    Returns:
        Dictionary with presentation_id, presentation_url, and title
    """
    try:
        logger.info(
            f"Starting presentation processing",
            operation="process_presentation",
            template=template_name
        )
        
        # Load configuration
        config = get_config(config_path)
        setup_logging_from_config(config)
        
        # Initialize OAuth manager
        auth_config = config.get_section('authentication')
        oauth_manager = OAuthManager(
            client_secrets_path=str(config.get_absolute_path(auth_config.get('client_secrets_path', 'credentials/client_secret.json'))),
            token_path=str(config.get_absolute_path(auth_config['token_path'])),
            scopes=auth_config['scopes']
        )
        
        # Authenticate
        oauth_manager.authenticate()
        
        # Extract presentation content
        logger.info("Extracting presentation content")
        extractor = SlidesExtractor(oauth_manager)
        extracted_data = extractor.extract_presentation(presentation_url)
        
        # Load template
        logger.info(f"Loading template: {template_name}")
        template_config = config.get_section('templates')
        template_loader = TemplateLoader(
            str(config.get_absolute_path(template_config['template_directory']))
        )
        template = template_loader.load_template(
            template_name or template_config['default_template']
        )
        
        # Apply design
        logger.info("Applying design template")
        applicator = DesignApplicator(template)
        designed_data = applicator.apply_design(extracted_data)
        
        # Build new presentation
        logger.info("Building new presentation")
        builder = PresentationBuilder(oauth_manager)
        result = builder.build_presentation(designed_data)
        
        logger.info(
            f"Presentation processing completed successfully",
            operation="process_presentation",
            presentation_id=result['presentation_id'],
            url=result['presentation_url']
        )
        
        return result
        
    except Exception as e:
        logger.error(
            f"Presentation processing failed: {e}",
            operation="process_presentation",
            exc_info=True
        )
        raise


def main():
    """Command-line interface for presentation design system."""
    parser = argparse.ArgumentParser(
        description="Automated Presentation Design System - Phase 1"
    )
    
    parser.add_argument(
        "presentation_url",
        nargs="?",
        help="Google Slides URL or presentation ID"
    )
    
    parser.add_argument(
        "-t", "--template",
        default="default",
        help="Template name to apply (default: default)"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available templates"
    )
    
    args = parser.parse_args()
    
    # List templates if requested
    if args.list_templates:
        config = get_config(args.config)
        template_config = config.get_section('templates')
        template_loader = TemplateLoader(
            str(config.get_absolute_path(template_config['template_directory']))
        )
        templates = template_loader.list_templates()
        print("Available templates:")
        for template in templates:
            print(f"  - {template}")
        return
    
    # Process presentation
    try:
        result = process_presentation(
            args.presentation_url,
            args.template,
            args.config
        )
        
        print(f"\n✓ Presentation designed successfully!")
        print(f"  Title: {result['title']}")
        print(f"  URL: {result['presentation_url']}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
