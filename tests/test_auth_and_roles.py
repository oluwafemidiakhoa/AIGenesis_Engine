# tests/test_auth_and_roles.py
from app import db
from app.models import User

def test_registration_and_login(test_client, new_user):
    """
    GIVEN a Flask application and a new user's details
    WHEN the '/auth/register' page is posted to
    THEN check that the user is created, logged in, and can log out
    """
    # Test registration
    response = test_client.post('/auth/register', data={
        'email': new_user.email,
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Logout' in response.data
    assert b'Dashboard' in response.data

    user_in_db = User.query.filter_by(email=new_user.email).first()
    assert user_in_db is not None
    assert user_in_db.check_password('password123')

    # Test logout
    response = test_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Logout' not in response.data

def test_subscription_required_decorator(test_client):
    """
    GIVEN a Flask application
    WHEN a non-subscribed user tries to access a protected route
    THEN check they are redirected and a flash message appears
    """
    # Register and log in a new user (who is not subscribed by default)
    test_client.post('/auth/register', data={
        'email': 'nonsubscriber@test.com',
        'password': 'password'
    }, follow_redirects=True)

    # Try to access the dashboard
    response = test_client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    # They should be redirected to the index page
    assert b"The Ultimate SaaS Boilerplate" in response.data
    # And see a flash message
    assert b"This feature requires an active subscription" in response.data

def test_dashboard_access_for_subscribed_user(test_client):
    """
    GIVEN a Flask application
    WHEN a subscribed user accesses the dashboard
    THEN check that they are granted access
    """
    # Manually create and log in a subscribed user
    user = User(email='subscriber@test.com', is_subscribed=True)
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    test_client.post('/auth/login', data={'email': 'subscriber@test.com', 'password': 'password'}, follow_redirects=True)

    response = test_client.get('/dashboard')
    assert response.status_code == 200
    assert b"Welcome to your Dashboard" in response.data