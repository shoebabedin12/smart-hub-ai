import faiss
import numpy as np
import os
import pickle

INDEX_DIR = 'faiss_index'
INDEX_FILE = os.path.join(INDEX_DIR, 'index.faiss')
META_FILE  = os.path.join(INDEX_DIR, 'meta.pkl')

os.makedirs(INDEX_DIR, exist_ok=True)

def _load():
    if os.path.exists(INDEX_FILE) and os.path.exists(META_FILE):
        try:
            index = faiss.read_index(INDEX_FILE)
            with open(META_FILE, 'rb') as f:
                meta = pickle.load(f)
            return index, meta
        except Exception as e:
            print(f"Error loading FAISS index, resetting... {e}")
            return None, []
    return None, []

def _save(index, meta):
    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, 'wb') as f:
        pickle.dump(meta, f)

def add_embeddings(embeddings: np.ndarray, metadata: list[dict]):
    index, meta = _load()

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    print("Embedding Shape:", embeddings.shape)
    print("Embedding Type :", type(embeddings))

    if len(embeddings.shape) != 2:
        raise ValueError(
            f"Expected 2D embeddings. Got {embeddings.shape}"
        )

    if index is None:
        dim = embeddings.shape[1]

        print(
            f"Creating new FAISS index with dimension={dim}"
        )

        index = faiss.IndexFlatL2(dim)

    index.add(embeddings)

    meta.extend(metadata)

    _save(index, meta)

def search(query_embedding: np.ndarray, top_k: int = 3):
    index, meta = _load()
    if index is None or index.ntotal == 0:
        return []

    D, I = index.search(query_embedding, top_k)
    results = []
    
    distances = D.flatten()
    indices = I.flatten()

    for dist, idx in zip(distances, indices):
        if int(idx) != -1 and float(dist) < 4.0: 
            results.append({**meta[int(idx)], 'distance': float(dist)})
            
    return results

def clear_index():
    if os.path.exists(INDEX_FILE):
        os.remove(INDEX_FILE)
    if os.path.exists(META_FILE):
        os.remove(META_FILE)
    print("FAISS Index & Metadata completely cleared!")