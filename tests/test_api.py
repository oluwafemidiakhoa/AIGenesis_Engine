# tests/test_api.py

from app import db
from app.models import User, Organization, Membership

def test_api_unauthorized(test_client):
    """Test API access without a key."""
    response = test_client.get('/api/v1/status')
    assert response.status_code == 401
    assert 'Authorization header is missing' in response.json['error']

def test_api_invalid_key(test_client):
    """Test API access with an invalid key."""
    response = test_client.get('/api/v1/status', headers={'Authorization': 'Bearer invalid-key'})
    assert response.status_code == 401
    assert 'Invalid API key' in response.json['error']

def test_api_valid_key(test_client, test_app):
    """Test successful API access."""
    with test_app.app_context():
        user = User(email='api_user@example.com', confirmed=True)
        org = Organization(name="API User Org")
        membership = Membership(user=user, organization=org)
        db.session.add_all([user, org, membership])
        db.session.commit()
        api_key = user.api_key

    response = test_client.get('/api/v1/status', headers={'Authorization': f'Bearer {api_key}'})
    assert response.status_code == 200
    assert response.json['authenticated_user'] == 'api_user@example.com'

def test_premium_api_for_unsubscribed_user(test_client, test_app):
    """Test premium API access for an unsubscribed user."""
    with test_app.app_context():
        user = User(email='api_unsub@example.com', confirmed=True)
        org = Organization(name="API Unsub Org", is_subscribed=False)
        membership = Membership(user=user, organization=org)
        db.session.add(user)
        db.session.add(org)
        db.session.add(membership)
        db.session.commit()
        api_key = user.api_key

    response = test_client.post('/api/v1/generate', headers={'Authorization': f'Bearer {api_key}'}, json={'prompt': 'test'})
    assert response.status_code == 403
    assert 'requires an active subscription' in response.json['error']

def test_premium_api_for_subscribed_user(test_client, test_app, mocker):
    """Test successful premium API access."""
    with test_app.app_context():
        user = User(email='api_sub@example.com', confirmed=True)
        org = Organization(name="API Sub Org", is_subscribed=True)
        membership = Membership(user=user, organization=org)
        db.session.add(user)
        db.session.add(org)
        db.session.add(membership)
        db.session.commit()
        api_key = user.api_key

    mock_create = mocker.patch('app.api.OpenAI').return_value.completions.create
    mock_create.return_value.choices[0].text = "API test response"

    response = test_client.post('/api/v1/generate', headers={'Authorization': f'Bearer {api_key}'}, json={'prompt': 'test'})
    assert response.status_code == 200
    assert response.json['generated_text'] == "API test response"
    mock_create.assert_called_once()

def test_premium_api_missing_prompt(test_client, test_app):
    """Test premium API access without a prompt."""
    with test_app.app_context():
        user = User(email='api_sub_prompt@example.com', confirmed=True)
        org = Organization(name="API Sub Prompt Org", is_subscribed=True)
        membership = Membership(user=user, organization=org)
        db.session.add(user)
        db.session.add(org)
        db.session.add(membership)
        db.session.commit()
        api_key = user.api_key

    response = test_client.post('/api/v1/generate', headers={'Authorization': f'Bearer {api_key}'}, json={})
    assert response.status_code == 400
    assert 'Prompt is required' in response.json['error']