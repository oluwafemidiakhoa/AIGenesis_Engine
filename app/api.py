# app/api.py

from openai import OpenAI
from flask import Blueprint, jsonify, request, g, current_app
from .decorators import api_key_required

api = Blueprint('api', __name__)

@api.route('/status')
@api_key_required
def status():
    """A simple status endpoint to verify API key authentication."""
    return jsonify({
        'status': 'ok',
        'authenticated_user': g.current_user.email
    })

@api.route('/generate', methods=['POST'])
@api_key_required
def generate():
    """A premium API endpoint for generating text."""
    if not g.current_user.is_subscribed:
        return jsonify({'error': 'This endpoint requires an active subscription.'}), 403

    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({'error': 'Prompt is required.'}), 400

    try:
        client = OpenAI(api_key=current_app.config['OPENAI_API_KEY'])
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=60
        )
        generated_text = response.choices[0].text.strip()
        return jsonify({'generated_text': generated_text})
    except Exception as e:
        return jsonify({'error': f'An error occurred: {e}'}), 500