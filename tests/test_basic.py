# tests/test_basic.py

def test_index_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid and contains expected content
    """
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"The Ultimate SaaS Boilerplate" in response.data
    assert b"Login" in response.data
    assert b"Sign up" in response.data

def test_app_is_testing(test_app):
    """
    GIVEN a Flask application configured for testing
    WHEN the app is created
    THEN check that the testing config is being used
    """
    assert test_app.config['TESTING']
    assert test_app.config['CELERY_TASK_ALWAYS_EAGER']
    assert 'sqlite:///:memory:' in test_app.config['SQLALCHEMY_DATABASE_URI']