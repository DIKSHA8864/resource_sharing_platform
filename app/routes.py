import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from werkzeug.utils import secure_filename
from app import db
from app.forms import RegisterForm, LoginForm, UploadForm
from app.models import User, Resource
from flask_login import login_user, logout_user, login_required, current_user

main = Blueprint('main', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@main.route('/')
def home():
    resources = Resource.query.all()
    print(f"Fetched {len(resources)} resources from DB")
    for res in resources:
        print(res.title, res.subject, res.filename)
    return render_template('index.html', resources=resources)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('main.register'))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.dashboard'))  # Correct URL reference for dashboard route
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    # Query the resources uploaded by the currently logged-in user
    resources = Resource.query.filter_by(user_id=current_user.id).all()
    # Render the dashboard.html template and pass the resources to it
    return render_template('dashboard.html', resources=resources)

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        resource = Resource(
            title=form.title.data,
            subject=form.subject.data,
            filename=filename,
            user_id=current_user.id
        )
        db.session.add(resource)
        db.session.commit()
        flash('Resource uploaded successfully.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('upload.html', form=form)