from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import uuid
from werkzeug.utils import secure_filename
from processor import SyllabusProcessor
import time
import logging

app = Flask(__name__)  # Fixed: __name__ instead of **name**
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

app.config.update({
    'UPLOAD_FOLDER': UPLOAD_FOLDER,
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024  # 16MB
})

# Ensure directories exist at startup
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

# Initialize processor
processor = SyllabusProcessor()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  # Fixed: __name__ instead of **name**

def allowed_file(filename: str) -> bool:
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Syllabus API is running',
        'timestamp': time.time()
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
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
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'message': 'File uploaded successfully'
        })
    except Exception as e:
        logger.exception("Upload error")
        return jsonify({'success': False, 'error': 'Failed to save file'}), 500

@app.route('/api/process', methods=['POST'])
def process_syllabus():
    data = request.get_json(silent=True)
    file_id = data.get('file_id') if data else None
    
    if not file_id:
        return jsonify({'success': False, 'error': 'No file ID provided'}), 400
    
    # Locate file by matching prefix
    try:
        uploaded_file = next(
            os.path.join(app.config['UPLOAD_FOLDER'], f)
            for f in os.listdir(app.config['UPLOAD_FOLDER'])
            if f.startswith(file_id)
        )
    except StopIteration:
        return jsonify({'success': False, 'error': 'File not found'}), 404
    
    logger.info(f"Processing file: {uploaded_file}")
    
    try:
        result = processor.process_syllabus(uploaded_file)
    except Exception as e:
        logger.exception("Processing error")
        return jsonify({'success': False, 'error': 'Processing failed'}), 500
    
    if not result.get('success'):
        return jsonify({'success': False, 'error': result.get('error', 'Processing failed')}), 500
    
    # Save results with new session_id
    session_id = str(uuid.uuid4())
    result.update({
        'processed_at': time.time(),
        'session_id': session_id,
    })
    
    result_path = os.path.join(DATA_FOLDER, f"{session_id}.json")
    try:
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
    except Exception as e:
        logger.exception("Error saving result data")
        return jsonify({'success': False, 'error': 'Failed to save results'}), 500
    
    logger.info(f"Processing completed. Session ID: {session_id}, Modules: {len(result.get('modules', []))}")
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'modules_count': len(result.get('modules', [])),
        'message': 'Processing completed successfully'
    })

@app.route('/api/results', methods=['GET'])
def get_results():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'success': False, 'error': 'No session ID provided'}), 400
    
    result_path = os.path.join(DATA_FOLDER, f"{session_id}.json")
    if not os.path.exists(result_path):
        return jsonify({'success': False, 'error': 'Results not found'}), 404
    
    try:
        with open(result_path, 'r') as f:
            results = json.load(f)
    except Exception as e:
        logger.exception("Error reading results")
        return jsonify({'success': False, 'error': 'Failed to read results'}), 500
    
    logger.info(f"Results retrieved for session: {session_id}")
    
    return jsonify({
        'success': True,
        'modules': results.get('modules', []),
        'processed_at': results.get('processed_at'),
        'total_modules': len(results.get('modules', []))
    })

if __name__ == '__main__':  # Fixed: __name__ and __main__ instead of **name** and **main**
    logger.info("Starting Syllabus API server...")
    logger.info(f"Upload folder: {UPLOAD_FOLDER}")
    logger.info(f"Data folder: {DATA_FOLDER}")
    app.run(debug=False, port=5001, host='0.0.0.0')
