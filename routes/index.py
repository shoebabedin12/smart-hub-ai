from flask import Blueprint, request, jsonify
from services.doc_parser import extract_text, chunk_text
from services.embedder import embed
from services.faiss_store import add_embeddings
from db.connection import get_conn, release_conn
import numpy as np
import os

index_bp = Blueprint('index', __name__)

@index_bp.route('/index', methods=['POST'])
def index_document():
    data = request.get_json()
    resource_id = data.get('resource_id')
    file_path   = data.get('file_path')
    
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
    file_path = os.path.join(BASE_DIR, file_path.replace('\\', '/'))

    if not resource_id or not file_path:
        return jsonify({'error': 'resource_id and file_path required'}), 400

    conn = None
    try:
        # Extract and chunk text
        raw_text = extract_text(file_path)
        if not raw_text:
            return jsonify({'error': 'Could not extract text'}), 400

        chunks = chunk_text(raw_text)
        if not chunks:
            return jsonify({'error': 'No chunks generated'}), 400

        # Generate embeddings
        embeddings = embed(chunks)

        # Prepare metadata for FAISS
        metadata = [
            {
                'resource_id': resource_id,
                'chunk_index': i,
                'chunk_text': chunk
            }
            for i, chunk in enumerate(chunks)
        ]

        add_embeddings(embeddings, metadata)

        # Save chunks to DB
        conn = get_conn()
        cur = conn.cursor()
        for i, chunk in enumerate(chunks):
            cur.execute(
                'INSERT INTO document_chunks (resource_id, chunk_text, chunk_index) VALUES (%s, %s, %s)',
                (resource_id, chunk, i)
            )

        # Mark resource as indexed
        cur.execute(
            'UPDATE resources SET is_indexed=TRUE WHERE id=%s',
            (resource_id,)
        )
        conn.commit()
        cur.close()

        return jsonify({'message': f'Indexed {len(chunks)} chunks', 'resource_id': resource_id})

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if conn:
            release_conn(conn)