import stripe
from flask import current_app, jsonify
from app import db
from app.models.user import User

def init_stripe():
    """Initialize Stripe with the secret key"""
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

def create_payment_intent(amount, currency='inr'):
    """
    Create a payment intent for the specified amount
    amount: amount in smallest currency unit (e.g., paise for INR)
    currency: currency code (default: 'inr')
    """
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={"enabled": True},
        )
        return intent
    except Exception as e:
        return None

def handle_successful_payment(payment_intent_id, user_id):
    """
    Handle successful payment and add credits to user
    """
    try:
        user = User.query.get(user_id)
        if user:
            # Add credits based on the payment amount
            # You can customize this based on your pricing
            credits_to_add = 10  # Example: Add 10 credits for successful payment
            user.credits += credits_to_add
            db.session.commit()
            return True
    except Exception as e:
        return False

def create_checkout_session(amount, currency='inr', success_url=None, cancel_url=None):
    """
    Create a Stripe Checkout Session
    """
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': 'Credits Purchase',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url or 'http://localhost:5000/payment/success',
            cancel_url=cancel_url or 'http://localhost:5000/payment/cancel',
        )
        return session
    except Exception as e:
        return None 