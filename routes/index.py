import requests
import os
import numpy as np
from flask import Blueprint, request, jsonify
from services.doc_parser import extract_text, chunk_text
from services.embedder import embed
from services.faiss_store import add_embeddings

index_bp = Blueprint('index', __name__)

TEMP_DIR = 'temp_files'
os.makedirs(TEMP_DIR, exist_ok=True)

@index_bp.route('/index-file', methods=['POST'])
def index_file():
    data = request.get_json() or {}
    file_url = data.get('file_url')         
    resource_id = data.get('resource_id')   

    if not file_url or not resource_id:
        return jsonify({'error': 'file_url and resource_id are required'}), 400

    temp_file_path = None
    try:
        print(f"Python processing remote file: {file_url}")
        
        url_lower = str(file_url).lower()
        if '.docx' in url_lower:
            ext = '.docx'
        elif '.pdf' in url_lower:
            ext = '.pdf'
        elif '.txt' in url_lower or '/raw/upload/' in url_lower:
            ext = '.txt'
        else:
            ext = '.pdf'

        response = requests.get(file_url, stream=True)
        if response.status_code != 200:
            return jsonify({'error': f'Failed to download file from Cloudinary. Status: {response.status_code}'}), 400

        temp_file_path = os.path.join(TEMP_DIR, f"resource_{resource_id}{ext}")
        with open(temp_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # Text extraction
        raw_text = extract_text(temp_file_path)
        extracted_text = str(raw_text) if raw_text else ""
        
        print(f"Successfully extracted characters count: {len(extracted_text.strip())}")

        if not extracted_text or len(extracted_text.strip()) == 0:
            if os.path.exists(temp_file_path): 
                os.remove(temp_file_path)
            # 🔴 এটি ৪-শো দেওয়ার মূল কারণ। স্ক্যান করা PDF হলে PyMuPDF টেক্সট পায় না।
            return jsonify({'error': 'No text could be extracted from this file (It might be scanned or image-based)'}), 400

        chunks = chunk_text(extracted_text)

        raw_embeddings = embed(chunks)
        
        if isinstance(raw_embeddings, tuple):
            embeddings = raw_embeddings[0]
        else:
            embeddings = raw_embeddings

        embeddings = np.array(embeddings, dtype=np.float32)
        print(f"✅ Final verified Embeddings Shape: {embeddings.shape}")

        metadata = [{'resource_id': int(resource_id), 'chunk_text': str(chunk)} for chunk in chunks]
        
        add_embeddings(embeddings, metadata)

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        return jsonify({'message': 'File downloaded and successfully indexed into FAISS'}), 200

    except Exception as e:
        print(f"Indexing Error: {str(e)}")
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return jsonify({'error': str(e)}), 500