import fitz  # PyMuPDF
from docx import Document
import os

def extract_text(file_path: str) -> str:
    text = ''
    file_path_str = str(file_path).lower()
    
    # প্রথমে আমরা চেষ্টা করব ফাইলটি আসলেই পিডিএফ কিনা তা PyMuPDF দিয়ে সরাসরি চেক করতে
    # কারণ নামের শেষে .txt থাকলেও বাইনারি ডেটা যদি পিডিএফের হয়, fitz ওটা চিনে ফেলবে
    try:
        print(f"Doc Parser inspecting file: {file_path}")
        doc = fitz.open(file_path)
        print(f"File recognized as PDF. Total pages: {len(doc)}")
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        if text.strip():
            return str(text.strip())
    except Exception:
        # পিডিএফ না হলে কোডটি সাইলেন্টলি এখানে চলে আসবে (কোনো ক্র্যাশ করবে se)
        pass

    # পিডিএফ হিসেবে রিড করতে না পারলে এবার সাধারণ টেক্সট ফাইল হিসেবে ট্রাই করবে
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        if text:
            return str(text)
    except Exception:
        pass

    # সবশেষে যদি ওয়ারড (.docx) ফাইল হয়
    try:
        if file_path_str.endswith('.docx') or file_path_str.endswith('.doc'):
            doc = Document(file_path)
            text = '\n'.join([p.text for p in doc.paragraphs])
            return str(text.strip())
    except Exception as doc_err:
        print(f"Word doc reading failed: {doc_err}")

    return str(text.strip())

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    if not text:
        return []
    text_str = str(text)
    words = text_str.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks