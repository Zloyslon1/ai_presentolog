"""
Debug script to examine the design data structure.
"""
import json
import sys
from presentation_design.utils.config import get_config
from presentation_design.utils.logger import get_logger, setup_logging_from_config
from presentation_design.auth.oauth_manager import OAuthManager
from presentation_design.extraction.slides_extractor import SlidesExtractor
from presentation_design.templates.template_loader import TemplateLoader
from presentation_design.design.design_applicator import DesignApplicator

logger = get_logger(__name__)

def debug_design_structure(presentation_url: str, template_name: str = "default"):
    """Debug the design structure to see what data is being generated."""
    
    # Load configuration
    config = get_config()
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
    print("\n=== EXTRACTING PRESENTATION ===")
    extractor = SlidesExtractor(oauth_manager)
    extracted_data = extractor.extract_presentation(presentation_url)
    
    print(f"\nExtracted {len(extracted_data.get('slides', []))} slides")
    print(f"First slide structure:")
    if extracted_data.get('slides'):
        first_slide = extracted_data['slides'][0]
        print(json.dumps(first_slide, indent=2))
    
    # Load template
    print(f"\n=== LOADING TEMPLATE: {template_name} ===")
    template_config = config.get_section('templates')
    template_loader = TemplateLoader(
        str(config.get_absolute_path(template_config['template_directory']))
    )
    template = template_loader.load_template(template_name)
    print(json.dumps(template, indent=2))
    
    # Apply design
    print("\n=== APPLYING DESIGN ===")
    applicator = DesignApplicator(template)
    designed_data = applicator.apply_design(extracted_data)
    
    print(f"\nDesigned {len(designed_data.get('slides', []))} slides")
    print(f"First slide design structure:")
    if designed_data.get('slides'):
        first_slide_designed = designed_data['slides'][0]
        print(json.dumps(first_slide_designed, indent=2, ensure_ascii=False))
    
    return designed_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_design.py <presentation_url> [template_name]")
        sys.exit(1)
    
    url = sys.argv[1]
    template = sys.argv[2] if len(sys.argv) > 2 else "default"
    
    debug_design_structure(url, template)
