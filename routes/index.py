import requests
import os
import numpy as np  # এটি নিশ্চিত করুন উপরে ইম্পোর্ট করা আছে
from flask import Blueprint, request, jsonify
from services.doc_parser import extract_text, chunk_text
from services.embedder import embed
from services.faiss_store import add_embeddings

index_bp = Blueprint('index', __name__)

TEMP_DIR = 'temp_files'
os.makedirs(TEMP_DIR, exist_ok=True)

@index_bp.route('/index-file', methods=['POST'])
def index_file():
    data = request.get_json()
    file_url = data.get('file_url')         
    resource_id = data.get('resource_id')   

    if not file_url or not resource_id:
        return jsonify({'error': 'file_url and resource_id are required'}), 400

    try:
        print(f"Python processing remote file: {file_url}")
        
        # ১. ইউআরএল চেক করে একদম নিখুঁতভাবে এক্সটেনশন নির্ধারণ করা
        url_lower = str(file_url).lower()
        if '.docx' in url_lower:
            ext = '.docx'
        elif '.pdf' in url_lower: # 🎯 স্পষ্ট করে পিডিএফ চেক আগে দেওয়া হলো
            ext = '.pdf'
        elif '.txt' in url_lower or '/raw/upload/' in url_lower:
            ext = '.txt'
        else:
            ext = '.pdf' # ডিফল্ট পিডিএফ

        response = requests.get(file_url, stream=True)
        if response.status_code != 200:
            return jsonify({'error': f'Failed to download file from Cloudinary. Status: {response.status_code}'}), 400

        temp_file_path = os.path.join(TEMP_DIR, f"resource_{resource_id}{ext}")
        with open(temp_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        raw_text = extract_text(temp_file_path)
        extracted_text = str(raw_text) 
        
        print(f"Successfully extracted characters count: {len(extracted_text)}")

        if not extracted_text or len(extracted_text.strip()) == 0:
            if os.path.exists(temp_file_path): os.remove(temp_file_path)
            return jsonify({'error': 'No text could be extracted from this file'}), 400

        chunks = chunk_text(extracted_text)

        # 🎯 টাপল বাগ ধ্বংস করার চূড়ান্ত লজিক:
        raw_embeddings = embed(chunks)
        
        # যদি embed() ফাংশন ভুল করে টাপল ফেরত দেয়, তবে তার প্রথম উপাদানটি (অ্যারে) নেব
        if isinstance(raw_embeddings, tuple):
            embeddings = raw_embeddings[0]
        else:
            embeddings = raw_embeddings

        # নিশ্চিত করা হচ্ছে এটি যেন শক্তপোক্ত NumPy Array হয়
        embeddings = np.array(embeddings, dtype=np.float32)
        print(f"✅ Final verified Embeddings Shape: {embeddings.shape}")

        metadata = [{'resource_id': int(resource_id), 'chunk_text': str(chunk)} for chunk in chunks]
        
        # FAISS-এ পাঠানো
        add_embeddings(embeddings, metadata)

        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        return jsonify({'message': 'File downloaded and successfully indexed into FAISS'}), 200

    except Exception as e:
        print(f"Indexing Error: {str(e)}")
        return jsonify({'error': str(e)}), 500