from flask import Blueprint, request, jsonify
from services.embedder import embed  # 🎯 এটি যেন আমাদের নতুন get_model() কেই কল করে
from services.faiss_store import search
# আপনার জেমিনি বা এলএলএম সার্ভিসের ইম্পোর্ট

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        # ১. চ্যাটের প্রশ্নটিকে নতুন বহুভাষী মডেল দিয়ে এম্বেড করা (৭৬৮ ডাইমেনশন)
        query_vector = embed([user_message]) 

        # ২. FAISS ইনডেক্সে মিল খুঁজে বের করা
        raw_results = search(query_vector)

        if not raw_results:
            # যদি FAISS-এ কোনো ম্যাচ না পায়
            return jsonify({
                'answer': "Sorry, I couldn't find an answer in the academic documents.",
                'source_resource_id': None
            })

        # ৩. সবচেয়ে কাছের ম্যাচিং টেক্সটটি নেওয়া
        best_match = raw_results[0]
        context_text = best_match['chunk_text']
        source_id = best_match['resource_id'] # এটিই আমাদের MySQL-এর আইডি ১০

        # ৪. জেমিনি বা আপনার এলএলএম-কে কনটেক্সট সহ প্রম্পট পাঠানো (যদি জেমিনি দিয়ে জেনারেট করান)
        # অথবা সরাসরি টেক্সট রিটার্ন করা:
        answer = f"According to the document:\n{context_text}"

        return jsonify({
            'answer': answer,
            'source_resource_id': source_id
        })

    except Exception as e:
        print(f"🎯 Actual Python Chat Error: {str(e)}") # টার্মিনালে আসল এরর প্রিন্ট হবে
        return jsonify({'error': str(e)}), 500