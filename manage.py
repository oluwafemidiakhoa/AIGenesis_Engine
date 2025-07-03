# manage.py
"""
Command-line utilities for the application.

To use, set the FLASK_APP environment variable to this file:
    export FLASK_APP=manage.py  (for Mac/Linux)
    set FLASK_APP=manage.py     (for Windows)

Then you can use the Flask CLI to manage the app. For example:
    flask db init       (to create the migration repository)
    flask db migrate    (to create a new migration)
    flask db upgrade    (to apply migrations to the database)
    flask create-admin <email> <password>
"""

import os
import click
from app import create_app, db # create_app must be imported for CLI to work
from app.models import User, Organization, Membership
 
# Create an app instance for the context
app = create_app(os.getenv('FLASK_CONFIG') or 'dev')

@app.cli.command('create-admin')
@click.argument('email')
@click.argument('password')
def create_admin_command(email, password):
    """Creates a new admin user."""
    with app.app_context():
        if User.query.filter_by(email=email).first():
            print(f"Error: User with email {email} already exists.")
            return

        admin_user = User(email=email, is_admin=True, confirmed=True)
        admin_user.set_password(password)

        org_name = f"{email.split('@')[0]}'s Team"
        new_org = Organization(name=org_name)

        membership = Membership(user=admin_user, organization=new_org, role='owner')

        db.session.add(admin_user)
        db.session.add(new_org)
        db.session.add(membership)
        db.session.commit()
        print(f"Admin user {email} created successfully.")
