# app/admin.py

from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for
from . import db
from .models import User, Organization, Membership

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

class AdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.index'))

# A custom, more detailed admin view for the User model
class UserAdminView(AdminView):
    # Columns to display in the list view
    column_list = ('id', 'email', 'is_admin', 'confirmed', 'created_at')

    # Enable searching by email
    column_searchable_list = ('email',)

    # Add filters for boolean fields
    column_filters = ('is_admin', 'confirmed')

    # Exclude the password hash from the list view for security
    column_exclude_list = ('password_hash',)

    # Disable model creation from the admin panel to enforce password hashing.
    # Admins should be created via the CLI.
    can_create = False

class OrganizationAdminView(AdminView):
    column_list = ('id', 'name', 'is_subscribed', 'stripe_customer_id', 'created_at')
    column_searchable_list = ('name', 'stripe_customer_id')
    column_filters = ('is_subscribed',)

class MembershipAdminView(AdminView):
    column_list = ('user.email', 'organization.name', 'role')
    column_searchable_list = ('user.email', 'organization.name')

admin = Admin(name='SaaS Admin', template_mode='bootstrap4', index_view=MyAdminIndexView())

# Add the customized User model view to the admin interface
admin.add_view(UserAdminView(User, db.session))
admin.add_view(OrganizationAdminView(Organization, db.session))
admin.add_view(MembershipAdminView(Membership, db.session))