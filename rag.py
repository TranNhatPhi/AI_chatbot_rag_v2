# ✅ rag.py
import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from agents import function_tool

# === Load FAISS và metadata
INDEX_PATH = "faiss_faq_tv_ts.index"
META_PATH = "faiss_faq_tv_ts_metadata.pkl"

if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        metadatas = pickle.load(f)
else:
    raise RuntimeError("❌ FAISS index not found, hãy build index trước!")

# === Khởi tạo mô hình embedding
model = SentenceTransformer("all-MiniLM-L6-v2")
DIM = 384

# === Hàm tạo embedding
def get_embedding(text: str) -> np.ndarray:
    embedding = model.encode(text).astype("float32")
    faiss.normalize_L2(embedding.reshape(1, -1))
    return embedding.reshape(1, -1)

# === Hàm tìm kiếm trong FAISS
def search_faiss(query: str, top_k: int = 3) -> str:
    query_embedding = get_embedding(query)
    D, I = index.search(query_embedding, top_k)
    results = []
    for i in I[0]:
        if 0 <= i < len(metadatas):
            results.append(f"- {metadatas[i]}")
    return "\n".join(results) if results else "Không tìm thấy thông tin phù hợp."

# === Tool dùng chung
@function_tool
def admission_policy_rag(query: str) -> str:
    return search_faiss(query)

@function_tool
def training_program_rag(query: str) -> str:
    return search_faiss(query)
