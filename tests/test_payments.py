# tests/test_payments.py

import stripe
from app import db
from app.models import User, Organization, Membership

def test_create_checkout_session(test_client, test_app, mocker):
    """
    GIVEN a logged-in user
    WHEN they post to '/payments/create-checkout-session'
    THEN check that a Stripe session is created and the user is redirected.
    """
    # Setup: create and log in a user
    with test_app.app_context():
        user = User(email='stripe_user@example.com', confirmed=True)
        user.set_password('password123')
        org = Organization(name="Stripe Org")
        membership = Membership(user=user, organization=org, role='owner')
        db.session.add_all([user, org, membership])
        db.session.commit()

    test_client.post('/auth/login', data={'email': 'stripe_user@example.com', 'password': 'password123'})

    # Mock the Stripe API call
    mock_session_create = mocker.patch('stripe.checkout.Session.create')
    mock_session_create.return_value = stripe.checkout.Session(id='cs_test_123', url='https://checkout.stripe.com/pay/cs_test_123')

    # Make the request
    response = test_client.post('/payments/create-checkout-session')

    # Assertions
    assert response.status_code == 303  # Check for redirect
    assert response.location == 'https://checkout.stripe.com/pay/cs_test_123'
    mock_session_create.assert_called_once()

def test_customer_portal_redirect(test_client, test_app, mocker):
    """
    GIVEN a logged-in user with a Stripe customer ID
    WHEN they post to '/payments/customer-portal'
    THEN check that a Stripe portal session is created and the user is redirected.
    """
    # Setup: create and log in a user with a stripe_customer_id
    with test_app.app_context():
        user = User(email='portal_user@example.com', confirmed=True)
        org = Organization(name="Portal Org", stripe_customer_id='cus_123')
        membership = Membership(user=user, organization=org, role='owner')
        user.set_password('password123')
        db.session.add_all([user, org, membership])
        db.session.commit()

    test_client.post('/auth/login', data={'email': 'portal_user@example.com', 'password': 'password123'})

    # Mock the Stripe API call
    mock_portal_create = mocker.patch('stripe.billing_portal.Session.create')
    mock_portal_create.return_value = stripe.billing_portal.Session(id='pts_test_123', url='https://billing.stripe.com/p/session/pts_test_123')

    response = test_client.post('/payments/customer-portal')

    assert response.status_code == 303
    assert response.location == 'https://billing.stripe.com/p/session/pts_test_123'
    mock_portal_create.assert_called_once_with(customer='cus_123', return_url='http://localhost.localdomain/dashboard')

def test_checkout_session_for_non_owner(test_client, test_app):
    """
    GIVEN a logged-in user who is not an organization owner
    WHEN they try to create a checkout session
    THEN they should be redirected with an error.
    """
    # Setup: create and log in a user with 'member' role
    with test_app.app_context():
        user = User(email='member@example.com', confirmed=True)
        user.set_password('password123')
        org = Organization(name="Member Org")
        membership = Membership(user=user, organization=org, role='member')
        db.session.add_all([user, org, membership])
        db.session.commit()

    test_client.post('/auth/login', data={'email': 'member@example.com', 'password': 'password123'})

    # Make the request
    response = test_client.post('/payments/create-checkout-session', follow_redirects=True)

    # Assertions
    assert response.status_code == 200
    assert b"This action requires the 'owner' role." in response.data
    assert b"Welcome to your Dashboard" in response.data