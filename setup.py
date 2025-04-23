import pandas as pd
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import chromadb
from tqdm import tqdm
# === 1. Đọc dữ liệu
df = pd.read_csv("faq_tv_ts_final_2024_2025.csv")
df = df[df["information"].notna()].reset_index(drop=True)

# === 2. Khởi tạo model embedding 384 chiều
model = SentenceTransformer("all-MiniLM-L6-v2")
DIM = 384

# === 3. Tạo embedding cho toàn bộ dữ liệu
df["embedding"] = df["information"].apply(lambda x: model.encode(x).tolist())

# === 4. Build FAISS index
embedding_array = np.array(df["embedding"].tolist()).astype("float32")
faiss.normalize_L2(embedding_array)
index = faiss.IndexFlatIP(DIM)
index.add(embedding_array)

# === 5. Lưu lại FAISS index và metadata
faiss.write_index(index, "faiss_faq_tv_ts.index")
with open("faiss_faq_tv_ts_metadata.pkl", "wb") as f:
    pickle.dump(df["information"].tolist(), f)

# === 6. Khởi tạo ChromaDB client
client = chromadb.PersistentClient(path="chroma_faq_store")  # thư mục lưu dữ liệu
collection = client.get_or_create_collection("faq_tv_ts")

# === 7. Đưa dữ liệu vào ChromaDB
try:
    collection.add(
        documents=df["information"].tolist(),
        embeddings=df["embedding"].tolist(),
        ids=[f"faq_{i}" for i in range(len(df))],
        metadatas=[{"index": i} for i in range(len(df))]
    )
    print("✅ Đã thêm vào ChromaDB.")
except Exception as e:
    print("❌ Lỗi khi thêm vào ChromaDB:", e)
results = collection.peek()
print(f"Có {len(results['documents'])} tài liệu đầu tiên trong collection.")
print(f" Đã lưu FAISS và ChromaDB cho {len(df)} dòng với embedding {DIM} chiều.")
