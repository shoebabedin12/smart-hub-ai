from sentence_transformers import SentenceTransformer
import numpy as np

_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading Multilingual SentenceTransformer model...")
        # আপনার প্রজেক্টে ব্যবহৃত সঠিক মডেলের নাম এখানে থাকবে
        _model = SentenceTransformer('distiluse-base-multilingual-cased-v1') 
    return _model

def embed(texts: list[str]) -> np.ndarray:
    try:
        model = get_model()
        # নিশ্চিত করছি ইনপুট যেন লিস্ট অফ স্ট্রিং হয়
        if isinstance(texts, str):
            texts = [texts]
            
        embeddings = model.encode(texts, convert_to_numpy=True)
        
        # 🎯 নিশ্চিত করছি শুধুমাত্র এবং শুধুমাত্র NumPy অ্যারে রিটার্ন হচ্ছে (কোনো টাপল নয়)
        return embeddings
        
    except Exception as e:
        print(f"Error in embedder service: {e}")
        raise e