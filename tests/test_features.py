# tests/test_features.py

from app import db
from app.models import User, Organization, Membership

def test_feature_page_for_unsubscribed_user(test_client, test_app):
    """
    GIVEN a logged-in, un-subscribed user
    WHEN they try to access a premium feature page
    THEN they should be redirected to the dashboard with a flash message.
    """
    # Setup: create and log in a confirmed but unsubscribed user
    with test_app.app_context():
        user = User(email='unsubscribed@example.com', confirmed=True)
        org = Organization(name="Unsub Org", is_subscribed=False)
        membership = Membership(user=user, organization=org)
        user.set_password('password123')
        db.session.add(user)
        db.session.add(org)
        db.session.add(membership)
        db.session.commit()
    
    test_client.post('/auth/login', data={'email': 'unsubscribed@example.com', 'password': 'password123'})

    # Make the request to the premium feature
    response = test_client.get('/features/generate-text', follow_redirects=True)

    # Assertions
    assert response.status_code == 200
    assert b"This feature requires an active subscription." in response.data
    assert b"Welcome to your Dashboard" in response.data # Should be on the dashboard

def test_feature_page_for_subscribed_user(test_client, test_app, mocker):
    """
    GIVEN a logged-in, subscribed user
    WHEN they access a premium feature page and submit the form
    THEN they should see the feature and get a result from the mocked API.
    """
    # Setup: create and log in a subscribed user
    with test_app.app_context():
        user = User(email='subscribed@example.com', confirmed=True)
        org = Organization(name="Sub Org", is_subscribed=True)
        membership = Membership(user=user, organization=org)
        user.set_password('password123')
        db.session.add(user)
        db.session.add(org)
        db.session.add(membership)
        db.session.commit()
    
    test_client.post('/auth/login', data={'email': 'subscribed@example.com', 'password': 'password123'})

    # Mock the OpenAI client's create method to avoid real API calls
    mock_create = mocker.patch('app.features.OpenAI').return_value.completions.create
    mock_create.return_value.choices[0].text = "This is a test response from the AI."

    response = test_client.post('/features/generate-text', data={'prompt': 'test prompt'}, follow_redirects=True)

    assert response.status_code == 200
    assert b"AI Text Generator" in response.data
    assert b"This is a test response from the AI." in response.data
    mock_create.assert_called_once()