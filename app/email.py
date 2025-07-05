"""Utility module for sending emails via Celery + Flask‑Mail.

Usage:
  send_email.delay("user@example.com", "Confirm your account", "email/confirm", user=user, token=token)

It renders both `<template>.txt` and `<template>.html` from your Flask templates
folder, injecting any kwargs you pass.
"""
from __future__ import annotations

import typing as _t

from flask import current_app, render_template
from flask_mail import Message

from . import mail, celery

__all__ = ["send_email"]

# ---------------------------------------------------------------------------
# Celery task
# ---------------------------------------------------------------------------

@celery.task(name="email.send")
def send_email(to: str, subject: str, template: str, **kwargs: _t.Any) -> None:  # pragma: no cover
    """Send an email *asynchronously* using Celery.

    Parameters
    ----------
    to : str
        Recipient email address.
    subject : str
        Email subject.
    template : str
        Jinja template path *without* the file extension.
        The function looks for both `<template>.txt` and `<template>.html`.
    **kwargs : Any
        Keyword arguments forwarded to the template renderer.
    """
    with current_app.app_context():
        # Pull sender from config (falls back to MAIL_USERNAME as best‑effort)
        sender = (
            current_app.config.get("MAIL_DEFAULT_SENDER")
            or current_app.config.get("MAIL_USERNAME")
        )

        msg = Message(subject=subject, sender=sender, recipients=[to])

        # Render plaintext and HTML bodies
        msg.body = render_template(f"{template}.txt", **kwargs)
        msg.html = render_template(f"{template}.html", **kwargs)

        mail.send(msg)
