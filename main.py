from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from brain import get_dashboard_data

app = Flask(__name__)
app.secret_key = "super_secret_key" # Required for sessions

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
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Your existing API route with a small tweak for Employees
@app.route('/api/data')
def api_data():
    if 'user' not in session: return jsonify({"error": "unauthorized"}), 401
    
    data = get_dashboard_data("data/Data_test.csv")
    
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