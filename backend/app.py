from flask import Flask, request, jsonify, send_from_directory, send_file, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

from utils.detector import ComponentDetector
from database.db_manager import DatabaseManager

# serve frontend files from project/frontend
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# root route returns index.html from frontend
@app.route('/')
def root():
    return app.send_static_file('index.html')

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max

# Initialize detector and database
# Detector will prefer a trained weights file if available (backend/models/best.pt)
# otherwise it falls back to the supplied default

detector = ComponentDetector()
db = DatabaseManager(connection_string='mongodb://localhost:27017/', db_name='green_mining')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/scan', methods=['POST'])
def upload_scan():
    # Check if file is present
    if 'image' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Use JPG, JPEG, or PNG'}), 415
    
    # Generate unique scan ID
    scan_id = str(uuid.uuid4())
    filename = secure_filename(f"{scan_id}.jpg")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save uploaded file
    file.save(filepath)
    
    try:
        # Process image
        results = detector.detect_components(filepath)
        
        # Save annotated image
        annotated_path = os.path.join(app.config['RESULTS_FOLDER'], f"{scan_id}_annotated.jpg")
        detector.save_annotated_image(results, annotated_path)
        
        # enrich detections with component database info
        enriched = []
        for det in results['detections']:
            cat = det.get('component')
            comp_entry = db.get_component_by_category(cat)
            if comp_entry:
                det['component_name'] = comp_entry.get('name', cat)
                det['component_category'] = comp_entry.get('category', cat)
                det['estimated_value'] = comp_entry.get('market_value_usd', det.get('estimated_value', 0))
                det['recyclability_score'] = comp_entry.get('recyclability_score', det.get('recyclability_score', 0))
            else:
                det['component_name'] = cat
                det['component_category'] = cat
            enriched.append(det)
        results['detections'] = enriched

        # Calculate total value and stats
        total_value = sum([det['estimated_value'] for det in results['detections']])
        recyclability = detector.calculate_recyclability(results['detections'])
        
        # Store in database
        scan_data = {
            'scan_id': scan_id,
            'original_image': filename,
            'processed_image': f"{scan_id}_annotated.jpg",
            'detections': results['detections'],
            'total_components': len(results['detections']),
            'total_value': total_value,
            'recyclability_score': recyclability,
            'processing_time_ms': results['processing_time'],
            'status': 'completed',
            'created_at': datetime.now()
        }
        db.insert_scan(scan_data)
        
        return jsonify({
            'scan_id': scan_id,
            'status': 'completed',
            'total_components': len(results['detections']),
            'total_value': f"${total_value:.2f}",
            'recyclability_score': recyclability
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500


@app.route('/api/scan/<scan_id>', methods=['GET'])
def get_scan_results(scan_id):
    try:
        scan = db.get_scan(scan_id)
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        
        # Convert ObjectId to string for JSON serialization
        scan['_id'] = str(scan['_id'])
        scan['created_at'] = scan['created_at'].isoformat()
        
        return jsonify(scan), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    try:
        stats = db.get_overall_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/<scan_id>/report', methods=['GET'])
def get_scan_report(scan_id):
    """Generate a simple PDF report for a scan and return it."""
    try:
        scan = db.get_scan(scan_id)
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404

        from fpdf import FPDF
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f"Scan Report: {scan_id}", ln=1)
        pdf.ln(5)
        # annotated image
        if scan.get('processed_image'):
            img_path = os.path.join(app.config['RESULTS_FOLDER'], scan['processed_image'])
            if os.path.exists(img_path):
                pdf.image(img_path, w=150)
                pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Detections:', ln=1)
        pdf.set_font('Arial', '', 10)
        pdf.cell(60, 8, 'Component', border=1)
        pdf.cell(40, 8, 'Category', border=1)
        pdf.cell(30, 8, 'Confidence', border=1)
        pdf.cell(30, 8, 'Value', border=1, ln=1)
        for det in scan.get('detections', []):
            pdf.cell(60, 6, det.get('component_name',''), border=1)
            pdf.cell(40, 6, det.get('component_category',''), border=1)
            pdf.cell(30, 6, f"{det.get('confidence',0)*100:.1f}%", border=1)
            pdf.cell(30, 6, f"${det.get('estimated_value',0):.2f}", border=1, ln=1)
        pdf.ln(5)
        pdf.cell(0, 10, f"Total components: {scan.get('total_components',0)}", ln=1)
        pdf.cell(0, 10, f"Estimated value: ${scan.get('total_value',0):.2f}", ln=1)
        pdf.cell(0, 10, f"Recyclability score: {scan.get('recyclability_score',0)}", ln=1)
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        return Response(pdf_bytes, mimetype='application/pdf', headers={'Content-Disposition': f'attachment; filename={scan_id}_report.pdf'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# component catalog endpoints
@app.route('/api/components', methods=['GET'])
def list_components():
    try:
        comps = db.list_components()
        # convert ObjectId to str if present
        for c in comps:
            if '_id' in c:
                c['_id'] = str(c['_id'])
        return jsonify(comps), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/components', methods=['POST'])
def add_component():
    data = request.json
    if not data or 'name' not in data or 'category' not in data:
        return jsonify({'error': 'name and category required'}), 400
    try:
        # basic validation
        comp = {
            'name': data['name'],
            'category': data['category'],
            'materials': data.get('materials', {}),
            'market_value_usd': data.get('market_value_usd', 0),
            'recyclability_score': data.get('recyclability_score', 0),
            'created_at': datetime.now()
        }
        if db.use_memory:
            db._mem_components.append(comp)
        else:
            db.components.insert_one(comp)
        return jsonify({'status': 'success'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/results/<filename>')
def result_file(filename):
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)


if __name__ == '__main__':
    # Ensure folders exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
