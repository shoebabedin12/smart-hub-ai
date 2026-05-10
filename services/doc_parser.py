import fitz  # PyMuPDF
from docx import Document
import os

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.pdf':
        doc = fitz.open(file_path)
        text = ''
        for page in doc:
            text += page.get_text()
        return text.strip()

    elif ext in ('.docx', '.doc'):
        doc = Document(file_path)
        return '\n'.join([p.text for p in doc.paragraphs]).strip()

    elif ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()

    return ''

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks
