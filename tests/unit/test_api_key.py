"""
Test API Key access to Google Slides API
"""
import json
from googleapiclient.discovery import build

# Load API Key from config
config_file_path = 'config/config.json'
with open(config_file_path, 'r', encoding='utf-8') as f:
    config_data = json.load(f)

API_KEY = config_data.get('authentication', {}).get('api_key', '')

print(f"API Key loaded: {API_KEY[:10]}...")
print(f"API Key length: {len(API_KEY)}")

# Test with a public presentation
# Using Google's example presentation (should be public)
PRESENTATION_ID = '1EAYk18WDjIG-zp_0vLm3CsfQh_i8eXc67Jo2O9C6Vuc'  # Google's sample presentation

print(f"\nAttempting to access presentation: {PRESENTATION_ID}")
print("This is Google's sample presentation which should be public.")

try:
    # Build service
    service = build('slides', 'v1', developerKey=API_KEY)
    print("✓ Service built successfully")
    
    # Get presentation
    presentation = service.presentations().get(presentationId=PRESENTATION_ID).execute()
    print("✓ Successfully retrieved presentation data")
    
    # Print basic info
    title = presentation.get('title', 'No title')
    slides_count = len(presentation.get('slides', []))
    
    print(f"\nPresentation Info:")
    print(f"  Title: {title}")
    print(f"  Number of slides: {slides_count}")
    print(f"\n✓ API Key is working correctly!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    
    print("\n" + "="*60)
    print("TROUBLESHOOTING:")
    print("="*60)
    print("1. Make sure Google Slides API is enabled in Google Cloud Console:")
    print("   https://console.cloud.google.com/apis/library/slides.googleapis.com")
    print("")
    print("2. Check that your API Key has proper restrictions:")
    print("   - Go to: https://console.cloud.google.com/apis/credentials")
    print("   - Click on your API Key")
    print("   - Under 'API restrictions', select 'Restrict key'")
    print("   - Add 'Google Slides API' to the allowed APIs")
    print("")
    print("3. If the presentation is private, API Key won't work.")
    print("   You need OAuth for private presentations.")
