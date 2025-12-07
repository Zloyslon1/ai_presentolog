"""
Flask Web Application for Presentation Design System
=====================================================

Provides web interface for processing Google Slides presentations
with design templates.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import sys
from pathlib import Path
import threading
import uuid
import json
from datetime import datetime, timedelta
import sqlite3
import os
from functools import wraps

# Add presentation_design to path
sys.path.insert(0, str(Path(__file__).parent))

from presentation_design.main import process_presentation
from presentation_design.templates.template_loader import TemplateLoader
from presentation_design.utils.config import get_config
from presentation_design.auth.web_oauth import WebOAuthManager

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize Web OAuth Manager
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), 'credentials', 'client_secret.json')
oauth_manager = WebOAuthManager(CLIENT_SECRETS_FILE)

# In-memory storage for processing jobs (use database in production)
jobs = {}

# Database configuration
DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'presentation_jobs.db')

def init_database():
    """Initialize SQLite database with jobs and user_sessions tables."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create user_sessions table for per-user authentication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_id TEXT PRIMARY KEY,
            user_email TEXT,
            credentials_json TEXT,
            created_at TIMESTAMP,
            last_used_at TIMESTAMP,
            expires_at TIMESTAMP
        )
    ''')
    
    # Create jobs table
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
            error TEXT,
            session_id TEXT,
            FOREIGN KEY (session_id) REFERENCES user_sessions(session_id)
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON jobs(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_updated_at ON jobs(updated_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON jobs(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_session_id ON jobs(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_email ON user_sessions(user_email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON user_sessions(expires_at)')
    
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
             slides_json, settings_json, generated_presentation_id, error, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            job_data.get('error'),
            job_data.get('session_id')  # Add session_id
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
    """List all jobs from database (admin only - not for regular use)."""
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


def list_user_jobs(session_id, limit=50, offset=0):
    """List jobs for a specific user by session_id."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT j.id, j.presentation_url, j.status, j.created_at, j.updated_at, 
                   j.generated_presentation_id, j.template,
                   CASE WHEN j.slides_json IS NOT NULL AND j.slides_json != '[]' THEN 1 ELSE 0 END as has_slides,
                   LENGTH(j.slides_json) as slides_json_length
            FROM jobs j
            WHERE j.session_id = ?
            ORDER BY j.created_at DESC
            LIMIT ? OFFSET ?
        ''', (session_id, limit, offset))
        
        rows = cursor.fetchall()
        
        # Get total count for this user
        cursor.execute('SELECT COUNT(*) as total FROM jobs WHERE session_id = ?', (session_id,))
        total = cursor.fetchone()['total']
        
        conn.close()
        
        jobs_list = []
        for row in rows:
            job = dict(row)
            # Calculate slides count from JSON length estimation (rough)
            if job.get('slides_json_length'):
                job['slides_count'] = max(1, job['slides_json_length'] // 200)
            else:
                job['slides_count'] = 0
            jobs_list.append(job)
        
        return {'jobs': jobs_list, 'total': total, 'limit': limit, 'offset': offset}
    except Exception as e:
        print(f"Error listing user jobs: {e}")
        import traceback
        traceback.print_exc()
        return {'jobs': [], 'total': 0, 'limit': limit, 'offset': offset}


def get_job_owner(job_id):
    """Get the session_id (owner) of a job."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT session_id FROM jobs WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row['session_id']
        return None
    except Exception as e:
        print(f"Error getting job owner: {e}")
        return None


def user_owns_job(job_id, session_id):
    """Check if a user (session) owns a specific job."""
    # Check in-memory jobs first
    job = jobs.get(job_id)
    if job:
        return job.get('session_id') == session_id
    
    # Check database
    owner = get_job_owner(job_id)
    return owner == session_id

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


def get_session_id():
    """Get current session ID from Flask session."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']


def save_user_session(session_id, user_email, credentials):
    """Save user session to database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        credentials_json = json.dumps(credentials)
        now = datetime.now()
        expires_at = now + timedelta(hours=24)  # 24 hour session
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_sessions
            (session_id, user_email, credentials_json, created_at, last_used_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            user_email,
            credentials_json,
            now.isoformat(),
            now.isoformat(),
            expires_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
        print(f"User session {session_id} saved for {user_email}")
        return True
    except Exception as e:
        print(f"Error saving user session: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_user_session(session_id):
    """Load user session from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_sessions WHERE session_id = ?', (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            session_data = dict(row)
            # Check if session expired
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if expires_at < datetime.now():
                print(f"Session {session_id} expired")
                return None
            
            # Deserialize credentials
            if session_data.get('credentials_json'):
                try:
                    session_data['credentials'] = json.loads(session_data['credentials_json'])
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse credentials_json for session {session_id}")
                    session_data['credentials'] = None
            
            return session_data
        
        return None
    except Exception as e:
        print(f"Error loading user session: {e}")
        import traceback
        traceback.print_exc()
        return None


def update_session_last_used(session_id):
    """Update last_used_at timestamp for session."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_sessions
            SET last_used_at = ?
            WHERE session_id = ?
        ''', (datetime.now().isoformat(), session_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating session last used: {e}")
        return False


def delete_user_session(session_id):
    """Delete user session from database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM user_sessions WHERE session_id = ?', (session_id,))
        
        conn.commit()
        conn.close()
        print(f"User session {session_id} deleted")
        return True
    except Exception as e:
        print(f"Error deleting user session: {e}")
        return False

# Initialize database on startup
init_database()


def requires_auth(f):
    """Decorator to require authentication for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user has valid credentials in session
        if not oauth_manager.is_authenticated():
            # Store the requested URL for post-login redirect
            session['next_url'] = request.url
            return redirect(url_for('login'))
        
        # Update session last used timestamp
        session_id = get_session_id()
        update_session_last_used(session_id)
        
        return f(*args, **kwargs)
    return decorated_function


def get_template_list():
    """Get list of available templates."""
    config = get_config()
    template_config = config.get_section('templates')
    template_loader = TemplateLoader(
        str(config.get_absolute_path(template_config['template_directory']))
    )
    return template_loader.list_templates()


# ========== Authentication Routes ==========

@app.route('/login')
def login():
    """Display login page or redirect if already authenticated."""
    if oauth_manager.is_authenticated():
        # Already authenticated, redirect to home
        return redirect(url_for('index'))
    
    return render_template('login.html')


@app.route('/auth/google')
def auth_google():
    """Initiate Google OAuth flow."""
    # Get the callback URL
    redirect_uri = url_for('auth_callback', _external=True)
    
    # Get authorization URL from oauth manager
    authorization_url = oauth_manager.get_authorization_url(redirect_uri)
    
    return redirect(authorization_url)


@app.route('/auth/callback')
def auth_callback():
    """Handle OAuth callback from Google."""
    try:
        # Get the full callback URL with query parameters
        authorization_response = request.url
        redirect_uri = url_for('auth_callback', _external=True)
        
        # Handle the callback and store credentials in session
        oauth_manager.handle_oauth_callback(redirect_uri, authorization_response)
        
        # Get user email from credentials (if available)
        credentials = oauth_manager.get_credentials()
        user_email = None
        
        # Try to get user email from Google
        try:
            from googleapiclient.discovery import build
            oauth_service = build('oauth2', 'v2', credentials=credentials)
            user_info = oauth_service.userinfo().get().execute()
            user_email = user_info.get('email')
            session['user_email'] = user_email
        except Exception as e:
            print(f"Warning: Could not retrieve user email: {e}")
        
        # Save session to database
        session_id = get_session_id()
        credentials_dict = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        save_user_session(session_id, user_email, credentials_dict)
        
        # Redirect to the originally requested URL or home
        next_url = session.pop('next_url', None)
        return redirect(next_url or url_for('index'))
        
    except Exception as e:
        print(f"Error during OAuth callback: {e}")
        import traceback
        traceback.print_exc()
        return render_template('auth_error.html', error=str(e))


@app.route('/logout')
def logout():
    """Log out the current user."""
    # Get session ID before clearing
    session_id = session.get('session_id')
    
    # Delete from database
    if session_id:
        delete_user_session(session_id)
    
    # Clear OAuth session
    oauth_manager.logout()
    
    # Clear Flask session
    session.clear()
    
    return redirect(url_for('login'))


# ========== Application Routes ==========


@app.route('/')
@requires_auth
def index():
    """Main page with presentation processing form."""
    # Get available templates
    config = get_config()
    template_config = config.get_section('templates')
    template_loader = TemplateLoader(
        str(config.get_absolute_path(template_config['template_directory']))
    )
    templates = template_loader.list_templates()
    
    # Get user info for display
    user_email = session.get('user_email', 'User')
    
    # Get current user's session_id
    session_id = get_session_id()
    
    # Get recent jobs for current user only
    result = list_user_jobs(session_id=session_id, limit=5, offset=0)
    user_jobs = {job['id']: job for job in result['jobs']}
    
    return render_template('index.html', templates=templates, jobs=user_jobs, user_email=user_email)


@app.route('/process', methods=['POST'])
@requires_auth
def process():
    """Extract presentation and redirect to editor."""
    presentation_url = request.form.get('presentation_url')
    # Template selection removed - no longer needed
    
    if not presentation_url:
        return jsonify({'error': 'Presentation URL is required'}), 400
    
    # Get credentials from session
    credentials = oauth_manager.get_credentials()
    if not credentials:
        return redirect(url_for('login'))
    
    # Convert credentials to dictionary
    credentials_dict = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    # Get session ID
    session_id = get_session_id()
    
    # Create job for extraction
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        'id': job_id,
        'url': presentation_url,
        'template': None,  # No template needed
        'status': 'extracting',
        'created_at': datetime.now().isoformat(),
        'result': None,
        'error': None,
        'session_id': session_id  # Link job to session
    }
    
    # Extract content in background thread
    thread = threading.Thread(
        target=extract_for_editor,
        args=(job_id, presentation_url, credentials_dict)
    )
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('extraction_status', job_id=job_id))


def extract_for_editor(job_id, presentation_url, credentials_dict):
    """Extract presentation content for editor - preserve exact 1:1 structure from Google Slides.
    
    Args:
        job_id: Job identifier
        presentation_url: URL of presentation to extract
        credentials_dict: User credentials dictionary from session
    """
    try:
        from presentation_design.extraction.slides_extractor import SlidesExtractor
        from presentation_design.extraction.content_parser import ContentParser
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        # Reconstruct credentials from dictionary
        credentials = Credentials(
            token=credentials_dict.get('token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri=credentials_dict.get('token_uri'),
            client_id=credentials_dict.get('client_id'),
            client_secret=credentials_dict.get('client_secret'),
            scopes=credentials_dict.get('scopes')
        )
        
        # Create a simple wrapper to provide the service method
        class CredentialWrapper:
            def __init__(self, credentials):
                self.credentials = credentials
            
            def build_service(self, service_name, version):
                return build(service_name, version, credentials=self.credentials)
        
        oauth_wrapper = CredentialWrapper(credentials)
        
        # Extract content in RAW MODE (preserve original text)
        extractor = SlidesExtractor(oauth_wrapper)
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
            
            # SKIP slides that have no text content (empty slides or image-only slides)
            if not all_text_parts:
                print(f"  -> Skipping slide {idx}: no text content")
                continue
            
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
@requires_auth
def slide_editor():
    """Visual slide editor."""
    # Get data from job instead of URL params
    job_id = request.args.get('job_id')
    session_id = get_session_id()
    
    if job_id:
        # Check if user owns this job
        if not user_owns_job(job_id, session_id):
            return render_template('auth_error.html', error='Access denied: This job belongs to another user'), 403
        
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
    
    # Get user info for display
    user_email = session.get('user_email', 'User')
    
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
                          job_id=job_id,
                          user_email=user_email)


@app.route('/extraction_status/<job_id>')
@requires_auth
def extraction_status(job_id):
    """Show extraction status and redirect to editor when ready."""
    session_id = get_session_id()
    
    # Check if user owns this job
    if not user_owns_job(job_id, session_id):
        return render_template('auth_error.html', error='Access denied: This job belongs to another user'), 403
    
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
@requires_auth
def process_slides():
    """Process slides from editor and generate presentation."""
    data = request.get_json()
    slides = data.get('slides', [])
    template_name = data.get('template', 'default')
    presentation_url = data.get('presentation_url')
    existing_presentation_id = data.get('existing_presentation_id')  # For updates
    settings = data.get('settings', {})  # NEW: presentation settings
    
    # Get credentials from session
    credentials = oauth_manager.get_credentials()
    if not credentials:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Convert credentials to dictionary
    credentials_dict = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    # Get session ID
    session_id = get_session_id()
    
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
        'slides': slides,  # NEW: Store slides in job object
        'session_id': session_id  # Link job to session
    }
    
    # Save to database immediately
    save_job_to_db(job_id, jobs[job_id])
    
    # Process with edited slides
    thread = threading.Thread(
        target=process_slides_in_background,
        args=(job_id, slides, template_name, existing_presentation_id, credentials_dict)
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


def process_slides_in_background(job_id, slides, template_name=None, existing_presentation_id=None, credentials_dict=None):
    """Process edited slides in background - create presentation with advanced formatting.
    
    Args:
        job_id: Job identifier
        slides: Slides data
        template_name: Template name (optional)
        existing_presentation_id: Existing presentation ID for updates (optional)
        credentials_dict: User credentials dictionary from session
    """
    try:
        from presentation_design.generation.presentation_builder import PresentationBuilder
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        # Reconstruct credentials from dictionary
        credentials = Credentials(
            token=credentials_dict.get('token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri=credentials_dict.get('token_uri'),
            client_id=credentials_dict.get('client_id'),
            client_secret=credentials_dict.get('client_secret'),
            scopes=credentials_dict.get('scopes')
        )
        
        # Create a simple wrapper to provide the service method
        class CredentialWrapper:
            def __init__(self, credentials):
                self.credentials = credentials
            
            def build_service(self, service_name, version):
                return build(service_name, version, credentials=self.credentials)
        
        oauth_wrapper = CredentialWrapper(credentials)
        
        # Build presentation with advanced formatting
        builder = PresentationBuilder(oauth_wrapper)
        
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
@requires_auth
def job_status(job_id):
    """Show job status page."""
    session_id = get_session_id()
    
    # Check if user owns this job
    if not user_owns_job(job_id, session_id):
        return render_template('auth_error.html', error='Access denied: This job belongs to another user'), 403
    
    # Try memory first, then database
    job = jobs.get(job_id)
    if not job:
        job = load_job_from_db(job_id)
        if job:
            jobs[job_id] = job  # Cache in memory
    
    if not job:
        return "Job not found", 404
    
    # Get user info for display
    user_email = session.get('user_email', 'User')
    
    return render_template('job_status.html', job=job, user_email=user_email)


@app.route('/api/job/<job_id>')
@requires_auth
def api_job_status(job_id):
    """API endpoint for job status (for AJAX polling)."""
    session_id = get_session_id()
    
    # Check if user owns this job
    if not user_owns_job(job_id, session_id):
        return jsonify({'error': 'Access denied'}), 403
    
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
@requires_auth
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
        
        # Get session ID
        session_id = get_session_id()
        
        # Check if job exists and user owns it
        existing_job = jobs.get(job_id) or load_job_from_db(job_id)
        if existing_job and existing_job.get('session_id') != session_id:
            return jsonify({'error': 'Access denied'}), 403
        
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
                    'settings': settings,
                    'session_id': session_id
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
@requires_auth
def api_load_slides():
    """Load slides and settings from database."""
    try:
        job_id = request.args.get('job_id')
        
        if not job_id:
            return jsonify({'error': 'job_id parameter is required'}), 400
        
        # Get session ID
        session_id = get_session_id()
        
        # Check if user owns this job
        if not user_owns_job(job_id, session_id):
            return jsonify({'error': 'Access denied'}), 403
        
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
@requires_auth
def history():
    """Show processing history for current user only."""
    # Get current user's session_id
    session_id = get_session_id()
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    limit = 50
    offset = (page - 1) * limit
    
    # Load jobs for current user only
    result = list_user_jobs(session_id=session_id, limit=limit, offset=offset)
    jobs_list = result['jobs']
    total = result['total']
    
    # Calculate pagination info
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    has_next = page < total_pages
    has_prev = page > 1
    
    # Get user info for display
    user_email = session.get('user_email', 'User')
    
    return render_template('history.html', 
                          jobs=jobs_list,
                          page=page,
                          total_pages=total_pages,
                          has_next=has_next,
                          has_prev=has_prev,
                          total=total,
                          user_email=user_email)


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
