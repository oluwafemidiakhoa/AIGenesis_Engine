# tests/conftest.py

import sys
import os
import pytest
from app import create_app, db

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope='module')
def test_app():
    """Creates a test Flask application instance for a test module."""
    app = create_app('test')
    with app.app_context():
        db.create_all()
        yield app  # this is where the testing happens
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(test_app):
    """Creates a test client for the Flask application."""
    return test_app.test_client()