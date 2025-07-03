# app/auth.py

from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from . import db
from .models import User, Organization, Membership
from .email import send_email

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.register'))

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists.', 'error')
            return redirect(url_for('auth.register'))

        new_user = User(email=email)
        new_user.set_password(password)

        # Create a personal organization for the new user
        org_name = f"{email.split('@')[0]}'s Team"
        new_org = Organization(name=org_name)

        # Add the user to the organization as the owner
        membership = Membership(user=new_user, organization=new_org, role='owner')

        db.session.add(new_user)
        db.session.add(new_org)
        db.session.add(membership)
        db.session.commit()

        token = new_user.generate_confirmation_token()
        send_email.delay(new_user.email, 'Confirm Your Account', 'email/confirm', user=new_user, token=token)

        flash('A confirmation email has been sent to you by email.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user)

        if not user.confirmed:
            return redirect(url_for('auth.unconfirmed'))

        return redirect(url_for('main.dashboard'))

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
    else:
        flash('The confirmation link is invalid or has expired.', 'error')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('unconfirmed.html')


@auth.route('/resend')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email.delay(current_user.email, 'Confirm Your Account', 'email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you.', 'info')
    return redirect(url_for('auth.unconfirmed'))


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.get_reset_token()
            send_email.delay(user.email, 'Reset Your Password', 'email/reset_password', user=user, token=token)
        flash('A password reset link has been sent to your email address.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html')


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if password != password2:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.reset_password', token=token))
        user.set_password(password)
        db.session.commit()
        flash('Your password has been updated.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)