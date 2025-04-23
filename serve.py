from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import os
import time
import pickle
import faiss
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import webbrowser
import chromadb
from contextlib import contextmanager
from agents import Agent, Runner, handoff, function_tool
from agents.handoffs import HandoffInputData
from prompt import (
    MANAGER_INSTRUCTION,
    ADMISSION_POLICY_INSTRUCTION,
    TRAINING_PROGRAM_INSTRUCTION
)
from rag import (
    admission_policy_rag,
    training_program_rag
)

# === Bypass OpenAI trace
@contextmanager
def trace(*args, **kwargs):
    yield

# === FAISS config
INDEX_PATH = "faiss_faq_tv_ts.index"
META_PATH = "faiss_faq_tv_ts_metadata.pkl"
DIM = 384

load_dotenv()
model = SentenceTransformer("all-MiniLM-L6-v2")

# === FAISS setup
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "rb") as f:
        metadatas = pickle.load(f)
else:
    index = faiss.IndexFlatIP(DIM)
    metadatas = []

if index.d != DIM:
    print(f"⚠️ FAISS index chiều {index.d}, model {DIM}. Reset!")
    index = faiss.IndexFlatIP(DIM)
    metadatas = []

if index.ntotal == 0:
    print("⚠️ FAISS index rỗng. Cần nạp dữ liệu.")

# === ChromaDB setup
chroma_client = chromadb.PersistentClient(path="chroma_faq_store")
chroma_collection = chroma_client.get_or_create_collection("faq_tv_ts")

# === Flask app
app = Flask(__name__)
CORS(app)

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500

@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "ok", "message": "Agentic RAG is running!"})

def custom_input_filter(input_data: HandoffInputData) -> HandoffInputData:
    return input_data

# === Tool mở trình duyệt
@function_tool
def open_google():
    webbrowser.open("https://www.google.com")
    return "Đã mở Google."

@function_tool
def open_ulaw_tuition_page():
    url = "https://ts.hcmulaw.edu.vn/hoc-phi"
    webbrowser.open(url)
    return "✅ Đã mở trang thông tin học phí của Trường Đại học Luật TP.HCM."

@function_tool
def open_ulaw_map_location(location: str):
    location_map = {
        "trụ sở": "https://www.google.com/maps/place/2+%C4%90.+Nguy%E1%BB%85n+T%E1%BA%A5t+Th%C3%A0nh,+Ph%C6%B0%E1%BB%9Dng+18,+Qu%E1%BA%ADn+4,+H%E1%BB%93+Ch%C3%AD+Minh/@10.755958,106.719163,17z/data=!3m1!4b1!4m6!3m5!1s0x31752f6337b3bc47:0xa18f1ace5960cb0!8m2!3d10.755958!4d106.719163!16s%2Fg%2F11vyh6hbwt?entry=ttu&g_ep=EgoyMDI1MDQxNi4xIKXMDSoASAFQAw%3D%3D",
        "cơ sở 2": "https://maps.app.goo.gl/KWqfNRRwXMCJKmxu5",
        "cơ sở 3": "https://maps.app.goo.gl/tLdLe8DTrmYA3NxN7"
    }
    url = location_map.get(location.lower())
    if url:
        webbrowser.open(url)
        return f"✅ Đã mở bản đồ Google Maps cho {location.title()} của Trường Đại học Luật TP.HCM."
    else:
        return "❌ Không tìm thấy địa chỉ phù hợp. Hãy nhập 'trụ sở', 'cơ sở 2' hoặc 'cơ sở 3'."

# === Agents
admission_policy_agent = Agent(
    name="admission_policy",
    instructions=ADMISSION_POLICY_INSTRUCTION,
    tools=[admission_policy_rag],
)

training_program_agent = Agent(
    name="training_program",
    instructions=TRAINING_PROGRAM_INSTRUCTION,
    tools=[training_program_rag],
)

manager_agent = Agent(
    name="manager",
    instructions=MANAGER_INSTRUCTION,
    tools=[open_google, open_ulaw_tuition_page, open_ulaw_map_location],
    handoffs=[
        handoff(admission_policy_agent),
        handoff(training_program_agent)
    ],
)

conversation_history = {}

# === Lưu vào FAISS + ChromaDB
def save_to_vector_store(message, thread_id, role="user"):
    try:
        if not message:
            raise ValueError("Empty message")
        embedding = model.encode(message).astype("float32")
        if embedding.shape[0] != DIM:
            raise ValueError(f"Embedding {embedding.shape[0]} không khớp FAISS {DIM} chiều")
        faiss.normalize_L2(np.expand_dims(embedding, axis=0))

        # FAISS
        index.add(np.expand_dims(embedding, axis=0))
        metadatas.append({
            "thread_id": thread_id,
            "message": message,
            "role": role,
            "timestamp": time.time()
        })
        faiss.write_index(index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(metadatas, f)

        # ChromaDB
        chroma_collection.add(
            documents=[message],
            embeddings=[embedding.tolist()],
            ids=[f"{thread_id}_{int(time.time()*1000)}"],
            metadatas=[{
                "thread_id": thread_id,
                "role": role,
                "timestamp": time.time()
            }]
        )
    except Exception as e:
        print(f"[⚠️] Vector store save error: {e}")
        import traceback
        traceback.print_exc()

# === Chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    query = data.get("message", "")
    thread_id = data.get("thread_id", "1")

    if not query:
        return jsonify({"error": "Missing query"}), 400

    if thread_id not in conversation_history:
        conversation_history[thread_id] = []

    with trace(workflow_name="Conversation", group_id=thread_id):
        new_input = conversation_history[thread_id] + [{"role": "user", "content": query}]
        result = asyncio.run(Runner.run(manager_agent, new_input))
        conversation_history[thread_id] = new_input + [{"role": "assistant", "content": str(result.final_output)}]

    save_to_vector_store(query, thread_id, role="user")
    save_to_vector_store(str(result.final_output), thread_id, role="assistant")

    return jsonify({
        "role": "assistant",
        "content": str(result.final_output)
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
