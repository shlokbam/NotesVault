from datetime import datetime
from app import db

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Amount in INR
    credits = db.Column(db.Integer, nullable=False)  # Number of credits purchased
    stripe_payment_id = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('payments', lazy=True))
    
    def __repr__(self):
        return f'<Payment {self.id}>' 