# app/decorators.py

from functools import wraps
from flask import flash, redirect, url_for, request, g, jsonify
from flask_login import current_user
from .models import User

def subscription_required(f):
    """
    Ensures that the current user has an active subscription.
    If not, it flashes a message and redirects to the dashboard.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        org = current_user.current_organization
        if not org or not org.is_subscribed:
            flash('This feature requires an active subscription.', 'warning')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role="owner"):
    """
    Ensures the current user has the specified role in their current organization.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            org = current_user.current_organization
            if not org:
                flash("You are not part of any organization.", "error")
                return redirect(url_for('main.dashboard'))

            # Find the membership for the current organization
            membership = next((m for m in current_user.memberships if m.organization_id == org.id), None)
            
            # For simplicity, we'll check for a single role. This could be a list.
            if not membership or membership.role != role:
                flash(f"This action requires the '{role}' role.", "error")
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_key_required(f):
    """
    Ensures that a valid API key is provided in the Authorization header.
    If valid, it sets `g.current_user` to the authenticated user.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header is missing or invalid'}), 401
        
        api_key = auth_header.split(' ')[1]
        user = User.query.filter_by(api_key=api_key).first()
        
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401
        
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function
