# tests/test_auth.py

from app import db
from app.models import User, Organization, Membership

def test_register_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/auth/register' page is requested (GET)
    THEN check that the response is valid and contains the registration form.
    """
    response = test_client.get('/auth/register')
    assert response.status_code == 200
    assert b"Create a New Account" in response.data

def test_successful_registration(test_client, test_app, mocker):
    """
    GIVEN a Flask application
    WHEN the '/auth/register' page is posted to with valid data
    THEN check that a new user is created and a confirmation email is "sent".
    """
    # Mock the send_email task so we can check if it's called
    mock_send_email = mocker.patch('app.auth.send_email.delay')

    response = test_client.post('/auth/register', data={
        'email': 'test@example.com',
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"A confirmation email has been sent" in response.data
    
    with test_app.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert not user.confirmed
    
    # Assert that our email sending task was called once
    mock_send_email.assert_called_once()

def test_successful_login_and_logout(test_client, test_app):
    """
    GIVEN a Flask application and a registered, confirmed user
    WHEN the user logs in with correct credentials
    THEN check that they are redirected to the dashboard.
    WHEN the user logs out
    THEN check that they are redirected to the landing page.
    """
    # Setup: create a confirmed user in the database
    with test_app.app_context():
        user = User(email='login@example.com', confirmed=True)
        user.set_password('password123')
        org = Organization(name="Login Org")
        membership = Membership(user=user, organization=org, role='owner')
        db.session.add_all([user, org, membership])
        db.session.commit()

    # Test Login
    login_response = test_client.post('/auth/login', data={
        'email': 'login@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert login_response.status_code == 200
    assert b"Welcome to your Dashboard" in login_response.data

    # Test Logout
    logout_response = test_client.get('/auth/logout', follow_redirects=True)
    assert logout_response.status_code == 200
    assert b"You have been logged out" in logout_response.data

def test_unconfirmed_user_login(test_client, test_app):
    """
    GIVEN a Flask application and an unconfirmed user
    WHEN the user tries to log in
    THEN check that they are redirected to the unconfirmed page.
    """
    # Setup: create an unconfirmed user
    with test_app.app_context():
        user = User(email='unconfirmed@example.com', confirmed=False)
        user.set_password('password123')
        org = Organization(name="Unconfirmed Org")
        membership = Membership(user=user, organization=org, role='owner')
        db.session.add_all([user, org, membership])
        db.session.commit()

    # Test Login
    response = test_client.post('/auth/login', data={
        'email': 'unconfirmed@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"You have not confirmed your account yet" in response.data

def test_email_confirmation(test_client, test_app):
    """
    GIVEN a Flask application and an unconfirmed user
    WHEN the user clicks the confirmation link
    THEN check that their account is confirmed.
    """
    # Setup: create an unconfirmed user
    with test_app.app_context():
        user = User(email='confirm_me@example.com', confirmed=False)
        user.set_password('password123')
        org = Organization(name="Confirm Org")
        membership = Membership(user=user, organization=org, role='owner')
        db.session.add_all([user, org, membership])
        db.session.commit()
        token = user.generate_confirmation_token()

    # Log in the user first, as the confirm route is login_required
    test_client.post('/auth/login', data={
        'email': 'confirm_me@example.com',
        'password': 'password123'
    }, follow_redirects=True)

    response = test_client.get(f'/auth/confirm/{token}', follow_redirects=True)
    assert response.status_code == 200
    assert b"You have confirmed your account" in response.data
    with test_app.app_context():
        user = User.query.filter_by(email='confirm_me@example.com').first()
        assert user.confirmed