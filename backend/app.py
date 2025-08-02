from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import uuid
from werkzeug.utils import secure_filename
from processor import SyllabusProcessor
import time
import logging

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize processor
processor = SyllabusProcessor()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'message': 'Syllabus API is running',
        'timestamp': time.time()
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
            
            # Save file
            file.save(filepath)
            
            logger.info(f"File uploaded successfully: {filename} (ID: {file_id})")
            
            return jsonify({
                'success': True,
                'file_id': file_id,
                'filename': filename,
                'message': 'File uploaded successfully'
            })
        
        return jsonify({'success': False, 'error': 'Invalid file type. Only PDF and TXT files are allowed.'}), 400
    
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/process', methods=['POST'])
def process_syllabus():
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        
        if not file_id:
            return jsonify({'success': False, 'error': 'No file ID provided'}), 400
        
        # Find the uploaded file
        upload_dir = app.config['UPLOAD_FOLDER']
        uploaded_file = None
        
        for filename in os.listdir(upload_dir):
            if filename.startswith(file_id):
                uploaded_file = os.path.join(upload_dir, filename)
                break
        
        if not uploaded_file:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        logger.info(f"Processing file: {uploaded_file}")
        
        # Process the file
        result = processor.process_syllabus(uploaded_file)
        
        if not result.get('success', False):
            return jsonify({
                'success': False,
                'error': result.get('error', 'Processing failed')
            }), 500
        
        # Generate session ID and save results
        session_id = str(uuid.uuid4())
        result_path = os.path.join(DATA_FOLDER, f"{session_id}.json")
        
        # Add metadata to results
        result['processed_at'] = time.time()
        result['session_id'] = session_id
        
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Processing completed. Session ID: {session_id}, Modules: {len(result.get('modules', []))}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'modules_count': len(result.get('modules', [])),
            'message': 'Processing completed successfully'
        })
    
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/results', methods=['GET'])
def get_results():
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'No session ID provided'}), 400
        
        result_path = os.path.join(DATA_FOLDER, f"{session_id}.json")
        
        if not os.path.exists(result_path):
            return jsonify({'success': False, 'error': 'Results not found'}), 404
        
        with open(result_path, 'r') as f:
            results = json.load(f)
        
        logger.info(f"Results retrieved for session: {session_id}")
        
        return jsonify({
            'success': True,
            'modules': results.get('modules', []),
            'processed_at': results.get('processed_at'),
            'total_modules': len(results.get('modules', []))
        })
    
    except Exception as e:
        logger.error(f"Results retrieval error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(DATA_FOLDER, exist_ok=True)
    
    logger.info("Starting Syllabus API server...")
    logger.info(f"Upload folder: {UPLOAD_FOLDER}")
    logger.info(f"Data folder: {DATA_FOLDER}")
    
    app.run(debug=True, port=5001, host='0.0.0.0')
