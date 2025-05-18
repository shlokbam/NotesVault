import stripe
from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from app.models.payment import Payment
from app import db
import time
import os

bp = Blueprint('payment', __name__, url_prefix='/payment')

# Initialize Stripe with your secret key from environment variables
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Get Stripe publishable key from environment variables
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')

def is_valid_vit_email(email):
    return email.endswith('vit.edu')

@bp.route('/buy-credits', methods=['GET'])
@login_required
def buy_credits():
    """Render the buy credits page"""
    if not is_valid_vit_email(current_user.email):
        return "Only VIT email addresses are allowed for payments.", 403
    return render_template('payment/buy_credits.html', stripe_publishable_key=STRIPE_PUBLISHABLE_KEY)

@bp.route('/create-payment-intent', methods=['POST'])
@login_required
def create_payment_intent():
    try:
        data = request.get_json()
        credits = int(data.get('credits', 1))
        amount = credits * 10  # 1 credit = 10 INR
        payment_method = data.get('payment_method', 'card')
        
        # Only allow card payments now
        if payment_method != 'card':
             return jsonify(error="Only card payments are supported"), 400

        # Get customer email from form data
        customer_email = data.get('email')
        if not customer_email:
            return jsonify(error="Customer email is required"), 400
            
        # Verify VIT email
        if not is_valid_vit_email(customer_email):
            return jsonify(error="Only VIT email addresses are allowed for payments."), 403

        # Create or retrieve Stripe Customer
        try:
            # Search for existing customer with this email
            customers = stripe.Customer.list(email=customer_email, limit=1)
            if customers.data:
                customer = customers.data[0]
            else:
                # Create new customer if not found
                customer = stripe.Customer.create(
                    email=customer_email,
                    name=data.get('name'),
                    metadata={
                        'user_id': current_user.id,
                        'is_vit_student': True
                    }
                )
        except stripe.error.StripeError as e:
            return jsonify(error=f"Error creating customer: {str(e)}"), 400
            
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to paise
            currency='inr',
            customer=customer.id,
            description=f'Purchase of {credits} credits for NotesVault',
            metadata={
                'user_id': current_user.id,
                'credits': credits,
                'customer_email': customer_email,
                'payment_method': payment_method,
            },
            shipping={
                'name': data.get('name', current_user.name),
                'address': {
                    'line1': data.get('address_line1', '123 Main St'),
                    'city': data.get('city', 'Mumbai'),
                    'state': data.get('state', 'Maharashtra'),
                    'postal_code': data.get('postal_code', '400001'),
                    'country': 'IN'
                }
            },
            receipt_email=customer_email,
            statement_descriptor='NOTESVAULT',
            statement_descriptor_suffix='CREDITS'
        )
        
        response_data = {
            'clientSecret': intent.client_secret,
            'payment_intent_id': intent.id,
            'publishableKey': STRIPE_PUBLISHABLE_KEY
        }
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify(error=str(e)), 403

@bp.route('/check-status/<payment_intent_id>', methods=['GET'])
@login_required
def check_payment_status(payment_intent_id):
    """Check the status of a payment intent"""
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        return jsonify({'status': intent.status})
    except Exception as e:
        return jsonify(error=str(e)), 400

@bp.route('/payment-success', methods=['GET'])
@login_required
def payment_success():
    try:
        payment_intent_id = request.args.get('payment_intent_id')
        if not payment_intent_id:
            return "Payment Intent ID missing", 400

        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        # Check if payment record already exists to prevent duplicates
        existing_payment = Payment.query.filter_by(stripe_payment_id=payment_intent.id).first()
        if existing_payment:
            # If payment already recorded, just render the success page with existing details
            return render_template('payment/success.html', 
                credits=existing_payment.credits, 
                total_credits=existing_payment.user.credits, 
                payment_id=existing_payment.stripe_payment_id, 
                amount=existing_payment.amount,
                status=existing_payment.status
            )

        if payment_intent.status != 'succeeded':
            return "Payment not successful", 400

        # Create payment record
        payment = Payment(
            user_id=current_user.id,
            amount=payment_intent.amount / 100,  # Convert from paise to INR
            credits=int(payment_intent.metadata.get('credits')),
            stripe_payment_id=payment_intent.id,
            status='completed'
        )
        
        # Update user's credits
        current_user.credits += payment.credits
        
        db.session.add(payment)
        db.session.commit()
        
        # Render the success page with payment details
        return render_template('payment/success.html', 
            credits=payment.credits, 
            total_credits=current_user.credits, 
            payment_id=payment.stripe_payment_id, 
            amount=payment.amount,
            status=payment.status
        )
    except Exception as e:
        return jsonify(error=str(e)), 400 