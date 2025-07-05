"""Stripe payment & subscription routes.

This blueprint handles:
  • Creating a Checkout session for the current organization
  • Redirecting owners to the Stripe Customer Portal
  • Receiving Stripe webhooks and updating org subscription state

All Stripe credentials are pulled from env‑vars that Render injects:
  STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY, STRIPE_PRICE_ID, STRIPE_WEBHOOK_SECRET

"""
from __future__ import annotations

import os
import stripe
from flask import Blueprint, current_app, flash, jsonify, redirect, request, url_for
from flask_login import current_user, login_required

from . import db
from .decorators import role_required
from .models import Organization

# ---------------------------------------------------------------------------
# Stripe SDK configuration (set once at import‑time)
# ---------------------------------------------------------------------------
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
if not stripe.api_key:
    raise RuntimeError("STRIPE_SECRET_KEY missing from environment variables.")

# Blueprint
payments = Blueprint("payments", __name__)

# ---------------------------------------------------------------------------
# Checkout session — subscription purchase
# ---------------------------------------------------------------------------
@payments.route("/create-checkout-session", methods=["POST"])
@login_required
@role_required("owner")
def create_checkout_session():
    """Start a Stripe Checkout subscription flow for the caller’s organization."""
    org: Organization | None = current_user.current_organization
    if org is None:
        flash("You are not part of any organization.", "error")
        return redirect(url_for("main.dashboard"))

    try:
        session = stripe.checkout.Session.create(
            client_reference_id=org.id,
            customer_email=current_user.email,
            mode="subscription",
            line_items=[{
                "price": current_app.config["STRIPE_PRICE_ID"],
                "quantity": 1,
            }],
            success_url=url_for("main.dashboard", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("main.dashboard", _external=True),
        )
        return redirect(session.url, code=303)

    except Exception as exc:  # noqa: BLE001 (broad catch is ok for user‑facing flash)
        flash(f"Error creating checkout session: {exc}", "error")
        current_app.logger.exception("Stripe checkout creation failed")
        return redirect(url_for("main.dashboard"))


# ---------------------------------------------------------------------------
# Customer Portal (billing management)
# ---------------------------------------------------------------------------
@payments.route("/customer-portal", methods=["POST"])
@login_required
@role_required("owner")
def customer_portal():
    """Redirect the owner to Stripe’s Customer Portal to manage the subscription."""
    org: Organization | None = current_user.current_organization
    if not (org and org.stripe_customer_id):
        flash("Your organization doesn't have a subscription to manage.", "error")
        return redirect(url_for("main.dashboard"))

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=org.stripe_customer_id,
            return_url=url_for("main.dashboard", _external=True),
        )
        return redirect(portal_session.url, code=303)

    except Exception as exc:  # noqa: BLE001
        flash(f"Error accessing customer portal: {exc}", "error")
        current_app.logger.exception("Stripe portal session failed")
        return redirect(url_for("main.dashboard"))


# ---------------------------------------------------------------------------
# Webhook endpoint
# ---------------------------------------------------------------------------
@payments.route("/stripe/webhook", methods=["POST"])
def stripe_webhook():
    """Receive Stripe webhook events & update subscription state."""
    payload: str = request.get_data(as_text=True)
    sig_header: str | None = request.headers.get("Stripe-Signature")
    secret = current_app.config.get("STRIPE_WEBHOOK_SECRET")
    if not secret:
        current_app.logger.error("STRIPE_WEBHOOK_SECRET not set; refusing webhook")
        return "Webhook secret not configured", 500

    # Verify signature first
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, secret)
    except (ValueError, stripe.error.SignatureVerificationError) as exc:
        current_app.logger.warning("Invalid Stripe webhook: %s", exc)
        return "Invalid payload or signature", 400

    event_type = event["type"]
    data_obj = event["data"]["object"]

    # ------------------ checkout.session.completed ------------------
    if event_type == "checkout.session.completed":
        org_id = data_obj.get("client_reference_id")
        customer_id = data_obj.get("customer")
        subscription_id = data_obj.get("subscription")

        if org_id:
            org = Organization.query.get(org_id)
            if org:
                org.stripe_customer_id = customer_id
                org.subscription_id = subscription_id
                org.is_subscribed = True
                db.session.commit()

    # ------------------ customer.subscription.deleted --------------
    elif event_type == "customer.subscription.deleted":
        customer_id = data_obj.get("customer")
        if customer_id:
            org = Organization.query.filter_by(stripe_customer_id=customer_id).first()
            if org:
                org.is_subscribed = False
                org.subscription_id = None
                db.session.commit()

    return jsonify(status="success"), 200
