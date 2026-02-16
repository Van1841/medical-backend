from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import pickle
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pandas as pd
import PyPDF2
from datetime import datetime
import json
from utils.ocr import extract_text_from_image
from utils.parser import parse_medical_values, validate_values
from utils.gemini import generate_explanation, get_health_tips
from utils.hospital_locator import find_nearest_hospitals, get_google_maps_link
from utils.chatbot import get_chatbot_response, build_report_context
from utils.risk_scoring import calculate_risk_score, get_risk_score_message, get_risk_color

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# CORS configuration for frontend
CORS(app, 
     supports_credentials=True, 
     origins=[
         'http://localhost:8000',
         'http://127.0.0.1:8000',
         'http://localhost:3000',
         'http://localhost:5173',
         'https://medical-frontend-lemon.vercel.app'
     ],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Changed from 'None' for localhost
app.config['SESSION_COOKIE_SECURE'] = True  # Changed to False for localhost

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# def load_ml_model():
#     with open('model/risk_model.pkl', 'rb') as f:
#         model = pickle.load(f)
#     return model

# model = load_ml_model()

init_db()
os.makedirs('uploads', exist_ok=True)

def load_ml_model():
    with open('model/risk_model.pkl', 'rb') as f:
        model = pickle.load(f)
    return model

model = load_ml_model()

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200

# Auth endpoints
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    
    hashed_password = generate_password_hash(password)
    
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                     (name, email, hashed_password))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Account created successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 409

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user[3], password):
        session['user_id'] = user[0]
        session['user_name'] = user[1]
        session['user_email'] = user[2]
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user[0],
                'name': user[1],
                'email': user[2]
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/user', methods=['GET'])
def get_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({
        'user': {
            'id': session.get('user_id'),
            'name': session.get('user_name'),
            'email': session.get('user_email')
        }
    }), 200

@app.route('/api/analyze', methods=['POST'])
def analyze():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        text = None
        
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'Invalid file type. Only PDF, images, and text files are allowed.'}), 400
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            if filename.lower().endswith('.pdf'):
                with open(filepath, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    text = ''
                    for page in pdf_reader.pages:
                        text += page.extract_text()
            elif filename.lower().endswith('.txt'):
                with open(filepath, 'r', encoding='utf-8') as txt_file:
                    text = txt_file.read()
            else:
                text = extract_text_from_image(filepath)
            
            os.remove(filepath)
        
        elif 'text' in request.form and request.form['text'].strip():
            text = request.form['text']
        
        else:
            return jsonify({'error': 'No input provided'}), 400
        
        if not text:
            return jsonify({'error': 'Could not extract text from the file'}), 400
        
        values = parse_medical_values(text)
        
        errors = validate_values(values)
        if errors:
            return jsonify({'error': 'Missing or invalid values: ' + ', '.join(errors)}), 400
        
        # Prepare values for ML prediction
        ml_values = {
            'hemoglobin': values['hemoglobin'] if values['hemoglobin'] is not None else 14.0,
            'blood_sugar': values['blood_sugar'] if values['blood_sugar'] is not None else 100.0,
            'cholesterol': values['cholesterol'] if values['cholesterol'] is not None else 190.0
        }
        
        input_data = pd.DataFrame([ml_values])
        prediction = model.predict(input_data)[0]
        
        # Calculate risk score
        risk_score = calculate_risk_score(values, prediction)
        risk_message = get_risk_score_message(risk_score)
        risk_color = get_risk_color(risk_score)
        
        explanation = generate_explanation(values, prediction)
        tips = get_health_tips(values, prediction)
        
        result = {
            'values': values,
            'risk_level': prediction,
            'risk_score': risk_score,
            'risk_message': risk_message,
            'risk_color': risk_color,
            'explanation': explanation,
            'tips': tips,
            'timestamp': datetime.now().isoformat(),
            'report_text': text[:500]
        }
        
        # Store in session
        session['last_result'] = result
        
        # Also store in report history
        if 'report_history' not in session:
            session['report_history'] = []
        session['report_history'].append(result)
        session.modified = True
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print("="*60)
        print("ERROR IN ANALYZE ROUTE:")
        print(error_details)
        print("="*60)
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/find-hospitals', methods=['POST'])
def find_hospitals():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))
        
        hospitals = find_nearest_hospitals(lat, lon, limit=5)
        maps_link = get_google_maps_link(lat, lon)
        
        return jsonify({
            'hospitals': hospitals,
            'maps_link': maps_link
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to find hospitals: {str(e)}'}), 500

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get report context if available
        report_context = None
        if 'last_result' in session:
            result = session['last_result']
            report_context = build_report_context(
                result.get('values', {}),
                result.get('risk_level', 'Unknown'),
                result.get('risk_score', 0)
            )
        
        # Get chatbot response
        bot_response = get_chatbot_response(user_message, report_context)
        
        return jsonify({
            'response': bot_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Chatbot error: {str(e)}'}), 500

@app.route('/api/analyze-multiple', methods=['POST'])
def analyze_multiple():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        files = request.files.getlist('files')
        
        if not files or len(files) == 0:
            return jsonify({'error': 'No files provided'}), 400
        
        results = []
        
        for file in files:
            if file and file.filename != '':
                if not allowed_file(file.filename):
                    continue
                
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Extract text
                text = ''
                if filename.lower().endswith('.pdf'):
                    with open(filepath, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        for page in pdf_reader.pages:
                            text += page.extract_text()
                elif filename.lower().endswith('.txt'):
                    with open(filepath, 'r', encoding='utf-8') as txt_file:
                        text = txt_file.read()
                else:
                    text = extract_text_from_image(filepath)
                
                os.remove(filepath)
                
                if text:
                    values = parse_medical_values(text)
                    errors = validate_values(values)
                    
                    if not errors:
                        ml_values = {
                            'hemoglobin': values['hemoglobin'] if values['hemoglobin'] is not None else 14.0,
                            'blood_sugar': values['blood_sugar'] if values['blood_sugar'] is not None else 100.0,
                            'cholesterol': values['cholesterol'] if values['cholesterol'] is not None else 190.0
                        }
                        
                        input_data = pd.DataFrame([ml_values])
                        prediction = model.predict(input_data)[0]
                        risk_score = calculate_risk_score(values, prediction)
                        
                        results.append({
                            'filename': filename,
                            'values': values,
                            'risk_level': prediction,
                            'risk_score': risk_score,
                            'timestamp': datetime.now().isoformat()
                        })
        
        if len(results) == 0:
            return jsonify({'error': 'No valid reports could be analyzed'}), 400
        
        # Calculate trends
        trends = calculate_trends(results)
        
        # Store in session
        session['report_history'] = results
        session.modified = True
        
        return jsonify({
            'reports': results,
            'trends': trends,
            'total_reports': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': f'Multi-report analysis failed: {str(e)}'}), 500

def calculate_trends(results):
    """Calculate health trends from multiple reports"""
    if len(results) < 2:
        return {'message': 'Need at least 2 reports for trend analysis'}
    
    trends = {}
    
    # Sort by timestamp
    sorted_results = sorted(results, key=lambda x: x['timestamp'])
    first = sorted_results[0]
    latest = sorted_results[-1]
    
    # Hemoglobin trend
    if first['values'].get('hemoglobin') and latest['values'].get('hemoglobin'):
        hb_diff = latest['values']['hemoglobin'] - first['values']['hemoglobin']
        trends['hemoglobin'] = {
            'change': round(hb_diff, 1),
            'direction': 'improving' if hb_diff > 0 else 'worsening' if hb_diff < 0 else 'stable',
            'first': first['values']['hemoglobin'],
            'latest': latest['values']['hemoglobin']
        }
    
    # Blood sugar trend
    if first['values'].get('blood_sugar') and latest['values'].get('blood_sugar'):
        bs_diff = latest['values']['blood_sugar'] - first['values']['blood_sugar']
        trends['blood_sugar'] = {
            'change': round(bs_diff, 1),
            'direction': 'worsening' if bs_diff > 0 else 'improving' if bs_diff < 0 else 'stable',
            'first': first['values']['blood_sugar'],
            'latest': latest['values']['blood_sugar']
        }
    
    # Cholesterol trend
    if first['values'].get('cholesterol') and latest['values'].get('cholesterol'):
        chol_diff = latest['values']['cholesterol'] - first['values']['cholesterol']
        trends['cholesterol'] = {
            'change': round(chol_diff, 1),
            'direction': 'worsening' if chol_diff > 0 else 'improving' if chol_diff < 0 else 'stable',
            'first': first['values']['cholesterol'],
            'latest': latest['values']['cholesterol']
        }
    
    # Risk score trend
    risk_diff = latest['risk_score'] - first['risk_score']
    trends['overall'] = {
        'change': risk_diff,
        'direction': 'worsening' if risk_diff > 0 else 'improving' if risk_diff < 0 else 'stable',
        'first_score': first['risk_score'],
        'latest_score': latest['risk_score']
    }
    
    return trends


# Initialize database on startup

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)


# if __name__ == '__main__':
#     init_db()
#     os.makedirs('uploads', exist_ok=True)
#     port = int(os.environ.get('PORT', 5000))
#     app.run(debug=False, host='0.0.0.0', port=port)
