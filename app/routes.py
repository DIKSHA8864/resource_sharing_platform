from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .forms import UploadForm
from .models import Resource, db

main = Blueprint('main', __name__)

# ---------- HOME ----------

@main.route('/')
def home():
    search = request.args.get('search')
    subject = request.args.get('subject')
    page = request.args.get('page', 1, type=int)

    subjects = ['Machine Learning Techniques', 'COI', 'Data Analytics', 'Software Project Management', 'Computer Network']

    query = Resource.query

    if search:
        query = query.filter(Resource.title.ilike(f'%{search}%'))
    if subject:
        query = query.filter(Resource.subject == subject)

    pagination = query.order_by(Resource.id.desc()).paginate(page=page, per_page=6)

    return render_template('home.html', 
                           resources=pagination.items,
                           pagination=pagination,
                           subjects=subjects,
                           search=search,
                           selected_subject=subject)

# ---------- GENERAL DASHBOARD (optional fallback) ----------
@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'student':
        return redirect(url_for('main.student_dashboard'))
    elif current_user.role == 'teacher':
        return redirect(url_for('main.teacher_dashboard'))
    else:
        flash('Access denied: Unknown role', 'danger')
        return redirect(url_for('main.home'))

# ---------- STUDENT DASHBOARD ----------
@main.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied: Only students allowed.', 'danger')
        return redirect(url_for('main.home'))

    resources = Resource.query.filter_by(user_id=current_user.id).all()
    return render_template('student_dashboard.html', resources=resources)

# ---------- TEACHER DASHBOARD ----------
@main.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('Access denied: Only teachers allowed.', 'danger')
        return redirect(url_for('main.home'))

    resources = Resource.query.order_by(Resource.id.desc()).all()
    return render_template('teacher_dashboard.html', resources=resources)

# ---------- UPLOAD ----------
@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.role != 'teacher':
        flash('Access denied: Only teachers can upload resources.', 'danger')
        return redirect(url_for('main.home'))

    form = UploadForm()

    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)

        # Ensure the upload folder exists
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        # Save the file
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        # Add the resource to the database
        new_resource = Resource(
            title=form.title.data,
            subject=form.subject.data,
            filename=filename,
            user_id=current_user.id
        )
        db.session.add(new_resource)
        db.session.commit()

        flash('File uploaded successfully!', 'success')
        return redirect(url_for('main.teacher_dashboard'))

    return render_template('upload.html', form=form)

# ---------- DOWNLOAD ----------
@main.route('/download/<filename>')
@login_required
def download(filename):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    safe_filename = secure_filename(filename)
    file_path = os.path.join(upload_folder, safe_filename)

    # Check if file exists before attempting to download
    if not os.path.exists(file_path):
        flash("File not found.", "danger")
        return redirect(url_for('main.home'))

    return send_from_directory(upload_folder, safe_filename, as_attachment=True)
