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
import analyser

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
DATA_FOLDER = os.path.join(BASE_DIR, 'data')  # For processed JSON results

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
CORS(
    app,
    origins=['http://localhost:3000', 'http://localhost:3001'],
    supports_credentials=True,
    allow_headers=['Content-Type', 'Authorization', 'X-CSRF-Token'],
    methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
)

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
 
# BEGIN FIXED CODE BLOCK (updated gesture detection)
 

# BEGIN UPDATED CODE BLOCK

# BEGIN FINAL GESTURE LOGIC

def detect_gesture(img: np.ndarray) -> str:
    """
    Detect hand gestures using MediaPipe with clearer separation between:
      - open_palm  -> start/next
      - fist         -> previous
      - point        -> select
      - thumbs_up    -> confirm
      - thumbs_down  -> cancel

    Updated to:
      - PRIORITIZE "closed hand" check (fist, thumbs up/down)
      - This correctly identifies a 'thumbs_up' even if other
        fingers are bent, not perfectly curled.
    """
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if not results.multi_hand_landmarks:
        return 'none'

    for hand_landmarks in results.multi_hand_landmarks:
        landmarks = hand_landmarks.landmark

        try:
            # Thumb
            thumb_mcp = landmarks[mp_hands.HandLandmark.THUMB_MCP]
            thumb_ip  = landmarks[mp_hands.HandLandmark.THUMB_IP]
            thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]

            # Index
            index_mcp = landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP]
            index_pip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP]
            index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Middle
            middle_mcp = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
            middle_pip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
            middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

            # Ring
            ring_mcp = landmarks[mp_hands.HandLandmark.RING_FINGER_MCP]
            ring_pip = landmarks[mp_hands.HandLandmark.RING_FINGER_PIP]
            ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]

            # Pinky
            pinky_mcp = landmarks[mp_hands.HandLandmark.PINKY_MCP]
            pinky_pip = landmarks[mp_hands.HandLandmark.PINKY_PIP]
            pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

        except IndexError:
            # Landmarks not fully detected
            return 'unknown'

        # ---- Helpers ----
        EXT_MARGIN = 0.035

        def is_extended(tip, pip, mcp, margin: float = EXT_MARGIN) -> bool:
            """
            Finger extended if tip is clearly above pip and mcp.
            """
            return (tip.y < pip.y - margin) and (pip.y < mcp.y - margin / 2)

        # Finger states (Extended or Not)
        index_extended = is_extended(index_tip, index_pip, index_mcp)
        middle_extended = is_extended(middle_tip, middle_pip, middle_mcp)
        ring_extended = is_extended(ring_tip, ring_pip, ring_mcp)
        pinky_extended = is_extended(pinky_tip, pinky_pip, pinky_mcp)

        # Thumb orientation: vertical vs horizontal
        thumb_vertical = abs(thumb_tip.y - thumb_mcp.y) > 1.2 * abs(thumb_tip.x - thumb_mcp.x)
        thumb_up = thumb_vertical and (thumb_tip.y < thumb_mcp.y - 0.05)
        thumb_down = thumb_vertical and (thumb_tip.y > thumb_mcp.y + 0.05)

        # Finger spread (for open palm)
        finger_spread = abs(index_tip.x - pinky_tip.x)

        # --- NEW GESTURE LOGIC (Solves thumbs_up vs fist) ---

        # 1) OPEN PALM: (Strict) all four fingers extended AND spread out
        if (
            index_extended and middle_extended and ring_extended and pinky_extended and
            finger_spread > 0.15
        ):
            return 'open_palm'

        # 2) POINT: (Robust) only index extended, others NOT extended.
        if (
            index_extended and
            not middle_extended and
            not ring_extended and
            not pinky_extended
        ):
            # Check thumb isn't vertical to avoid confusion
            if not thumb_vertical:
                 return 'point'

        # 3) CLOSED HAND CHECK (Fist, Thumbs Up, Thumbs Down)
        # This is the main fix. We check for a closed hand FIRST.
        if (
            not index_extended and
            not middle_extended and
            not ring_extended and
            not pinky_extended
        ):
            # Hand is closed. NOW, check the thumb.
            if thumb_up:
                return 'thumbs_up'  # <-- Solves your "bent finger" problem
            
            if thumb_down:
                return 'thumbs_down'
            
            # If thumb is not up or down, it's a fist
            return 'fist'

    # No confident match
    return 'unknown'

# END FINAL GESTURE LOGIC

def speak_without_saving(text: str):
    """Placeholder for text-to-speech"""
    print(f"[TTS]: {text}")
    # TODO: Implement actual TTS


def process_file_with_ai(file_path: str) -> Dict[str, Any]:
    """
    Helper for GESTURE upload (one-step)
    Process uploaded file using the SyllabusProcessor
    
    UPDATED: Now uses the global processor and PROCESSING_FILES lock
    to ensure thread-safety and consistency with /api/process.
    """
    # Use the file_path itself as a unique ID for the lock
    file_id_lock = os.path.basename(file_path) 
    
    if file_id_lock in PROCESSING_FILES:
        logger.warning(f"Gesture upload: File is already being processed: {file_id_lock}")
        return {
            'success': False, 
            'error': 'This file is already being processed.', 
            'modules': []
        }

    try:
        PROCESSING_FILES.add(file_id_lock)
        logger.info(f"Gesture upload: Processing file: {file_path}")

        # Use the global processor instance, just like /api/process
        result = processor.process_syllabus(file_path) 

        if not result.get('success'):
            return {
                'success': False, 
                'error': result.get('error', 'Processing failed'), 
                'modules': []
            }

        # The gesture flow doesn't need to save to a session_id.json,
        # it returns the result directly.
        logger.info(f"Gesture upload: Processing completed for {file_id_lock}")
        return result

    except Exception as e:
        logger.exception(f"Error in process_file_with_ai: {e}")
        return {'success': False, 'error': str(e), 'modules': []}
    
    finally:
        # IMPORTANT: Always remove the file from the set
        if file_id_lock in PROCESSING_FILES:
            PROCESSING_FILES.remove(file_id_lock)
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
            # New for gesture stability
            session['last_raw_gesture'] = 'none'
            session['gesture_start_time'] = 0.0

        DEBOUNCE_INTERVAL = 2.5
        SPEAK_INTERVAL = 3.0

        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({
                'error': 'No image data provided',
                'status': 'Error: No image data',
                'gesture': 'unknown',
                'state': 'ERROR'
            }), 400

        current_time = time.time()

        raw_gesture = 'none'
        gesture = 'none'

        try:
            image_data = data.get('image', '').split(',')[1]
            np_arr = np.frombuffer(base64.b64decode(image_data), np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            raw_gesture = 'none' if img is None else detect_gesture(img)
        except Exception as e:
            print(f"Image processing error: {e}")
            raw_gesture = 'none'

        # ---- Gesture stability filter (to avoid quick mis-detections) ----
        STABLE_GESTURE_TIME = 0.6  # seconds the same gesture must be seen
 
        last_raw = session.get('last_raw_gesture', 'none')
        gesture_start_time = session.get('gesture_start_time', current_time)

        if raw_gesture == last_raw and raw_gesture not in ('none', 'unknown'):
            # Same gesture continuing
            if current_time - gesture_start_time >= STABLE_GESTURE_TIME:
                gesture = raw_gesture
            else:
                gesture = 'none'  # not stable long enough yet
        else:
            # New gesture started or went back to none
            session['last_raw_gesture'] = raw_gesture
            session['gesture_start_time'] = current_time
            gesture = 'none'

        try:
            all_files = os.listdir(GESTURE_SOURCE_FOLDER)
            files = [f for f in all_files if allowed_file(f) and not f.startswith('.')]
        except Exception as e:
            print(f"File listing error: {e}")
            files = []

        if not files:
            return jsonify({
                'status': f'No valid files (pdf, txt) found in {GESTURE_SOURCE_FOLDER}',
                'gesture': gesture,
                'raw_gesture': raw_gesture,
                'state': 'NO_FILES',
                'current_file': None
            })

        current_index = session.get('current_file_index', 0)
        current_state = session.get('gesture_state', 'IDLE')
        last_speak_time = session.get('last_speak_time', 0)
        debounce_time = session.get('debounce_time', 0)

        if current_index >= len(files):
            current_index = 0
            session['current_file_index'] = 0

        if current_time - debounce_time < DEBOUNCE_INTERVAL:
            return jsonify({
                'status': f'Processing... {current_state}',
                'gesture': gesture,
                'raw_gesture': raw_gesture,
                'state': current_state,
                'current_file': files[current_index]
            })

        response_data = {
            'status': 'Ready',
            'gesture': gesture,          # stable gesture
            'raw_gesture': raw_gesture,  # immediate detection (debugging)
            'state': current_state,
            'current_file': files[current_index],
            'total_files': len(files)
        }

               # STATE MACHINE
        if current_state == 'IDLE':
            # Start browsing with OPEN PALM instead of POINT
            if gesture == 'open_palm':
                session['gesture_state'] = 'BROWSING'
                session['current_file_index'] = 0
                session['debounce_time'] = current_time
                if current_time - last_speak_time > SPEAK_INTERVAL:
                    threading.Thread(
                        target=speak_without_saving,
                        args=(f"Started browsing. Current file: {files[0]}",),
                        daemon=True
                    ).start()
                    session['last_speak_time'] = current_time
                response_data.update({
                    'status': 'Started browsing files',
                    'state': 'BROWSING'
                })

        elif current_state == 'BROWSING':
            # OPEN PALM -> NEXT FILE
            if gesture == 'open_palm':
                current_index = (current_index + 1) % len(files)
                session['current_file_index'] = current_index
                session['debounce_time'] = current_time
                if current_time - last_speak_time > SPEAK_INTERVAL:
                    threading.Thread(
                        target=speak_without_saving,
                        args=(f"File: {files[current_index]}",),
                        daemon=True
                    ).start()
                    session['last_speak_time'] = current_time
                response_data.update({
                    'status': f'Browsing: {files[current_index]}',
                    'current_file': files[current_index]
                })

            # FIST -> PREVIOUS FILE
            elif gesture == 'fist':
                current_index = (current_index - 1) % len(files)
                session['current_file_index'] = current_index
                session['debounce_time'] = current_time
                if current_time - last_speak_time > SPEAK_INTERVAL:
                    threading.Thread(
                        target=speak_without_saving,
                        args=(f"File: {files[current_index]}",),
                        daemon=True
                    ).start()
                    session['last_speak_time'] = current_time
                response_data.update({
                    'status': f'Browsing: {files[current_index]}',
                    'current_file': files[current_index]
                })

            # POINT -> SELECT FILE (go to CONFIRMING)
            elif gesture == 'point':
                session['gesture_state'] = 'CONFIRMING'
                session['selected_file'] = files[current_index]
                session['confirmation_start'] = current_time
                session['debounce_time'] = current_time
                if current_time - last_speak_time > SPEAK_INTERVAL:
                    threading.Thread(
                        target=speak_without_saving,
                        args=(f"Selected {files[current_index]}. Show thumbs up to confirm, thumbs down to cancel.",),
                        daemon=True
                    ).start()
                    session['last_speak_time'] = current_time
                response_data.update({
                    'status': f'Confirm upload of {files[current_index]}?',
                    'state': 'CONFIRMING',
                    'selected_file': files[current_index]
                })

            # THUMBS DOWN -> EXIT BROWSING, BACK TO IDLE
            elif gesture == 'thumbs_down':
                session['gesture_state'] = 'IDLE'
                session['selected_file'] = None
                session['debounce_time'] = current_time
                if current_time - last_speak_time > SPEAK_INTERVAL:
                    threading.Thread(
                        target=speak_without_saving,
                        args=("Browsing cancelled. Back to idle.",),
                        daemon=True
                    ).start()
                    session['last_speak_time'] = current_time
                response_data.update({
                    'status': 'Browsing cancelled',
                    'state': 'IDLE'
                })

        elif current_state == 'CONFIRMING':
            # THUMBS UP -> CONFIRM UPLOAD (only meaning for 👍)
            if gesture == 'thumbs_up':
                selected_file = session.get('selected_file')
                source_path = os.path.join(GESTURE_SOURCE_FOLDER, selected_file)
                dest_path = os.path.join(UPLOAD_FOLDER, selected_file)
                try:
                    import shutil
                    shutil.copy2(source_path, dest_path)
                    processing_result = process_file_with_ai(dest_path)  # One-step process
                    session['gesture_state'] = 'IDLE'
                    session['debounce_time'] = current_time
                    if current_time - last_speak_time > SPEAK_INTERVAL:
                        threading.Thread(
                            target=speak_without_saving,
                            args=("Upload successful. Processing complete.",),
                            daemon=True
                        ).start()
                        session['last_speak_time'] = current_time
                    response_data.update({
                        'status': 'Upload successful',
                        'state': 'IDLE',
                        'uploaded_file': selected_file,
                        'processing_result': processing_result
                    })
                except Exception as e:
                    print(f"Upload error: {e}")
                    response_data.update({
                        'status': f'Upload failed: {str(e)}',
                        'state': 'ERROR'
                    })

            # THUMBS DOWN -> CANCEL CONFIRMATION (back to BROWSING)
            elif gesture == 'thumbs_down':
                session['gesture_state'] = 'BROWSING'
                session['selected_file'] = None
                session['debounce_time'] = current_time
                if current_time - last_speak_time > SPEAK_INTERVAL:
                    threading.Thread(
                        target=speak_without_saving,
                        args=("Selection cancelled. Continue browsing.",),
                        daemon=True
                    ).start()
                    session['last_speak_time'] = current_time
                response_data.update({
                    'status': 'Selection cancelled',
                    'state': 'BROWSING'
                })


        # --- End of Gesture Logic ---
        session.modified = True
        return jsonify(response_data)

    except Exception as e:
        print(f"Critical error in detect_image: {e}")
        return jsonify({
            'error': str(e),
            'status': 'System error',
            'gesture': 'unknown',
            'state': 'ERROR'
        }), 500


@gesture_bp.route('/reset', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['http://localhost:3000', 'http://localhost:3001'], supports_credentials=True)
def reset_session():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    session.clear()
    return jsonify({'status': 'Session reset', 'state': 'RESET'})


@gesture_bp.route('/status', methods=['GET', 'OPTIONS'])
@cross_origin(origins=['http://localhost:3000', 'http://localhost:3001'], supports_credentials=True)
def session_status():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
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
        return jsonify({
            'success': False,
            'error': 'This file is already being processed. Please wait.'
        }), 409

    uploaded_file = find_uploaded_file_by_id(file_id)
    if not uploaded_file:
        return jsonify({'success': False, 'error': 'File not found'}), 404

    try:
        PROCESSING_FILES.add(file_id)
        logger.info(f"Processing file: {uploaded_file}")

        # Use the global processor instance
        result = processor.process_syllabus(uploaded_file)

        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', 'Processing failed')
            }), 500

        session_id = str(uuid.uuid4())
        result.update({
            'processed_at': time.time(),
            'session_id': session_id,
        })

        result_path = os.path.join(DATA_FOLDER, f"{session_id}.json")
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(
            f"Processing completed. Session ID: {session_id}, Modules: {len(result.get('modules', []))}"
        )

        return jsonify({
            'success': True,
            'session_id': session_id,
            'modules_count': len(result.get('modules', [])),
            'message': 'Processing completed successfully'
        }), 200

    except Exception as e:
        logger.exception("Processing error during main execution")
        return jsonify({
            'success': False,
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500

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

# Outcomes generation route


@app.route('/api/generate_outcomes', methods=['GET', 'OPTIONS'])
@cross_origin(origins=['http://localhost:3000', 'http://localhost:3001'], supports_credentials=True)
def generate_outcomes():
    """
    Generate course outcomes from processed modules.
    Query param: session_id (string)
    """
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'success': False, 'error': 'No session_id provided'}), 400

    safe_id = secure_filename(session_id)
    result_path = os.path.join(DATA_FOLDER, f"{safe_id}.json")
    if not os.path.exists(result_path):
        return jsonify({
            'success': False,
            'error': 'Results not found for provided session_id'
        }), 404

    try:
        with open(result_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        modules = results.get('modules', [])
        if not modules:
            return jsonify({
                'success': False,
                'error': 'No modules available in results'
            }), 400

        outcomes = analyser.generate_outcomes_per_module(modules)
        # Print formatted results in terminal
        analyser.print_generated_outcomes(outcomes)

        logger.info(f"Generated outcomes for session {session_id}")

        return jsonify({
            'success': True,
            'session_id': session_id,
            'models_loaded': getattr(analyser, "MODELS_LOADED", False),
            'outcomes': outcomes,
            'course_outcomes': outcomes
        }), 200
    except Exception as e:
        logger.exception("Error generating outcomes")
        return jsonify({
            'success': False,
            'error': f'Failed to generate outcomes: {str(e)}'
        }), 500

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
    print("Unified Syllabus Upload & Processing Backend (v1.1)")
    print("=" * 70)
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Gesture source folder: {GESTURE_SOURCE_FOLDER}")
    print(f"Data folder: {DATA_FOLDER}")
    print(f"CORS enabled for: http://localhost:3000, http://localhost:3001")
    print(f" Max file size: {MAX_FILE_SIZE // 1024 // 1024}MB")
    print(f"Allowed types: {ALLOWED_EXTENSIONS}")
    print("=" * 70)
    print("\n Starting Flask server...\n")

    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )
