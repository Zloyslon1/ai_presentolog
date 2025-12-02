"""
Local Testing Script for Presentation Design System
===================================================

This script helps you test the implementation locally without needing
a real Google Slides presentation initially.
"""

import sys
from pathlib import Path

# Add presentation_design to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")
    
    try:
        from presentation_design.utils.config import Config
        print("✓ Config module imported")
        
        from presentation_design.utils.logger import get_logger
        print("✓ Logger module imported")
        
        from presentation_design.utils.retry import exponential_backoff
        print("✓ Retry module imported")
        
        from presentation_design.templates.template_loader import TemplateLoader
        print("✓ Template loader imported")
        
        from presentation_design.templates.template_validator import TemplateValidator
        print("✓ Template validator imported")
        
        print("\n✅ All modules imported successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        return False


def test_configuration():
    """Test configuration loading."""
    print("\n" + "="*50)
    print("Testing configuration...")
    
    try:
        from presentation_design.utils.config import Config
        
        config = Config(
            config_path="config/config.json",
            environment="development"
        )
        
        print(f"✓ Configuration loaded: {config}")
        print(f"✓ Template directory: {config.get('templates.template_directory')}")
        print(f"✓ Log level: {config.get('logging.log_level')}")
        
        print("\n✅ Configuration test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_templates():
    """Test template loading."""
    print("\n" + "="*50)
    print("Testing template system...")
    
    try:
        from presentation_design.utils.config import Config
        from presentation_design.templates.template_loader import TemplateLoader
        
        config = Config(config_path="config/config.json")
        template_dir = config.get_absolute_path(
            config.get('templates.template_directory')
        )
        
        loader = TemplateLoader(str(template_dir))
        
        # List templates
        templates = loader.list_templates()
        print(f"✓ Available templates: {templates}")
        
        # Load default template
        default_template = loader.load_template("default")
        print(f"✓ Loaded template: {default_template['metadata']['name']}")
        print(f"  - Colors: {list(default_template['colors'].keys())}")
        print(f"  - Typography roles: {list(default_template['typography'].keys())}")
        
        # Load corporate_blue template
        corporate_template = loader.load_template("corporate_blue")
        print(f"✓ Loaded template: {corporate_template['metadata']['name']}")
        print(f"  - Primary color: {corporate_template['colors']['primary']}")
        
        print("\n✅ Template system test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Template error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_logging():
    """Test logging system."""
    print("\n" + "="*50)
    print("Testing logging system...")
    
    try:
        from presentation_design.utils.logger import get_logger
        
        logger = get_logger(__name__)
        
        logger.info("Test info message")
        logger.debug("Test debug message")
        logger.warning("Test warning message")
        
        print("✓ Logger created and messages logged")
        print(f"✓ Check logs directory for output")
        
        print("\n✅ Logging system test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Logging error: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_credentials():
    """Check if OAuth credentials exist."""
    print("\n" + "="*50)
    print("Checking OAuth credentials...")
    
    creds_path = Path("credentials/client_secret.json")
    
    if creds_path.exists():
        print(f"✓ OAuth credentials found at: {creds_path}")
        print("✅ Ready to authenticate with Google!")
        return True
    else:
        print(f"⚠ OAuth credentials NOT found at: {creds_path}")
        print("\nTo set up credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create OAuth 2.0 credentials (Desktop app)")
        print("3. Download as client_secret.json")
        print("4. Place in credentials/ directory")
        return False


def main():
    """Run all local tests."""
    print("="*50)
    print("PRESENTATION DESIGN SYSTEM - LOCAL TESTING")
    print("="*50)
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Configuration", test_configuration()))
    results.append(("Template System", test_templates()))
    results.append(("Logging System", test_logging()))
    results.append(("OAuth Credentials", check_credentials()))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! System is ready for use.")
        print("\nNext steps:")
        print("1. Set up OAuth credentials (if not done)")
        print("2. Run: python -m presentation_design.main --list-templates")
        print("3. Process a presentation with a real Google Slides URL")
    else:
        print("\n⚠ Some tests failed. Please fix issues above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
