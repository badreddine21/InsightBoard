from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from brain import get_dashboard_data, compare_files
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super_secret_key" # Required for sessions
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder if it doesn't exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# In-memory storage for comments (in production, use a database)
comments_storage = {
    'boss': [],
    'sales': [],
    'hr': []
}

# Dummy user database
USERS = {
    "boss@company.com": {"password": "123", "role": "boss", "name": "Director"},
    "acc@company.com": {"password": "123", "role": "sales", "name": "Head Accountant"},
    "hr@company.com": {"password": "123", "role": "hr", "name": "HR Manager"}
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = USERS.get(email)
        if user and user['password'] == password:
            session['user'] = user
            return redirect(url_for('upload'))
    return render_template('login.html')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload.html', user=session['user'], error='No file selected', page_title='Upload Data')
        
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', user=session['user'], error='No file selected', page_title='Upload Data')
        
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Store the data path in session for dashboard
            session['data_file'] = filepath
            return redirect(url_for('dashboard'))
        else:
            return render_template('upload.html', user=session['user'], error='Please upload a CSV file', page_title='Upload Data')
    
    return render_template('upload.html', user=session['user'], page_title='Upload Data')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'], page_title='Dashboard')

@app.route('/insights')
def insights():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('insights.html', user=session['user'], page_title='Insights')

@app.route('/comments')
def comments():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('comments.html', user=session['user'], page_title='Comments')

@app.route('/compare', methods=['GET', 'POST'])
def compare():
    # Boss and sales can access this
    if 'user' not in session or session['user']['role'] not in ['boss', 'sales']:
        return redirect(url_for('login'))
    
    comparison_result = None
    error = None
    
    if request.method == 'POST':
        if 'file1' not in request.files or 'file2' not in request.files:
            error = 'Please upload both files'
        else:
            file1 = request.files['file1']
            file2 = request.files['file2']
            
            if file1.filename == '' or file2.filename == '':
                error = 'Both files must be selected'
            elif not (file1.filename.endswith('.csv') and file2.filename.endswith('.csv')):
                error = 'Both files must be CSV format'
            else:
                try:
                    # Save both files temporarily
                    filename1 = secure_filename(file1.filename)
                    filename2 = secure_filename(file2.filename)
                    filepath1 = os.path.join(app.config['UPLOAD_FOLDER'], 'compare_' + filename1)
                    filepath2 = os.path.join(app.config['UPLOAD_FOLDER'], 'compare_' + filename2)
                    
                    file1.save(filepath1)
                    file2.save(filepath2)
                    
                    # Compare the files
                    comparison_result = compare_files(filepath1, filepath2)
                except Exception as e:
                    error = f'Error comparing files: {str(e)}'
    
    return render_template('compare.html', user=session['user'], comparison=comparison_result, error=error, page_title='Compare Files')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/api/comments', methods=['GET', 'POST', 'DELETE'])
def api_comments():
    if 'user' not in session:
        return jsonify({"error": "unauthorized"}), 401
    
    user_role = session['user']['role']
    
    if request.method == 'POST':
        # Only boss can send comments
        if user_role != 'boss':
            return jsonify({"error": "only boss can send comments"}), 403
        
        data = request.get_json()
        department = data.get('department')
        message = data.get('message')
        
        if not department or not message:
            return jsonify({"error": "department and message required"}), 400
        
        if department not in comments_storage:
            return jsonify({"error": "invalid department"}), 400
        
        comment = {
            "sender": session['user']['name'],
            "content": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        comments_storage[department].append(comment)
        return jsonify({"success": True, "message": "Comment sent successfully"})
    
    elif request.method == 'DELETE':
        # Non-boss users can delete comments from their department
        if user_role == 'boss':
            return jsonify({"error": "boss cannot delete comments"}), 403
        
        data = request.get_json()
        comment_index = data.get('index')
        
        if comment_index is None:
            return jsonify({"error": "comment index required"}), 400
        
        comments_list = comments_storage.get(user_role, [])
        if 0 <= comment_index < len(comments_list):
            comments_list.pop(comment_index)
            return jsonify({"success": True, "message": "Comment marked as read"})
        else:
            return jsonify({"error": "invalid comment index"}), 400
    
    else:
        # GET: Retrieve comments for user's department
        comments = comments_storage.get(user_role, [])
        return jsonify({"comments": comments})

# Your existing API route with a small tweak for Employees
@app.route('/api/data')
def api_data():
    if 'user' not in session: return jsonify({"error": "unauthorized"}), 401
    
    # Use uploaded file if available, otherwise use default
    data_file = session.get('data_file', 'data/Data_test.csv')
    data = get_dashboard_data(data_file)
    
    # Calculate bonuses for EVERYONE (for HR/Boss/Sales to see)
    # 3% of net_amount for each cashier
    bonuses = []
    labels = data['cashier_sales']['labels']
    values = data['cashier_sales']['values']
    
    for i in range(len(labels)):
        bonuses.append({
            "name": labels[i],
            "total_sales": values[i],
            "bonus": round(values[i] * 0.03, 2)
        })
    
    data['bonus_report'] = bonuses # Attach this to the main data object
    return jsonify(data)
if __name__ == "__main__":
    app.run(debug=True)