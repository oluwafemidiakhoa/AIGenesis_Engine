# app/payments.py

import stripe
from flask import Blueprint, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Organization
from .decorators import role_required

payments = Blueprint('payments', __name__)

@payments.route('/create-checkout-session', methods=['POST'])
@login_required
@role_required('owner')
def create_checkout_session():
    """Creates a Stripe Checkout session for the user's current organization."""
    org = current_user.current_organization
    if not org:
        flash("You are not part of any organization.", "error")
        return redirect(url_for('main.dashboard'))

    try:
        checkout_session = stripe.checkout.Session.create(
            client_reference_id=org.id,
            customer_email=current_user.email,
            line_items=[
                {
                    'price': current_app.config['STRIPE_PRICE_ID'],
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=url_for('main.dashboard', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('main.dashboard', _external=True),
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash(f"Error creating checkout session: {e}", "error")
        return redirect(url_for('main.dashboard'))

@payments.route('/customer-portal', methods=['POST'])
@login_required
@role_required('owner')
def customer_portal():
    """Redirects a subscribed user to their organization's Stripe Customer Portal."""
    org = current_user.current_organization
    if not org or not org.stripe_customer_id:
        flash("Your organization doesn't have a subscription to manage.", "error")
        return redirect(url_for('main.dashboard'))

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=org.stripe_customer_id,
            return_url=url_for('main.dashboard', _external=True),
        )
        return redirect(portal_session.url, code=303)
    except Exception as e:
        flash(f"Error accessing customer portal: {e}", "error")
        return redirect(url_for('main.dashboard'))

@payments.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handles incoming webhooks from Stripe to update subscription status."""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config['STRIPE_WEBHOOK_SECRET']

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        return f'Invalid payload or signature: {e}', 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        org_id = session.get('client_reference_id')
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')

        org = Organization.query.get(org_id)
        if org:
            org.stripe_customer_id = customer_id
            org.subscription_id = subscription_id
            org.is_subscribed = True
            db.session.commit()

    # Handle the customer.subscription.deleted event
    if event['type'] == 'customer.subscription.deleted':
        session = event['data']['object']
        customer_id = session.get('customer')

        org = Organization.query.filter_by(stripe_customer_id=customer_id).first()
        if org:
            org.is_subscribed = False
            org.subscription_id = None
            db.session.commit()

    return jsonify(status='success'), 200