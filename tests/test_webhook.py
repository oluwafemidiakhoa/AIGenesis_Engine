# tests/test_webhook.py

import stripe
from app import db
from app.models import User, Organization, Membership

def test_webhook_checkout_session_completed(test_client, test_app, mocker):
    """
    GIVEN a user and organization exist in the database
    WHEN a valid 'checkout.session.completed' webhook is received from Stripe
    THEN the organization's subscription status should be updated correctly.
    """
    # 1. Setup: Create a user and organization that is about to subscribe.
    with test_app.app_context():
        user = User(email='webhook_user@example.com', confirmed=True)
        org = Organization(name="Webhook Org")
        membership = Membership(user=user, organization=org)
        db.session.add_all([user, org, membership])
        db.session.commit()
        org_id = org.id

    # 2. Mock the Stripe event payload
    mock_event_payload = {
        'id': 'evt_123',
        'object': 'event',
        'type': 'checkout.session.completed',
        'data': {
            'object': {
                'client_reference_id': org_id,
                'customer': 'cus_12345',
                'subscription': 'sub_12345'
            }
        }
    }

    # 3. Mock the Stripe SDK's construct_event method to return our mock payload
    mocker.patch('stripe.Webhook.construct_event', return_value=mock_event_payload)

    # 4. Make the POST request to our webhook endpoint
    response = test_client.post('/payments/webhook',
                                data='mock_payload',
                                headers={'Stripe-Signature': 'mock_sig'})

    # 5. Assertions
    assert response.status_code == 200
    with test_app.app_context():
        updated_org = Organization.query.get(org_id)
        assert updated_org.is_subscribed is True
        assert updated_org.stripe_customer_id == 'cus_12345'
        assert updated_org.subscription_id == 'sub_12345'

def test_webhook_invalid_signature(test_client, mocker):
    """
    GIVEN a request with an invalid signature
    WHEN it hits the webhook endpoint
    THEN the application should return a 400 Bad Request error.
    """
    # Mock the construct_event to simulate a signature verification failure
    mocker.patch('stripe.Webhook.construct_event', side_effect=stripe.error.SignatureVerificationError('test error', 'sig_header'))

    response = test_client.post('/payments/webhook', data='payload', headers={'Stripe-Signature': 'bad_sig'})

    assert response.status_code == 400

def test_webhook_subscription_deleted(test_client, test_app, mocker):
    """
    GIVEN a subscribed organization exists in the database
    WHEN a 'customer.subscription.deleted' webhook is received from Stripe
    THEN the organization's subscription status should be updated correctly.
    """
    # 1. Setup: Create a user and a currently subscribed organization.
    with test_app.app_context():
        user = User(email='cancel_sub@example.com', confirmed=True)
        org = Organization(name="Cancel Org", is_subscribed=True,
                           stripe_customer_id='cus_cancel', subscription_id='sub_cancel')
        membership = Membership(user=user, organization=org)
        db.session.add_all([user, org, membership])
        db.session.commit()

    # 2. Mock the Stripe event payload
    mock_event_payload = {
        'id': 'evt_456',
        'object': 'event',
        'type': 'customer.subscription.deleted',
        'data': {
            'object': { 'id': 'sub_cancel', 'customer': 'cus_cancel' }
        }
    }

    # 3. Mock the Stripe SDK
    mocker.patch('stripe.Webhook.construct_event', return_value=mock_event_payload)

    # 4. Make the request
    response = test_client.post('/payments/webhook', data='mock_payload', headers={'Stripe-Signature': 'mock_sig'})

    # 5. Assertions
    assert response.status_code == 200
    with test_app.app_context():
        updated_org = Organization.query.filter_by(stripe_customer_id='cus_cancel').first()
        assert updated_org.is_subscribed is False
        assert updated_org.subscription_id is None