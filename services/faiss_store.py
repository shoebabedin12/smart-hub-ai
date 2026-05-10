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
        index = faiss.read_index(INDEX_FILE)
        with open(META_FILE, 'rb') as f:
            meta = pickle.load(f)
        return index, meta
    return None, []

def _save(index, meta):
    faiss.write_index(index, INDEX_FILE)
    with open(META_FILE, 'wb') as f:
        pickle.dump(meta, f)

def add_embeddings(embeddings: np.ndarray, metadata: list[dict]):
    index, meta = _load()

    if index is None:
        dim = embeddings.shape[1]
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
    for dist, idx in zip(D[0], I[0]):
        if idx != -1 and dist < 1.5:
            results.append({**meta[idx], 'distance': float(dist)})
    return results