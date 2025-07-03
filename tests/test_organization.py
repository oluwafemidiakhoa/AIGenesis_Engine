# tests/test_organization.py

from app import db
from app.models import User, Organization, Membership

def test_user_registration_creates_organization(test_client, test_app, mocker):
    """
    GIVEN a new user is registering
    WHEN the registration is successful
    THEN a new User, Organization, and Membership should be created,
    and the user should be the owner of the new organization.
    """
    # Mock the email sending to prevent actual email sending during tests
    mocker.patch('app.auth.send_email.delay')

    # Register a new user
    test_client.post('/auth/register', data={
        'email': 'org_owner@example.com',
        'password': 'password123',
        'password2': 'password123'
    }, follow_redirects=True)

    # Verify the database state
    with test_app.app_context():
        user = User.query.filter_by(email='org_owner@example.com').first()
        assert user is not None

        # Check that the user has exactly one membership
        assert len(user.memberships) == 1
        membership = user.memberships[0]
        assert membership.role == 'owner'
        assert membership.organization.name == "org_owner's Team"