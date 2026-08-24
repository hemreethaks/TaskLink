from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from datetime import datetime
from models.user import User
from utils.db_logger import log

auth = Blueprint('auth', __name__)

# ─── LOGIN ────────────────────────────────────────────────────────────────────
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if not user:
            flash('No account found with that email.', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('Your account has been deactivated. Contact admin.', 'danger')
            return redirect(url_for('auth.login'))

        if not check_password_hash(user.password_hash, password):
            flash('Incorrect password.', 'danger')
            return redirect(url_for('auth.login'))

        # Store in session
        session['user_id']    = user.user_id
        session['user_name']  = user.name
        session['role']       = user.role
        session['login_time'] = datetime.now().strftime('%I:%M %p')

        log('User logged in')

        # Redirect based on role
        if user.role == 'ADMIN':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'CLIENT':
            return redirect(url_for('client.dashboard'))
        else:
            return redirect(url_for('freelancer.dashboard'))

    return render_template('login.html')


# ─── REGISTER ─────────────────────────────────────────────────────────────────
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role     = request.form.get('role', '')

        # Basic validation
        if not name or not email or not password or role not in ('CLIENT', 'FREELANCER'):
            flash('Please fill all fields correctly.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'danger')
            return redirect(url_for('auth.register'))

        new_user = User(
            name          = name,
            email         = email,
            password_hash = generate_password_hash(password),
            role          = role
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ─── LOGOUT ───────────────────────────────────────────────────────────────────
@auth.route('/logout')
def logout():
    log('User logged out')
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
