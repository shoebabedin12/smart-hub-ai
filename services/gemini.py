import google.generativeai as genai
import os

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-flash-latest')

def summarize_text(text: str) -> str:
    try:
        prompt = f"""Summarize the following university notice in 2-3 clear sentences.
Keep it concise and informative. Notice:

{text}"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return None

def answer_question(question: str, context: str) -> str:
    try:
        prompt = f"""You are a helpful academic assistant for university students. Answer the
student's question using ONLY the context excerpt below, taken from their course
documents. Be direct and concise. If the context doesn't actually contain the
answer, say so instead of guessing.

Context:
{context}

Question: {question}

Answer:"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return None