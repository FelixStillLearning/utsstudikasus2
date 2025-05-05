from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app.auth.utils import hash_password, verify_password
from app.auth.models import User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app import db  # Delayed import to avoid circular import
    
    if request.method == 'GET':
        return render_template('auth/login.html', current_year=datetime.now().year)
    
    # Handle POST request
    if request.is_json:
        # Handle JSON API request
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        # Handle form submission
        username = request.form.get('username')
        password = request.form.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and verify_password(password, user.password):
        if request.is_json:
            return jsonify({"message": "Login successful"}), 200
        # For form submission, redirect to homepage or dashboard
        return redirect(url_for('home'))
    
    if request.is_json:
        return jsonify({"message": "Invalid credentials"}), 401
    # For form submission, re-render the login page with an error
    return render_template('auth/login.html', error="Invalid username or password", current_year=datetime.now().year)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    from app import db  # Delayed import to avoid circular import
    
    if request.method == 'GET':
        return render_template('auth/register.html', current_year=datetime.now().year)
    
    # Handle POST request
    if request.is_json:
        # Handle JSON API request
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')  # Email might be optional for API
    else:
        # Handle form submission
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        
        # Check if passwords match for form submission
        if password != confirm_password:
            return render_template('auth/register.html', error="Passwords do not match", current_year=datetime.now().year)
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        if request.is_json:
            return jsonify({"message": "User already exists"}), 400
        return render_template('auth/register.html', error="Username already exists", current_year=datetime.now().year)
    
    # Create new user
    hashed_password = hash_password(password)
    new_user = User(username=username, password=hashed_password, email=email)
    db.session.add(new_user)
    db.session.commit()
    
    if request.is_json:
        return jsonify({"message": "User registered successfully"}), 201
    # For form submission, redirect to login page
    return redirect(url_for('auth.login'))