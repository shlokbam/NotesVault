from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import string
from sqlalchemy.orm import validates

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    college = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128))
    credits = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6))
    verification_code_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    uploaded_notes = db.relationship('Note', backref=db.backref('uploader', lazy=True), lazy='dynamic')
    viewed_notes = db.relationship('NoteView', backref=db.backref('viewer', lazy=True), lazy='dynamic')

    @validates('email')
    def validate_email(self, key, email):
        if not email.endswith('vit.edu'):
            raise ValueError('Only VIT email addresses are allowed')
        return email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_credits(self, amount, transaction_type, description, related_user=None, note=None):
        """Add credits and record the transaction."""
        self.credits += amount
        from app.models.credit_transaction import CreditTransaction
        transaction = CreditTransaction(
            user_id=self.id,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            related_user_id=related_user.id if related_user else None,
            note_id=note.id if note else None
        )
        db.session.add(transaction)
        db.session.commit()

    def use_credits(self, amount, transaction_type, description, note=None):
        """Use credits and record the transaction."""
        if self.credits >= amount:
            self.credits -= amount
            from app.models.credit_transaction import CreditTransaction
            transaction = CreditTransaction(
                user_id=self.id,
                amount=-amount,  # Negative amount for spending
                transaction_type=transaction_type,
                description=description,
                note_id=note.id if note else None
            )
            db.session.add(transaction)
            db.session.commit()
            return True
        return False

    def generate_verification_code(self):
        """Generate a 6-digit verification code and set expiration time."""
        self.verification_code = ''.join(random.choices(string.digits, k=6))
        self.verification_code_expires = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()

    def verify_email(self, code):
        """Verify the email with the provided code."""
        if (self.verification_code == code and 
            self.verification_code_expires > datetime.utcnow()):
            self.is_verified = True
            self.verification_code = None
            self.verification_code_expires = None
            db.session.commit()
            return True
        return False

    def __repr__(self):
        return f'<User {self.id}: {self.email}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 