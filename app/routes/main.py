from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.note import Note
from app.models.note_view import NoteView

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    recent_notes = Note.query.order_by(Note.upload_date.desc()).limit(6).all()
    return render_template('main/index.html', recent_notes=recent_notes)

@bp.route('/dashboard')
@login_required
def dashboard():
    user_notes = Note.query.filter_by(uploader_id=current_user.id).count()
    viewed_notes = current_user.viewed_notes.count()
    total_credits = current_user.credits
    
    recent_uploads = Note.query.filter_by(uploader_id=current_user.id)\
        .order_by(Note.upload_date.desc()).limit(5).all()
    
    recent_views = current_user.viewed_notes\
        .order_by(NoteView.view_date.desc()).limit(5).all()
    
    return render_template('main/dashboard.html',
                         user_notes=user_notes,
                         viewed_notes=viewed_notes,
                         total_credits=total_credits,
                         recent_uploads=recent_uploads,
                         recent_views=recent_views) 