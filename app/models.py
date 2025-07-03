# app/models.py

from __future__ import annotations

import secrets
from datetime import datetime
from typing import Optional, Tuple

from flask import current_app
from itsdangerous import BadTimeSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from . import db
from flask_login import UserMixin

class Organization(db.Model):
    __tablename__ = 'organizations'
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(120), nullable=False)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    # Stripe-related fields now belong to the organization
    stripe_customer_id: Optional[str] = db.Column(db.String(120), unique=True, nullable=True)
    is_subscribed: bool = db.Column(db.Boolean, default=False, nullable=False)
    subscription_id: Optional[str] = db.Column(db.String(120), unique=True, nullable=True)
    stripe_price_id: Optional[str] = db.Column(db.String(120), nullable=True)

    members = db.relationship('Membership', back_populates='organization', cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f'<Organization {self.name}>'

class Membership(db.Model):
    __tablename__ = 'memberships'
    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    organization_id: int = db.Column(db.Integer, db.ForeignKey('organizations.id'), primary_key=True)
    role: str = db.Column(db.String(50), nullable=False, default='member') # e.g., 'owner', 'admin', 'member'

    user = db.relationship('User', back_populates='memberships')
    organization = db.relationship('Organization', back_populates='members')

class User(UserMixin, db.Model):
    """
    User model for the application.

    Represents a user with authentication details, subscription status,
    and administrative rights.
    """
    __tablename__ = 'users'  # Explicit table naming is a good practice.

    id: int = db.Column(db.Integer, primary_key=True)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    password_hash: Optional[str] = db.Column(db.String(256), nullable=True)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    # Administrative rights
    is_admin: bool = db.Column(db.Boolean, default=False, nullable=False)

    # Confirmation status
    confirmed: bool = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on: Optional[datetime] = db.Column(db.DateTime, nullable=True)

    # API Key
    api_key: str = db.Column(db.String(64), unique=True, nullable=False, index=True)

    # Relationships
    memberships = db.relationship('Membership', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f'<User {self.email}>'

    def set_password(self, password: str) -> None:
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Checks if the provided password matches the user's hashed password.
        Returns False if the user has no password (e.g., social login).
        """
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def generate_token(self, salt: str, expires_sec: int = 1800) -> str:
        """
        Generates a secure, timed token with a given salt.

        Args:
            salt: A unique salt for the token's purpose (e.g., 'email-confirm').
            expires_sec: The token's validity duration in seconds.

        Returns:
            A secure token string.
        """
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt=salt)

    def generate_confirmation_token(self, expires_sec: int = 3600) -> str:
        """Generates an email confirmation token."""
        return self.generate_token('email-confirm', expires_sec)

    def confirm(self, token: str, expires_sec: int = 3600) -> bool:
        """Verifies the confirmation token and updates the user's status."""
        user_id = User.verify_token(token, 'email-confirm', expires_sec)
        if user_id != self.id:
            return False
        self.confirmed = True
        self.confirmed_on = datetime.utcnow()
        db.session.add(self)
        return True

    def get_reset_token(self, expires_sec: int = 1800) -> str:
        """Generates a password reset token."""
        return self.generate_token('password-reset', expires_sec)

    @staticmethod
    def verify_reset_token(token: str, expires_sec: int = 1800) -> Optional[User]:
        """
        Verifies a password reset token and returns the corresponding user.

        Args:
            token: The token to verify.
            expires_sec: The maximum age of the token in seconds.

        Returns:
            The User object if the token is valid and not expired, otherwise None.
        """
        user_id = User.verify_token(token, 'password-reset', expires_sec)
        if user_id is None:
            return None
        return User.query.get(user_id)

    @staticmethod
    def verify_token(token: str, salt: str, expires_sec: int = 1800) -> Optional[int]:
        """Verifies a token and returns the user_id if valid."""
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, salt=salt, max_age=expires_sec)
            return data.get('user_id')
        except (SignatureExpired, BadTimeSignature):
            # Catches expired or invalid tokens specifically.
            return None
        except Exception:
            # Catches other potential errors like malformed payloads.
            return None

    @staticmethod
    def find_or_create_from_oauth(user_info: dict) -> Tuple[User, bool]:
        """
        Finds an existing user by email or creates a new one from OAuth information.
        This is used for social logins (e.g., Google).

        Args:
            user_info: A dictionary containing user information from the OAuth provider.
                       Must contain an 'email' key.

        Returns:
            A tuple containing the User object and a boolean indicating if the
            user was newly created. (user, created)
        """
        user = User.query.filter_by(email=user_info['email']).first()
        if user:
            return user, False

        # User does not exist, create a new one.
        # Password hash is None, indicating a social-only login.
        user = User(email=user_info['email'])
        db.session.add(user)
        db.session.commit()
        return user, True

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.api_key is None:
            self.api_key = secrets.token_hex(32)
