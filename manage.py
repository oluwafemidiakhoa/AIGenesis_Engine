# manage.py
"""
#!/usr/bin/env python
"""
Command-line utilities for managing the Flask application.

Usage:
  export FLASK_APP=manage.py      # Mac/Linux
  set FLASK_APP=manage.py         # Windows

Then use Flask CLI:
  flask db init       # create migrations folder
  flask db migrate    # generate a new migration
  flask db upgrade    # apply migrations
  flask create-admin <email> <password>
"""
import os
import click
from app import create_app, db
from app.models import User, Organization, Membership

# Create Flask app with selected configuration
config_name = os.environ.get('FLASK_CONFIG', 'prod')
app = create_app(config_name)

# Register Flask CLI commands
@app.cli.command('create-admin')
@click.argument('email')
@click.argument('password')
def create_admin(email, password):
    """Create a new administrator user."""
    with app.app_context():
        if User.query.filter_by(email=email).first():
            click.secho(f"Error: User '{email}' already exists.", fg='red')
            return

        # Create admin user and organization
        admin = User(email=email, is_admin=True, confirmed=True)
        admin.set_password(password)

        org_name = f"{email.split('@')[0]}'s Organization"
        org = Organization(name=org_name)

        # Link admin to organization as owner
        membership = Membership(user=admin, organization=org, role='owner')

        db.session.add_all([admin, org, membership])
        db.session.commit()

        click.secho(f"Admin user '{email}' created successfully.", fg='green')

if __name__ == '__main__':
    # When invoked directly: run Flask CLI
    from flask.cli import main
    main()
