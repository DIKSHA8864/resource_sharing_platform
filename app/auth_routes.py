from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .forms import RegisterForm, LoginForm, ForgotPasswordForm
from .models import User, db

auth = Blueprint('auth', __name__)

# ---------- REGISTER ----------
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('auth.login'))

        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_pw,
            role=form.role.data  # assuming role is part of the form
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


# ---------- LOGIN ----------
@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Query only by email
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            session['role'] = user.role  # Store role in session

            flash('Login successful!', 'success')

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            # Redirect by role
            if user.role == 'teacher':
                return redirect(url_for('main.teacher_dashboard'))
            elif user.role == 'student':
                return redirect(url_for('main.student_dashboard'))
            else:
                return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials or role mismatch.', 'danger')

    return render_template('login.html', form=form)


# ---------- LOGOUT ----------
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.home'))


# ---------- FORGOT PASSWORD ----------
@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            # Simulate password reset (you could email a link here)
            flash('Password reset link sent to your email (simulated).', 'info')
        else:
            flash('Email address not found.', 'danger')

        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html', form=form)
