from app import db
from datetime import datetime

class NoteView(db.Model):
    __tablename__ = 'note_view'

    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    viewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    view_date = db.Column(db.DateTime, default=datetime.utcnow)
    credits_spent = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<NoteView {self.id}: Note {self.note_id} viewed by User {self.viewer_id}>' 