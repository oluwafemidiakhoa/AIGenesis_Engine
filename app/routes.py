from flask import render_template, request, jsonify
from . import main
import time

@main.route('/')
def index():
    """Serves the interactive landing page."""
    return render_template('index.html')

@main.route('/generate', methods=['POST'])
def generate():
    """Handles the AI generation request from the landing page."""
    data = request.get_json()
    if not data or 'prompt' not in data or not data['prompt'].strip():
        return jsonify({'error': 'Prompt is empty or invalid.'}), 400

    prompt = data['prompt']

    # --- Placeholder for your actual AI Genesis Engine logic ---
    # In a real application, you would call your AI model here.
    # For this example, we'll just simulate a delay and a simple response.
    try:
        time.sleep(1.5) # Simulate network/processing delay
        generated_text = f"This is a generated result for the prompt: '{prompt}'"
        return jsonify({'result': generated_text})
    except Exception as e:
        return jsonify({'error': f'An error occurred during generation: {e}'}), 500
