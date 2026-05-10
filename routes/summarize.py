from flask import Blueprint, request, jsonify
from services.gemini import summarize_text

summarize_bp = Blueprint('summarize', __name__)

@summarize_bp.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text', '').strip()

    if not text:
        return jsonify({'error': 'text required'}), 400

    summary = summarize_text(text)
    if summary:
        return jsonify({'summary': summary})
    return jsonify({'summary': None, 'error': 'Summarization failed'}), 500