# tests/test_password_reset.py

from app import db
from app.models import User, Organization, Membership

def test_forgot_password_request(test_client, test_app, mocker):
    """
    GIVEN a registered user
    WHEN they request a password reset
    THEN a password reset email should be "sent".
    """
    # Setup: create a user
    with test_app.app_context():
        user = User(email='reset_me@example.com', confirmed=True)
        user.set_password('old_password')
        org = Organization(name="Reset Me Org")
        membership = Membership(user=user, organization=org, role='owner')
        db.session.add_all([user, org, membership])
        db.session.commit()

    # Mock the email sending task
    mock_send_email = mocker.patch('app.auth.send_email.delay')

    # Make the request
    response = test_client.post('/auth/forgot_password', data={
        'email': 'reset_me@example.com'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"A password reset link has been sent" in response.data
    mock_send_email.assert_called_once()

def test_password_reset_with_valid_token(test_client, test_app):
    """
    GIVEN a valid password reset token
    WHEN the user submits a new password
    THEN the password should be updated and they should be able to log in.
    """
    # Setup: create a user and generate a token
    with test_app.app_context():
        user = User(email='reset_success@example.com', confirmed=True)
        user.set_password('old_password')
        org = Organization(name="Reset Success Org")
        membership = Membership(user=user, organization=org, role='owner')
        db.session.add_all([user, org, membership])
        db.session.commit()
        token = user.get_reset_token()

    # Make the request to reset the password
    response = test_client.post(f'/auth/reset_password/{token}', data={
        'password': 'new_password',
        'password2': 'new_password'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Your password has been updated" in response.data

    # Verify login with the new password
    login_response = test_client.post('/auth/login', data={'email': 'reset_success@example.com', 'password': 'new_password'}, follow_redirects=True)
    assert login_response.status_code == 200
    assert b"Welcome to your Dashboard" in login_response.data

def test_password_reset_with_invalid_token(test_client):
    """
    GIVEN an invalid password reset token
    WHEN the user attempts to reset their password
    THEN they should see an error message.
    """
    response = test_client.post('/auth/reset_password/invalid-token', data={'password': 'new_password', 'password2': 'new_password'}, follow_redirects=True)

    assert response.status_code == 200
    assert b"The password reset link is invalid or has expired." in response.data