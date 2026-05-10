import google.generativeai as genai
import os

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

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