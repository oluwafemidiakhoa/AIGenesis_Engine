# app/main.py

from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import current_user, login_required

main = Blueprint('main', __name__)

@main.route('/healthz')
def health_check():
    """A simple health check endpoint that doesn't hit the database."""
    return jsonify(status="ok"), 200

@main.route('/')
def index():
    """Serves the landing page if the user is not authenticated, otherwise redirects to the dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing_page.html')

@main.route('/dashboard')
@login_required
def dashboard():
    """Serves the user's dashboard, accessible only to logged-in users."""
    return render_template('dashboard.html')
