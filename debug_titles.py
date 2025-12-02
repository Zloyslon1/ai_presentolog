"""
Debug script to check title detection and formatting.
"""
import sys
import json
from presentation_design.utils.config import get_config
from presentation_design.auth.oauth_manager import OAuthManager
from presentation_design.extraction.slides_extractor import SlidesExtractor
from presentation_design.templates.template_loader import TemplateLoader
from presentation_design.design.design_applicator import DesignApplicator

def debug_titles(presentation_url: str):
    """Debug title detection and styling."""
    
    # Load configuration
    config = get_config()
    
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
    
    # Check first 3 slides
    for idx in range(min(3, len(extracted_data['slides']))):
        slide = extracted_data['slides'][idx]
        print(f"\n--- SLIDE {idx} ---")
        print(f"Layout type: {slide['layout_type']}")
        print(f"Elements: {len(slide['elements'])}")
        
        for elem_idx, element in enumerate(slide['elements']):
            print(f"\n  Element {elem_idx}:")
            print(f"    Role: {element['role']}")
            print(f"    Content (first 100 chars): {element['content'][:100]}")
            
            # Check if content analyzer added analysis
            if 'text_analysis' in element:
                analysis = element['text_analysis']
                print(f"    Content type: {analysis['content_type']}")
                print(f"    Has emphasis: {analysis['has_emphasis']}")
                print(f"    Is title case: {analysis['is_title_case']}")
    
    # Load template and apply design
    print("\n=== APPLYING DESIGN ===")
    template_config = config.get_section('templates')
    template_loader = TemplateLoader(
        str(config.get_absolute_path(template_config['template_directory']))
    )
    template = template_loader.load_template('corporate_blue')
    
    applicator = DesignApplicator(template)
    designed_data = applicator.apply_design(extracted_data)
    
    # Check designed slides
    for idx in range(min(3, len(designed_data['slides']))):
        slide = designed_data['slides'][idx]
        print(f"\n--- DESIGNED SLIDE {idx} ---")
        print(f"Background color: {slide['background_color']}")
        print(f"Elements: {len(slide['elements'])}")
        
        for elem_idx, element in enumerate(slide['elements']):
            print(f"\n  Designed Element {elem_idx}:")
            print(f"    Role: {element['role']}")
            print(f"    Font family: {element['font_family']}")
            print(f"    Font size: {element['font_size']}")
            print(f"    Font weight: {element['font_weight']}")
            print(f"    Color: {element['color']}")
            if 'styled_position' in element:
                print(f"    Position: {element['styled_position']}")
            print(f"    Content (first 50 chars): {element['content'][:50]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_titles.py <presentation_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    debug_titles(url)
