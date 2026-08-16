from flask import Blueprint, request, jsonify
from services.embedder import embed  # 🎯 এটি যেন আমাদের নতুন get_model() কেই কল করে
from services.faiss_store import search
from services.gemini import answer_question

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        # ১. চ্যাটের প্রশ্নটিকে নতুন বহুভাষী মডেল দিয়ে এম্বেড করা (৭৬৮ ডাইমেনশন)
        query_vector = embed([user_message])

        # ২. FAISS ইনডেক্সে মিল খুঁজে বের করা
        raw_results = search(query_vector)

        if not raw_results:
            # যদি FAISS-এ কোনো ম্যাচ না পায়
            return jsonify({
                'answer': "Sorry, I couldn't find an answer in the academic documents.",
                'source_resource_id': None
            })

        # ৩. সবচেয়ে কাছের কয়েকটি ম্যাচিং চাঙ্ক একসাথে কনটেক্সট হিসেবে নেওয়া
        top_matches = raw_results[:3]
        context_text = "\n\n---\n\n".join(m['chunk_text'] for m in top_matches)
        source_id = top_matches[0]['resource_id'] # এটিই আমাদের MySQL-এর আইডি

        # ৪. জেমিনিকে কনটেক্সট সহ প্রশ্নটি পাঠিয়ে একটি সরাসরি, স্বাভাবিক উত্তর তৈরি করানো
        answer = answer_question(user_message, context_text)

        # জেমিনি ব্যর্থ হলে (যেমন API quota/key সমস্যা) raw chunk টাই fallback হিসেবে ফেরত দেওয়া
        if not answer:
            answer = f"According to the document:\n{top_matches[0]['chunk_text']}"

        return jsonify({
            'answer': answer,
            'source_resource_id': source_id
        })

    except Exception as e:
        print(f"🎯 Actual Python Chat Error: {str(e)}") # টার্মিনালে আসল এরর প্রিন্ট হবে
        return jsonify({'error': str(e)}), 500
