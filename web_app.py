"""
Flask Web Application for Presentation Design System
=====================================================

Provides web interface for processing Google Slides presentations
with design templates.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
from pathlib import Path
import threading
import uuid
import json
from datetime import datetime, timedelta
import sqlite3
import os

# Add presentation_design to path
sys.path.insert(0, str(Path(__file__).parent))

from presentation_design.main import process_presentation
from presentation_design.templates.template_loader import TemplateLoader
from presentation_design.utils.config import get_config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# In-memory storage for processing jobs (use database in production)
jobs = {}

# Database configuration
DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'presentation_jobs.db')

def init_database():
    """Initialize SQLite database with jobs table."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            presentation_url TEXT,
            template TEXT,
            status TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            slides_json TEXT,
            settings_json TEXT,
            generated_presentation_id TEXT,
            error TEXT
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON jobs(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_updated_at ON jobs(updated_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON jobs(status)')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def save_job_to_db(job_id, job_data):
    """Save job to database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Serialize complex fields to JSON
        slides_json = json.dumps(job_data.get('slides', []))
        settings_json = json.dumps(job_data.get('settings', {}))
        
        cursor.execute('''
            INSERT OR REPLACE INTO jobs 
            (id, presentation_url, template, status, created_at, updated_at, 
             slides_json, settings_json, generated_presentation_id, error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_id,
            job_data.get('url'),
            job_data.get('template'),
            job_data.get('status'),
            job_data.get('created_at'),
            datetime.now().isoformat(),
            slides_json,
            settings_json,
            job_data.get('generated_presentation_id'),
            job_data.get('error')
        ))
        
        conn.commit()
        conn.close()
        print(f"Job {job_id} saved to database")
        return True
    except Exception as e:
        print(f"Error saving job to database: {e}")
        import traceback
        traceback.print_exc()
        return False

def load_job_from_db(job_id):
    """Load job from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Convert row to dictionary
            job_data = dict(row)
            
            # Deserialize JSON fields
            if job_data.get('slides_json'):
                try:
                    job_data['slides'] = json.loads(job_data['slides_json'])
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse slides_json for job {job_id}")
                    job_data['slides'] = []
            else:
                job_data['slides'] = []
            
            if job_data.get('settings_json'):
                try:
                    job_data['settings'] = json.loads(job_data['settings_json'])
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse settings_json for job {job_id}")
                    job_data['settings'] = {}
            else:
                job_data['settings'] = {}
            
            # Map database fields to job format
            job_data['url'] = job_data.get('presentation_url')
            job_data['id'] = job_data.get('id')
            
            print(f"Job {job_id} loaded from database with {len(job_data.get('slides', []))} slides")
            return job_data
        
        return None
    except Exception as e:
        print(f"Error loading job from database: {e}")
        import traceback
        traceback.print_exc()
        return None

def list_all_jobs(limit=50, offset=0):
    """List all jobs from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, presentation_url, status, created_at, updated_at, 
                   generated_presentation_id,
                   CASE WHEN slides_json IS NOT NULL AND slides_json != '[]' THEN 1 ELSE 0 END as has_slides,
                   LENGTH(slides_json) as slides_json_length
            FROM jobs
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        rows = cursor.fetchall()
        
        # Get total count
        cursor.execute('SELECT COUNT(*) as total FROM jobs')
        total = cursor.fetchone()['total']
        
        conn.close()
        
        jobs_list = []
        for row in rows:
            job = dict(row)
            # Calculate slides count from JSON length estimation (rough)
            if job['slides_json_length']:
                job['slides_count'] = max(1, job['slides_json_length'] // 200)
            else:
                job['slides_count'] = 0
            jobs_list.append(job)
        
        return {'jobs': jobs_list, 'total': total, 'limit': limit, 'offset': offset}
    except Exception as e:
        print(f"Error listing jobs: {e}")
        import traceback
        traceback.print_exc()
        return {'jobs': [], 'total': 0, 'limit': limit, 'offset': offset}

def cleanup_old_jobs(days=30):
    """Delete jobs older than specified days."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        cursor.execute('DELETE FROM jobs WHERE created_at < ?', (cutoff_date.isoformat(),))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"Deleted {deleted_count} jobs older than {days} days")
        return deleted_count
    except Exception as e:
        print(f"Error cleaning up old jobs: {e}")
        return 0

# Initialize database on startup
init_database()


def get_template_list():
    """Get list of available templates."""
    config = get_config()
    template_config = config.get_section('templates')
    template_loader = TemplateLoader(
        str(config.get_absolute_path(template_config['template_directory']))
    )
    return template_loader.list_templates()


@app.route('/')
def index():
    """Main page with presentation processing form."""
    # Get available templates
    config = get_config()
    template_config = config.get_section('templates')
    template_loader = TemplateLoader(
        str(config.get_absolute_path(template_config['template_directory']))
    )
    templates = template_loader.list_templates()
    
    return render_template('index.html', templates=templates, jobs=jobs)


@app.route('/process', methods=['POST'])
def process():
    """Extract presentation and redirect to editor."""
    presentation_url = request.form.get('presentation_url')
    # Template selection removed - no longer needed
    
    if not presentation_url:
        return jsonify({'error': 'Presentation URL is required'}), 400
    
    # Create job for extraction
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        'id': job_id,
        'url': presentation_url,
        'template': None,  # No template needed
        'status': 'extracting',
        'created_at': datetime.now().isoformat(),
        'result': None,
        'error': None
    }
    
    # Extract content in background thread
    thread = threading.Thread(
        target=extract_for_editor,
        args=(job_id, presentation_url)
    )
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('extraction_status', job_id=job_id))


def extract_for_editor(job_id, presentation_url):
    """Extract presentation content for editor - preserve exact 1:1 structure from Google Slides."""
    try:
        from presentation_design.extraction.slides_extractor import SlidesExtractor
        from presentation_design.extraction.content_parser import ContentParser
        from presentation_design.auth.oauth_manager import OAuthManager
        from presentation_design.utils.config import get_config
        
        config = get_config()
        auth_config = config.get_section('authentication')
        
        # Authenticate
        oauth_manager = OAuthManager(
            client_secrets_path=str(config.get_absolute_path(auth_config.get('client_secrets_path', 'credentials/client_secret.json'))),
            token_path=str(config.get_absolute_path(auth_config['token_path'])),
            scopes=auth_config['scopes']
        )
        oauth_manager.authenticate()
        
        # Extract content in RAW MODE (preserve original text)
        extractor = SlidesExtractor(oauth_manager)
        raw_data = extractor.extract_presentation(presentation_url, raw_mode=True)
        
        print(f"DEBUG: Extracted {len(raw_data.get('slides', []))} slides in raw mode")
        
        # Convert raw data to editor format - ALL TEXT goes to mainText, preserve 1:1 order
        slides = []
        for idx, slide in enumerate(raw_data.get('slides', [])):
            raw_elements = slide.get('raw_elements', [])
            print(f"\n=== DEBUG: Slide {idx} ===")
            print(f"Total raw elements: {len(raw_elements)}")
            
            # Collect ALL text in the EXACT order it appears
            all_text_parts = []
            
            for i, element in enumerate(raw_elements):
                content = element.get('content', '')
                placeholder_type = element.get('placeholder_type', '')
                
                # Clean up special characters: replace vertical tab and other whitespace with regular space
                content = content.replace('\v', ' ').replace('\r', ' ')
                
                print(f"  Element {i}: type='{placeholder_type}', content_length={len(content)}, preview='{content[:80] if content else '(empty)'}...")
                
                # Add ALL non-empty content to mainText
                if content.strip():
                    all_text_parts.append(content)
                    print(f"    -> Added to mainText")
                else:
                    print(f"    -> Skipped (empty)")
            
            # Create editor slide: ALL text in mainText, title empty
            editor_slide = {
                'title': '',  # No title separation
                'mainText': '\n\n'.join(all_text_parts),  # ALL text here
                'secondaryText': '',
                'original_objectIds': [el.get('objectId', '') for el in raw_elements]
            }
            
            print(f"\n  RESULT: mainText_length={len(editor_slide['mainText'])}")
            print(f"  MainText preview: '{editor_slide['mainText'][:150]}...'" if editor_slide['mainText'] else "  MainText: (empty)")
            slides.append(editor_slide)
        
        print(f"DEBUG: Total slides for editor: {len(slides)}")
        print(f"\nDEBUG: Slide 0 data being saved to jobs:")
        if slides:
            print(f"  title: '{slides[0].get('title')}'")
            print(f"  mainText length: {len(slides[0].get('mainText', ''))}")
            print(f"  mainText preview: '{slides[0].get('mainText', '')[:100]}'")
        jobs[job_id]['status'] = 'extracted'
        jobs[job_id]['slides'] = slides
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        print(f"\nDEBUG: Saved to jobs['{job_id}']['slides'], count: {len(jobs[job_id]['slides'])}")
        
        # Save to database
        save_job_to_db(job_id, jobs[job_id])
        
    except Exception as e:
        print(f"Error extracting presentation: {e}")
        import traceback
        traceback.print_exc()
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        
        # Save error to database
        save_job_to_db(job_id, jobs[job_id])


def process_in_background(job_id, presentation_url, template_name):
    """Process presentation in background thread (direct processing without editor)."""
    try:
        result = process_presentation(
            presentation_url=presentation_url,
            template_name=template_name
        )
        
        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['result'] = result
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)
        jobs[job_id]['completed_at'] = datetime.now().isoformat()


@app.route('/slide_editor')
def slide_editor():
    """Visual slide editor."""
    # Get data from job instead of URL params
    job_id = request.args.get('job_id')
    
    if job_id:
        # Try to get from memory first, then from database
        job = jobs.get(job_id)
        if not job:
            # Try loading from database
            job = load_job_from_db(job_id)
            if job:
                # Cache in memory
                jobs[job_id] = job
        
        if job:
            presentation_url = job.get('url')
            template = job.get('template', 'default')
            slides_data = job.get('slides', [])
        else:
            # Job not found - show helpful error
            return render_template('job_not_found.html', job_id=job_id), 404
    else:
        # Fallback to old method
        presentation_url = request.args.get('presentation_url')
        template = request.args.get('template', 'default')
        slides_json = request.args.get('slides_json', '[]')
        try:
            slides_data = json.loads(slides_json)
        except:
            slides_data = []
    
    # Get available templates
    templates = get_template_list()
    
    print(f"\n=== SLIDE EDITOR DEBUG ===")
    print(f"Rendering slide_editor with {len(slides_data)} slides")
    if slides_data:
        print(f"First slide data:")
        print(f"  title: '{slides_data[0].get('title')}'")
        print(f"  mainText length: {len(slides_data[0].get('mainText', ''))}")
        print(f"  mainText preview: '{slides_data[0].get('mainText', '')[:100]}'")
    print(f"=========================\n")
    
    return render_template('slide_editor.html',
                          presentation_url=presentation_url,
                          template=template,
                          slides_data=slides_data,
                          templates=templates,
                          job_id=job_id)


@app.route('/extraction_status/<job_id>')
def extraction_status(job_id):
    """Show extraction status and redirect to editor when ready."""
    # Try memory first, then database
    job = jobs.get(job_id)
    if not job:
        job = load_job_from_db(job_id)
        if job:
            jobs[job_id] = job  # Cache in memory
    
    if not job:
        return "Job not found", 404
    
    # If extraction completed, redirect to editor
    if job['status'] == 'extracted':
        # Don't pass slides in URL - too long!
        # Instead, pass job_id and fetch slides from jobs dict
        return redirect(url_for('slide_editor',
                               job_id=job_id))
    
    # If error occurred, show error
    if job['status'] == 'error':
        return render_template('job_status.html', job=job)
    
    # Otherwise show loading page with auto-refresh
    return render_template('extraction_status.html', job=job)


@app.route('/process_slides', methods=['POST'])
def process_slides():
    """Process slides from editor and generate presentation."""
    data = request.get_json()
    slides = data.get('slides', [])
    template_name = data.get('template', 'default')
    presentation_url = data.get('presentation_url')
    existing_presentation_id = data.get('existing_presentation_id')  # For updates
    settings = data.get('settings', {})  # NEW: presentation settings
    
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        'id': job_id,
        'url': presentation_url,
        'template': template_name,
        'status': 'processing',
        'created_at': datetime.now().isoformat(),
        'result': None,
        'error': None,
        'existing_presentation_id': existing_presentation_id,
        'settings': settings,  # Store settings
        'slides': slides  # NEW: Store slides in job object
    }
    
    # Save to database immediately
    save_job_to_db(job_id, jobs[job_id])
    
    # Process with edited slides
    thread = threading.Thread(
        target=process_slides_in_background,
        args=(job_id, slides, template_name, existing_presentation_id)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'job_id': job_id})


@app.route('/process_direct', methods=['POST'])
def process_slides_direct():
    """Direct processing without editor (fallback)."""
    presentation_url = request.args.get('presentation_url')
    template_name = request.args.get('template', 'default')
    
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        'id': job_id,
        'url': presentation_url,
        'template': template_name,
        'status': 'processing',
        'created_at': datetime.now().isoformat(),
        'result': None,
        'error': None
    }
    
    # Process in background thread
    thread = threading.Thread(
        target=process_in_background,
        args=(job_id, presentation_url, template_name)
    )
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('job_status', job_id=job_id))


def process_slides_in_background(job_id, slides, template_name=None, existing_presentation_id=None):
    """Process edited slides in background - create presentation with advanced formatting."""
    try:
        from presentation_design.generation.presentation_builder import PresentationBuilder
        from presentation_design.utils.config import get_config
        from presentation_design.auth.oauth_manager import OAuthManager
        
        config = get_config()
        auth_config = config.get_section('authentication')
        oauth_manager = OAuthManager(
            client_secrets_path=str(config.get_absolute_path(auth_config.get('client_secrets_path', 'credentials/client_secret.json'))),
            token_path=str(config.get_absolute_path(auth_config['token_path'])),
            scopes=auth_config['scopes']
        )
        oauth_manager.authenticate()
        
        # Build presentation with advanced formatting
        builder = PresentationBuilder(oauth_manager)
        
        # Get presentation settings from job data
        settings = jobs[job_id].get('settings', {})
        
        print(f"Creating presentation with {len(slides)} slides")
        print(f"Settings: {settings}")
        
        result = builder.build_simple_presentation(
            slides_data=slides,
            title="New Presentation",
            settings=settings
        )
        
        jobs[job_id].update({
            'status': 'completed',
            'result': result,
            'generated_presentation_id': result.get('presentation_id')
        })
        
    except Exception as e:
        print(f"Error processing slides: {e}")
        import traceback
        traceback.print_exc()
        jobs[job_id].update({
            'status': 'error',
            'error': str(e)
        })


@app.route('/job/<job_id>')
def job_status(job_id):
    """Show job status page."""
    # Try memory first, then database
    job = jobs.get(job_id)
    if not job:
        job = load_job_from_db(job_id)
        if job:
            jobs[job_id] = job  # Cache in memory
    
    if not job:
        return "Job not found", 404
    
    return render_template('job_status.html', job=job)


@app.route('/api/job/<job_id>')
def api_job_status(job_id):
    """API endpoint for job status (for AJAX polling)."""
    job = jobs.get(job_id)
    if not job:
        # Try database
        job = load_job_from_db(job_id)
    
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Add metadata for frontend
    response = {
        'id': job.get('id'),
        'url': job.get('url'),
        'status': job.get('status'),
        'created_at': job.get('created_at'),
        'updated_at': job.get('updated_at'),
        'generated_presentation_id': job.get('generated_presentation_id'),
        'has_slides': len(job.get('slides', [])) > 0,
        'slides_count': len(job.get('slides', []))
    }
    
    return jsonify(response)


@app.route('/api/save_slides', methods=['POST'])
def api_save_slides():
    """Save slides and settings to database."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        job_id = data.get('job_id')
        slides = data.get('slides', [])
        settings = data.get('settings', {})
        
        if not job_id:
            return jsonify({'error': 'job_id is required'}), 400
        
        # Get or create job
        job = jobs.get(job_id)
        if not job:
            # Try loading from database
            job = load_job_from_db(job_id)
            if not job:
                # Create new job entry
                job = {
                    'id': job_id,
                    'url': data.get('presentation_url', ''),
                    'template': data.get('template', 'default'),
                    'status': 'editing',
                    'created_at': datetime.now().isoformat(),
                    'slides': slides,
                    'settings': settings
                }
                jobs[job_id] = job
        
        # Update job with new slides and settings
        jobs[job_id]['slides'] = slides
        jobs[job_id]['settings'] = settings
        jobs[job_id]['updated_at'] = datetime.now().isoformat()
        
        # Save to database
        success = save_job_to_db(job_id, jobs[job_id])
        
        if success:
            return jsonify({
                'status': 'saved',
                'timestamp': jobs[job_id]['updated_at'],
                'slides_count': len(slides)
            })
        else:
            return jsonify({'error': 'Failed to save to database'}), 500
            
    except Exception as e:
        print(f"Error in api_save_slides: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/load_slides', methods=['GET'])
def api_load_slides():
    """Load slides and settings from database."""
    try:
        job_id = request.args.get('job_id')
        
        if not job_id:
            return jsonify({'error': 'job_id parameter is required'}), 400
        
        # Try memory first, then database
        job = jobs.get(job_id)
        if not job:
            job = load_job_from_db(job_id)
            if job:
                # Cache in memory
                jobs[job_id] = job
        
        if not job:
            return jsonify({
                'slides': [],
                'settings': None,
                'message': 'No saved slides found'
            })
        
        return jsonify({
            'slides': job.get('slides', []),
            'settings': job.get('settings', {}),
            'last_updated': job.get('updated_at', job.get('created_at')),
            'status': job.get('status')
        })
        
    except Exception as e:
        print(f"Error in api_load_slides: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/history')
def history():
    """Show processing history from database."""
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    limit = 50
    offset = (page - 1) * limit
    
    # Load jobs from database
    result = list_all_jobs(limit=limit, offset=offset)
    jobs_list = result['jobs']
    total = result['total']
    
    # Calculate pagination info
    total_pages = (total + limit - 1) // limit
    has_next = page < total_pages
    has_prev = page > 1
    
    return render_template('history.html', 
                          jobs=jobs_list,
                          page=page,
                          total_pages=total_pages,
                          has_next=has_next,
                          has_prev=has_prev,
                          total=total)


if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    print("="*60)
    print("Presentation Design System - Web Interface")
    print("="*60)
    print("\nStarting server at http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    # Use debug mode only for local development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, port=5000, host='0.0.0.0')
