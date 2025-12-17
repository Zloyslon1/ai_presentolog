"""
Test Service Account access to Google Slides API
"""
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to service account credentials
SERVICE_ACCOUNT_FILE = os.path.join('credentials', 'service_account.json')

# Check if file exists
if not os.path.exists(SERVICE_ACCOUNT_FILE):
    print(f"❌ Service account file not found: {SERVICE_ACCOUNT_FILE}")
    print("\nPlease follow the setup guide in SETUP_SERVICE_ACCOUNT.md")
    print("to create and download the service account JSON file.")
    exit(1)

print(f"✓ Service account file found: {SERVICE_ACCOUNT_FILE}")

# Load and display service account info
try:
    with open(SERVICE_ACCOUNT_FILE, 'r') as f:
        sa_data = json.load(f)
    
    print(f"\nService Account Info:")
    print(f"  Email: {sa_data.get('client_email', 'N/A')}")
    print(f"  Project ID: {sa_data.get('project_id', 'N/A')}")
    print(f"  Type: {sa_data.get('type', 'N/A')}")
except Exception as e:
    print(f"❌ Error reading service account file: {e}")
    exit(1)

# Create credentials
try:
    SCOPES = [
        'https://www.googleapis.com/auth/presentations.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    print(f"✓ Credentials created successfully")
except Exception as e:
    print(f"❌ Error creating credentials: {e}")
    exit(1)

# Build service
try:
    service = build('slides', 'v1', credentials=credentials)
    print(f"✓ Google Slides service built successfully")
except Exception as e:
    print(f"❌ Error building service: {e}")
    exit(1)

# Test with a public presentation
# Using Google's example presentation (should be public)
PRESENTATION_ID = '1EAYk18WDjIG-zp_0vLm3CsfQh_i8eXc67Jo2O9C6Vuc'

print(f"\n{'='*60}")
print(f"Testing access to Google's sample presentation...")
print(f"Presentation ID: {PRESENTATION_ID}")
print(f"{'='*60}\n")

try:
    # Get presentation
    presentation = service.presentations().get(presentationId=PRESENTATION_ID).execute()
    
    # Print basic info
    title = presentation.get('title', 'No title')
    slides_count = len(presentation.get('slides', []))
    
    print(f"✓ Successfully retrieved presentation!\n")
    print(f"Presentation Info:")
    print(f"  Title: {title}")
    print(f"  Number of slides: {slides_count}")
    
    print(f"\n{'='*60}")
    print(f"✅ SERVICE ACCOUNT IS WORKING CORRECTLY!")
    print(f"{'='*60}\n")
    
    print(f"Service account email: {sa_data.get('client_email')}")
    print(f"\nYou can now:")
    print(f"  1. Access public presentations (anyone with the link)")
    print(f"  2. Access presentations where this email has viewer access")
    
except Exception as e:
    print(f"❌ Error accessing presentation: {e}")
    import traceback
    traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"TROUBLESHOOTING:")
    print(f"{'='*60}")
    print(f"1. Make sure Google Slides API is enabled:")
    print(f"   https://console.cloud.google.com/apis/library/slides.googleapis.com")
    print(f"")
    print(f"2. For public presentations:")
    print(f"   - Open the presentation in Google Slides")
    print(f"   - Click Share → Anyone with the link → Viewer")
    print(f"")
    print(f"3. For private presentations:")
    print(f"   - Share the presentation with: {sa_data.get('client_email')}")
    print(f"   - Give it Viewer access")
