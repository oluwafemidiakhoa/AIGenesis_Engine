# app/features.py

from openai import OpenAI
from flask import Blueprint, render_template, current_app, flash, request
from flask_login import login_required
from .decorators import subscription_required

features = Blueprint('features', __name__)

@features.route('/generate-text', methods=['GET', 'POST'])
@login_required
@subscription_required
def generate_text():
    """
    A premium feature that uses the OpenAI API to generate text.
    Accessible only to subscribed users.
    """
    generated_text = None
    if request.method == 'POST':
        prompt = request.form.get('prompt', 'A short poem about a robot learning to code:')
        try:
            client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
            response = client.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=60
            )
            generated_text = response.choices[0].text.strip()
        except Exception as e:
            flash(f"An error occurred while contacting the AI service: {e}", "error")

    return render_template('feature_page.html', generated_text=generated_text)