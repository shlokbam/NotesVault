from app import db
from datetime import datetime

class CreditTransaction(db.Model):
    __tablename__ = 'credit_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Positive for credits added, negative for credits spent
    transaction_type = db.Column(db.String(50), nullable=False)  # 'upload', 'view', 'gift_sent', 'gift_received', 'initial'
    description = db.Column(db.String(200), nullable=False)
    related_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # For gift transactions
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=True)  # For upload/view transactions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('credit_transactions', lazy='dynamic'))
    related_user = db.relationship('User', foreign_keys=[related_user_id])
    note = db.relationship('Note', backref='credit_transactions')

    def __repr__(self):
        return f'<CreditTransaction {self.id}: {self.transaction_type} {self.amount}>' 