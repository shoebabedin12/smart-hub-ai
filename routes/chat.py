from flask import Blueprint, request, jsonify
from services.embedder import embed
from services.faiss_store import search
import numpy as np

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data    = request.get_json()
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'error': 'message required'}), 400

    try:
        # Embed the question
        query_embedding = embed([message])

        # Search FAISS
        results = search(query_embedding, top_k=3)

        if not results:
            return jsonify({
                'answer': "I couldn't find relevant information in the academic documents. Please ask your faculty or check the resource library.",
                'source_resource_id': None
            })

        # Build answer from top chunks
        top_chunks = [r['chunk_text'] for r in results]
        answer = '\n\n'.join(top_chunks)
        source_resource_id = int(results[0]['resource_id']) if results[0]['resource_id'] else None

        return jsonify({
            'answer': answer,
            'source_resource_id': source_resource_id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500