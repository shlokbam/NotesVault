from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.note import Note
from app.models.note_view import NoteView
import os
from datetime import datetime

bp = Blueprint('notes', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            note = Note(
                title=request.form.get('title'),
                description=request.form.get('description'),
                subject=request.form.get('subject'),
                semester=int(request.form.get('semester')),
                teacher=request.form.get('teacher'),
                department=request.form.get('department'),
                file_path=filename,
                file_type=filename.rsplit('.', 1)[1].lower(),
                uploader_id=current_user.id
            )
            db.session.add(note)
            current_user.add_credits(
                current_app.config['CREDITS_PER_UPLOAD'],
                'upload',
                f'Earned credits for uploading note: {note.title}',
                note=note
            )

            flash('Note uploaded successfully!', 'success')
            return redirect(url_for('notes.view', note_id=note.id))

    return render_template('notes/upload.html')

@bp.route('/view/<int:note_id>')
@login_required
def view(note_id):
    note = Note.query.get_or_404(note_id)
    
    # If user is viewing their own note, show it directly
    if note.uploader_id == current_user.id:
        return render_template('notes/view.html', note=note)
    
    # For viewing others' notes, check if already viewed
    existing_view = NoteView.query.filter_by(
        note_id=note_id,
        viewer_id=current_user.id
    ).first()

    if existing_view:
        return render_template('notes/view.html', note=note)
    
    # If not viewed before, show confirmation page
    credits_to_view = current_app.config['CREDITS_TO_VIEW']
    return render_template('notes/view_confirm.html', note=note, credits_to_view=credits_to_view)

@bp.route('/view/<int:note_id>/confirm', methods=['POST'])
@login_required
def confirm_view(note_id):
    note = Note.query.get_or_404(note_id)
    
    # Check if user has already viewed this note
    existing_view = NoteView.query.filter_by(
        note_id=note_id,
        viewer_id=current_user.id
    ).first()

    if not existing_view:
        if not current_user.use_credits(
            current_app.config['CREDITS_TO_VIEW'],
            'view',
            f'Spent credits to view note: {note.title}',
            note=note
        ):
            flash('Insufficient credits to view this note.', 'error')
            return redirect(url_for('main.index'))

        view = NoteView(
            note_id=note_id,
            viewer_id=current_user.id,
            credits_spent=current_app.config['CREDITS_TO_VIEW']
        )
        note.views_count += 1
        db.session.add(view)
        db.session.commit()

    return redirect(url_for('notes.view', note_id=note_id))

@bp.route('/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit(note_id):
    note = Note.query.get_or_404(note_id)
    
    # Check if user owns the note
    if note.uploader_id != current_user.id:
        flash('You do not have permission to edit this note.', 'error')
        return redirect(url_for('notes.view', note_id=note_id))

    if request.method == 'POST':
        note.title = request.form.get('title')
        note.description = request.form.get('description')
        note.subject = request.form.get('subject')
        note.semester = int(request.form.get('semester'))
        note.teacher = request.form.get('teacher')
        note.department = request.form.get('department')

        # Handle file upload if a new file is provided
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if file and allowed_file(file.filename):
                # Delete old file
                old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], note.file_path)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

                # Save new file
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                note.file_path = filename
                note.file_type = filename.rsplit('.', 1)[1].lower()

        db.session.commit()
        flash('Note updated successfully!', 'success')
        return redirect(url_for('notes.view', note_id=note.id))

    return render_template('notes/edit.html', note=note)

@bp.route('/delete/<int:note_id>', methods=['POST'])
@login_required
def delete(note_id):
    note = Note.query.get_or_404(note_id)
    
    # Check if user owns the note
    if note.uploader_id != current_user.id:
        flash('You do not have permission to delete this note.', 'error')
        return redirect(url_for('notes.view', note_id=note_id))

    # Delete the file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], note.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete the note
    db.session.delete(note)
    db.session.commit()

    flash('Note deleted successfully!', 'success')
    return redirect(url_for('notes.my_notes'))

@bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    semester = request.args.get('semester')
    department = request.args.get('department')
    subject = request.args.get('subject')

    notes = Note.query

    if query:
        notes = notes.filter(Note.title.ilike(f'%{query}%') | 
                           Note.description.ilike(f'%{query}%'))
    if semester:
        notes = notes.filter_by(semester=semester)
    if department:
        notes = notes.filter_by(department=department)
    if subject:
        notes = notes.filter_by(subject=subject)

    notes = notes.order_by(Note.upload_date.desc()).all()
    return render_template('notes/search.html', notes=notes)

@bp.route('/my-notes')
@login_required
def my_notes():
    notes = Note.query.filter_by(uploader_id=current_user.id).order_by(Note.upload_date.desc()).all()
    return render_template('notes/my_notes.html', notes=notes)

@bp.route('/file/<int:note_id>')
@login_required
def serve_file(note_id):
    note = Note.query.get_or_404(note_id)
    
    # If user is viewing their own note, serve it directly
    if note.uploader_id == current_user.id:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], note.file_path)
        if not os.path.exists(file_path):
            flash('File not found.', 'error')
            return redirect(url_for('notes.view', note_id=note_id))
        return send_file(file_path, as_attachment=False)
    
    # For others' notes, check if they have already viewed it
    existing_view = NoteView.query.filter_by(
        note_id=note_id,
        viewer_id=current_user.id
    ).first()
    
    if not existing_view:
        flash('You need to confirm viewing this note first.', 'error')
        return redirect(url_for('notes.view', note_id=note_id))
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], note.file_path)
    if not os.path.exists(file_path):
        flash('File not found.', 'error')
        return redirect(url_for('notes.view', note_id=note_id))
    
    return send_file(file_path, as_attachment=False) 