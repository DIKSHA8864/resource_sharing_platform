from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from .forms import UploadForm
from .models import Resource, db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/dashboard')
@login_required
def dashboard():
    resources = Resource.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', resources=resources)

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        resource = Resource(title=form.title.data, subject=form.subject.data,
                            filename=filename, user_id=current_user.id)
        db.session.add(resource)
        db.session.commit()
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('upload.html', form=form)

@main.route('/download/<filename>')
@login_required
def download(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
