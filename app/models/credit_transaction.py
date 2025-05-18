from app import db
from datetime import datetime

class CreditTransaction(db.Model):
    __tablename__ = 'credit_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Can be positive (earning) or negative (spending)
    transaction_type = db.Column(db.String(50), nullable=False)  # 'upload', 'download', 'initial', 'purchase', 'gift_sent', 'gift_received'
    description = db.Column(db.String(200))
    payment_id = db.Column(db.String(100))  # Payment gateway transaction ID
    payment_amount = db.Column(db.Float)    # Amount paid in rupees
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys for related entities
    related_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'))

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='credit_transactions')
    related_user = db.relationship('User', foreign_keys=[related_user_id])
    note = db.relationship('Note', backref='credit_transactions')

    def __repr__(self):
        return f'<CreditTransaction {self.id}: {self.transaction_type}>' 