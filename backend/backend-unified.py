# This Flask application combines:
# 1. Gesture-based file browsing and upload (one-step processing)
# 2. Manual, two-step file upload and processing for the Next.js frontend
#    - POST /api/upload -> Returns file_id
#    - POST /api/process -> Starts processing, returns session_id
#    - GET /api/results -> Returns modules
 

import os
import cv2
import base64
import json
import numpy as np
import time
import threading
import uuid
from typing import Dict, Any, List
from flask import Flask, Blueprint, request, jsonify, session
from flask_cors import CORS, cross_origin
from flask_session import Session
from werkzeug.utils import secure_filename
import mediapipe as mp
import logging
from processor import SyllabusProcessor
from analyser import generate_course_outcomes_from_modules
 

app = Flask(__name__)

# Get the absolute path of the directory containing this script
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Security and Session Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True  
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour

# File Upload Configuration
 
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'syllabus_uploads')
GESTURE_SOURCE_FOLDER = os.path.join(BASE_DIR, 'gesture_source_files')
DATA_FOLDER = os.path.join(BASE_DIR, 'data') # For processed JSON results

 
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
 
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GESTURE_SOURCE_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# Initialize Flask-Session
Session(app)

# CORS Configuration for Next.js
CORS(app, 
     origins=['http://localhost:3000', 'http://localhost:3001'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization', 'X-CSRF-Token'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# State for manual upload processing
PROCESSING_FILES = set()

# Initialize AI processor
processor = SyllabusProcessor()
 
# MEDIAPIPE HAND GESTURE DETECTION SETUP
 
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# HELPER FUNCTIONS
 
def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed (new version)"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in ALLOWED_EXTENSIONS

def find_uploaded_file_by_id(prefix_id: str) -> str | None:
    """Finds a file in the upload folder by its UUID prefix"""
    folder = app.config['UPLOAD_FOLDER']
    for fname in os.listdir(folder):
        if fname.startswith(prefix_id + "_"):
            return os.path.join(folder, fname)
    return None

# ==================================================================
# BEGIN FIXED CODE BLOCK
# ==================================================================

def detect_gesture(img: np.ndarray) -> str:
    """
    Detect hand gestures using MediaPipe with more robust logic.
    Checks for curled vs. straight fingers.
    """
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    if not results.multi_hand_landmarks:
        return 'none'
    
    for hand_landmarks in results.multi_hand_landmarks:
        landmarks = hand_landmarks.landmark
        
        # --- Get all relevant landmarks ---
        try:
            # Tips
            thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]       # 4
            index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP] # 8
            middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]# 12
            ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]   # 16
            pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]      # 20
            
            # PIPs (middle joints)
            index_pip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP] # 6
            middle_pip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]# 10
            ring_pip = landmarks[mp_hands.HandLandmark.RING_FINGER_PIP]   # 14
            pinky_pip = landmarks[mp_hands.HandLandmark.PINKY_PIP]      # 18
            
            # MCPs (base knuckles)
            thumb_mcp = landmarks[mp_hands.HandLandmark.THUMB_MCP]        # 2
            index_mcp = landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP] # 5
            
        except IndexError:
            # This can happen if landmarks are not fully detected
            return 'unknown'

        # --- Calculate finger states ---
        # A finger is "straight" if its tip is higher (smaller Y) than its middle joint.
        index_straight = index_tip.y < index_pip.y
        
        # A finger is "curled" if its tip is lower (larger Y) than its middle joint.
        index_curled = index_tip.y > index_pip.y
        middle_curled = middle_tip.y > middle_pip.y
        ring_curled = ring_tip.y > ring_pip.y
        pinky_curled = pinky_tip.y > pinky_pip.y

        # --- Gesture Logic (Prioritized with if/elif) ---
        
        # 1. Check for POINT
        # Condition: Index is straight, all others are curled.
        # Thumb is also tucked in (tip lower than index pip).
        if (index_straight and 
            middle_curled and 
            ring_curled and 
            pinky_curled and
            thumb_tip.y > index_pip.y): # Thumb tucked
            return 'point'
        
        # 2. Check for THUMBS UP
        # Condition: Thumb is "up" (tip higher than index base), other fingers are curled.
        if (thumb_tip.y < index_mcp.y and
            index_curled and
            middle_curled and
            ring_curled and
            pinky_curled):
            return 'thumbs_up'
            
        # 3. Check for THUMBS DOWN
        # Condition: Thumb is "down" (tip lower than its own base), other fingers are curled.
        if (thumb_tip.y > thumb_mcp.y and # Thumb points down relative to its base
            index_curled and
            middle_curled and
            ring_curled and
            pinky_curled):
            return 'thumbs_down'

    # Default case if no specific gesture is matched
    return 'unknown'

# ==================================================================
# END FIXED CODE BLOCK
# ==================================================================

def speak_without_saving(text: str):
    """Placeholder for text-to-speech"""
    print(f"[TTS]: {text}")
    # TODO: Implement actual TTS

def process_file_with_ai(file_path: str) -> Dict[str, Any]:
    """
    Helper for GESTURE upload (one-step)
    Process uploaded file using the SyllabusProcessor
    Returns: processing results with extracted modules
    """
    try:
        # Note: We re-initialize the processor here for thread-safety
        # if this causes issues, initialize it once globally
        gesture_processor = SyllabusProcessor()
        result = gesture_processor.process_syllabus(file_path)
        return result
    except Exception as e:
        print(f"Error in process_file_with_ai: {e}")
        return {'success': False, 'error': str(e), 'modules': []}
 
# GESTURE-BASED UPLOAD ROUTES  
 
gesture_bp = Blueprint('gesture', __name__, url_prefix='/api/gesture')

@gesture_bp.route('/detect', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['http://localhost:3000', 'http://localhost:3001'], supports_credentials=True)
def detect_image():
    """Main gesture detection endpoint (one-step process)"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    
    try:
        # --- Start of Gesture Logic ---
        if 'gesture_state' not in session:
            session['gesture_state'] = 'IDLE'
            session['current_file_index'] = 0
            session['last_speak_time'] = 0
            session['selected_file'] = None
            session['debounce_time'] = 0
            session['anonymous_id'] = str(time.time()).replace('.', '')
        
        DEBOUNCE_INTERVAL = 2.0
        SPEAK_INTERVAL = 3.0
        
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided', 'status': 'Error: No image data', 'gesture': 'unknown', 'state': 'ERROR'}), 400
        
        current_time = time.time()
        
        try:
            image_data = data.get('image', '').split(',')[1]
            np_arr = np.frombuffer(base64.b64decode(image_data), np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            gesture = 'none' if img is None else detect_gesture(img)
        except Exception as e:
            print(f"Image processing error: {e}")
            gesture = 'none'
        
        try:
            all_files = os.listdir(GESTURE_SOURCE_FOLDER)
            files = [f for f in all_files if allowed_file(f) and not f.startswith('.')]
        except Exception as e:
            print(f"File listing error: {e}")
            files = []
        
        if not files:
            return jsonify({'status': f'No valid files (pdf, txt) found in {GESTURE_SOURCE_FOLDER}', 'gesture': gesture, 'state': 'NO_FILES', 'current_file': None})
        
        current_index = session.get('current_file_index', 0)
        current_state = session.get('gesture_state', 'IDLE')
        last_speak_time = session.get('last_speak_time', 0)
        debounce_time = session.get('debounce_time', 0)
        
        if current_index >= len(files):
            current_index = 0
            session['current_file_index'] = 0
        
        if current_time - debounce_time < DEBOUNCE_INTERVAL:
            return jsonify({'status': f'Processing... {current_state}', 'gesture': gesture, 'state': current_state, 'current_file': files[current_index]})
        
        response_data = {'status': 'Ready', 'gesture': gesture, 'state': current_state, 'current_file': files[current_index], 'total_files': len(files)}
        
        # STATE MACHINE
        if current_state == 'IDLE':
            if gesture == 'point':
                session['gesture_state'] = 'BROWSING'
                session['current_file_index'] = 0
                session['debounce_time'] = current_time
                if current_time - last_speak_time > SPEAK_INTERVAL:
                    threading.Thread(target=speak_without_saving, args=(f"Started browsing. Current file: {files[0]}",), daemon=True).start()
                    session['last_speak_time'] = current_time
                response_data.update({'status': 'Started browsing files', 'state': 'BROWSING'})
        
        elif current_state == 'BROWSING':
            if gesture == 'thumbs_up':
                current_index = (current_index + 1) % len(files)
                session['current_file_index'] = current_index
                session['debounce_time'] = current_time
                if current_time - last_speak_time > SPEAK_INTERVAL:
                    threading.Thread(target=speak_without_saving, args=(f"File: {files[current_index]}",), daemon=True).start()
                    session['last_speak_time'] = current_time
                response_data.update({'status': f'Browsing: {files[current_index]}', 'current_file': files[current_index]})
            
            elif gesture == 'thumbs_down':
                current_index = (current_index - 1) % len(files)
                session['current_file_index'] = current_index
                session['debounce_time'] = current_time
                if current_time - last_speak_time > SPEAK_INTERVAL:
                    threading.Thread(target=speak_without_saving, args=(f"File: {files[current_index]}",), daemon=True).start()
                    session['last_speak_time'] = current_time
                response_data.update({'status': f'Browsing: {files[current_index]}', 'current_file': files[current_index]})
            
            elif gesture == 'point':
                session['gesture_state'] = 'CONFIRMING'
                session['selected_file'] = files[current_index]
                session['confirmation_start'] = current_time
                session['debounce_time'] = current_time
                if current_time - last_speak_time > SPEAK_INTERVAL:
                    threading.Thread(target=speak_without_saving, args=(f"Selected {files[current_index]}. Show thumbs up to confirm upload.",), daemon=True).start()
                    session['last_speak_time'] = current_time
                response_data.update({'status': f'Confirm upload of {files[current_index]}?', 'state': 'CONFIRMING', 'selected_file': files[current_index]})
        
        elif current_state == 'CONFIRMING':
            if gesture == 'thumbs_up':
                selected_file = session.get('selected_file')
                source_path = os.path.join(GESTURE_SOURCE_FOLDER, selected_file)
                dest_path = os.path.join(UPLOAD_FOLDER, selected_file)
                try:
                    import shutil
                    shutil.copy2(source_path, dest_path)
                    processing_result = process_file_with_ai(dest_path) # One-step process
                    session['gesture_state'] = 'IDLE'
                    session['debounce_time'] = current_time
                    if current_time - last_speak_time > SPEAK_INTERVAL:
                        threading.Thread(target=speak_without_saving, args=(f"Upload successful. Processing complete.",), daemon=True).start()
                        session['last_speak_time'] = current_time
                    response_data.update({'status': 'Upload successful', 'state': 'IDLE', 'uploaded_file': selected_file, 'processing_result': processing_result})
                except Exception as e:
                    print(f"Upload error: {e}")
                    response_data.update({'status': f'Upload failed: {str(e)}', 'state': 'ERROR'})
            
            elif gesture == 'thumbs_down':
                session['gesture_state'] = 'BROWSING'
                session['selected_file'] = None
                session['debounce_time'] = current_time
                if current_time - last_speak_time > SPEAK_INTERVAL:
                    threading.Thread(target=speak_without_saving, args=("Selection cancelled. Continue browsing.",), daemon=True).start()
                    session['last_speak_time'] = current_time
                response_data.update({'status': 'Selection cancelled', 'state': 'BROWSING'})
        
        # --- End of Gesture Logic ---
        session.modified = True
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Critical error in detect_image: {e}")
        return jsonify({'error': str(e), 'status': 'System error', 'gesture': 'unknown', 'state': 'ERROR'}), 500

# (Other gesture routes remain unchanged)
@gesture_bp.route('/reset', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['http://localhost:3000', 'http://localhost:3001'], supports_credentials=True)
def reset_session():
    if request.method == 'OPTIONS': return jsonify({'status': 'OK'}), 200
    session.clear()
    return jsonify({'status': 'Session reset', 'state': 'RESET'})

@gesture_bp.route('/status', methods=['GET', 'OPTIONS'])
@cross_origin(origins=['http://localhost:3000', 'http://localhost:3001'], supports_credentials=True)
def session_status():
    if request.method == 'OPTIONS': return jsonify({'status': 'OK'}), 200
    return jsonify({
        'anonymous_id': session.get('anonymous_id', 'none'),
        'gesture_state': session.get('gesture_state', 'IDLE'),
        'current_file_index': session.get('current_file_index', 0),
        'selected_file': session.get('selected_file'),
        'status': 'Session active'
    })

# MANUAL UPLOAD ROUTES (Blueprint) - MODIFIED FOR 2-STEP PROCESS
 
upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')

@upload_bp.route('/', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['http://localhost:3000', 'http://localhost:3001'], supports_credentials=True)
def upload_file():
    """
    Step 1: Handle file upload from frontend, save with UUID, return file_id.
    This route now matches what FileUpload.tsx expects.
    """
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    file = request.files.get('file')
    if not file:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type. Only PDF and TXT files allowed.'}), 400

    try:
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(save_path)

        logger.info(f"File uploaded successfully: {filename} (ID: {file_id})")

        # This response is exactly what FileUpload.tsx expects
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'message': 'File uploaded successfully'
        }), 200
    except Exception:
        logger.exception("Upload error")
        return jsonify({'success': False, 'error': 'Failed to save file'}), 500
 
# NEW ROOT ROUTES FOR 2-STEP PROCESSING
 
@app.route('/api/process', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['http://localhost:3000', 'http://localhost:3001'], supports_credentials=True)
def process_syllabus():
    """
    Step 2: Process the file identified by file_id.
    This is called by the /processing page in the frontend.
    """
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
        
    data = request.get_json(silent=True) or {}
    file_id = data.get('file_id')

    if not file_id:
        return jsonify({'success': False, 'error': 'No file ID provided'}), 400

    if file_id in PROCESSING_FILES:
        logger.warning(f"Attempted to process an already processing file: {file_id}")
        return jsonify({'success': False, 'error': 'This file is already being processed. Please wait.'}), 409

    uploaded_file = find_uploaded_file_by_id(file_id)
    if not uploaded_file:
        return jsonify({'success': False, 'error': 'File not found'}), 404

    try:
        PROCESSING_FILES.add(file_id)
        logger.info(f"Processing file: {uploaded_file}")

        # Use the global processor instance
        result = processor.process_syllabus(uploaded_file)
        
        if not result.get('success'):
            return jsonify({'success': False, 'error': result.get('error', 'Processing failed')}), 500

        session_id = str(uuid.uuid4())
        result.update({
            'processed_at': time.time(),
            'session_id': session_id,
        })

        result_path = os.path.join(DATA_FOLDER, f"{session_id}.json")
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"Processing completed. Session ID: {session_id}, Modules: {len(result.get('modules', []))}")

        return jsonify({
            'success': True,
            'session_id': session_id,
            'modules_count': len(result.get('modules', [])),
            'message': 'Processing completed successfully'
        }), 200

    except Exception as e:
        logger.exception("Processing error during main execution")
        return jsonify({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}), 500
    
    finally:
        if file_id in PROCESSING_FILES:
            PROCESSING_FILES.remove(file_id)


@app.route('/api/results', methods=['GET', 'OPTIONS'])
@cross_origin(origins=['http://localhost:3000', 'http://localhost:3001'], supports_credentials=True)
def get_results():
    """
    Step 3: Retrieve the processed results using the session_id.
    """
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'success': False, 'error': 'No session ID provided'}), 400

    result_path = os.path.join(DATA_FOLDER, f"{secure_filename(session_id)}.json")
    if not os.path.exists(result_path):
        return jsonify({'success': False, 'error': 'Results not found'}), 404

    try:
        with open(result_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
    except Exception:
        logger.exception("Error reading results")
        return jsonify({'success': False, 'error': 'Failed to read results'}), 500

    logger.info(f"Results retrieved for session: {session_id}")

    # Return the modules as expected by the frontend
    return jsonify({
        'success': True,
        'modules': results.get('modules', []),
        'processed_at': results.get('processed_at'),
        'total_modules': len(results.get('modules', []))
    }), 200

# REGISTER BLUEPRINTS
app.register_blueprint(gesture_bp)
app.register_blueprint(upload_bp) 
# HEALTH CHECK & ROOT ROUTES
 
@app.route('/')
def index():
    return jsonify({
        'status': 'online',
        'service': 'Syllabus Upload & Processing API',
        'version': '1.1.0 (Unified)',
        'endpoints': {
            'gesture': '/api/gesture/detect',
            'manual_upload': '/api/upload',
            'manual_process': '/api/process',
            'manual_results': '/api/results'
        }
    })

@app.route('/health') 
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Syllabus API is running',
        'timestamp': time.time()
    }), 200

# ERROR HANDLERS

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size is {MAX_FILE_SIZE // 1024 // 1024}MB.'
    }), 413

@app.errorhandler(500)
def internal_server_error(error):
    logger.exception("Internal Server Error (500)")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
    
# MAIN ENTRY POINT
 
if __name__ == '__main__':
    print("=" * 70)
    print("🚀 Unified Syllabus Upload & Processing Backend (v1.1)")
    print("=" * 70)
    print(f"📁 Upload folder: {UPLOAD_FOLDER}")
    print(f"🤚 Gesture source folder: {GESTURE_SOURCE_FOLDER}")
    print(f"📄 Data folder: {DATA_FOLDER}")
    print(f"🌐 CORS enabled for: http://localhost:3000, http://localhost:3001")
    print(f"⚖️  Max file size: {MAX_FILE_SIZE // 1024 // 1024}MB")
    print(f"✅ Allowed types: {ALLOWED_EXTENSIONS}")
    print("=" * 70)
    print("\n📡 Starting Flask server...\n")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )