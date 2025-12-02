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
from datetime import datetime

# Add presentation_design to path
sys.path.insert(0, str(Path(__file__).parent))

from presentation_design.main import process_presentation
from presentation_design.templates.template_loader import TemplateLoader
from presentation_design.utils.config import get_config

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# In-memory storage for processing jobs (use database in production)
jobs = {}


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
    template_name = request.form.get('template_name', 'default')
    
    if not presentation_url:
        return jsonify({'error': 'Presentation URL is required'}), 400
    
    # Create job for extraction
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        'id': job_id,
        'url': presentation_url,
        'template': template_name,
        'status': 'extracting',
        'created_at': datetime.now().isoformat(),
        'result': None,
        'error': None
    }
    
    # Extract content in background thread
    thread = threading.Thread(
        target=extract_for_editor,
        args=(job_id, presentation_url, template_name)
    )
    thread.daemon = True
    thread.start()
    
    return redirect(url_for('extraction_status', job_id=job_id))


def extract_for_editor(job_id, presentation_url, template_name):
    """Extract presentation content for editor."""
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
        
        # Extract content (already parsed by extractor)
        extractor = SlidesExtractor(oauth_manager)
        parsed_data = extractor.extract_presentation(presentation_url)
        
        print(f"DEBUG: Parsed {len(parsed_data.get('slides', []))} slides")
        
        # Convert parsed data to editor format
        slides = []
        for idx, slide in enumerate(parsed_data.get('slides', [])):
            editor_slide = {
                'title': '',
                'mainText': '',
                'secondaryText': ''
            }
            
            elements = slide.get('elements', [])
            print(f"DEBUG: Slide {idx} has {len(elements)} elements")
            
            for element in elements:
                if element.get('type') == 'TEXT':
                    role = element.get('role', 'BODY').upper()
                    content = element.get('content', '')
                    print(f"DEBUG: Slide {idx}, role={role}, content_preview={content[:50] if content else 'empty'}")
                    
                    if role in ['TITLE', 'SUBTITLE']:
                        if editor_slide['title']:
                            editor_slide['title'] += '\n' + content
                        else:
                            editor_slide['title'] = content
                    elif role in ['BODY', 'HEADING']:
                        if editor_slide['mainText']:
                            editor_slide['mainText'] += '\n' + content
                        else:
                            editor_slide['mainText'] = content
                    elif role == 'FOOTER':
                        if editor_slide['secondaryText']:
                            editor_slide['secondaryText'] += '\n' + content
                        else:
                            editor_slide['secondaryText'] = content
            
            print(f"DEBUG: Slide {idx} editor format: title={len(editor_slide['title'])}, main={len(editor_slide['mainText'])}, secondary={len(editor_slide['secondaryText'])}")
            slides.append(editor_slide)
        
        print(f"DEBUG: Total slides for editor: {len(slides)}")
        jobs[job_id]['status'] = 'extracted'
        jobs[job_id]['slides'] = slides
        jobs[job_id]['completed_at'] = datetime.now().isoformat()
        
    except Exception as e:
        print(f"Error extracting presentation: {e}")
        import traceback
        traceback.print_exc()
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)
        jobs[job_id]['completed_at'] = datetime.now().isoformat()


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
        job = jobs.get(job_id)
        if job:
            presentation_url = job.get('url')
            template = job.get('template', 'default')
            slides_data = job.get('slides', [])
        else:
            return "Job not found", 404
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
    
    return render_template('slide_editor.html',
                          presentation_url=presentation_url,
                          template=template,
                          slides_data=slides_data,
                          templates=templates)


@app.route('/extraction_status/<job_id>')
def extraction_status(job_id):
    """Show extraction status and redirect to editor when ready."""
    job = jobs.get(job_id)
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
    existing_presentation_id = data.get('existing_presentation_id')  # NEW: for updates
    
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        'id': job_id,
        'url': presentation_url,
        'template': template_name,
        'status': 'processing',
        'created_at': datetime.now().isoformat(),
        'result': None,
        'error': None,
        'existing_presentation_id': existing_presentation_id  # Store for updates
    }
    
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


def process_slides_in_background(job_id, slides, template_name, existing_presentation_id=None):
    """Process edited slides in background."""
    try:
        from presentation_design.main import process_presentation
        from presentation_design.templates.template_loader import TemplateLoader
        from presentation_design.design.design_applicator import DesignApplicator
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
        
        # Load template
        template_config = config.get_section('templates')
        template_loader = TemplateLoader(
            str(config.get_absolute_path(template_config['template_directory']))
        )
        template = template_loader.load_template(template_name)
        
        # Create presentation data from editor slides
        presentation_data = {
            'presentation_id': 'editor',
            'title': 'Edited Presentation',
            'slides': []
        }
        
        for idx, slide in enumerate(slides):
            slide_data = {
                'index': idx,
                'slide_id': f'slide_{idx}',
                'layout_type': 'TITLE' if idx == 0 else 'CONTENT',
                'elements': []
            }
            
            # Add title if present
            if slide.get('title'):
                slide_data['elements'].append({
                    'type': 'TEXT',
                    'content': slide['title'],
                    'role': 'TITLE',
                    'position': {},
                    'text_analysis': {
                        'content_type': 'plain',
                        'items': [],
                        'has_emphasis': False,
                        'is_title_case': True,
                        'original_text': slide['title']
                    }
                })
            
            # Add main text if present
            if slide.get('mainText'):
                # Check if it's a list
                main_text = slide['mainText']
                is_list = '\n•' in main_text or '\n-' in main_text or any(line.strip().startswith(str(i)+'.') for i in range(1,10) for line in main_text.split('\n'))
                
                slide_data['elements'].append({
                    'type': 'TEXT',
                    'content': main_text,
                    'role': 'BODY',
                    'position': {},
                    'text_analysis': {
                        'content_type': 'bullet_list' if is_list else 'plain',
                        'items': main_text.split('\n') if is_list else [],
                        'has_emphasis': False,
                        'is_title_case': False,
                        'original_text': main_text
                    }
                })
            
            # Add secondary text if present
            if slide.get('secondaryText'):
                slide_data['elements'].append({
                    'type': 'TEXT',
                    'content': slide['secondaryText'],
                    'role': 'FOOTER',
                    'position': {},
                    'text_analysis': {
                        'content_type': 'plain',
                        'items': [],
                        'has_emphasis': False,
                        'is_title_case': False,
                        'original_text': slide['secondaryText']
                    }
                })
            
            presentation_data['slides'].append(slide_data)
        
        # Apply design
        applicator = DesignApplicator(template)
        designed_data = applicator.apply_design(presentation_data)
        
        # Build or update presentation
        builder = PresentationBuilder(oauth_manager)
        
        if existing_presentation_id:
            # UPDATE existing presentation
            print(f"Updating existing presentation: {existing_presentation_id}")
            result = builder.update_presentation(existing_presentation_id, designed_data)
        else:
            # CREATE new presentation
            print(f"Creating new presentation")
            result = builder.build_presentation(designed_data)
        
        jobs[job_id].update({
            'status': 'completed',
            'result': result,
            'generated_presentation_id': result.get('presentation_id')  # Store for future updates
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
    job = jobs.get(job_id)
    if not job:
        return "Job not found", 404
    
    return render_template('job_status.html', job=job)


@app.route('/api/job/<job_id>')
def api_job_status(job_id):
    """API endpoint for job status (for AJAX polling)."""
    job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job)


@app.route('/history')
def history():
    """Show processing history."""
    sorted_jobs = sorted(
        jobs.values(),
        key=lambda x: x['created_at'],
        reverse=True
    )
    return render_template('history.html', jobs=sorted_jobs)


if __name__ == '__main__':
    print("="*60)
    print("Presentation Design System - Web Interface")
    print("="*60)
    print("\nStarting server at http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
