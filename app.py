# app.py - Language Learning Application
# This is the main application file that handles routes and user authentication

# Standard library imports
import os
import json
import random
import secrets
import smtplib
import sqlite3
import hashlib
import uuid
import traceback
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict, Counter
from random import sample, shuffle
from functools import wraps
import time

# Apply universal database fix - eliminated in favor of database_config.py
# Database connection is now handled by bulletproof system in database_config.py
print("🔧 Using bulletproof database system from database_config.py")

# Third-party imports
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import google.generativeai as genai
import pandas as pd
import io
import csv
import difflib
import mimetypes

# Optional imports with error handling
# psutil is used for memory monitoring in development/debugging
PSUTIL_AVAILABLE = False
psutil = None
try:
    import psutil  # type: ignore
    PSUTIL_AVAILABLE = True
except ImportError:
    # psutil is optional - memory monitoring will be disabled if not available
    pass

# Environment variable support
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass

# Initialize Flask application
app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'FL4sk-L4ngu4g3-L34rn1ng-S3cr3t-K3y-2024-S3cur3-R4nd0m-K3y-P3rs1st3nc3')

# --- File Upload Configuration ---
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# --- SMTP Configuration for Email Notifications ---
# These settings are used for sending OTP and password reset emails
USE_CONSOLE_OTP = os.getenv('USE_CONSOLE_OTP', 'True').lower() == 'true'

# SMTP settings for Gmail - using environment variables for security
smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
smtp_port = int(os.getenv('SMTP_PORT', '465'))  # SSL port for Gmail
smtp_user = os.getenv('SMTP_USER', 'your_email@gmail.com')
smtp_password = os.getenv('SMTP_PASSWORD', 'your_app_password')

# --- Google Gemini AI Configuration ---
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables")
    API_KEY = "your_api_key_here"  # Fallback for development
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# Add Gemini Vision model for image support
vision_model = genai.GenerativeModel('gemini-1.5-flash')

# --- Flashcards now load from database instead of Excel files ---

# --- Database Functions ---
# These functions handle database connections and common database operations

def get_db_connection():
    """
    Get bulletproof database connection with full error handling
    """
    from database_config import get_db_connection as get_bulletproof_connection
    return get_bulletproof_connection()

# No longer needed - using bulletproof database system
print("✅ Using bulletproof database system from database_config.py")

        # Ensure all tables have required columns for compatibility
try:
    from database_config import ensure_all_table_compatibility
    ensure_all_table_compatibility()
    
    # Ensure avatar and other profile columns exist with proper PostgreSQL handling
    with get_db_connection() as conn:
        # Get database type to handle PostgreSQL vs SQLite differently
        db_type = getattr(conn, 'db_type', 'sqlite')
        
        if db_type == 'postgresql':
            # PostgreSQL: Check if columns exist before adding them
            columns_to_add = {
                'avatar': 'TEXT',
                'name': 'TEXT', 
                'phone': 'TEXT',
                'location': 'TEXT',
                'website': 'TEXT',
                'timezone': 'TEXT',
                'datetime_format': 'TEXT'
            }
            
            for column_name, column_type in columns_to_add.items():
                try:
                    # Check if column exists in PostgreSQL
                    result = conn.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'users' AND column_name = ?
                    """, (column_name,)).fetchone()
                    
                    if not result:
                        # Column doesn't exist, add it
                        conn.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
                        conn.commit()
                        print(f"✅ Added '{column_name}' column to users table")
                    else:
                        print(f"ℹ️ Column '{column_name}' already exists in users table")
                        
                except Exception as e:
                    print(f"⚠️ Could not add column '{column_name}': {e}")
                    # Rollback the failed transaction
                    conn.rollback()
                    
        else:
            # SQLite: Use simpler approach with try/catch
            columns_to_add = ['avatar', 'name', 'phone', 'location', 'website', 'timezone', 'datetime_format']
            
            for column_name in columns_to_add:
                try:
                    conn.execute(f"ALTER TABLE users ADD COLUMN {column_name} TEXT")
                    conn.commit()
                    print(f"✅ Added '{column_name}' column to users table")
                except Exception:
                    # Column likely already exists
                    pass
            
except Exception as e:
    print(f"⚠️ Warning: Could not ensure table compatibility: {e}")

def ensure_user_columns_on_connection(conn):
    """Ensures all required tables exist on the given connection"""
    try:
        # Create study_list table if it doesn't exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS study_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                word TEXT NOT NULL,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                note TEXT,
                language TEXT DEFAULT 'english',
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, word)
            )
        ''')
        
        # Create user_progress table if it doesn't exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                words_learned INTEGER DEFAULT 0,
                conversation_count INTEGER DEFAULT 0,
                accuracy_rate FLOAT DEFAULT 0.0,
                daily_streak INTEGER DEFAULT 0,
                last_activity_date DATE,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Ensure quiz_results table has percentage column
        try:
            conn.execute('ALTER TABLE quiz_results ADD COLUMN percentage REAL DEFAULT 0')
            conn.commit()
            print("✅ Added 'percentage' column to quiz_results table")
        except Exception:
            # Column likely already exists
            pass
        
        conn.commit()
    except Exception as e:
        print(f"Error creating additional tables: {e}")

def _initialize_database_tables(conn):
    """Initialize database tables safely"""
    try:
        print("🔧 Initializing database tables...")
        
        # Create tables using the bulletproof wrapper
        from database_config import create_tables
        create_tables(conn)
        
        print("✅ Database tables initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

def _ensure_admin_user_and_sample_data(conn):
    """Ensure admin user and sample quiz questions exist"""
    try:
        # Check if admin user exists
        admin_exists = conn.execute("SELECT id FROM users WHERE is_admin = 1").fetchone()
        
        if not admin_exists:
            print("🔑 Creating admin user...")
            from werkzeug.security import generate_password_hash
            
            # Create admin user with default credentials
            admin_username = "admin"
            admin_email = "admin@example.com"
            admin_password = "admin123"
            admin_security_answer = "admin"
            
            # Hash the password
            hashed_password = generate_password_hash(admin_password)
            
            conn.execute('''
                INSERT INTO users (username, email, password, security_answer, is_admin)
                VALUES (?, ?, ?, ?, 1)
            ''', (admin_username, admin_email, hashed_password, admin_security_answer))
            
            print(f"✅ Admin user created: {admin_email} / {admin_password}")
        
        # COMMENTED OUT: Auto-generation of sample questions removed per user request
        # This prevents questions from reappearing after deletion from admin dashboard
        # Users should use the import function in admin dashboard to add their own questions
        # 
        # # Check if sample questions exist
        # sample_count = conn.execute("SELECT COUNT(*) FROM quiz_questions").fetchone()[0]
        # if sample_count == 0:
        #     print("📝 Adding sample quiz questions...")
        #     
        #     sample_questions = [
        #         ("English", "Beginner", "What is the plural of 'cat'?", '["cats", "cat", "cates", "caties"]', "cats", "multiple_choice", 10),
        #         ("English", "Beginner", "Choose the correct verb: 'I ___ happy.'", '["am", "is", "are", "be"]', "am", "multiple_choice", 10),
        #         ("English", "Intermediate", "What does 'ubiquitous' mean?", '["rare", "everywhere", "beautiful", "ancient"]', "everywhere", "multiple_choice", 15),
        #         ("Spanish", "Beginner", "How do you say 'hello' in Spanish?", '["hola", "adios", "gracias", "por favor"]', "hola", "multiple_choice", 10),
        #         ("Spanish", "Beginner", "What is 'casa' in English?", '["car", "house", "cat", "dog"]', "house", "multiple_choice", 10),
        #         ("French", "Beginner", "How do you say 'thank you' in French?", '["bonjour", "au revoir", "merci", "s\'il vous plait"]', "merci", "multiple_choice", 10),
        #         ("Chinese", "Beginner", "How do you say 'hello' in Chinese?", '["你好", "再见", "谢谢", "请"]', "你好", "multiple_choice", 10),
        #         ("Malay", "Beginner", "How do you say 'thank you' in Malay?", '["terima kasih", "selamat pagi", "selamat tinggal", "maaf"]', "terima kasih", "multiple_choice", 10),
        #         ("Portuguese", "Beginner", "How do you say 'hello' in Portuguese?", '["olá", "tchau", "obrigado", "por favor"]', "olá", "multiple_choice", 10),
        #         ("Tamil", "Beginner", "How do you say 'hello' in Tamil?", '["வணக்கம்", "போய் வருகிறேன்", "நன்றி", "தயவுசெய்து"]', "வணக்கம்", "multiple_choice", 10),
        #     ]
        #     
        #     for question_data in sample_questions:
        #         conn.execute('''
        #             INSERT INTO quiz_questions (language, difficulty, question, options, answer, question_type, points)
        #             VALUES (?, ?, ?, ?, ?, ?, ?)
        #         ''', question_data)
        #     
        #     print(f"✅ Added {len(sample_questions)} sample questions")
        
        conn.commit()
        
    except Exception as e:
        print(f"Error ensuring admin user and sample data: {e}")

def get_user_id(email):
    """
    Retrieves a user's ID from their email address.

    Args:
        email (str): The user's email address

    Returns:
        int or None: The user's ID if found, None otherwise
    """
    conn = None
    try:
        conn = get_db_connection()
        user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        return user['id'] if user else None
    finally:
        # Ensure connection is closed even if an exception occurs
        if conn:
            conn.close()

def check_login(email, password, security_answer):
    """
    Validates user login credentials including security answer.

    Args:
        email (str): The user's email
        password (str): The user's password (plain text)
        security_answer (str): Answer to the security question

    Returns:
        dict or None: User data if authentication succeeds, None otherwise
    """
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user['password'], password) and user['security_answer'] == security_answer:
            # Check if account is active
            is_active = user['is_active'] if 'is_active' in user.keys() else 1
            if is_active == 0:
                # Account is deactivated, return None but don't indicate why for security
                return None
            return user
        return None

def register_user(username, email, password, security_answer):
    """
    Registers a new user in the database.

    Args:
        username (str): The user's chosen username
        email (str): The user's email address
        password (str): The user's password (will be hashed)
        security_answer (str): Answer to the security question

    Returns:
        bool: True if registration succeeded, False otherwise
    """
    print(f"🔍 REGISTERING USER: {username}, {email}")
    
    with get_db_connection() as conn:
        # Check if email already exists
        existing_user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing_user:
            print(f"❌ User already exists with email: {email}")
            return False

        try:
            print(f"📝 Inserting new user: {username}")
            result = conn.execute(
                "INSERT INTO users (username, email, password, security_answer) VALUES (?, ?, ?, ?)",
                (username, email, generate_password_hash(password), security_answer))
            
            # FORCE COMMIT
            conn.commit()
            
            # Verify the user was actually inserted
            new_user = conn.execute("SELECT id, username FROM users WHERE email = ?", (email,)).fetchone()
            if new_user:
                print(f"✅ USER SUCCESSFULLY REGISTERED: ID={new_user['id']}, Username={new_user['username']}")
                
                # Double-check by counting total users
                total_users = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
                print(f"📊 Total users in database: {total_users}")
                return True
            else:
                print(f"❌ FAILED: User not found after registration")
                return False
                
        except Exception as e:
            if 'integrity' in str(e).lower() or 'unique' in str(e).lower():
                print(f"❌ INTEGRITY ERROR during registration: {e}")
            else:
                print(f"❌ UNEXPECTED ERROR during registration: {e}")
            return False

# --- Helper Functions ---
# These utility functions support various features throughout the application

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_otp():
    """Generates a 6-digit OTP"""
    return ''.join(random.choices('0123456789', k=6))

def send_otp(email, otp):
    """
    Sends an OTP to the user's email address.

    Args:
        email (str): The recipient's email address
        otp (str): The OTP to send

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    if USE_CONSOLE_OTP:
        print(f"OTP for {email}: {otp}")
        return True

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = email
        msg['Subject'] = "Your OTP for Language Learning"

        body = f"""
        Hello,

        Your verification code is: {otp}

        This code is valid for 10 minutes.
        If you did not request this code, please ignore this email.

        Best regards,
        Language Learning App Team
        """
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            return True
    except Exception as e:
        print(f"Error sending OTP email: {str(e)}")
        return False

def add_notification(user_id, notification_message):
    """
    Adds a notification for a user.

    Args:
        user_id (int): The ID of the user to notify
        notification_message (str): The notification message
    """
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO notifications (user_id, message, timestamp) VALUES (?, ?, ?)",
            (user_id, notification_message, datetime.now())
        )
        conn.commit()

def update_user_progress(user_id):
    """
    Updates user progress metrics immediately after an activity.
    
    Args:
        user_id (int): The ID of the user to update progress for
    """
    conn = None
    try:
        conn = get_db_connection()
        # Set a timeout for the database connection to avoid hanging
        conn.execute('PRAGMA busy_timeout = 5000')  # 5 second timeout
        
        # Calculate current stats
        words_learned = conn.execute(
            'SELECT COUNT(*) as count FROM study_list WHERE user_id = ?',
            (user_id,)
        ).fetchone()['count']

        conversation_count = conn.execute(
            'SELECT COUNT(DISTINCT session_id) as count FROM chat_sessions WHERE user_id = ?',
            (user_id,)
        ).fetchone()['count']

        # Calculate accuracy rate from both quiz tables
        total_score = 0
        total_questions = 0
        
        try:
            quiz_stats_enhanced = conn.execute('''
                SELECT 
                    SUM(score) as total_score,
                    SUM(total) as total_questions
                FROM quiz_results_enhanced 
                WHERE user_id = ?
            ''', (user_id,)).fetchone()
            total_score += quiz_stats_enhanced['total_score'] or 0
            total_questions += quiz_stats_enhanced['total_questions'] or 0
        except Exception as e:
            print(f"Error querying quiz_results_enhanced in update_user_progress: {e}")

        try:
            quiz_stats_legacy = conn.execute('''
                SELECT 
                    SUM(score) as total_score,
                    SUM(total) as total_questions
                FROM quiz_results 
                WHERE user_id = ?
            ''', (user_id,)).fetchone()
            total_score += quiz_stats_legacy['total_score'] or 0
            total_questions += quiz_stats_legacy['total_questions'] or 0
        except Exception as e:
            print(f"Error querying quiz_results (legacy) in update_user_progress: {e}")

        accuracy_rate = 0
        if total_questions and total_questions > 0:
            accuracy_rate = (total_score / total_questions) * 100

        # Update or insert progress record
        today = datetime.now().date()
        existing_progress = conn.execute(
            'SELECT daily_streak, last_activity_date FROM user_progress WHERE user_id = ?',
            (user_id,)
        ).fetchone()

        # Calculate streak
        if existing_progress:
            last_activity = None
            if existing_progress['last_activity_date']:
                try:
                    last_activity = datetime.strptime(existing_progress['last_activity_date'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    last_activity = None
            
            if last_activity:
                days_diff = (today - last_activity).days
                if days_diff == 1:  # Consecutive day
                    new_streak = (existing_progress['daily_streak'] or 0) + 1
                elif days_diff == 0:  # Same day
                    new_streak = existing_progress['daily_streak'] or 1
                else:  # Streak broken
                    new_streak = 1
            else:
                new_streak = 1
        else:
            new_streak = 1

        conn.execute('''
            INSERT OR REPLACE INTO user_progress 
            (user_id, words_learned, conversation_count, accuracy_rate, daily_streak, last_activity_date, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, words_learned, conversation_count, accuracy_rate, new_streak, today))
        conn.commit()
        
    except Exception as e:
        print(f"Error updating user progress: {e}")
    finally:
        if conn:
            conn.close()

# --- Admin Decorator ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin') or not session.get('admin_user_id'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def index():
    """Home page: show dashboard if logged in, else show landing page"""
    if 'user_id' in session:
        return render_template('dashboard.html', username=session.get('username', 'User'), is_admin=session.get('is_admin', False))
    else:
        return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        security_answer = request.form.get('security_answer')

        # First check if the account exists and is deactivated
        with get_db_connection() as conn:
            existing_user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if existing_user and check_password_hash(existing_user['password'], password) and existing_user['security_answer'] == security_answer:
                # Valid credentials, but check if account is deactivated
                is_active = existing_user['is_active'] if 'is_active' in existing_user.keys() else 1
                if is_active == 0:
                    flash('Your account has been deactivated. Would you like to reactivate it?', 'info')
                    return redirect(url_for('reactivate_account'))
        
        user = check_login(email, password, security_answer)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['is_admin'] = user['is_admin'] if 'is_admin' in user.keys() else False

            # Generate and send OTP
            otp = generate_otp()
            session['otp'] = otp
            session['otp_timestamp'] = datetime.now().isoformat()
            if send_otp(email, otp):
                return redirect(url_for('verify_otp'))
            else:
                flash('Error sending OTP. Please try again.', 'error')
        else:
            flash('Invalid email, password, or security answer.', 'error')

    return render_template('login.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    """Handles OTP verification"""
    if 'otp' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_otp = request.form.get('otp')
        if user_otp == session['otp']:
            # Check if OTP is expired (5 minutes)
            otp_time = datetime.fromisoformat(session['otp_timestamp'])
            if (datetime.now() - otp_time).total_seconds() > 300:
                flash('OTP has expired. Please login again.', 'error')
                return redirect(url_for('login'))
            
            # Add login notification
            add_notification(session['user_id'], f"Welcome back! You logged in successfully at {datetime.now().strftime('%I:%M %p')}")
            
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid OTP. Please try again.', 'error')

    return render_template('verify_otp.html')

@app.route('/resend_otp', methods=['GET'])
def resend_otp():
    """Resends the OTP"""
    if 'email' not in session:
        return redirect(url_for('login'))
    otp = generate_otp()
    session['otp'] = otp
    session['otp_timestamp'] = datetime.now().isoformat()
    if send_otp(session['email'], otp):
        flash('New OTP has been sent to your email.', 'success')
    else:
        flash('Error sending OTP. Please try again.', 'error')
    return redirect(url_for('verify_otp'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handles password reset requests"""
    if request.method == 'POST':
        email = request.form.get('email')
        security_answer = request.form.get('security_answer')

        with get_db_connection() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE email = ? AND security_answer = ?",
                (email, security_answer)
            ).fetchone()

            if user:
                # Generate reset token
                reset_token = secrets.token_urlsafe(32)
                expiry = datetime.now() + timedelta(hours=1)
                conn.execute(
                    "INSERT INTO password_resets (user_id, token, expiry) VALUES (?, ?, ?)",
                    (user['id'], reset_token, expiry)
                )
                conn.commit()
                # Send reset email
                reset_link = url_for('reset_password', reset_token=reset_token, _external=True)
                msg = MIMEMultipart()
                msg['From'] = smtp_user
                msg['To'] = email
                msg['Subject'] = "Password Reset Request"
                body = f"""
                You requested a password reset for your Language Learning account.

                Click the following link to reset your password:
                {reset_link}

                This link will expire in 1 hour.
                If you didn't request this reset, please ignore this email.
                """
                msg.attach(MIMEText(body, 'plain'))
                try:
                    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                        server.login(smtp_user, smtp_password)
                        server.send_message(msg)
                    flash('Password reset instructions have been sent to your email.', 'success')
                except Exception as e:
                    print(f"Error sending password reset email: {e}")
                    flash('Error sending reset email. Please try again.', 'error')
            else:
                flash('Invalid email or security answer.', 'error')
    return render_template('forgot_password.html')

@app.route('/reset_password/<reset_token>', methods=['GET', 'POST'])
def reset_password(reset_token):
    """Handles password reset"""
    with get_db_connection() as conn:
        reset = conn.execute(
            "SELECT * FROM password_resets WHERE token = ? AND expiry > ?",
            (reset_token, datetime.now())
        ).fetchone()
        if not reset:
            flash('Invalid or expired reset token.', 'error')
            return redirect(url_for('login'))
        if request.method == 'POST':
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            if new_password != confirm_password:
                flash('Passwords do not match.', 'error')
            else:
                conn.execute(
                    "UPDATE users SET password = ? WHERE id = ?",
                    (generate_password_hash(new_password), reset['user_id'])
                )
                conn.execute("DELETE FROM password_resets WHERE token = ?", (reset_token,))
            conn.commit()
            flash('Your password has been reset successfully.', 'success')
            return redirect(url_for('login'))
    return render_template('reset_password.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles user registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        security_answer = request.form.get('security_answer')
        
        if register_user(username, email, password, security_answer):
            # Get the newly created user ID to send welcome notification
            with get_db_connection() as conn:
                new_user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
                if new_user:
                    add_notification(new_user['id'], f"🎉 Welcome to the Language Learning Platform, {username}! Start your learning journey today.")
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already exists or invalid data.', 'error')

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    """Displays the user's dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html',
                         username=session.get('username', 'User'),
                         is_admin=session.get('is_admin', False))

@app.route('/logout')
def logout():
    """Handles user logout"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Handles user settings"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Critical: Check database consistency before any user data operations (wrapped in try-catch)
    try:
        check_database_consistency()
    except Exception as e:
        print(f"⚠️ Database consistency check warning in settings: {e}")
        # Continue with degraded functionality rather than crashing
    
    with get_db_connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        
        if request.method == 'POST':
            action = request.form.get('action')
            
            if action == 'save_profile':
                # Handle profile information update
                name = request.form.get('name', '').strip()
                email = request.form.get('email', '').strip()
                phone = request.form.get('phone', '').strip()
                location = request.form.get('location', '').strip()
                website = request.form.get('website', '').strip()
                bio = request.form.get('bio', '').strip()
                selected_avatar = request.form.get('selected_avatar', '').strip()
                
                # Handle profile picture upload
                profile_picture = None
                if 'profile_picture' in request.files:
                    file = request.files['profile_picture']
                    if file and file.filename != '' and allowed_file(file.filename):
                        import os
                        import uuid
                        # Create uploads directory if it doesn't exist
                        upload_dir = os.path.join('static', 'uploads')
                        os.makedirs(upload_dir, exist_ok=True)
                        
                        # Generate unique filename
                        file_extension = file.filename.rsplit('.', 1)[1].lower()
                        filename = f"{uuid.uuid4().hex}.{file_extension}"
                        file.save(os.path.join(upload_dir, filename))
                        profile_picture = filename
                
                # Update user profile
                try:
                    if profile_picture:
                        # Clear avatar if uploading new picture
                        conn.execute("""
                            UPDATE users SET name = ?, email = ?, phone = ?, location = ?, 
                            website = ?, bio = ?, profile_picture = ?, avatar = NULL 
                            WHERE id = ?
                        """, (name, email, phone, location, website, bio, profile_picture, session['user_id']))
                    elif selected_avatar:
                        # Clear profile picture if selecting avatar
                        conn.execute("""
                            UPDATE users SET name = ?, email = ?, phone = ?, location = ?, 
                            website = ?, bio = ?, avatar = ?, profile_picture = NULL 
                            WHERE id = ?
                        """, (name, email, phone, location, website, bio, selected_avatar, session['user_id']))
                    else:
                        # Update without changing pictures
                        conn.execute("""
                            UPDATE users SET name = ?, email = ?, phone = ?, location = ?, 
                            website = ?, bio = ? WHERE id = ?
                        """, (name, email, phone, location, website, bio, session['user_id']))
                    
                    conn.commit()
                    
                    # Update session data to reflect changes immediately
                    session['username'] = name if name else session.get('username')
                    session['email'] = email if email else session.get('email')
                    
                    flash('Profile updated successfully!', 'success')
                    print(f"✅ Profile updated for user {session['user_id']}: avatar={selected_avatar}, picture={profile_picture}")
                except Exception as e:
                    flash(f'Error updating profile: {str(e)}', 'error')
                    print(f"❌ Profile update error for user {session['user_id']}: {e}")
                    
            elif action == 'change_password':
                # Handle password change
                current_password = request.form.get('current_password')
                new_password = request.form.get('new_password')
                confirm_password = request.form.get('confirm_password')
                
                if not current_password or not new_password or not confirm_password:
                    flash('All password fields are required.', 'error')
                elif not check_password_hash(user['password'], current_password):
                    flash('Current password is incorrect.', 'error')
                elif new_password != confirm_password:
                    flash('New passwords do not match.', 'error')
                elif len(new_password) < 8:
                    flash('New password must be at least 8 characters.', 'error')
                else:
                    try:
                        conn.execute(
                            "UPDATE users SET password = ? WHERE id = ?",
                            (generate_password_hash(new_password), session['user_id'])
                        )
                        conn.commit()
                        flash('Password changed successfully!', 'success')
                    except Exception as e:
                        flash(f'Error changing password: {str(e)}', 'error')
                        
            elif action == 'save_preferences':
                # Handle preferences update
                timezone = request.form.get('timezone', '').strip()
                datetime_format = request.form.get('datetime_format', '').strip()
                
                try:
                    conn.execute("""
                        UPDATE users SET timezone = ?, datetime_format = ? WHERE id = ?
                    """, (timezone, datetime_format, session['user_id']))
                    conn.commit()
                    flash('Preferences saved successfully!', 'success')
                except Exception as e:
                    flash(f'Error saving preferences: {str(e)}', 'error')
            
            # Refresh user data after any update
            user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    # Get available avatars (create some default ones if directory is empty)
    import os
    avatars = []
    avatar_dir = os.path.join('static', 'avatars')
    if os.path.exists(avatar_dir):
        avatars = [f for f in os.listdir(avatar_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    return render_template('settings.html', user=user, avatars=avatars)

@app.route('/notifications', methods=['GET', 'POST'])
def notifications():
    """Displays user notifications and handles notification operations"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        action = request.json.get('action')
        if action == 'mark_read':
            notification_id = request.json.get('notification_id')
            with get_db_connection() as conn:
                conn.execute(
                    "UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?",
                    (notification_id, session['user_id'])
                )
                conn.commit()
            return jsonify({'success': True})
        elif action == 'mark_all_read':
            with get_db_connection() as conn:
                conn.execute(
                    "UPDATE notifications SET is_read = 1 WHERE user_id = ?",
                    (session['user_id'],)
                )
                conn.commit()
            return jsonify({'success': True})
    with get_db_connection() as conn:
        notifications = conn.execute(
            "SELECT * FROM notifications WHERE user_id = ? ORDER BY timestamp DESC",
            (session['user_id'],)
        ).fetchall()
        
        # Separate notifications into read and unread
        unread_notifications = [n for n in notifications if n['is_read'] == 0]
        read_notifications = [n for n in notifications if n['is_read'] == 1]
        
    return render_template('notifications.html', 
                         notifications=notifications,
                         unread_notifications=unread_notifications,
                         read_notifications=read_notifications,
                         username=session.get('username', 'User'))

@app.route('/notifications/count')
def notifications_count():
    """Returns the count of unread notifications"""
    if 'user_id' not in session:
        return jsonify({'count': 0})

    with get_db_connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_read = 0",
            (session['user_id'],)
        ).fetchone()['count']

    return jsonify({'count': count})

@app.route('/notifications/json')
def notifications_json():
    """Returns notifications as JSON"""
    if 'user_id' not in session:
        return jsonify([])

    with get_db_connection() as conn:
        notifications = conn.execute(
            "SELECT * FROM notifications WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5",
            (session['user_id'],)
        ).fetchall()

    return jsonify([{
        'id': n['id'],
        'message': n['message'],
        'timestamp': n['timestamp'],
        'is_read': bool(n['is_read'])
    } for n in notifications])

@app.route('/mark_notification_read', methods=['POST'])
def mark_notification_read():
    """Mark a specific notification as read"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 401
    
    data = request.get_json()
    notification_id = data.get('notification_id')
    
    if not notification_id:
        return jsonify({'status': 'error', 'message': 'Notification ID required'}), 400
    
    try:
        with get_db_connection() as conn:
            conn.execute(
                "UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?",
                (notification_id, session['user_id'])
            )
            conn.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """Handles admin login (no security answer required)"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        print(f"🔐 Admin login attempt: {email}")
        
        # Only check email and password for admin login
        with get_db_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            
            if user:
                print(f"👤 User found: ID={user['id']}, Username={user['username']}, IsAdmin={user['is_admin']}")
                
                if user['is_admin']:
                    if check_password_hash(user['password'], password):
                        print("✅ Admin login successful")
                        # CRITICAL FIX: Use separate session variables for admin to avoid overwriting user session
                        session['admin_user_id'] = user['id']
                        session['admin_username'] = user['username']
                        session['admin_email'] = user['email']
                        session['is_admin'] = True
                        print(f"🔧 Admin session created: ID={user['id']}, keeping existing user session intact")
                        return redirect(url_for('admin_dashboard'))
                    else:
                        print("❌ Password check failed")
                        flash('Invalid password.', 'error')
                else:
                    print("❌ User is not an admin")
                    flash('Insufficient permissions - not an admin user.', 'error')
            else:
                print("❌ User not found")
                flash('User not found.', 'error')
                
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    """Displays the admin dashboard"""
    if not session.get('is_admin') or not session.get('admin_user_id'):
        return redirect(url_for('admin_login'))
    languages = ['English', 'Chinese', 'Malay', 'Spanish', 'French', 'Portuguese', 'Tamil']
    difficulties = ['beginner', 'intermediate', 'advanced']
    quiz_data = {lang: {diff: [] for diff in difficulties} for lang in languages}
    with get_db_connection() as conn:
        users = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
        questions = conn.execute("SELECT * FROM quiz_questions").fetchall()
        for q in questions:
            lang = q['language']
            diff = q['difficulty'].lower()
            if lang in quiz_data and diff in quiz_data[lang]:
                quiz_data[lang][diff].append({
                    'id': q['id'],
                    'question': q['question'],
                    'options': json.loads(q['options']) if q['options'] else [],
                    'answer': q['answer'],
                    'question_type': q['question_type'],
                    'points': q['points']
                })
    return render_template('admin_dashboard.html', users=users, languages=languages, quiz_data=quiz_data)

@app.route('/admin/reset_progress/<int:user_id>', methods=['POST'])
def admin_reset_progress(user_id):
    """Completely resets a user's progress across all app features"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    try:
        with get_db_connection() as conn:
            # Get user info for logging
            user_info = conn.execute("SELECT username, email FROM users WHERE id = ?", (user_id,)).fetchone()
            if not user_info:
                return jsonify({'success': False, 'message': 'User not found'})
            
            username = user_info['username']
            
            # Reset all progress-related data
            print(f"🔄 Resetting progress for user {username} (ID: {user_id})...")
            
            # 1. Quiz Results (both legacy and enhanced)
            quiz_results_count = conn.execute("SELECT COUNT(*) as count FROM quiz_results WHERE user_id = ?", (user_id,)).fetchone()['count']
            quiz_enhanced_count = conn.execute("SELECT COUNT(*) as count FROM quiz_results_enhanced WHERE user_id = ?", (user_id,)).fetchone()['count']
            conn.execute("DELETE FROM quiz_results WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM quiz_results_enhanced WHERE user_id = ?", (user_id,))
            print(f"  ✅ Deleted {quiz_results_count} legacy quiz results and {quiz_enhanced_count} enhanced quiz results")
            
            # 2. User Progress
            progress_count = conn.execute("SELECT COUNT(*) as count FROM user_progress WHERE user_id = ?", (user_id,)).fetchone()['count']
            conn.execute("DELETE FROM user_progress WHERE user_id = ?", (user_id,))
            print(f"  ✅ Deleted {progress_count} user progress records")
            
            # 3. Achievements
            achievements_count = conn.execute("SELECT COUNT(*) as count FROM achievements WHERE user_id = ?", (user_id,)).fetchone()['count']
            conn.execute("DELETE FROM achievements WHERE user_id = ?", (user_id,))
            print(f"  ✅ Deleted {achievements_count} achievements")
            
            # 4. User Badges
            badges_count = conn.execute("SELECT COUNT(*) as count FROM user_badges WHERE user_id = ?", (user_id,)).fetchone()['count']
            conn.execute("DELETE FROM user_badges WHERE user_id = ?", (user_id,))
            print(f"  ✅ Deleted {badges_count} user badges")
            
            # 5. Study List
            study_count = conn.execute("SELECT COUNT(*) as count FROM study_list WHERE user_id = ?", (user_id,)).fetchone()['count']
            conn.execute("DELETE FROM study_list WHERE user_id = ?", (user_id,))
            print(f"  ✅ Deleted {study_count} study list entries")
            
            # 6. Chat History & Sessions
            chat_sessions = conn.execute("SELECT session_id FROM chat_sessions WHERE user_id = ?", (user_id,)).fetchall()
            chat_messages_count = 0
            for session_row in chat_sessions:
                messages_count = conn.execute("SELECT COUNT(*) as count FROM chat_messages WHERE session_id = ?", (session_row['session_id'],)).fetchone()['count']
                chat_messages_count += messages_count
            
            # Delete chat messages first (foreign key constraint)
            conn.execute("""
                DELETE FROM chat_messages 
                WHERE session_id IN (
                    SELECT session_id FROM chat_sessions WHERE user_id = ?
                )
            """, (user_id,))
            
            # Delete chat sessions
            sessions_count = conn.execute("SELECT COUNT(*) as count FROM chat_sessions WHERE user_id = ?", (user_id,)).fetchone()['count']
            conn.execute("DELETE FROM chat_sessions WHERE user_id = ?", (user_id,))
            
            # Delete legacy chat history
            legacy_chat_count = conn.execute("SELECT COUNT(*) as count FROM chat_history WHERE user_id = ?", (user_id,)).fetchone()['count']
            conn.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
            
            print(f"  ✅ Deleted {sessions_count} chat sessions, {chat_messages_count} chat messages, and {legacy_chat_count} legacy chat records")
            
            # 7. Account Activity (progress-related activities)
            activity_count = conn.execute("SELECT COUNT(*) as count FROM account_activity WHERE user_id = ?", (user_id,)).fetchone()['count']
            conn.execute("DELETE FROM account_activity WHERE user_id = ?", (user_id,))
            print(f"  ✅ Deleted {activity_count} account activity records")
            
            # 8. Notifications (progress-related notifications)
            notification_count = conn.execute("SELECT COUNT(*) as count FROM notifications WHERE user_id = ?", (user_id,)).fetchone()['count']
            conn.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
            print(f"  ✅ Deleted {notification_count} notifications")
            
            # Commit all changes
            conn.commit()
            
            # Log the reset action
            print(f"🎉 Successfully reset all progress for user {username} (ID: {user_id})")
            
            return jsonify({
                'success': True, 
                'message': f'Successfully reset all progress for user {username}',
                'details': {
                    'quiz_results_legacy': quiz_results_count,
                    'quiz_results_enhanced': quiz_enhanced_count,
                    'user_progress': progress_count,
                    'achievements': achievements_count,
                    'badges': badges_count,
                    'study_list': study_count,
                    'chat_sessions': sessions_count,
                    'chat_messages': chat_messages_count,
                    'legacy_chat': legacy_chat_count,
                    'account_activity': activity_count,
                    'notifications': notification_count
                }
            })
            
    except Exception as e:
        print(f"❌ Error resetting progress for user {user_id}: {str(e)}")
        return jsonify({'success': False, 'message': f'Error resetting progress: {str(e)}'})

@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
def admin_toggle_admin(user_id):
    """Toggles admin status for a user"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    with get_db_connection() as conn:
        user = conn.execute("SELECT is_admin FROM users WHERE id = ?", (user_id,)).fetchone()
        if user:
            new_status = 0 if user['is_admin'] else 1
            conn.execute("UPDATE users SET is_admin = ? WHERE id = ?", (new_status, user_id))
            conn.commit()
            return jsonify({'success': True, 'new_status': new_status})
    return jsonify({'success': False, 'message': 'User not found'})

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def admin_delete_user(user_id):
    """Deletes a user"""
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    with get_db_connection() as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    return jsonify({'success': True})

@app.route('/admin_logout')
def admin_logout():
    """Handles admin logout - only clears admin session, preserves user session"""
    # CRITICAL FIX: Only clear admin-specific session variables
    admin_keys_to_remove = ['admin_user_id', 'admin_username', 'admin_email', 'is_admin']
    for key in admin_keys_to_remove:
        session.pop(key, None)
    print("🔓 Admin logged out, user session preserved")
    return redirect(url_for('index'))

@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    """Handles the chatbot interface"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            response = get_gemini_response(message)
            return jsonify({'response': response})
    
    return render_template('chatbot.html')

@app.route('/chat_history/sessions')
def get_chat_sessions():
    """Returns chat session history"""
    if 'user_id' not in session:
        return jsonify([])
    with get_db_connection() as conn:
        sessions = conn.execute(
            "SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY last_message_at DESC",
            (session['user_id'],)
        ).fetchall()
        session_data = []
        for s in sessions:
            # Get the first user message for this session
            first_msg_row = conn.execute(
                "SELECT message FROM chat_messages WHERE session_id = ? AND message IS NOT NULL AND TRIM(message) != '' ORDER BY timestamp ASC LIMIT 1",
                (s['session_id'],)
            ).fetchone()
            first_message = first_msg_row['message'] if first_msg_row else ''
            session_data.append({
                'id': s['session_id'],
                'session_id': s['session_id'],
                'language': s['language'],
                'started_at': s['started_at'],
                'last_message_at': s['last_message_at'],
                'first_message': first_message
            })
    return jsonify(session_data)

@app.route('/chat_history/session/<session_id>')
def get_session_messages(session_id):
    """Returns messages for a specific chat session"""
    if 'user_id' not in session:
        return jsonify([])
    
    with get_db_connection() as conn:
        # First verify this session belongs to the current user
        session_check = conn.execute(
            "SELECT 1 FROM chat_sessions WHERE session_id = ? AND user_id = ?",
            (session_id, session['user_id'])
        ).fetchone()
        
        if not session_check:
            return jsonify([])  # Session doesn't belong to this user
            
        messages = conn.execute(
            "SELECT * FROM chat_messages WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        ).fetchall()
    
    return jsonify([{
        'id': m['id'],
        'message': m['message'],
        'bot_response': m['bot_response'],
        'timestamp': m['timestamp']
    } for m in messages])

@app.route('/chat_history/delete/<session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    """Delete a specific chat session and all its messages"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        with get_db_connection() as conn:
            # First verify this session belongs to the current user
            session_check = conn.execute(
                "SELECT 1 FROM chat_sessions WHERE session_id = ? AND user_id = ?",
                (session_id, session['user_id'])
            ).fetchone()
            
            if not session_check:
                return jsonify({'error': 'Session not found or access denied'}), 404
            
            # Delete all messages in this session first (due to foreign key constraint)
            conn.execute(
                "DELETE FROM chat_messages WHERE session_id = ?",
                (session_id,)
            )
            
            # Delete the session itself
            conn.execute(
                "DELETE FROM chat_sessions WHERE session_id = ? AND user_id = ?",
                (session_id, session['user_id'])
            )
            
            conn.commit()
            
            return jsonify({'success': True, 'message': 'Chat session deleted successfully'})
            
    except Exception as e:
        print(f'Error deleting chat session {session_id}: {e}')
        return jsonify({'error': 'Failed to delete chat session'}), 500

@app.route('/chat_history/delete_all', methods=['DELETE'])
def delete_all_chat_sessions():
    """Delete all chat sessions and messages for the current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        with get_db_connection() as conn:
            # Get all session IDs for this user
            sessions = conn.execute(
                "SELECT session_id FROM chat_sessions WHERE user_id = ?",
                (session['user_id'],)
            ).fetchall()
            
            # Delete all messages for this user's sessions
            conn.execute("""
                DELETE FROM chat_messages 
                WHERE session_id IN (
                    SELECT session_id FROM chat_sessions WHERE user_id = ?
                )
            """, (session['user_id'],))
            
            # Delete all sessions for this user
            deleted_count = conn.execute(
                "DELETE FROM chat_sessions WHERE user_id = ?",
                (session['user_id'],)
            ).rowcount
            
            conn.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Deleted {deleted_count} chat sessions successfully'
            })
            
    except Exception as e:
        print(f'Error deleting all chat sessions for user {session["user_id"]}: {e}')
        return jsonify({'error': 'Failed to delete chat sessions'}), 500

def get_gemini_response(prompt):
    """
    Gets a response from the Gemini AI model.
    Args:
        prompt (str): The user's input prompt
    Returns:
        str: The AI's response
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error getting Gemini response: {str(e)}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again later."



def ensure_user_columns():
    """Ensures all required columns exist in the users table and creates additional tables"""
    with get_db_connection() as conn:
        # First, check if users table exists
        table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users';"
        ).fetchone()
        
        if not table_exists:
            print("Users table doesn't exist yet - skipping column additions")
            return
            
        # Get existing columns
        existing_columns = [row['name'] for row in conn.execute("PRAGMA table_info(users);")]
        
        # Add missing columns to users table
        columns_to_add = [
            ('is_admin', 'INTEGER DEFAULT 0'),
            ('is_active', 'INTEGER DEFAULT 1'),
            ('timezone', 'TEXT'),
            ('datetime_format', 'TEXT'),
            ('name', 'TEXT'),
            ('phone', 'TEXT'),
            ('location', 'TEXT'),
            ('website', 'TEXT'),
            ('bio', 'TEXT'),
            ('profile_picture', 'TEXT'),
            ('avatar', 'TEXT'),
        ]
        
        for col, typ in columns_to_add:
            if col not in existing_columns:
                try:
                    conn.execute(f'ALTER TABLE users ADD COLUMN {col} {typ};')
                    print(f"✅ Column '{col}' added to users table!")
                except Exception as e:
                    print(f"Column '{col}' already exists or error: {e}")
        
        # Create additional tables if they don't exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS study_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                word TEXT NOT NULL,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                note TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, word)
            )
        ''')
        print("✅ Table 'study_list' created/verified!")

        conn.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                words_learned INTEGER DEFAULT 0,
                conversation_count INTEGER DEFAULT 0,
                accuracy_rate FLOAT DEFAULT 0.0,
                daily_streak INTEGER DEFAULT 0,
                last_activity_date DATE,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        print("✅ Table 'user_progress' created/verified!")

        conn.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                achievement_type TEXT NOT NULL,
                achievement_name TEXT NOT NULL,
                description TEXT NOT NULL,
                earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        print("✅ Table 'achievements' created/verified!")

        conn.execute('''
            CREATE TABLE IF NOT EXISTS account_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        print("✅ Table 'account_activity' created/verified!")

        # Create password_resets table if it doesn't exist
        conn.execute('''
            CREATE TABLE IF NOT EXISTS password_resets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT NOT NULL,
                expiry DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        print("✅ Table 'password_resets' created/verified!")

        conn.commit()

@app.route('/chat', methods=['POST'])
def chat():
    """Handles chat messages with optional image support"""
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in to use the chatbot'}), 401
    try:
        # Accept both JSON and multipart/form-data
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            print("Received multipart/form-data")
            message = request.form.get('message', '').strip()
            language = request.form.get('language', 'english').strip()
            session_id = request.form.get('session_id')
            image_file = request.files.get('image')
            print(f"Form data - message: '{message}', language: '{language}', image_file: {image_file is not None}")
            if image_file:
                print(f"Image file details - filename: {image_file.filename}, content_type: {image_file.content_type}")
        else:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data received'}), 400
            message = data.get('message', '').strip()
            language = data.get('language', 'english').strip()
            session_id = data.get('session_id')
            image_file = None
            
        if not message and not image_file:
            return jsonify({'error': 'Message or image is required'}), 400
            
        # Create or update chat session
        with get_db_connection() as conn:
            if session_id:
                conn.execute('''
                    UPDATE chat_sessions 
                    SET last_message_at = CURRENT_TIMESTAMP
                    WHERE session_id = ? AND user_id = ?
                ''', (session_id, session['user_id']))
            else:
                session_id = f"sess-{secrets.token_hex(16)}"
                conn.execute('''
                    INSERT INTO chat_sessions (session_id, user_id, language)
                    VALUES (?, ?, ?)
                ''', (session_id, session['user_id'], language))
                conn.commit()  # Commit immediately to release the lock
                
        # If image is present, use Gemini Vision
        has_image = False  # Initialize has_image flag
        if image_file and allowed_file(image_file.filename):
            has_image = True  # Set flag when image is being processed
            print(f"Processing image file: {image_file.filename}")
            filename = secure_filename(image_file.filename)
            
            # Monitor memory before processing
            monitor_memory("before_image_processing")
            
            # Apply Render free tier optimizations
            optimizations = optimize_for_render_free_tier()
            
            # Ensure upload directory exists
            upload_dir = app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, filename)
            try:
                image_file.save(file_path)
                print(f"Image saved to {file_path}")
                monitor_memory("after_image_save")
            except Exception as e:
                print(f"Error saving image: {e}")
                return jsonify({'error': 'Failed to save the uploaded image.'}), 500

            # Try Gemini Vision first
            gemini_failed = False
            prompt = f"""
You are a helpful and encouraging language tutor. The user has uploaded an image and asked: '{message}'.

Analyze the image and provide a clear, concise description in {language} that addresses the user's question. Then provide the English translation.

Format your response exactly like this:
[Response in {language}]
[English translation]

Response:
"""
            try:
                import PIL.Image
                # Check if Gemini API key is properly configured
                if not API_KEY or API_KEY == "your_api_key_here":
                    print("ERROR: GEMINI_API_KEY is not properly configured")
                    gemini_failed = True
                    response_text = f'[API key not configured. Please set GEMINI_API_KEY environment variable.]\n[API key not configured. Please set GEMINI_API_KEY environment variable.]'
                else:
                    print(f"Using Gemini API key: {API_KEY[:20]}...")
                    # Load and optimize image for Gemini Vision (resize large images to prevent memory issues)
                    pil_image = PIL.Image.open(file_path)
                    print(f"Original image size: {pil_image.size}")
                    
                    # Resize if image is too large (to prevent memory issues on Render free tier)
                    max_size = optimizations.get('max_image_size', (800, 800))
                    if pil_image.size[0] > max_size[0] or pil_image.size[1] > max_size[1]:
                        pil_image.thumbnail(max_size, PIL.Image.Resampling.LANCZOS)
                        print(f"Resized image to: {pil_image.size}")
                        monitor_memory("after_gemini_resize")
                    
                    # Convert to RGB if necessary (removes alpha channel which can cause issues)
                    if pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')
                        print(f"Converted image to RGB mode")
                    
                    print(f"Processing optimized image: {pil_image.size}")
                    response = vision_model.generate_content([prompt, pil_image])
                    if response and hasattr(response, 'text') and response.text.strip():
                        response_text = response.text.strip()
                        print(f"Gemini Vision response: {response_text[:100]}...")  # Debug log
                    else:
                        print("Empty or invalid response from Gemini Vision API")
                        gemini_failed = True
                    
                    # Clean up memory immediately after Gemini processing
                    del pil_image
                    import gc
                    gc.collect()
                    monitor_memory("after_gemini_cleanup")
            except ImportError as ie:
                print(f"Import error in Gemini Vision: {str(ie)}")
                gemini_failed = True
                response_text = f'[PIL import error: {str(ie)}]\n[PIL import error: {str(ie)}]'
            except Exception as e:
                print(f"Error in Gemini Vision image processing: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                gemini_failed = True

            # If Gemini Vision failed, use BLIP as fallback
            if gemini_failed:
                print("Falling back to BLIP image captioning...")
                try:
                    from PIL import Image
                    
                    # Use cached BLIP models
                    processor, blip_model = get_cached_blip_models()
                    
                    print("Processing image with BLIP...")
                    raw_image = Image.open(file_path).convert('RGB')
                    
                    # Resize image for BLIP to prevent memory issues
                    blip_max_size = (400, 400)  # Even smaller for BLIP on free tier
                    if raw_image.size[0] > blip_max_size[0] or raw_image.size[1] > blip_max_size[1]:
                        raw_image.thumbnail(blip_max_size, Image.Resampling.LANCZOS)
                        print(f"Resized image for BLIP to: {raw_image.size}")
                        monitor_memory("after_blip_resize")
                    
                    inputs = processor(raw_image, return_tensors="pt")
                    out = blip_model.generate(**inputs)
                    caption = processor.decode(out[0], skip_special_tokens=True)
                    print(f"BLIP caption: {caption}")
                    
                    # Clean up memory immediately after BLIP processing
                    del raw_image, inputs, out
                    import gc
                    gc.collect()
                    monitor_memory("after_blip_cleanup")
                    
                    # Now translate the caption using Gemini text model
                    translation_prompt = f"Translate the following image description into {language}, then provide the English translation on a new line.\nDescription: {caption}\n\nFormat:\n[Response in {language}]\n[English translation]\n\nResponse:"
                    response_text = get_gemini_response(translation_prompt)
                except ImportError as ie:
                    print(f"Import error in BLIP: {str(ie)}")
                    # Use simple fallback
                    simple_desc = get_simple_image_description(file_path)
                    fallback_prompt = f"A user uploaded an image and asked: '{message}'. I can see basic image properties: {simple_desc}. Please provide a helpful response about image analysis in {language} and English translation.\n\nFormat:\n[Response in {language}]\n[English translation]\n\nResponse:"
                    response_text = get_gemini_response(fallback_prompt)
                except Exception as blip_e:
                    print(f"BLIP image captioning error: {blip_e}")
                    print(f"BLIP error type: {type(blip_e).__name__}")
                    # Use simple fallback
                    simple_desc = get_simple_image_description(file_path)
                    fallback_prompt = f"A user uploaded an image and asked: '{message}'. I can see basic image properties: {simple_desc}. Please provide a helpful response about image analysis in {language} and English translation.\n\nFormat:\n[Response in {language}]\n[English translation]\n\nResponse:"
                    try:
                        response_text = get_gemini_response(fallback_prompt)
                    except Exception as final_e:
                        print(f"Final fallback error: {final_e}")
                        response_text = f'[Image uploaded but analysis is temporarily unavailable. Basic info: {simple_desc}]\n[Image uploaded but analysis is temporarily unavailable. Basic info: {simple_desc}]'
        else:
            # Text-only response
            prompt_text = f"You are a helpful and encouraging language tutor teaching {language}. The student's message is: '{message}'\nPlease provide a very concise response that directly addresses the student's message. Avoid unnecessary details or conversational filler unless specifically asked.\nProvide your response in the following format:\n[Response in {language}]\n[English translation]\nResponse:"
            try:
                response_text = get_gemini_response(prompt_text)
            except Exception as e:
                print(f"Error getting Gemini response: {e}")
                response_text = f"[Sorry, I'm having trouble processing your message right now. Please try again.]\n[Sorry, I'm having trouble processing your message right now. Please try again.]"
        
        # Split the response into the target language response and English translation
        # Handle various response formats and clean up any duplications
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        
        # Find the target language response and English translation
        target_language_response = ""
        english_translation = ""
        
        # Remove any duplicate or repetitive lines
        unique_lines = []
        for line in lines:
            # Skip if this line is very similar to any previous line
            is_duplicate = False
            for existing_line in unique_lines:
                # Check if lines are similar (allowing for small differences)
                if len(line) > 50 and len(existing_line) > 50:
                    # For longer lines, check for substantial overlap
                    similarity = len(set(line.lower().split()) & set(existing_line.lower().split())) / max(len(set(line.lower().split())), len(set(existing_line.lower().split())))
                    if similarity > 0.7:  # 70% word overlap indicates duplication
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_lines.append(line)
        
        # Now extract the target language and English responses
        if len(unique_lines) >= 2:
            target_language_response = unique_lines[0]
            english_translation = unique_lines[1]
        elif len(unique_lines) == 1:
            target_language_response = unique_lines[0]
            english_translation = unique_lines[0]  # Use same text as fallback
        else:
            target_language_response = response_text.strip()
            english_translation = response_text.strip()
        
        # Store the message and response
        with get_db_connection() as conn:
            conn.execute('''
                INSERT INTO chat_messages (session_id, message, bot_response)
                VALUES (?, ?, ?)
            ''', (session_id, message, response_text))
            conn.commit()
        
        # Clean up uploaded image file to save disk space (optional)
        if has_image and 'file_path' in locals():
            try:
                os.remove(file_path)
                print(f"Cleaned up uploaded file: {file_path}")
            except Exception as cleanup_error:
                print(f"Could not clean up file {file_path}: {cleanup_error}")
        
        # Note: Progress metrics will be updated by the progress stats endpoint when user views dashboard/chatbot
        
        return jsonify({
            'response': target_language_response,
            'translation': english_translation,
            'session_id': session_id
        }), 200
        
    except Exception as e:
        print(f"Error in chat route: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'An error occurred processing your message'}), 500

@app.route('/quiz', methods=['GET', 'POST'])
def quiz_select():
    """Quiz language and difficulty selector page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    languages = ['English', 'Chinese', 'Malay', 'Spanish', 'French', 'Portuguese', 'Tamil']
    difficulties = ['Beginner', 'Intermediate', 'Advanced']
    if request.method == 'POST':
        language = request.form.get('language')
        difficulty = request.form.get('difficulty')
        return redirect(url_for('quiz_questions', language=language, difficulty=difficulty))
    return render_template('quiz_select.html', languages=languages, difficulties=difficulties)

@app.route('/quiz/questions', methods=['GET', 'POST'])
def quiz_questions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    language = request.args.get('language') or request.form.get('language')
    difficulty = request.args.get('difficulty') or request.form.get('difficulty')
    user_id = session.get('user_id')

    # If it's a GET request, fetch new random questions and store in session
    if request.method == 'GET':
        # Clear any previous quiz results from the session
        session.pop('quiz_result', None)

        print(f"[DEBUG] GET /quiz/questions: Language={language}, Difficulty={difficulty}") # Debug log
        questions = []
        if language and difficulty:
            with get_db_connection() as conn:
                db_questions = conn.execute(
                    "SELECT * FROM quiz_questions WHERE language = ? AND LOWER(difficulty) = ? ORDER BY RANDOM() LIMIT 10",
                    (language, difficulty.lower())
                ).fetchall()

                # Process fetched questions to parse options/explanations as needed
                for q in db_questions:
                    options = json.loads(q['options']) if q['options'] else []

                    # Replicate question processing logic for display
                    if q['question_type'] == 'word_matching' and options:
                        # Handle both old and new word matching formats
                        pairs = []
                        if isinstance(options, dict) and 'pairs' in options:
                            # Newer format: {"pairs": [{"key": "Dog", "value": "狗 (Gǒu)"}], "format": "key_value_matching"}
                            pairs = [(pair['key'], pair['value']) for pair in options['pairs']]
                        elif isinstance(options, list):
                            # Older format: [["Dog", "狗 (Gǒu)"], ["Cat", "猫 (Māo)"]]
                            pairs = [(pair[0], pair[1]) for pair in options]
                        
                        if pairs:
                            left = [pair[0] for pair in pairs]
                            right = [pair[1] for pair in pairs]
                            random.shuffle(left)
                            random.shuffle(right)
                            processed_options = list(zip(left, right))
                            questions.append({
                                'id': q['id'],
                                'question': q['question'],
                                'options': processed_options,
                                'original_options': pairs, # Store normalized pairs for grading
                                'answer': q['answer'],
                                'question_type': q['question_type'],
                                'points': q['points']
                            })
                    elif q['question_type'] in ['error_spotting', 'idiom_interpretation', 'cultural_nuances'] and options and isinstance(options, dict):
                        questions.append({
                            'id': q['id'],
                            'question': q['question'],
                            'options': options.get('options', []), # Extract the list of options
                            'original_options': options,  # Store the full dict for explanation
                            'answer': q['answer'],
                            'question_type': q['question_type'],
                            'points': q['points']
                        })
                    elif q['question_type'] == 'fill_in_the_blanks' and options and isinstance(options, dict):
                         questions.append({
                             'id': q['id'],
                             'question': q['question'],
                             'options': options, # Store the hint dict
                             'original_options': options, # Keep original for consistency
                             'answer': q['answer'],
                             'question_type': q['question_type'],
                             'points': q['points']
                         })
                    elif q['question_type'] == 'complex_rephrasing' and options and isinstance(options, dict):
                         questions.append({
                             'id': q['id'],
                             'question': q['question'],
                             'options': options.get('options', []), # Extract the list of options
                             'original_options': options,  # Keep original for consistency
                             'answer': q['answer'],
                             'question_type': q['question_type'],
                             'points': q['points']
                         })
                    else:
                        # For other types, options are already a list or simple value
                        questions.append({
                            'id': q['id'],
                            'question': q['question'],
                            'options': options, # Options should already be in the correct format (list or string)
                            'original_options': options, # Keep original for consistency
                            'answer': q['answer'],
                            'question_type': q['question_type'],
                            'points': q['points']
                        })

        # Store the fetched and processed questions in the session for the POST request
        session['quiz_questions'] = questions
        session['quiz_start_time'] = time.time()
        print(f"[DEBUG] GET /quiz/questions: Stored {len(questions)} questions in session.") # Debug log
        return render_template('quiz_questions.html', language=language, difficulty=difficulty, questions=questions)

    # POST: grade answers
    # Retrieve questions from the session to grade against the correct set
    print(f"[DEBUG] POST /quiz/questions: Attempting to retrieve questions from session.") # Debug log
    questions = session.get('quiz_questions', [])
    print(f"[DEBUG] POST /quiz/questions: Retrieved {len(questions)} questions from session.") # Debug log
    if not questions:
        flash('Could not retrieve quiz questions from session. Please try the quiz again.', 'danger')
        return redirect(url_for('quiz_select'))

    user_answers = request.form.to_dict()
    start_time = session.get('quiz_start_time', time.time())
    end_time = time.time()
    time_taken = int(end_time - start_time)
    correct = 0
    # total = len(questions) # Total is now based on the number of questions retrieved from session
    review = []

    # Create a dictionary of questions by ID for easy lookup from the session questions
    questions_by_id = {q['id']: q for q in questions}

    # Iterate over submitted answers to grade
    # Exclude language and difficulty fields from user_answers
    question_answers = {}
    for key, value in user_answers.items():
        if key.startswith('q'):
            # Extract question ID, handling the '_matches' suffix for word matching
            if key.endswith('_matches'):
                qid_str = key[1:- len('_matches')]
            else:
                qid_str = key[1:]

            try:
                qid = int(qid_str)
                if qid not in question_answers:
                    question_answers[qid] = {}
                if key.endswith('_matches'):
                    # Store the raw JSON string for word matching
                    question_answers[qid]['word_matching_matches'] = value
                else:
                    # Store the answer for other types
                    question_answers[qid]['answer'] = value
            except ValueError:
                print(f"Warning: Could not parse question ID from key: {key}")
                continue # Skip this key if QID is not a valid integer

    # Iterate over the questions from the session to ensure all are considered, even if no answer submitted
    for q in questions:
        qid = q['id']
        user_ans_data = question_answers.get(qid, {})

        # qid = int(qid_str) # This line is no longer needed here
        # user_ans_raw = user_answers.get(qid_str) # This line is no longer needed here

        # q = questions_by_id.get(qid) # This lookup is no longer needed here as we iterate over questions directly

        # if q: # This check is implicitly handled by iterating over 'questions'
        user_ans = None
        is_correct = False
        correct_ans = ''
        explanation = ''

        # Get the original options and question type from the session question
        original_options = q.get('original_options', q.get('options'))
        question_type = q['question_type']

        # Grading logic based on question type
        if question_type in ['multiple_choice', 'fill_in_the_blanks', 'phrase_completion', 'context_response']:
             user_ans_raw = user_ans_data.get('answer')
             if user_ans_raw is not None:
                 user_ans = str(user_ans_raw).strip()
             else:
                 user_ans = "" # Or handle missing answer

             correct_answers = [a.strip().lower() for a in str(q['answer']).split(';')]
             is_correct = user_ans.lower() in correct_answers
             correct_ans = q['answer']

        elif question_type == 'word_matching':
             # For word matching, user_ans_raw is a JSON string of selected pairs
             try:
                 user_matches_raw = user_ans_data.get('word_matching_matches')
                 if user_matches_raw is not None:
                     user_matches = json.loads(user_matches_raw)
                 else:
                     user_matches = [] # Handle missing word matching data

                 user_ans = user_matches # Store the parsed list of pairs
                 # Correct pairs are in original_options for word_matching
                 correct_pairs = [list(pair) for pair in original_options]
                 # Compare sets of tuples for order-independent matching
                 is_correct = Counter(tuple(pair) for pair in user_matches) == Counter(tuple(pair) for pair in correct_pairs)
                 correct_ans = user_matches if is_correct else correct_pairs # Show user's answer if correct, otherwise correct pairs
             except (json.JSONDecodeError, TypeError):
                 user_ans = [] # Invalid JSON
                 is_correct = False
                 correct_ans = [list(pair) for pair in original_options] # Show correct pairs on error
                 flash(f'Error processing word matching answer for question {qid}. Please try the quiz again.', 'warning')

        elif question_type in ['error_spotting', 'idiom_interpretation', 'cultural_nuances', 'complex_rephrasing']:
              user_ans_raw = user_ans_data.get('answer')
              if user_ans_raw is not None:
                  user_ans = str(user_ans_raw).strip()
              else:
                  user_ans = "" # Or handle missing answer

              correct_ans = str(q['answer']).strip() # Correct answer is stored in the 'answer' field, strip it

              # Debug log for comparison values
              print(f"[DEBUG] QID {qid} ({question_type}) Grading: User='{user_ans.lower()}', Correct='{correct_ans.lower()}'")

              is_correct = user_ans.lower() == correct_ans.lower() # Compare stripped and lowercased answers

              # Special handling for complex_rephrasing to ignore ending punctuation
              if question_type == 'complex_rephrasing':
                  user_ans_cleaned = user_ans.rstrip('.?! ') # Strip ., ?, !, and space from end
                  correct_ans_cleaned = correct_ans.rstrip('.?! ') # Strip ., ?, !, and space from end
                  is_correct = user_ans_cleaned.lower() == correct_ans_cleaned.lower()

              # Extract explanation if available in original_options (for types that have it)
              if question_type in ['error_spotting', 'idiom_interpretation', 'cultural_nuances']:
                   if isinstance(original_options, dict):
                        explanation = original_options.get('explanation', '')


         # Append result to review list
        review.append({
             'question': q['question'],
             'type': question_type,
             'user_answer': user_ans,
             'correct_answer': correct_ans,
             'is_correct': is_correct,
             'options': {'explanation': explanation} if explanation else None # Include explanation if found
         })

    # If question not found in session questions (shouldn't happen with correct flow)
    # else:
    #     print(f"Warning: Question with ID {qid} not found in session questions for grading. This answer will be skipped.")
    #     # Optionally add a placeholder review item or handle as error

    # Update total and correct based on processed review items
    total = len(review)
    correct = sum(item['is_correct'] for item in review)

    # Points system (re-calculated based on the graded questions)
    points_per = {'Beginner': 1, 'Intermediate': 3, 'Advanced': 5}
    bonus_perfect = {'Beginner': 5, 'Intermediate': 8, 'Advanced': 10}
    
    # Calculate user's current level dynamically based on their points in this language
    with get_db_connection() as conn:
        quizzes_enhanced = conn.execute('''
            SELECT difficulty, COUNT(*) as cnt 
            FROM quiz_results_enhanced 
            WHERE user_id = ? AND language = ? 
            GROUP BY difficulty
        ''', (user_id, language)).fetchall()
        counts = {'beginner': 0, 'intermediate': 0, 'advanced': 0}
        for row in quizzes_enhanced:
            diff = row['difficulty'].lower()
            if diff in counts:
                counts[diff] = row['cnt']
        # Calculate points for each level
        beginner_pts = min(counts['beginner'], 300)
        intermediate_pts = min(counts['intermediate'] * 3, 400) if beginner_pts >= 300 else 0
        advanced_pts = min(counts['advanced'] * 5, 800) if intermediate_pts >= 400 else 0
        total_pts = beginner_pts + intermediate_pts + advanced_pts
        if total_pts >= 701:
            current_level = 'advanced'
        elif total_pts >= 301:
            current_level = 'intermediate'
        else:
            current_level = 'beginner'
    # Calculate points based on current level and quiz difficulty
    points = 0
    if current_level == 'beginner':
        points = correct * points_per.get(difficulty, 1)
    elif current_level == 'intermediate':
        if difficulty in ['Intermediate', 'Advanced']:
            points = correct * points_per.get(difficulty, 3)
    elif current_level == 'advanced':
        if difficulty == 'Advanced':
            points = correct * points_per.get(difficulty, 5)
    # Calculate bonus
    bonus = 0
    if correct == total:
        bonus = bonus_perfect.get(difficulty, 0)
    if time_taken < 60:
        bonus += 5

    # Streaks (simple: check last 5 quizzes) - logic seems okay, uses user_id
    with get_db_connection() as conn:
         last_quizzes = conn.execute("SELECT passed FROM quiz_results_enhanced WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (user_id,)).fetchall()
         streak = 0
         for qz in last_quizzes:
             if qz['passed']:
                 streak += 1
             else:
                 break
         # If current quiz is perfect and there was a streak, extend it
         if correct == total and (not last_quizzes or last_quizzes[0]['passed']):
             streak += 1
         # Apply streak bonus only if streak is > 1 after this quiz
         if streak > 1:
             bonus += 5 # Add streak bonus

    total_points = points + bonus

    # Save result using language and difficulty from form
    with get_db_connection() as conn:
        # Capitalize difficulty for legacy table
        difficulty_cap = difficulty.capitalize() if difficulty else ''
        
        
        conn.execute(
            "INSERT INTO quiz_results_enhanced (user_id, language, difficulty, score, total, percentage, passed, timestamp, question_details, points_earned, streak_bonus, time_bonus) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, language, difficulty, correct, total, (correct/total)*100, int(correct==total), datetime.now(), json.dumps(review), points, 5 if streak > 1 else 0, 5 if time_taken < 60 else 0)
        )
        # --- Add this block to also insert into legacy quiz_results for progress tracking ---
        percentage = (correct/total)*100
        conn.execute(
            "INSERT INTO quiz_results (user_id, language, difficulty, score, total, percentage, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, language, difficulty_cap, correct, total, percentage, datetime.now())
        )
        conn.commit()
        
        # Create quiz completion notification
        percentage_score = int((correct/total)*100)
        quiz_notification = f"You scored {correct}/{total} ({percentage_score}%) in {language} {difficulty} quiz"
        add_notification(user_id, quiz_notification)
        
        # Update user progress metrics
        update_user_progress(user_id)
        
        # Create achievement notifications for special scores
        if correct == total:  # Perfect score
            add_notification(user_id, "🎉 Perfect Score! You got 100% on your quiz!")
        elif percentage_score >= 90:  # Excellent score
            add_notification(user_id, "⭐ Excellent! You scored 90% or higher!")
        elif percentage_score >= 80:  # Good score
            add_notification(user_id, "👍 Good job! You're making great progress!")
        
        # === ACHIEVEMENT UNLOCK LOGIC ===
        # Helper to check if achievement already unlocked
        def has_achievement(user_id, ach_type):
            return conn.execute(
                'SELECT 1 FROM achievements WHERE user_id = ? AND achievement_type = ?',
                (user_id, ach_type)
            ).fetchone() is not None
        
        now = datetime.now()
        hour = now.hour
        today = now.date()
        # Only award global achievements if the quiz is taken in English
        if language == 'English':
            # Night Owl: Complete a quiz after midnight (00:00-05:59)
            if 0 <= hour < 6 and not has_achievement(user_id, 'night_owl'):
                conn.execute(
                    'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                    (user_id, 'night_owl', 'Night Owl', 'Complete a quiz after midnight')
                )
            # Early Bird: Complete a quiz before 7am (05:00-06:59)
            if 5 <= hour < 7 and not has_achievement(user_id, 'early_bird'):
                conn.execute(
                    'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                    (user_id, 'early_bird', 'Early Bird', 'Complete a quiz before 7am')
                )
            # Speed Demon: Finish a quiz in under 60 seconds
            if time_taken < 60 and not has_achievement(user_id, 'speed_demon'):
                conn.execute(
                    'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                    (user_id, 'speed_demon', 'Speed Demon', 'Finish a quiz in record time')
                )
            # Hot Streak: 5 correct quizzes in a row
            last_5 = conn.execute("SELECT passed FROM quiz_results_enhanced WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (user_id,)).fetchall()
            if len(last_5) == 5 and all(qz['passed'] for qz in last_5):
                if not has_achievement(user_id, 'hot_streak'):
                    conn.execute(
                        'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                        (user_id, 'hot_streak', 'Hot Streak', '5 correct quizzes in a row')
                    )
            # Perfectionist: 100% in 3 quizzes in a row
            last_3 = conn.execute("SELECT score, total FROM quiz_results_enhanced WHERE user_id = ? ORDER BY timestamp DESC LIMIT 3", (user_id,)).fetchall()
            if len(last_3) == 3 and all(qz['score'] == qz['total'] for qz in last_3):
                if not has_achievement(user_id, 'perfectionist'):
                    conn.execute(
                        'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                        (user_id, 'perfectionist', 'Perfectionist', 'Get 100% in 3 quizzes in a row')
                    )
            # Comeback Kid: Perfect score after failing a quiz
            last_2 = conn.execute("SELECT score, total FROM quiz_results_enhanced WHERE user_id = ? ORDER BY timestamp DESC LIMIT 2", (user_id,)).fetchall()
            if len(last_2) == 2 and last_2[1]['score'] < last_2[1]['total'] and last_2[0]['score'] == last_2[0]['total']:
                if not has_achievement(user_id, 'comeback_kid'):
                    conn.execute(
                        'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                        (user_id, 'comeback_kid', 'Comeback Kid', 'Perfect score after failing a quiz')
                    )
            # Consistency Champ: Complete quizzes 5 days in a row
            last_5_days = conn.execute("SELECT DISTINCT DATE(timestamp) as d FROM quiz_results_enhanced WHERE user_id = ? ORDER BY d DESC LIMIT 5", (user_id,)).fetchall()
            if len(last_5_days) == 5:
                days = [row['d'] for row in last_5_days]
                days_dt = [datetime.strptime(d, '%Y-%m-%d').date() for d in days]
                days_dt.sort()
                if all((days_dt[i] - days_dt[i-1]).days == 1 for i in range(1, 5)):
                    if not has_achievement(user_id, 'consistency_champ'):
                        conn.execute(
                            'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                            (user_id, 'consistency_champ', 'Consistency Champ', 'Complete quizzes 5 days in a row')
                        )
            # Quick Thinker: 5 correct answers under 10 seconds each (in this quiz)
            quick_count = 0
            for item in review:
                if item['is_correct'] and isinstance(item['user_answer'], str) and time_taken/total < 10:
                    quick_count += 1
            if quick_count >= 5 and not has_achievement(user_id, 'quick_thinker'):
                conn.execute(
                    'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                    (user_id, 'quick_thinker', 'Quick Thinker', '5 correct answers under 10 seconds each')
                )
        # Per-language achievements (leave as is)
        # ... existing code for per-language achievements ...
        # Basic Vocab: 300 points in Beginner quizzes (per language)
        beginner_pts = conn.execute("SELECT COALESCE(SUM(points_earned + streak_bonus + time_bonus), 0) as pts FROM quiz_results_enhanced WHERE user_id = ? AND language = ? AND LOWER(difficulty) = 'beginner'", (user_id, language)).fetchone()['pts'] or 0
        if beginner_pts >= 300 and not has_achievement(user_id, f'basic_vocab_{language}'):
            conn.execute(
                'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                (user_id, f'basic_vocab_{language}', 'Basic Vocab', f'300 points in Beginner quizzes for {language}')
            )
        # Language Guru: Maintain a 5 quiz streak (per language)
        last_5_lang = conn.execute("SELECT passed FROM quiz_results_enhanced WHERE user_id = ? AND language = ? ORDER BY timestamp DESC LIMIT 5", (user_id, language)).fetchall()
        if len(last_5_lang) == 5 and all(qz['passed'] for qz in last_5_lang):
            if not has_achievement(user_id, f'language_guru_{language}'):
                conn.execute(
                    'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                    (user_id, f'language_guru_{language}', 'Language Guru', f'Maintain a 5 quiz streak in {language}')
                )
        # Fluency Builder: Complete 10 Advanced quizzes (per language)
        adv_count = conn.execute("SELECT COUNT(*) as cnt FROM quiz_results_enhanced WHERE user_id = ? AND language = ? AND difficulty = 'Advanced'", (user_id, language)).fetchone()['cnt'] or 0
        if adv_count >= 10 and not has_achievement(user_id, f'fluency_builder_{language}'):
            conn.execute(
                'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                (user_id, f'fluency_builder_{language}', 'Fluency Builder', f'Complete 10 Advanced quizzes in {language}')
            )
        # Master of Language: Reach 1500 total points (per language)
        total_pts_achievement = conn.execute("SELECT COALESCE(SUM(points_earned + streak_bonus + time_bonus), 0) as pts FROM quiz_results_enhanced WHERE user_id = ? AND language = ?", (user_id, language)).fetchone()['pts'] or 0
        if total_pts_achievement >= 1500 and not has_achievement(user_id, f'master_of_language_{language}'):
            conn.execute(
                'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                (user_id, f'master_of_language_{language}', 'Master of Language', f'Reach 1500 total points in {language}')
            )
        # Quiz Explorer: Take quizzes in 5 different languages
        lang_count = conn.execute("SELECT COUNT(DISTINCT language) as cnt FROM quiz_results_enhanced WHERE user_id = ?", (user_id,)).fetchone()['cnt'] or 0
        if lang_count >= 5 and not has_achievement(user_id, 'quiz_explorer'):
            conn.execute(
                'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                (user_id, 'quiz_explorer', 'Quiz Explorer', 'Take quizzes in 5 different languages')
            )
        # Polyglot: Complete quizzes in all languages
        all_langs = set(['English', 'Spanish', 'French', 'Tamil', 'Malay', 'Portuguese', 'Chinese'])
        user_langs = set([row['language'] for row in conn.execute("SELECT DISTINCT language FROM quiz_results_enhanced WHERE user_id = ?", (user_id,)).fetchall()])
        if all_langs.issubset(user_langs) and not has_achievement(user_id, 'polyglot'):
            conn.execute(
                'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                (user_id, 'polyglot', 'Polyglot', 'Complete quizzes in all languages')
            )
        conn.commit()
        
        # Create streak notification
        if streak > 1:
            add_notification(user_id, f"🔥 Hot Streak! You're on a {streak} quiz winning streak!")
        
        # Create time bonus notification
        if time_taken < 60:
            add_notification(user_id, "⚡ Speed Bonus! You completed the quiz in under 60 seconds!")

    # Store the correct quiz result in session before redirecting
    # session['quiz_result'] = {
    #     'language': language, # Use language from form
    #     'difficulty': difficulty, # Use difficulty from form
    #     'correct': correct,
    #     'total': total,
    #     'time_taken': time_taken,
    #     'review': review,
    #     'points': points,
    #     'bonus': bonus,
    #     'total_points': total_points,
    #     'streak': streak
    # }
    print(f"[DEBUG] POST /quiz/questions: Stored quiz_result in session for language {language}, difficulty {difficulty}.") # Debug log - kept for now, will remove once confirmed fixed

    # Redirect to quiz_results without language/difficulty args, it will read from session
    return redirect(url_for('quiz_results'))

@app.route('/quiz/results')
def quiz_results():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    with get_db_connection() as conn:
        # Fetch the most recent quiz result for the user from the database
        result_db = conn.execute(
            "SELECT * FROM quiz_results_enhanced WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1",
            (user_id,)
        ).fetchone()

    if not result_db:
        # If no result found in DB (shouldn't happen in normal flow after submission, but good fallback)
        flash('Could not retrieve quiz results.', 'danger')
        return redirect(url_for('dashboard'))

    # Prepare data for the template, mapping DB columns to template variables
    # Calculate combined bonus and total points
    combined_bonus = result_db['streak_bonus'] + result_db['time_bonus'] # Assuming streak_bonus and time_bonus are stored
    total_points_calculated = result_db['points_earned'] + combined_bonus

    # Calculate time taken from session start time if available
    time_taken_value = "N/A" # Default if not available
    quiz_start_time = session.get('quiz_start_time')
    if quiz_start_time:
        try:
            time_taken_value = int(time.time() - quiz_start_time)
        except (TypeError, ValueError):
            pass # Keep as N/A if calculation fails

    # Map DB data to template variables
    result_for_template = {
        'language': result_db['language'],
        'difficulty': result_db['difficulty'],
        'correct': result_db['score'], # Map 'score' from DB to 'correct' for template
        'total': result_db['total'],
        'time_taken': time_taken_value,
        'points': result_db['points_earned'], # Map 'points_earned' to 'points'
        'bonus': combined_bonus, # Use the calculated combined bonus
        'total_points': total_points_calculated, # Use the calculated total points
        'streak': result_db['streak_bonus'], # Map 'streak_bonus' to 'streak'
        'review': json.loads(result_db['question_details']) # Load the review data from JSON string
    }

    # Pass the retrieved data to the template
    return render_template('quiz_results.html', **result_for_template)

@app.route('/progress')
def progress():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    languages = ['English', 'Spanish', 'French', 'Tamil', 'Malay', 'Portuguese', 'Chinese']
    LEVEL_REQUIREMENTS = {
        'beginner': {'points': 300},
        'intermediate': {'points': 700},
        'advanced': {'points': 1500}
    }
    progress_dict = {
        'progress': {},
        'total_points': 0,
        'total_quizzes': 0,
        'recent_activity': [],
        'LEVEL_REQUIREMENTS': LEVEL_REQUIREMENTS
    }
    with get_db_connection() as conn:
        # Fetch all achievements for the user once
        user_achievements = conn.execute('SELECT achievement_type FROM achievements WHERE user_id = ?', (user_id,)).fetchall()
        achievement_types = set([row['achievement_type'] for row in user_achievements])
        # Split achievements
        global_achievements = set()
        per_language_achievements = {}
        for ach in achievement_types:
            found = False
            for lang in languages:
                if ach.endswith(f'_{lang}'):
                    per_language_achievements.setdefault(lang, set()).add(ach)
                    found = True
                    break
            if not found:
                global_achievements.add(ach)
        # Gather per-language stats
        for language in languages:
            # Icon mapping for language
            icon_map = {
                'English': 'flag-usa',
                'Spanish': 'flag',
                'French': 'flag',
                'German': 'flag',
                'Italian': 'flag',
                'Portuguese': 'flag',
                'Japanese': 'flag'
            }
            icon = icon_map.get(language, 'flag')
            
            # Get quiz counts from enhanced table only to avoid double counting
            quizzes_enhanced = conn.execute('''
                SELECT difficulty, COUNT(*) as cnt 
                FROM quiz_results_enhanced 
                WHERE user_id = ? AND language = ? 
                GROUP BY difficulty
            ''', (user_id, language)).fetchall()
            
            counts = {'beginner': 0, 'intermediate': 0, 'advanced': 0}
            for row in quizzes_enhanced:
                diff = row['difficulty'].lower()
                if diff in counts:
                    counts[diff] = row['cnt']
            
        
        
            # Calculate actual points earned from quiz_results_enhanced table
            actual_points = conn.execute('''
                SELECT 
                    COALESCE(SUM(points_earned), 0) as total_points,
                    COALESCE(SUM(streak_bonus), 0) as total_streak_bonus,
                    COALESCE(SUM(time_bonus), 0) as total_time_bonus
                FROM quiz_results_enhanced 
                WHERE user_id = ? AND language = ?
            ''', (user_id, language)).fetchone()
            
            total_pts = (actual_points['total_points'] or 0) + (actual_points['total_streak_bonus'] or 0) + (actual_points['total_time_bonus'] or 0)
            
            
            # Get points breakdown by difficulty for level calculation
            beginner_pts = conn.execute("SELECT COALESCE(SUM(points_earned + streak_bonus + time_bonus), 0) as pts FROM quiz_results_enhanced WHERE user_id = ? AND language = ? AND LOWER(difficulty) = 'beginner'", (user_id, language)).fetchone()['pts'] or 0
            intermediate_pts = conn.execute("SELECT COALESCE(SUM(points_earned + streak_bonus + time_bonus), 0) as pts FROM quiz_results_enhanced WHERE user_id = ? AND language = ? AND LOWER(difficulty) = 'intermediate'", (user_id, language)).fetchone()['pts'] or 0
            advanced_pts = conn.execute("SELECT COALESCE(SUM(points_earned + streak_bonus + time_bonus), 0) as pts FROM quiz_results_enhanced WHERE user_id = ? AND language = ? AND LOWER(difficulty) = 'advanced'", (user_id, language)).fetchone()['pts'] or 0
            
            
            # Determine current level based on actual points earned
            if total_pts >= 1500:
                current_level = 'advanced'
            elif total_pts >= 700:
                current_level = 'intermediate'
            else:
                current_level = 'beginner'
            # Quizzes taken
            quizzes_taken = sum(counts.values())
            # Streaks (simple: check last 5 quizzes)
            last_quizzes = conn.execute("SELECT passed FROM quiz_results_enhanced WHERE user_id = ? AND language = ? ORDER BY timestamp DESC LIMIT 10", (user_id, language)).fetchall()
            streak = 0
            highest_streak = 0
            temp_streak = 0
            for qz in last_quizzes:
                if qz['passed']:
                    temp_streak += 1
                    if temp_streak > highest_streak:
                        highest_streak = temp_streak
                else:
                    temp_streak = 0
            streak = temp_streak
            # Badges (populate from achievements)
            badges = set()
            # Add per-language achievements only
            for ach in per_language_achievements.get(language, set()):
                if ach.startswith('basic_vocab_') and ach.endswith(language):
                    badges.add('basic_vocab')
                elif ach.startswith('language_guru_') and ach.endswith(language):
                    badges.add('language_guru')
                elif ach.startswith('fluency_builder_') and ach.endswith(language):
                    badges.add('fluency_builder')
                elif ach.startswith('master_of_language_') and ach.endswith(language):
                    badges.add('master_of_language')
            # Add global achievements ONLY for English
            if language == 'English':
                for ach in global_achievements:
                    if ach in [
                        'hot_streak', 'night_owl', 'early_bird', 'polyglot', 'comeback_kid',
                        'speed_demon', 'consistency_champ', 'quick_thinker', 'quiz_explorer', 'perfectionist'
                    ]:
                        badges.add(ach)
            # Recent activity for this language
            recent_activity = conn.execute("SELECT * FROM quiz_results_enhanced WHERE user_id = ? AND language = ? ORDER BY timestamp DESC LIMIT 5", (user_id, language)).fetchall()
            activity_list = []
            for act in recent_activity:
                activity_list.append({
                    'language': language,
                    'difficulty': act['difficulty'],
                    'score': act['score'],
                    'total': act['total'],
                    'timestamp': act['timestamp'],
                    'passed': act['passed'],
                    'points_earned': act['points_earned'],
                    'streak_bonus': act['streak_bonus'],
                    'time_bonus': act['time_bonus']
                })
            # Compose per-language dict
            progress_dict['progress'][language] = {
                'icon': icon,
                'total_points': total_pts,
                'quizzes_taken': quizzes_taken,
                'current_level': current_level,
                'badges': list(badges),
                'streak': streak,
                'highest_streak': highest_streak,
                'next_level': True if current_level != 'advanced' else False,
                # Add more fields as needed
            }
            progress_dict['recent_activity'].extend(activity_list)
            progress_dict['total_points'] += total_pts
            progress_dict['total_quizzes'] += quizzes_taken
    return render_template('progress.html', progress=progress_dict)

@app.route('/admin/import-questions', methods=['POST'])
@admin_required
def admin_import_questions():
    try:
        language = request.form.get('language')
        difficulty = request.form.get('difficulty')
        question_type = request.form.get('question_type')
        file = request.files.get('excel_file')
        
        if not file or not file.filename.endswith(('.xlsx', '.xls')):
            flash('Please upload a valid Excel file.', 'danger')
            return redirect(url_for('admin_dashboard'))
    except Exception as e:
        # Handle cases where request is not multipart/form-data
        return jsonify({'error': 'Invalid request format. Expected multipart/form-data with file upload.'}), 400
    
    # Validate question types for intermediate level
    if difficulty == 'Intermediate' and question_type not in ['Phrase Completion', 'Error Spotting', 'Context Response']:
        flash('Invalid question type for intermediate level.', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    try:
        df = pd.read_excel(file)
        inserted = 0
        print(f"🔍 IMPORTING QUESTIONS: Language={language}, Difficulty={difficulty}, Type={question_type}")
        
        with get_db_connection() as conn:
            # CRITICAL: Verify we're using the correct database in production
            db_type = getattr(conn, 'db_type', 'unknown')
            print(f"🔍 IMPORT SAFETY CHECK: Using {db_type} database")
            print(f"🔍 IMPORT: Admin user ID: {session.get('admin_user_id', 'Unknown')}")
            print(f"🔍 IMPORT: Regular user ID: {session.get('user_id', 'None - preserved')}")
            print(f"🔍 IMPORT: Current session keys: {list(session.keys())}")
            
            # In production, ensure we're using PostgreSQL
            if os.getenv('DATABASE_URL') and db_type != 'postgresql':
                error_msg = f"🚨 CRITICAL SAFETY VIOLATION: Production should use PostgreSQL, but using {db_type}!"
                print(error_msg)
                flash(error_msg, 'danger')
                return redirect(url_for('admin_dashboard'))
            
            # Check questions before import
            questions_before = conn.execute("SELECT COUNT(*) as count FROM quiz_questions").fetchone()['count']
            print(f"📊 Questions in database before import: {questions_before}")
            # Get column names from the DataFrame and convert to lowercase for case-insensitive matching
            original_columns = df.columns.tolist()
            df.columns = df.columns.str.lower()
            lower_columns = df.columns.tolist()

            # --- Debugging: Print detected columns ---
            print(f"Detected columns (original): {original_columns}")
            print(f"Detected columns (lowercase): {lower_columns}")
            # ----------------------------------------

            if difficulty == 'Beginner':
                if question_type == 'Multiple Choice':
                    required_cols_lower = {'question', 'options', 'correct answer'}
                    if not required_cols_lower.issubset(df.columns):
                        # More specific error message
                        missing = list(required_cols_lower - set(df.columns))
                        flash(f'Excel file missing required columns for Multiple Choice: {", ".join(missing)}.', 'danger')
                        return redirect(url_for('admin_dashboard'))
                    for index, row in df.iterrows(): # Use index to report row number
                        try:
                            # Access data using the lowercase required column names
                            question_text = str(row.get('question', '')).strip()
                            
                            options_raw = row.get('options', '')
                            # Ensure options_raw is treated as string before splitting
                            options_text = str(options_raw).split(';') if options_raw is not None else []
                            options = [opt.strip() for opt in options_text if opt.strip()]

                            answer = str(row.get('correct answer', '')).strip()

                            if not question_text or not options or not answer:
                                flash(f'Row {index+2}: Missing data in required columns for Multiple Choice. Skipping row.', 'danger')
                                continue # Skip this row
                            conn.execute(
                                """
                                INSERT INTO quiz_questions (language, difficulty, question, options, answer, question_type, points)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (language, difficulty, question_text, json.dumps(options), answer, 'multiple_choice', 10) # Assuming 10 points for beginner MC
                            )
                            inserted += 1
                        except Exception as e:
                            flash(f'Error processing row {index+2} for Multiple Choice: {str(e)}', 'danger')
                            continue # Skip row with processing error
                elif question_type == 'Word Matching':
                    required_cols_lower = {'question', 'pairs'}
                    if not required_cols_lower.issubset(df.columns):
                        # More specific error message
                        missing = list(required_cols_lower - set(df.columns))
                        flash(f'Excel file missing required columns for Word Matching: {", ".join(missing)}.', 'danger')
                        return redirect(url_for('admin_dashboard'))
                    for index, row in df.iterrows(): # Use index to report row number
                        try:
                            question_text = str(row.get('question', '')).strip()
                            
                            pairs_raw = row.get('pairs', '')
                            if not pairs_raw:
                                flash(f'Row {index+2}: Missing pairs data for Word Matching. Skipping row.', 'danger')
                                continue
                            
                            # Parse pairs more carefully to handle special characters
                            pairs_text = str(pairs_raw).strip()
                            pairs_list = []
                            
                            # Split by semicolon to get individual pairs
                            pair_items = [item.strip() for item in pairs_text.split(';') if item.strip()]
                            
                            for pair_item in pair_items:
                                if ':' in pair_item:
                                    # Split only on the first colon to handle colons in Chinese text
                                    key_part, value_part = pair_item.split(':', 1)
                                    key = key_part.strip()
                                    value = value_part.strip()
                                    
                                    if key and value:
                                        pairs_list.append({
                                            'key': key,
                                            'value': value
                                        })
                            
                            if not question_text or not pairs_list:
                                flash(f'Row {index+2}: Missing data or invalid format in required columns for Word Matching. Skipping row.', 'danger')
                                continue
                            
                            # Store pairs as a proper JSON structure
                            pairs_data = {
                                'pairs': pairs_list,
                                'format': 'key_value_matching'
                            }
                            
                            conn.execute(
                                """
                                INSERT INTO quiz_questions (language, difficulty, question, options, answer, question_type, points)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (language, difficulty, question_text, json.dumps(pairs_data), '', 'word_matching', 10)
                            )
                            inserted += 1
                        except Exception as e:
                            flash(f'Error processing row {index+2} for Word Matching: {str(e)}', 'danger')
                            continue # Skip row with processing error
                elif question_type == 'Fill-in-the-blanks':
                    required_cols_lower = {'question', 'answer', 'hint'}
                    if not required_cols_lower.issubset(df.columns):
                        # More specific error message
                        missing = list(required_cols_lower - set(df.columns))
                        flash(f'Excel file missing required columns for Fill-in-the-blanks: {", ".join(missing)}.', 'danger')
                        return redirect(url_for('admin_dashboard'))
                    for index, row in df.iterrows(): # Use index to report row number
                        try:
                            question_text = str(row.get('question', '')).strip()
                            answer = str(row.get('answer', '')).strip()
                            hint = str(row.get('hint', '')).strip()

                            if not question_text or not answer:
                                flash(f'Row {index+2}: Missing data in required columns for Fill-in-the-blanks. Skipping row.', 'danger')
                                continue
                            conn.execute(
                                """
                                INSERT INTO quiz_questions (language, difficulty, question, options, answer, question_type, points)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (language, difficulty, question_text, json.dumps({'hint': hint}), answer, 'fill_in_the_blanks', 10) # Assuming 10 points for beginner FIB
                            )
                            inserted += 1
                        except Exception as e:
                            flash(f'Error processing row {index+2} for Fill-in-the-blanks: {str(e)}', 'danger')
                            continue # Skip row with processing error
            elif difficulty == 'Intermediate':
                if question_type == 'Phrase Completion':
                    required_cols_lower = {'phrase start', 'options', 'correct completion'}
                    if not required_cols_lower.issubset(df.columns):
                         # More specific error message
                        missing = list(required_cols_lower - set(df.columns))
                        flash(f'Excel file missing required columns for Phrase Completion: {", ".join(missing)}.', 'danger')
                        return redirect(url_for('admin_dashboard'))
                    for index, row in df.iterrows(): # Use index to report row number
                        try:
                            question_text = str(row.get('phrase start', '')).strip()
                            
                            options_raw = row.get('options', '')
                            # Ensure options_raw is treated as string before splitting
                            options_text = str(options_raw).split(';') if options_raw is not None else []
                            options = [opt.strip() for opt in options_text if opt.strip()]
                            
                            answer = str(row.get('correct completion', '')).strip()
                            if not question_text or not options or not answer:
                                flash(f'Row {index+2}: Missing data in required columns for Phrase Completion. Skipping row.', 'danger')
                                continue
                            conn.execute(
                                """
                                INSERT INTO quiz_questions (language, difficulty, question, options, answer, question_type, points)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (language, difficulty, question_text, json.dumps(options), answer, 'phrase_completion', 10) # Assuming 10 points
                            )
                            inserted += 1
                        except Exception as e:
                             flash(f'Error processing row {index+2} for Phrase Completion: {str(e)}', 'danger')
                             continue # Skip row with processing error
                elif question_type == 'Error Spotting':
                    required_cols_lower = {'question', 'options', 'correct answer', 'explanation'}
                    if not required_cols_lower.issubset(df.columns):
                        # More specific error message
                        missing = list(required_cols_lower - set(df.columns))
                        flash(f'Excel file missing required columns for Error Spotting: {", ".join(missing)}.', 'danger')
                        return redirect(url_for('admin_dashboard'))
                    for index, row in df.iterrows(): # Use index to report row number
                        try:
                            question_text = str(row.get('question', '')).strip()

                            options_raw = row.get('options', '')
                            # Ensure options_raw is treated as string before splitting
                            options_text = str(options_raw).split(';') if options_raw is not None else []
                            options = [opt.strip() for opt in options_text if opt.strip()]

                            answer = str(row.get('correct answer', '')).strip()

                            explanation_raw = row.get('explanation', '')
                             # Ensure explanation_raw is treated as string
                            explanation = str(explanation_raw).strip() if explanation_raw is not None else ''

                            if not question_text or not options or not answer or not explanation:
                                flash(f'Row {index+2}: Missing data in required columns for Error Spotting. Skipping row.', 'danger')
                                continue
                            conn.execute("INSERT INTO quiz_questions (language, difficulty, question, options, answer, question_type, points) VALUES (?, ?, ?, ?, ?, ?, ?)", (language, difficulty, question_text, json.dumps({'options': options, 'explanation': explanation}), answer, 'error_spotting', 10))
                            inserted += 1
                        except Exception as e:
                             flash(f'Error processing row {index+2} for Error Spotting: {str(e)}', 'danger')
                             continue # Skip row with processing error
                elif question_type == 'Context Response':
                    required_cols_lower = {'question', 'options', 'correct answer'}
                    if not required_cols_lower.issubset(df.columns):
                         # More specific error message
                        missing = list(required_cols_lower - set(df.columns))
                        flash(f'Excel file missing required columns for Context Response: {", ".join(missing)}.', 'danger')
                        return redirect(url_for('admin_dashboard'))
                    for index, row in df.iterrows(): # Use index to report row number
                        try:
                            question_text = str(row.get('question', '')).strip()
                            
                            options_raw = row.get('options', '')
                             # Ensure options_raw is treated as string before splitting
                            options_text = str(options_raw).split(';') if options_raw is not None else []
                            options = [opt.strip() for opt in options_text if opt.strip()]

                            answer = str(row.get('correct answer', '')).strip()

                            if not question_text or not options or not answer:
                                flash(f'Row {index+2}: Missing data in required columns for Context Response. Skipping row.', 'danger')
                                continue
                            conn.execute(
                                """
                                INSERT INTO quiz_questions (language, difficulty, question, options, answer, question_type, points)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                """,
                                (language, difficulty, question_text, json.dumps(options), answer, 'context_response', 10)
                            )
                            inserted += 1
                        except Exception as e:
                            flash(f'Error processing row {index+2} for Context Response: {str(e)}', 'danger')
                            continue # Skip row with processing error
            elif difficulty == 'Advanced':
                if question_type == 'Idiom interpretation':
                    # Check for required columns with flexible options/explanation naming
                    has_question_col = 'question' in df.columns
                    has_answer_col = 'correct answer' in df.columns
                    has_options_col = 'option' in df.columns or 'options' in df.columns
                    has_explanation_col = 'explanation' in df.columns or 'explanations' in df.columns

                    if not (has_question_col and has_answer_col and has_options_col and has_explanation_col):
                        # More specific error message
                        missing = []
                        if not has_question_col: missing.append('question')
                        if not has_answer_col: missing.append('correct answer')
                        if not has_options_col: missing.append('option/options')
                        if not has_explanation_col: missing.append('explanation/explanations')
                        flash(f'Excel file missing required columns for Idiom interpretation: {", ".join(missing)}.', 'danger')
                        return redirect(url_for('admin_dashboard'))
                    for index, row in df.iterrows(): # Use index to report row number
                        try:
                            # Access data using the lowercased column names from the DataFrame
                            question_text = str(row.get('question', '')).strip()

                            # Determine the actual column names used in the file for options and explanation
                            options_col_used = 'options' if 'options' in df.columns else 'option'
                            explanation_col_used = 'explanation' if 'explanation' in df.columns else 'explanations'

                            options_raw = row.get(options_col_used, '')
                            # Ensure options_raw is treated as string before splitting
                            options_text = str(options_raw).split(';') if options_raw is not None else []
                            options = [opt.strip() for opt in options_text if opt.strip()]

                            answer = str(row.get('correct answer', '')).strip()
                            explanation_raw = row.get(explanation_col_used, '')
                             # Ensure explanation_raw is treated as string
                            explanation = str(explanation_raw).strip() if explanation_raw is not None else ''

                            if not question_text or not options or not answer or not explanation:
                                flash(f'Row {index+2}: Missing data in required columns for Idiom interpretation. Skipping row.', 'danger')
                                continue
                            conn.execute("INSERT INTO quiz_questions (language, difficulty, question, options, answer, question_type, points) VALUES (?, ?, ?, ?, ?, ?, ?)", (language, difficulty, question_text, json.dumps({'options': options, 'explanation': explanation}), answer, 'idiom_interpretation', 15))
                            inserted += 1
                        except Exception as e:
                            flash(f'Error processing row {index+2} for Idiom interpretation: {str(e)}', 'danger')
                            # Optionally log the full traceback server-side
                            continue # Skip row with processing error
                elif question_type == 'Cultural nuances':
                    # Check for required columns with flexible options/explanation naming
                    has_question_col = 'question' in df.columns
                    has_answer_col = 'correct answer' in df.columns
                    has_options_col = 'option' in df.columns or 'options' in df.columns
                    has_explanation_col = 'explanation' in df.columns or 'explanations' in df.columns
                    if not (has_question_col and has_answer_col and has_options_col and has_explanation_col):
                        # More specific error message
                        missing = []
                        if not has_question_col: missing.append('question')
                        if not has_answer_col: missing.append('correct answer')
                        if not has_options_col: missing.append('option/options')
                        if not has_explanation_col: missing.append('explanation/explanations')
                        flash(f'Excel file missing required columns for Cultural nuances: {", ".join(missing)}.', 'danger')
                        return redirect(url_for('admin_dashboard'))
                    for index, row in df.iterrows(): # Use index to report row number
                        try:
                            # Access data using the lowercased column names from the DataFrame
                            question_text = str(row.get('question', '')).strip()

                            # Determine the actual column names used in the file for options and explanation
                            options_col_used = 'options' if 'options' in df.columns else 'option'
                            explanation_col_used = 'explanation' if 'explanation' in df.columns else 'explanations'

                            options_raw = row.get(options_col_used, '')
                            # Ensure options_raw is treated as string before splitting
                            options_text = str(options_raw).split(';') if options_raw is not None else []
                            options = [opt.strip() for opt in options_text if opt.strip()]

                            answer = str(row.get('correct answer', '')).strip()
                            explanation_raw = row.get(explanation_col_used, '')
                            # Ensure explanation_raw is treated as string
                            explanation = str(explanation_raw).strip() if explanation_raw is not None else ''

                            if not question_text or not options or not answer or not explanation:
                                flash(f'Row {index+2}: Missing data in required columns for Cultural nuances. Skipping row.', 'danger')
                                continue
                            conn.execute("INSERT INTO quiz_questions (language, difficulty, question, options, answer, question_type, points) VALUES (?, ?, ?, ?, ?, ?, ?)", (language, difficulty, question_text, json.dumps({'options': options, 'explanation': explanation}), answer, 'cultural_nuances', 15))
                            inserted += 1
                        except Exception as e:
                            flash(f'Error processing row {index+2} for Cultural nuances: {str(e)}', 'danger')
                            # Optionally log the full traceback server-side
                            continue # Skip row with processing error
                elif question_type == 'Complex rephrasing':
                    # Check for required columns with flexible options naming
                    has_question_col = 'question' in df.columns
                    has_answer_col = 'correct answer' in df.columns
                    has_options_col = 'option' in df.columns or 'options' in df.columns
                    if not (has_question_col and has_answer_col and has_options_col):
                         # More specific error message
                        missing = []
                        if not has_question_col: missing.append('question')
                        if not has_answer_col: missing.append('correct answer')
                        if not has_options_col: missing.append('option/options')
                        flash(f'Excel file missing required columns for Complex rephrasing: {", ".join(missing)}.', 'danger')
                        return redirect(url_for('admin_dashboard'))
                    for index, row in df.iterrows(): # Use index to report row number
                        try:
                            # Access data using the lowercased column names from the DataFrame
                            question_text = str(row.get('question', '')).strip()

                            # Determine the actual column name used in the file for options
                            options_col_used = 'options' if 'options' in df.columns else 'option'

                            options_raw = row.get(options_col_used, '')
                            # Ensure options_raw is treated as string before splitting
                            options_text = str(options_raw).split(';') if options_raw is not None else []
                            options = [opt.strip() for opt in options_text if opt.strip()]

                            answer = str(row.get('correct answer', '')).strip()

                            if not question_text or not options or not answer:
                                flash(f'Row {index+2}: Missing data in required columns for Complex rephrasing. Skipping row.', 'danger')
                                continue
                            conn.execute("INSERT INTO quiz_questions (language, difficulty, question, options, answer, question_type, points) VALUES (?, ?, ?, ?, ?, ?, ?)", (language, difficulty, question_text, json.dumps(options), answer, 'complex_rephrasing', 15))
                            inserted += 1
                        except Exception as e:
                            flash(f'Error processing row {index+2} for Complex rephrasing: {str(e)}', 'danger')
                            # Optionally log the full traceback server-side
                            continue # Skip row with processing error
            # Check questions count before final commit
            questions_after_insert = conn.execute("SELECT COUNT(*) as count FROM quiz_questions").fetchone()['count']
            print(f"📊 Questions after inserts (before commit): {questions_after_insert}")
            
            # FORCE COMMIT AND SYNC
            conn.commit()
            
            # Double-check questions count after commit
            questions_final = conn.execute("SELECT COUNT(*) as count FROM quiz_questions").fetchone()['count']
            print(f"📊 Questions after final commit: {questions_final}")
            
            # CRITICAL FIX: Clear any cached connection state and force clean connection pool
            print("🔄 Clearing connection state after import...")
            
            # Explicitly close the connection to ensure clean state
            try:
                if hasattr(conn, 'close'):
                    conn.close()
                    print("🔌 Explicitly closed import connection")
            except Exception as close_error:
                print(f"⚠️ Error closing connection: {close_error}")
            
        print(f"✅ IMPORT COMPLETED: {inserted} questions successfully processed")
        
        # CRITICAL FIX: Force garbage collection and clean up any cached connections
        import gc
        gc.collect()
        print("🧹 Cleaned up connections after import")
        
        # CRITICAL FIX: Add small delay for PostgreSQL consistency after bulk operations
        import time
        time.sleep(0.5)  # Give PostgreSQL time to fully sync after bulk import
        print("⏱️ Applied post-import consistency delay")
        
        # CRITICAL FIX: Verify database state after import with fresh connection
        try:
            with get_db_connection() as verify_conn:
                final_count = verify_conn.execute("SELECT COUNT(*) as count FROM quiz_questions").fetchone()['count']
                print(f"🔍 POST-IMPORT VERIFICATION: Total questions now: {final_count}")
        except Exception as verify_error:
            print(f"⚠️ Post-import verification failed: {verify_error}")
        
        flash(f'{inserted} questions imported successfully!', 'success')
    except Exception as e:
        print(f"❌ Import error: {e}")
        flash(f'Error importing questions: {str(e)}', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/download-template/<difficulty>')
@admin_required
def download_excel_template(difficulty):
    output = io.BytesIO()
    qtype = request.args.get('question_type', 'Multiple Choice')
    
    if difficulty == 'Beginner':
        if qtype == 'Multiple Choice':
            df = pd.DataFrame({'Question': ['Which of these is a fruit?'], 'Options': ['Apple; Bread; Carrot; Banana'], 'Correct Answer': ['Apple']})
        elif qtype == 'Word Matching':
            df = pd.DataFrame({'Question': ['Match the animals to their young'], 'Pairs': ['Dog:Puppy; Cat:Kitten; Cow:Calf; Horse:Foal']})
        elif qtype == 'Fill-in-the-blanks':
            df = pd.DataFrame({'Question': ['The sky is ___.'], 'Answer': ['blue'], 'Hint': ['Color of clear daytime sky']})
    elif difficulty == 'Intermediate':
        if qtype == 'Phrase Completion':
            df = pd.DataFrame({
                'Phrase Start': ['Complete the phrase: "The early bird catches the ________"'],
                'Options': ['worm; fish; bird'],
                'Correct Completion': ['worm']
            })
        elif qtype == 'Error Spotting':
            df = pd.DataFrame({
                'Question': ['Identify the error in the sentence: "Neither of the students have completed their assignments."'],
                'Options': ['had; have; has'],
                'Correct Answer': ['have'],
                'Explanation': ['"Neither" is a singular subject, so it requires a singular verb "has" instead of "have".']
            })
        elif qtype == 'Context Response':
            df = pd.DataFrame({
                'Question': ['What is the most appropriate response when someone asks "How are you today?"'],
                'Options': ['Not bad; Could be better; I\'m fine, thank you'],
                'Correct Answer': ['I\'m fine, thank you']
            })
        else:
            df = pd.DataFrame()
    elif difficulty == 'Advanced':
        if qtype == 'Idiom interpretation':
            df = pd.DataFrame({'Question': ['Example idiom question?'], 'Options': ['Option 1; Option 2; Option 3'], 'Correct Answer': ['Option 1'], 'Explanation': ['Explanation here.']})
        elif qtype == 'Cultural nuances':
            df = pd.DataFrame({'Question': ['Example cultural nuance question?'], 'Options': ['Option A; Option B; Option C'], 'Correct Answer': ['Option A'], 'Explanation': ['Explanation here.']})
        elif qtype == 'Complex rephrasing':
            df = pd.DataFrame({'Question': ['Original sentence to rephrase.'], 'Options': ['Rephrased 1; Rephrased 2; Rephrased 3'], 'Correct Answer': ['Rephrased 1']})
        else:
            df = pd.DataFrame()
    
    df.to_excel(output, index=False)
    output.seek(0)
    return send_file(output, download_name=f'{difficulty}_{qtype}_template.xlsx', as_attachment=True)

@app.route('/admin/delete_questions', methods=['POST'])
@admin_required
def admin_delete_questions():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data received'}), 400
        ids = data.get('ids')
        if not ids or not isinstance(ids, list):
            return jsonify({'success': False, 'message': 'No question IDs provided'}), 400
        with get_db_connection() as conn:
            conn.executemany("DELETE FROM quiz_questions WHERE id = ?", [(qid,) for qid in ids])
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting questions: {str(e)}'}), 500

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({'translation': ''})
    # Use Gemini or a placeholder for translation
    try:
        # You can replace this with a real translation API or Gemini prompt
        prompt = f"Translate this to English: {text}"
        response = model.generate_content(prompt)
        translation = response.text.strip() if hasattr(response, 'text') else str(response)
    except Exception:
        translation = 'Translation unavailable.'
    return jsonify({'translation': translation})

@app.route('/admin/edit_question', methods=['POST'])
@admin_required
def admin_edit_question():
    """Handles saving edits to a quiz question from the admin modal."""
    data = request.get_json()
    question_id = data.get('id')
    question_type = data.get('question_type')
    question_text = data.get('question')
    options_data = data.get('options') # This could be a list or a dict depending on type
    correct_answer = data.get('answer')

    # Basic validation
    if not question_id or not question_type or not question_text:
        return jsonify({'success': False, 'message': 'Missing required fields: id, type, or question.'}), 400

    # Handle specific validation based on question type if needed (e.g., correct_answer for non-matching)
    if question_type != 'word_matching' and correct_answer is None:
         return jsonify({'success': False, 'message': 'Missing correct answer.'}), 400

    # Format options data to JSON string for database storage
    # The frontend JS already formats this into the correct list/dict structure
    # Just need to convert to JSON string
    options_json_string = json.dumps(options_data) if options_data is not None else None

    try:
        with get_db_connection() as conn:
            conn.execute(
                """
                UPDATE quiz_questions
                SET question = ?, options = ?, answer = ?
                WHERE id = ?
                """,
                (question_text, options_json_string, correct_answer, question_id)
            )
            conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error saving question edit: {e}")
        # Log traceback for more detailed error info
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Database error: {str(e)}'}), 500

# --- Study List Endpoints ---
@app.route('/study_list')
def get_study_list():
    if 'user_id' not in session:
        return jsonify([])
    
    with get_db_connection() as conn:
        rows = conn.execute('SELECT word, added_at, note, language FROM study_list WHERE user_id = ? ORDER BY added_at DESC', (session['user_id'],)).fetchall()
    # Always return note and language, even if None
    return jsonify([{'word': row['word'], 'added_at': row['added_at'], 'note': row['note'] if row['note'] is not None else '', 'language': row['language'] if row['language'] is not None else 'english'} for row in rows])

@app.route('/add_to_study_list', methods=['POST'])
def add_to_study_list():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 403
    data = request.get_json()
    words = data.get('words')
    language = data.get('language', 'english').strip()
    
    print(f"Add to study list - User: {session['user_id']}, Words: {words}, Language: {language}")
    
    if words and isinstance(words, list):
        added = 0
        with get_db_connection() as conn:
            for word in words:
                word = word.strip()
                if not word:
                    continue
                try:
                    # Use bulletproof INSERT OR IGNORE (will auto-convert to PostgreSQL syntax)
                    result = conn.execute('INSERT OR IGNORE INTO study_list (user_id, word, language, added_at, note) VALUES (?, ?, ?, CURRENT_TIMESTAMP, NULL)', (session['user_id'], word, language))
                    
                    # Check if word was actually added (PostgreSQL doesn't support total_changes)
                    if hasattr(conn.raw_conn, 'total_changes') and conn.raw_conn.total_changes > 0:
                        added += 1
                        print(f"Successfully added word: {word}")
                    else:
                        # For PostgreSQL, do a count check instead
                        try:
                            count = conn.execute('SELECT COUNT(*) as count FROM study_list WHERE user_id = ? AND word = ?', (session['user_id'], word)).fetchone()
                            if count and count['count'] > 0:
                                # Word exists, might be old or just added
                                print(f"Word in database: {word}")
                                added += 1  # Count as added since we attempted
                        except Exception as count_error:
                            print(f"Error checking word count: {count_error}")
                            added += 1  # Assume it was added
                            
                except Exception as e:
                    print(f"Error adding word '{word}' to study list: {e}")
                    # Continue with other words instead of failing completely
        print(f"Total words added: {added}")
        
        # Update user progress metrics if words were added
        if added > 0:
            update_user_progress(session['user_id'])
            
        return jsonify({'status': 'success', 'added': added})
    
    # Fallback to single word
    word = data.get('word', '').strip()
    if not word:
        return jsonify({'status': 'error', 'message': 'No word provided'}), 400
    try:
        with get_db_connection() as conn:
            # Use bulletproof INSERT OR IGNORE (will auto-convert to PostgreSQL syntax)
            result = conn.execute('INSERT OR IGNORE INTO study_list (user_id, word, language, added_at, note) VALUES (?, ?, ?, CURRENT_TIMESTAMP, NULL)', (session['user_id'], word, language))
            
            print(f"Single word add result - Word: {word}")
            
            # Update user progress metrics (always update to be safe)
            update_user_progress(session['user_id'])
                
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error in add_to_study_list: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/save_study_note', methods=['POST'])
def save_study_note():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 403
    data = request.get_json()
    word = data.get('word', '').strip()
    note = data.get('note', '').strip()
    if not word:
        return jsonify({'status': 'error', 'message': 'No word provided'}), 400
    with get_db_connection() as conn:
        conn.execute('UPDATE study_list SET note = ? WHERE user_id = ? AND word = ?', (note, session['user_id'], word))
        conn.commit()
    return jsonify({'status': 'success'})

@app.route('/remove_from_study_list', methods=['POST'])
def remove_from_study_list():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 403
    data = request.get_json()
    word = data.get('word', '').strip()
    if not word:
        return jsonify({'status': 'error', 'message': 'No word provided'}), 400
    try:
        with get_db_connection() as conn:
            conn.execute('DELETE FROM study_list WHERE user_id = ? AND word = ?', (session['user_id'], word))
            conn.commit()
            
            # Update user progress metrics after word removal
            update_user_progress(session['user_id'])
            
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error in remove_from_study_list: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# --- Progress Stats Endpoint ---
@app.route('/get_progress_stats')
def get_progress_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    try:
        with get_db_connection() as conn:
            print(f"📊 Getting progress stats for user {session['user_id']}")
            
            # Get or create progress record
            progress = conn.execute('SELECT * FROM user_progress WHERE user_id = ?',
                (session['user_id'],)
            ).fetchone()

            if not progress:
                # Initialize progress for new users
                conn.execute(
                    'INSERT INTO user_progress (user_id) VALUES (?)',
                    (session['user_id'],)
                )
                conn.commit()
                progress = conn.execute(
                    'SELECT * FROM user_progress WHERE user_id = ?',
                    (session['user_id'],)
                ).fetchone()

            # Update daily streak
            today = datetime.now().date()
            last_activity = None
            if progress['last_activity_date']:
                try:
                    last_activity = datetime.strptime(progress['last_activity_date'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    last_activity = None
            
            if last_activity:
                days_diff = (today - last_activity).days
                if days_diff == 1:  # Consecutive day
                    new_streak = (progress['daily_streak'] or 0) + 1
                elif days_diff == 0:  # Same day
                    new_streak = progress['daily_streak'] or 1
                else:  # Streak broken
                    new_streak = 1
            else:
                new_streak = 1

            # Calculate additional stats
            try:
                words_learned = conn.execute(
                    'SELECT COUNT(*) as count FROM study_list WHERE user_id = ?',
                    (session['user_id'],)
                ).fetchone()['count']
                print(f"Progress Stats - User {session['user_id']}: Words learned = {words_learned}")
            except Exception as e:
                print(f"Error getting words learned: {e}")
                words_learned = 0

            try:
                conversation_count = conn.execute(
                    'SELECT COUNT(DISTINCT session_id) as count FROM chat_sessions WHERE user_id = ?',
                    (session['user_id'],)
                ).fetchone()['count']
                print(f"Progress Stats - User {session['user_id']}: Conversations = {conversation_count}")
            except Exception as e:
                print(f"Error getting conversation count: {e}")
                conversation_count = 0

            # Calculate accuracy rate from quiz results (using both tables for compatibility)
            total_score = 0
            total_questions = 0
            
            try:
                quiz_stats_enhanced = conn.execute('''
                    SELECT 
                        SUM(score) as total_score,
                        SUM(total) as total_questions
                    FROM quiz_results_enhanced 
                    WHERE user_id = ?
                ''', (session['user_id'],)).fetchone()
                total_score += quiz_stats_enhanced['total_score'] or 0
                total_questions += quiz_stats_enhanced['total_questions'] or 0
            except Exception as e:
                print(f"Error querying quiz_results_enhanced: {e}")

            try:
                quiz_stats_legacy = conn.execute('''
                    SELECT 
                        SUM(score) as total_score,
                        SUM(total) as total_questions
                    FROM quiz_results 
                    WHERE user_id = ?
                ''', (session['user_id'],)).fetchone()
                total_score += quiz_stats_legacy['total_score'] or 0
                total_questions += quiz_stats_legacy['total_questions'] or 0
            except Exception as e:
                print(f"Error querying quiz_results (legacy): {e}")

            accuracy_rate = 0
            if total_questions and total_questions > 0:
                accuracy_rate = (total_score / total_questions) * 100

            # Calculate overall progress percentage (weighted average)
            progress_percentage = min(100, (
                (words_learned * 0.4) +  # 40% weight for words learned
                (conversation_count * 0.3) +  # 30% weight for conversations
                (accuracy_rate * 0.3)  # 30% weight for accuracy
            ))

            # Check for new achievements
            achievements = []
            try:
                if words_learned >= 10 and not conn.execute(
                    'SELECT 1 FROM achievements WHERE user_id = ? AND achievement_type = ?',
                    (session['user_id'], 'words_10')
                ).fetchone():
                    achievements.append({
                        'type': 'words_10',
                        'name': 'Word Collector',
                        'description': 'Learned 10 words'
                    })
                    conn.execute(
                        'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                        (session['user_id'], 'words_10', 'Word Collector', 'Learned 10 words')
                    )

                if new_streak >= 7 and not conn.execute(
                    'SELECT 1 FROM achievements WHERE user_id = ? AND achievement_type = ?',
                    (session['user_id'], 'streak_7')
                ).fetchone():
                    achievements.append({
                        'type': 'streak_7',
                        'name': 'Consistent Learner',
                        'description': '7-day learning streak'
                    })
                    conn.execute(
                        'INSERT INTO achievements (user_id, achievement_type, achievement_name, description) VALUES (?, ?, ?, ?)',
                        (session['user_id'], 'streak_7', 'Consistent Learner', '7-day learning streak')
                    )
            except Exception as e:
                print(f"Error checking/creating achievements: {e}")

            # Update progress record
            try:
                conn.execute('''
                    UPDATE user_progress 
                    SET words_learned = ?,
                        conversation_count = ?,
                        accuracy_rate = ?,
                        daily_streak = ?,
                        last_activity_date = ?,
                        last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (words_learned, conversation_count, accuracy_rate, new_streak, today, session['user_id']))
                conn.commit()
            except Exception as e:
                print(f"Error updating progress record: {e}")

            # Get all achievements with better error handling and column compatibility
            user_achievements = []
            try:
                # First try the full query with all columns
                try:
                    achievements_result = conn.execute('''
                        SELECT achievement_type, achievement_name, description, earned_at
                        FROM achievements
                        WHERE user_id = ?
                        ORDER BY earned_at DESC
                    ''', (session['user_id'],)).fetchall()
                    user_achievements = [dict(achievement) for achievement in achievements_result] if achievements_result else []
                except Exception as column_error:
                    print(f"Full achievement query failed: {column_error}")
                    # Fallback to basic query with only achievement_type and earned_at
                    try:
                        achievements_result = conn.execute('''
                            SELECT achievement_type, earned_at
                            FROM achievements
                            WHERE user_id = ?
                            ORDER BY earned_at DESC
                        ''', (session['user_id'],)).fetchall()
                        # Convert to full format with default values
                        user_achievements = []
                        for achievement in achievements_result:
                            ach_dict = dict(achievement)
                            ach_dict['achievement_name'] = ach_dict.get('achievement_type', 'Unknown Achievement')
                            ach_dict['description'] = f"Achievement: {ach_dict.get('achievement_type', 'Unknown')}"
                            user_achievements.append(ach_dict)
                    except Exception as fallback_error:
                        print(f"Fallback achievement query also failed: {fallback_error}")
                        user_achievements = []
                
                print(f"📈 Retrieved {len(user_achievements)} achievements for user {session['user_id']}")
            except Exception as e:
                print(f"Error getting user achievements: {e}")
                user_achievements = []

            return jsonify({
                'words_learned': words_learned or 0,
                'conversation_count': conversation_count or 0,
                'accuracy_rate': round(accuracy_rate or 0, 1),
                'progress_percentage': round(progress_percentage or 0, 1),
                'daily_streak': new_streak or 0,
                'new_achievements': achievements or [],
                'achievements': user_achievements
            })

    except Exception as e:
        print(f"Error getting progress stats: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Error calculating progress'}), 500

# --- Pronunciation Check Endpoint ---
@app.route('/check_pronunciation', methods=['POST'])
def check_pronunciation():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    data = request.get_json()
    expected = data.get('expected', '').strip()
    spoken = data.get('spoken', '').strip()
    language = data.get('language', 'english')
    if not expected or not spoken:
        return jsonify({'similarity': 0, 'feedback': 'Missing input.'}), 400
    # Compute similarity (case-insensitive, ignore punctuation)
    def normalize(s):
        import re
        return re.sub(r'[^\w\s]', '', s).lower()
    expected_norm = normalize(expected)
    spoken_norm = normalize(spoken)
    similarity = difflib.SequenceMatcher(None, expected_norm, spoken_norm).ratio()
    similarity_pct = int(round(similarity * 100))
    # Feedback message
    if similarity_pct > 90:
        feedback = '✅ Excellent! Your pronunciation is very close.'
    elif similarity_pct > 75:
        feedback = '👍 Good! Minor differences detected.'
    elif similarity_pct > 50:
        feedback = '🙂 Not bad, but try again for better accuracy.'
    else:
        feedback = '❌ Quite different. Listen and try to match the phrase.'
    return jsonify({'similarity': similarity_pct, 'feedback': feedback})

# --- Flashcards Endpoints ---
@app.route('/flashcards')
def flashcards():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('flashcards.html', username=session.get('username', 'User'))

@app.route('/get_flashcards/<language>')
def get_flashcards(language):
    if 'username' not in session:
        return jsonify({'error': 'Please log in to access flashcards'}), 401
    
    # Map frontend language value to database value
    language_map = {
        'english': 'English',
        'spanish': 'Spanish',
        'french': 'French',
        'chinese': 'Chinese',
        'tamil': 'Tamil',
        'malay': 'Malay',
        'portuguese': 'Portuguese',
    }
    db_language = language_map.get(language.lower(), language)
    flashcards = []
    
    print(f"🔍 Flashcards request for language: {language} -> {db_language}")
    
    try:
        with get_db_connection() as conn:
            # Check total questions available
            result = conn.execute("SELECT COUNT(*) as count FROM quiz_questions WHERE language = ?", (db_language,)).fetchone()
            total_questions = result['count'] if result else 0
            print(f"📊 Total questions for {db_language}: {total_questions}")
            
            if total_questions == 0:
                print(f"⚠️ No questions found for language: {db_language}")
                available_languages = conn.execute("SELECT DISTINCT language FROM quiz_questions").fetchall()
                available_langs = [lang['language'] for lang in available_languages]
                print(f"Available languages: {available_langs}")
                return jsonify({'message': f'No flashcards available for {db_language}. Available languages: {", ".join(available_langs)}'})
            
            # Strictly select 50 random questions for the selected language only
            questions = conn.execute("""
                SELECT question, options, answer, question_type, points 
                FROM quiz_questions 
                WHERE language = ? 
                ORDER BY RANDOM() 
                LIMIT 50
            """, (db_language,)).fetchall()
            
            print(f"🎯 Retrieved {len(questions)} questions from database")
            
            for q in questions:
                question_text = q['question']
                answer = q['answer']
                
                # Parse options from JSON or handle different formats
                options = []
                question_type = q['question_type'] if 'question_type' in q.keys() else 'multiple_choice'
                
                try:
                    if q['options']:
                        options_data = json.loads(q['options'])
                        
                        # Handle Word Matching questions
                        if question_type == 'word_matching':
                            if isinstance(options_data, dict) and 'pairs' in options_data:
                                pairs = options_data['pairs']
                                options = []
                                correct_pairs = []
                                for pair in pairs:
                                    if isinstance(pair, dict) and 'key' in pair and 'value' in pair:
                                        options.extend([pair['key'], pair['value']])
                                        correct_pairs.append(f"{pair['key']} ↔ {pair['value']}")
                                # Limit answer length for better display
                                answer = '\n'.join(correct_pairs[:3])  # Show max 3 pairs
                                if len(correct_pairs) > 3:
                                    answer += f"\n... and {len(correct_pairs)-3} more pairs"
                            elif isinstance(options_data, list):
                                options = []
                                correct_pairs = []
                                for pair in options_data:
                                    if isinstance(pair, list) and len(pair) >= 2:
                                        options.extend([pair[0], pair[1]])
                                        correct_pairs.append(f"{pair[0]} ↔ {pair[1]}")
                                # Limit answer length for better display
                                answer = '\n'.join(correct_pairs[:3])  # Show max 3 pairs
                                if len(correct_pairs) > 3:
                                    answer += f"\n... and {len(correct_pairs)-3} more pairs"
                            else:
                                options = list(options_data.values()) if options_data else []
                        elif isinstance(options_data, dict):
                            if 'options' in options_data:
                                options = options_data['options']
                            elif isinstance(options_data, dict) and len(options_data) > 0:
                                options = list(options_data.values())
                        elif isinstance(options_data, list):
                            options = options_data
                        else:
                            options = str(q['options']).split(';')
                except (json.JSONDecodeError, TypeError):
                    if q['options']:
                        options = [opt.strip() for opt in str(q['options']).split(';') if opt.strip()]
                
                # Only include questions that have valid data
                if question_text and answer and options:
                    flashcards.append({
                        'question': question_text,
                        'options': [opt.strip() for opt in options if opt.strip()],
                        'answer': answer.strip(),
                        'type': q['question_type'] if 'question_type' in q.keys() else 'multiple_choice',
                        'points': q['points'] if 'points' in q.keys() else 10
                    })
                    
    except Exception as e:
        print(f'❌ Error reading flashcards for {language} from database: {e}')
        print(f'Exception type: {type(e).__name__}')
        import traceback
        print(f'Full traceback: {traceback.format_exc()}')
        return jsonify({'error': 'Error loading flashcards. Please contact administrator.'}), 500
    
    # If no flashcards found, return helpful message
    if not flashcards:
        print(f"⚠️ No flashcards created for {language}, even though questions exist")
        return jsonify({'message': f'No flashcards available for {language}. Admin can add questions via the admin dashboard.'})
    
    print(f"✅ Successfully created {len(flashcards)} flashcards for {language}")
    return jsonify(flashcards)

# --- Account Management Endpoints ---
@app.route('/deactivate_account', methods=['POST'])
def deactivate_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get the deactivation reason from the form
    deactivation_reason = request.form.get('deactivation_reason', '').strip()
    
    if not deactivation_reason:
        flash('Please provide a reason for deactivation.', 'error')
        return redirect(url_for('settings'))
    
    try:
        with get_db_connection() as conn:
            # Deactivate the account
            conn.execute(
                "UPDATE users SET is_active = 0 WHERE id = ?",
                (session['user_id'],)
            )
            
            # Store the deactivation reason in account_activity table
            conn.execute(
                "INSERT INTO account_activity (user_id, activity_type, details) VALUES (?, ?, ?)",
                (session['user_id'], 'deactivation', deactivation_reason)
            )
            
            conn.commit()
            
            # Add notification
            add_notification(
                session['user_id'],
                "Your account has been deactivated. You can reactivate it at any time."
            )
            
            flash('Your account has been deactivated. You have been logged out.', 'info')
            session.clear()
            return redirect(url_for('login'))
            
    except Exception as e:
        flash(f'Error deactivating account: {str(e)}', 'error')
        return redirect(url_for('settings'))

@app.route('/reactivate_account', methods=['GET', 'POST'])
def reactivate_account():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        security_answer = request.form.get('security_answer')
        reason = request.form.get('reason')
        if not all([email, password, security_answer, reason]):
            flash('All fields are required', 'error')
            return redirect(url_for('reactivate_account'))
        try:
            with get_db_connection() as conn:
                user = conn.execute(
                    "SELECT * FROM users WHERE email = ? AND is_active = 0",
                    (email,)
                ).fetchone()
                if not user:
                    flash('No deactivated account found with this email', 'error')
                    return redirect(url_for('reactivate_account'))
                if not (check_password_hash(user['password'], password) and user['security_answer'] == security_answer):
                    flash('Invalid credentials', 'error')
                    return redirect(url_for('reactivate_account'))
                conn.execute(
                    "UPDATE users SET is_active = 1 WHERE email = ?",
                    (email,)
                )
                conn.commit()
                add_notification(
                    user['id'],
                    "Your account has been reactivated. Welcome back!"
                )
                conn.execute(
                    "INSERT INTO account_activity (user_id, activity_type, details) VALUES (?, ?, ?)",
                    (user['id'], 'reactivation', reason)
                )
                conn.commit()
                flash('Your account has been reactivated successfully!', 'success')
                return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error reactivating account: {str(e)}', 'error')
            return redirect(url_for('reactivate_account'))
    return render_template('reactivate_account.html')

# --- BLIP Image Captioning Route ---
@app.route('/blip_caption', methods=['POST'])
def blip_caption():
    if 'username' not in session:
        return jsonify({'error': 'Please log in to use image captioning'}), 401
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    image_file = request.files['image']
    try:
        from PIL import Image
        from transformers import BlipProcessor, BlipForConditionalGeneration
        
        # Load BLIP model and processor
        processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        # Process the image
        image = Image.open(image_file).convert('RGB')
        inputs = processor(image, return_tensors="pt")
        
        # Generate caption
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        
        return jsonify({'caption': caption})
    except Exception as e:
        print(f"BLIP image captioning error: {e}")
        return jsonify({'error': 'BLIP image captioning failed. Please ensure all dependencies are installed.'}), 500

@app.route('/close_account', methods=['POST'])
def close_account():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    close_reason = request.form.get('close_reason', '').strip()
    if not close_reason:
        flash('Please provide a reason for closing your account.', 'error')
        return redirect(url_for('settings'))
    user_id = session['user_id']
    try:
        with get_db_connection() as conn:
            # Log the closure reason before deleting
            conn.execute(
                "INSERT INTO account_activity (user_id, activity_type, details) VALUES (?, ?, ?)",
                (user_id, 'closure', close_reason)
            )
            # Delete all user-related data (order matters due to FKs)
            conn.execute("DELETE FROM chat_messages WHERE session_id IN (SELECT session_id FROM chat_sessions WHERE user_id = ?)", (user_id,))
            conn.execute("DELETE FROM chat_sessions WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM notifications WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM achievements WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM user_progress WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM study_list WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM quiz_results WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM quiz_results_enhanced WHERE user_id = ?", (user_id,))
            conn.execute("DELETE FROM account_activity WHERE user_id = ? AND activity_type != 'closure'", (user_id,))
            # Finally, delete the user
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
        session.clear()
        flash('Your account and all data have been permanently deleted.', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error closing account: {str(e)}', 'error')
        return redirect(url_for('settings'))

@app.route('/examples')
def examples():
    """Show example screenshots of the website"""
    return render_template('examples.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        with get_db_connection() as conn:
            # Test database connectivity
            user_count = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
            question_count = conn.execute("SELECT COUNT(*) as count FROM quiz_questions").fetchone()['count']
            admin_count = conn.execute("SELECT COUNT(*) as count FROM users WHERE is_admin = 1").fetchone()['count']
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'database': 'connected',
                'users': user_count,
                'quiz_questions': question_count,
                'admins': admin_count
            })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'error',
            'error': str(e)
        }), 500

@app.route('/debug/database')
def debug_database():
    """Debug endpoint to check database status"""
    try:
        with get_db_connection() as conn:
            # Get all tables
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [table['name'] for table in tables]
            
            # Get admin users
            admins = conn.execute("SELECT id, username, email, is_admin FROM users WHERE is_admin = 1").fetchall()
            admin_list = [{'id': a['id'], 'username': a['username'], 'email': a['email']} for a in admins]
            
            # Get question counts by language
            language_counts = conn.execute("""
                SELECT language, COUNT(*) as count 
                FROM quiz_questions 
                GROUP BY language
            """).fetchall()
            
            return jsonify({
                'tables': table_names,
                'admins': admin_list,
                'question_counts': [{'language': lc['language'], 'count': lc['count']} for lc in language_counts],
                'total_questions': conn.execute("SELECT COUNT(*) as count FROM quiz_questions").fetchone()['count'],
                'total_users': conn.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug/database/detailed')
def debug_database_detailed():
    """Detailed debug endpoint with file system and database path info"""
    try:
        # Environment and file system info
        env_info = {
            'RENDER': os.getenv('RENDER'),
            'RENDER_SERVICE_ID': os.getenv('RENDER_SERVICE_ID'),
            'cwd': os.getcwd(),
            '/data_exists': os.path.exists('/data'),
            '/data_readable': os.access('/data', os.R_OK) if os.path.exists('/data') else False,
            '/data_writable': None,
            '/data_executable': os.access('/data', os.X_OK) if os.path.exists('/data') else False,
            'database_path': None,
            'database_exists': None,
            'database_size': None
        }
        
        # Test /data writability
        try:
            test_file = '/data/test_debug.tmp'
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            env_info['/data_writable'] = True
        except Exception as e:
            env_info['/data_writable'] = f"Error: {e}"
        
        # Get database path info (without connecting)
        is_render = os.getenv('RENDER') is not None or os.getenv('RENDER_SERVICE_ID') is not None
        
        if is_render and os.path.exists('/data') and os.access('/data', os.W_OK):
            db_path = '/data/database.db'
        else:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
        
        env_info['database_path'] = db_path
        env_info['database_exists'] = os.path.exists(db_path)
        env_info['database_size'] = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        
        # Now connect and get database info
        conn = get_db_connection()
        try:
            from database_config import get_database_config
            db_type, _ = get_database_config()
            
            if db_type == 'postgresql':
                cursor = conn.cursor()
                
                # Get table info for PostgreSQL
                cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
                tables = cursor.fetchall()
                table_names = [table['tablename'] for table in tables]
                
                # Get user count and recent users
                cursor.execute("SELECT COUNT(*) as count FROM users")
                user_count = cursor.fetchone()['count']
                
                cursor.execute("SELECT id, username, email FROM users ORDER BY id DESC LIMIT 5")
                recent_users = cursor.fetchall()
                recent_user_list = [{'id': u['id'], 'username': u['username'], 'email': u['email']} for u in recent_users]
                
                # Get question counts by language
                cursor.execute("SELECT language, COUNT(*) as count FROM quiz_questions GROUP BY language ORDER BY language")
                question_counts = cursor.fetchall()
                question_data = [{'language': q['language'], 'count': q['count']} for q in question_counts]
                
                # Total questions
                cursor.execute("SELECT COUNT(*) as count FROM quiz_questions")
                total_questions = cursor.fetchone()['count']
                
            else:
                # SQLite handling
                tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                table_names = [table[0] for table in tables]
                
                user_count = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
                recent_users = conn.execute("SELECT id, username, email FROM users ORDER BY id DESC LIMIT 5").fetchall()
                recent_user_list = [{'id': u['id'], 'username': u['username'], 'email': u['email']} for u in recent_users]
                
                question_counts = conn.execute("SELECT language, COUNT(*) as count FROM quiz_questions GROUP BY language ORDER BY language").fetchall()
                question_data = [{'language': q[0], 'count': q[1]} for q in question_counts]
                
                total_questions = conn.execute("SELECT COUNT(*) as count FROM quiz_questions").fetchone()['count']
            
            return jsonify({
                'environment': env_info,
                'database': {
                    'type': db_type,
                    'tables': table_names,
                    'total_users': user_count,
                    'recent_users': recent_user_list,
                    'question_counts': question_data,
                    'total_questions': total_questions
                }
            })
        finally:
            if hasattr(conn, 'close'):
                conn.close()
    except Exception as e:
        return jsonify({'error': str(e), 'environment': env_info if 'env_info' in locals() else 'Failed to get env info'}), 500

@app.route('/debug/database/connection')
def debug_database_connection():
    """Debug database connection setup"""
    try:
        # Check environment variables
        database_url = os.getenv('DATABASE_URL')
        render_env = os.getenv('RENDER')
        render_service = os.getenv('RENDER_SERVICE_ID')
        
        debug_info = {
            'environment_variables': {
                'DATABASE_URL': 'SET' if database_url else 'NOT SET',
                'DATABASE_URL_preview': database_url[:20] + '...' if database_url else None,
                'RENDER': render_env,
                'RENDER_SERVICE_ID': render_service
            },
            'database_config_import': None,
            'connection_test': None
        }
        
        # Test database_config import
        try:
            from database_config import get_database_config
            db_type, config = get_database_config()
            debug_info['database_config_import'] = 'SUCCESS'
            debug_info['detected_db_type'] = db_type
            debug_info['config_preview'] = str(config)[:100] + '...' if len(str(config)) > 100 else str(config)
        except Exception as e:
            debug_info['database_config_import'] = f'FAILED: {e}'
        
        # Test actual connection
        try:
            from database_config import get_db_connection, safe_dict_get, execute_safe_query, safe_function_call, get_safe_db_connection as get_configured_connection
            conn = get_configured_connection()
            db_type = conn.db_type if hasattr(conn, 'db_type') else 'unknown'
            debug_info['connection_test'] = f'SUCCESS - {db_type}'
            conn.close()
        except Exception as e:
            debug_info['connection_test'] = f'FAILED: {e}'
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug/env/check')
def debug_env_check():
    """Check environment variables and PostgreSQL setup"""
    try:
        database_url = os.getenv('DATABASE_URL')
        
        env_check = {
            'database_url_set': bool(database_url),
            'database_url_length': len(database_url) if database_url else 0,
            'database_url_starts_with': database_url[:20] if database_url else None,
            'render_env': os.getenv('RENDER'),
            'render_service_id': os.getenv('RENDER_SERVICE_ID'),
            'port': os.getenv('PORT'),
            'postgresql_test': None
        }
        
        # Test PostgreSQL connection specifically
        if database_url:
            try:
                import psycopg2
                from urllib.parse import urlparse
                parsed = urlparse(database_url)
                
                # Test connection
                test_conn = psycopg2.connect(
                    host=parsed.hostname,
                    port=parsed.port or 5432,
                    database=parsed.path[1:],
                    user=parsed.username,
                    password=parsed.password
                )
                test_conn.close()
                env_check['postgresql_test'] = 'SUCCESS'
            except Exception as pg_error:
                env_check['postgresql_test'] = f'FAILED: {pg_error}'
        else:
            env_check['postgresql_test'] = 'NO DATABASE_URL SET'
        
        return jsonify(env_check)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug/render/config')
def debug_render_config():
    """Check Render persistent storage configuration"""
    try:
        is_render = os.getenv('RENDER') is not None or os.getenv('RENDER_SERVICE_ID') is not None
        
        config_check = {
            'render_detected': is_render,
            'data_directory': {
                'exists': os.path.exists('/data'),
                'is_directory': os.path.isdir('/data') if os.path.exists('/data') else False,
                'readable': os.access('/data', os.R_OK) if os.path.exists('/data') else False,
                'writable': os.access('/data', os.W_OK) if os.path.exists('/data') else False,
                'executable': os.access('/data', os.X_OK) if os.path.exists('/data') else False,
            },
            'database_location': None,
            'recommendations': []
        }
        
        # Determine database location
        if is_render and os.path.exists('/data') and os.access('/data', os.W_OK):
            config_check['database_location'] = '/data/database.db (PERSISTENT)'
            config_check['recommendations'].append("✅ SUCCESS: Persistent storage is configured correctly!")
        elif is_render:
            config_check['database_location'] = 'local/ephemeral (DATA WILL BE LOST)'
            if not os.path.exists('/data'):
                config_check['recommendations'].append(
                    "🚨 CRITICAL: /data directory doesn't exist. Add persistent disk in Render dashboard."
                )
            elif not os.access('/data', os.W_OK):
                config_check['recommendations'].append(
                    "🚨 CRITICAL: /data directory exists but is not writable. Check disk permissions."
                )
        else:
            config_check['database_location'] = 'local development'
            config_check['recommendations'].append("ℹ️ INFO: Running locally - persistent storage not needed.")
        
        # Test write if possible
        write_test = None
        if os.path.exists('/data'):
            try:
                test_file = '/data/test_config.tmp'
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                write_test = "SUCCESS"
            except Exception as e:
                write_test = f"FAILED: {e}"
        
        config_check['write_test'] = write_test
        
        # Add instructions if there's a problem
        if is_render and (not os.path.exists('/data') or not os.access('/data', os.W_OK)):
            config_check['instructions'] = {
                'steps': [
                    "1. Go to your Render Dashboard",
                    "2. Navigate to your service",
                    "3. Go to Settings tab",
                    "4. Scroll to 'Disks' section",
                    "5. Click 'Add Disk' if no disk exists",
                    "6. Configure: Name=sqlite-data, Mount Path=/data, Size=1GB",
                    "7. Save and redeploy your service"
                ],
                'yaml_config': "disk:\n  name: sqlite-data\n  mountPath: /data\n  sizeGB: 1"
            }
        
        return jsonify(config_check)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug/create_admin')
def debug_create_admin():
    """Debug endpoint to force create admin user"""
    try:
        with get_db_connection() as conn:
            from werkzeug.security import generate_password_hash
            
            # Check if admin exists
            admin_check = conn.execute("SELECT * FROM users WHERE email = ?", ('admin@example.com',)).fetchone()
            
            if admin_check:
                # Update existing user to be admin
                conn.execute("UPDATE users SET is_admin = 1 WHERE email = ?", ('admin@example.com',))
                conn.commit()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Admin privileges granted to existing user',
                    'user_id': admin_check['id'],
                    'username': admin_check['username'],
                    'email': 'admin@example.com',
                    'credentials': 'admin@example.com / admin123'
                })
            else:
                # Create new admin user
                conn.execute('''
                    INSERT INTO users (username, email, password, security_answer, is_admin)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    'admin',
                    'admin@example.com',
                    generate_password_hash('admin123'),
                    generate_password_hash('admin'),
                    1
                ))
                conn.commit()
                
                # Get the newly created user
                new_admin = conn.execute("SELECT * FROM users WHERE email = ?", ('admin@example.com',)).fetchone()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Admin user created successfully',
                    'user_id': new_admin['id'],
                    'username': new_admin['username'],
                    'email': 'admin@example.com',
                    'credentials': 'admin@example.com / admin123'
                })
                
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

# Initialize database on startup - handled in get_db_connection()
print("✅ Database initialization handled by connection setup")

# Add model caching variables
_blip_processor = None
_blip_model = None

def monitor_memory(stage_name):
    """Monitor memory usage for debugging on Render free tier"""
    try:
        if not PSUTIL_AVAILABLE or psutil is None:
            print(f"📊 Memory monitoring not available (psutil not installed)")
            return
            
        process = psutil.Process()  # type: ignore
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        print(f"🧠 Memory usage at {stage_name}: {memory_mb:.1f} MB")
        
        # Warn if approaching Render free tier limits (~512MB)
        if memory_mb > 400:
            print(f"⚠️ High memory usage detected: {memory_mb:.1f} MB")
            
    except Exception as e:
        print(f"❌ Memory monitoring error: {e}")

def optimize_for_render_free_tier():
    """Apply memory optimizations for Render's free tier"""
    try:
        import gc
        gc.collect()  # Force garbage collection
        
        # Set lower limits for image processing
        return {
            'max_image_size': (512, 512),  # Smaller images for free tier
            'cleanup_files': True,         # Always cleanup uploaded files
            'aggressive_gc': True          # More frequent garbage collection
        }
    except Exception as e:
        print(f"Error applying optimizations: {e}")
        return {
            'max_image_size': (800, 800),
            'cleanup_files': False,
            'aggressive_gc': False
        }

def get_cached_blip_models():
    """Load and cache BLIP models to avoid reloading on each request"""
    global _blip_processor, _blip_model
    
    if _blip_processor is None or _blip_model is None:
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            print("Loading BLIP models (this may take a moment on first use)...")
            
            # Use a smaller, more memory-efficient model for Render free tier
            model_name = "Salesforce/blip-image-captioning-base"
            _blip_processor = BlipProcessor.from_pretrained(model_name)
            _blip_model = BlipForConditionalGeneration.from_pretrained(model_name)
            
            # Move model to eval mode to save memory
            _blip_model.eval()
            
            print("BLIP models loaded and cached successfully")
            
            # Force garbage collection after model loading
            import gc
            gc.collect()
            
        except Exception as e:
            print(f"Error loading BLIP models: {e}")
            # Don't cache failed models
            _blip_processor = None
            _blip_model = None
            raise e
    
    return _blip_processor, _blip_model

def get_simple_image_description(file_path):
    """Provide a simple fallback image description when all AI models fail"""
    try:
        from PIL import Image
        with Image.open(file_path) as img:
            width, height = img.size
            format_name = img.format or "Unknown"
            mode = img.mode
            
            # Basic image properties
            description = f"This is a {format_name.lower()} image with dimensions {width}x{height} pixels in {mode} color mode."
            
            # Add some basic analysis
            if width > height:
                orientation = "landscape"
            elif height > width:
                orientation = "portrait"
            else:
                orientation = "square"
            
            description += f" The image has a {orientation} orientation."
            
            return description
    except Exception as e:
        return f"An image file was uploaded, but detailed analysis is currently unavailable. Error: {str(e)}"

@app.route('/debug/database/critical', methods=['GET'])
def debug_database_critical():
    """Critical debug endpoint to identify database switching issues"""
    try:
        results = {
            'timestamp': datetime.now().isoformat(),
            'environment': {
                'DATABASE_URL_exists': 'DATABASE_URL' in os.environ,
                'DATABASE_URL_preview': os.getenv('DATABASE_URL', 'NOT SET')[:30] + '...' if os.getenv('DATABASE_URL') else 'NOT SET'
            },
            'database_checks': []
        }
        
        # Test multiple database connections to see if they're consistent
        for i in range(3):
            try:
                with get_db_connection() as conn:
                    db_type = getattr(conn, 'db_type', 'unknown')
                    
                    # Check user data
                    user_count = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
                    question_count = conn.execute("SELECT COUNT(*) as count FROM quiz_questions").fetchone()['count']
                    study_list_count = conn.execute("SELECT COUNT(*) as count FROM study_list").fetchone()['count']
                    
                    # Get specific user data if session exists
                    user_data = None
                    if session.get('user_id'):
                        user = conn.execute("SELECT avatar, name, email FROM users WHERE id = ?", (session['user_id'],)).fetchone()
                        user_study_count = conn.execute("SELECT COUNT(*) as count FROM study_list WHERE user_id = ?", (session['user_id'],)).fetchone()['count']
                        user_data = {
                            'avatar': user['avatar'] if user else None,
                            'name': user['name'] if user else None,
                            'email': user['email'] if user else None,
                            'study_list_count': user_study_count
                        }
                    
                    results['database_checks'].append({
                        'connection_attempt': i + 1,
                        'db_type': db_type,
                        'total_users': user_count,
                        'total_questions': question_count,
                        'total_study_items': study_list_count,
                        'current_user_data': user_data
                    })
                    
            except Exception as e:
                results['database_checks'].append({
                    'connection_attempt': i + 1,
                    'error': str(e)
                })
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def check_database_consistency():
    """
    Critical function to ensure database consistency and prevent data loss
    """
    try:
        with get_db_connection() as conn:
            db_type = getattr(conn, 'db_type', 'unknown')
            
            # Log current database type
            print(f"🔍 Database consistency check: Using {db_type}")
            
            # In production with DATABASE_URL, must use PostgreSQL
            if os.getenv('DATABASE_URL'):
                if db_type != 'postgresql':
                    error_msg = f"🚨 CRITICAL: Production environment but using {db_type} instead of PostgreSQL!"
                    print(error_msg)
                    raise Exception(error_msg)
                else:
                    print("✅ Production database check passed: Using PostgreSQL")
            else:
                print(f"ℹ️ Development environment: Using {db_type}")
            
            return db_type
    except Exception as e:
        print(f"❌ Database consistency check failed: {e}")
        raise

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=os.environ.get('FLASK_ENV') != 'production', host='0.0.0.0', port=port)