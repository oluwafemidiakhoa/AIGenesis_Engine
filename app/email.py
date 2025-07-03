# app/email.py

import os
from flask_mail import Message
from flask import render_template
from . import mail, celery

@celery.task
def send_email(to, subject, template, **kwargs):
    """
    Sends an email using a template as a background task.
    """
    # This task will run within the Flask application context,
    # so it has access to `mail` and `celery.conf`.
    msg = Message(subject, sender=celery.conf.get('MAIL_DEFAULT_SENDER'), recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)