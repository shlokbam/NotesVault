from flask import current_app, render_template
from flask_mail import Message
from app import mail

def send_verification_email(user):
    msg = Message(
        'Verify your NotesVault account',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[user.email]
    )
    msg.html = render_template(
        'email/verify_email.html',
        user=user,
        verification_code=user.verification_code
    )
    mail.send(msg)

def send_credit_gift_email(recipient, sender, credit_amount):
    msg = Message(
        'You received a credit gift on NotesVault!',
        sender=current_app.config['MAIL_USERNAME'],
        recipients=[recipient.email]
    )
    msg.html = render_template(
        'email/credit_gift.html',
        recipient=recipient,
        sender=sender,
        credit_amount=credit_amount
    )
    mail.send(msg) 