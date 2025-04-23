import streamlit as st
import requests
import uuid
from datetime import datetime

# === Cấu hình trang
st.set_page_config(
    page_title="Agentic RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === CSS giao diện hiện đại - tương thích dark theme
st.markdown("""
<style>
    /* Style cho header */
    .header-container {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }

    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        color: white !important;
    }

    .header-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        color: white !important;
    }

    /* Style cho chat messages */
    .chat-message {
        display: flex;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border-radius: 1rem;
        animation: fadeIn 0.5s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* User message style */
    .chat-message.user {
        background: rgba(59, 130, 246, 0.1);
        border-left: 4px solid #3b82f6;
        margin-left: 3rem;
        color: inherit;
    }

    /* Assistant message style */
    .chat-message.assistant {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        margin-right: 3rem;
        color: inherit;
    }

    /* Avatar style */
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 1rem;
        border: 2px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .message-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
        color: inherit;
    }

    .message-timestamp {
        font-size: 0.75rem;
        opacity: 0.7;
        margin-top: 0.25rem;
    }

    /* Style cho input form */
    .stForm {
        background: var(--background-color);
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }

    /* Style cho sidebar */
    .sidebar-section {
        background: var(--background-color);
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        color: inherit;
    }

    /* Đảm bảo caption hiển thị rõ */
    .stCaption {
        color: inherit;
        opacity: 0.8;
    }

    /* Ẩn các phần tử không cần thiết */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {visibility: hidden;}

    /* Fix cho dark theme */
    [data-testid="stMarkdownContainer"] {
        color: inherit;
    }

    .sidebar-section h3 {
        color: inherit;
    }
</style>
""", unsafe_allow_html=True)

# === API cấu hình
# API_ENDPOINT = "http://localhost:5001/chat"
API_ENDPOINT = "https://agentic-rag-597624481467.asia-southeast1.run.app/chat"
HEADERS = {"Content-Type": "application/json"}

# === Trạng thái session
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# === Hiển thị tiêu đề động
st.markdown("""
    <div class="header-container">
        <div class="header-title">
            <span style="font-size: 2.5rem;">🤖</span>
            Agentic RAG Assistant
        </div>
        <div class="header-subtitle">
            Trợ lý thông minh với khả năng tìm kiếm và trả lời chính xác
        </div>
    </div>
""", unsafe_allow_html=True)

# === Main chat container
chat_container = st.container()


# === Hiển thị lịch sử chat
def display_messages():
    with chat_container:
        for message in st.session_state.messages:
            role = message["role"]
            content = message["content"]
            timestamp = message.get("timestamp", datetime.now().strftime("%H:%M"))

            avatar_url = "https://api.dicebear.com/7.x/bottts/svg?seed=assistant" if role == "assistant" else "https://api.dicebear.com/7.x/personas/svg?seed=user"

            st.markdown(f"""
            <div class="chat-message {role}">
                <img class="avatar" src="{avatar_url}" />
                <div class="message-content">
                    <div>{content}</div>
                    <div class="message-timestamp">{timestamp}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# === Gửi tin nhắn
def send_message():
    user_input = st.session_state.get("user_input", "")
    if not user_input.strip():
        return

    # Thêm timestamp
    timestamp = datetime.now().strftime("%H:%M")

    # Append user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": timestamp
    })

    # Show loading indicator
    with st.spinner("🤔 Đang xử lý..."):
        try:
            response = requests.post(API_ENDPOINT, json={
                "message": user_input,
                "thread_id": st.session_state.thread_id
            }, headers=HEADERS)

            if response.status_code == 200:
                assistant_content = response.json()["content"]
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_content,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
            else:
                st.error(f"❌ Lỗi: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"⚠️ Lỗi kết nối: {e}")


# === Hiển thị tin nhắn
display_messages()

# === Giao diện nhập tin nhắn
with st.form(key="chat_form", clear_on_submit=True):
    cols = st.columns([11, 2])
    with cols[0]:
        st.text_input(
            "💬",
            key="user_input",
            label_visibility="collapsed",
            placeholder="Nhập câu hỏi của bạn..."
        )
    with cols[1]:
        submit_button = st.form_submit_button(
            "Gửi ✨",
            on_click=send_message,
            type="primary"
        )

# === Sidebar với các tính năng
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 🎛️ Bảng điều khiển")

    if st.button("🔄 Bắt đầu cuộc trò chuyện mới", type="primary"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    if st.button("💾 Lưu lịch sử chat"):
        if st.session_state.messages:
            chat_history = "\n\n".join(
                [f"{msg['role'].upper()}: {msg['content']}" for msg in st.session_state.messages])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"chat_history_{timestamp}.txt"
            st.download_button(
                label="📥 Tải xuống",
                data=chat_history,
                file_name=file_name,
                mime="text/plain"
            )
        else:
            st.info("Chưa có tin nhắn để lưu.")

    st.markdown("</div>", unsafe_allow_html=True)

    # === Câu hỏi gần đây
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 📜 Câu hỏi gần đây")

    previous_questions = [msg for msg in st.session_state.messages if msg["role"] == "user"]

    if previous_questions:
        for i, q in enumerate(reversed(previous_questions[-5:])):  # Hiển thị 5 câu hỏi gần nhất
            if st.button(f"🗨️ {q['content'][:50]}...", key=f"resend_{i}"):
                try:
                    with st.spinner("🔄 Đang gửi lại..."):
                        response = requests.post(API_ENDPOINT, json={
                            "message": q['content'],
                            "thread_id": st.session_state.thread_id
                        }, headers=HEADERS)

                        if response.status_code == 200:
                            assistant_content = response.json()["content"]
                            timestamp = datetime.now().strftime("%H:%M")
                            st.session_state.messages.append({
                                "role": "user",
                                "content": q['content'],
                                "timestamp": timestamp
                            })
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": assistant_content,
                                "timestamp": timestamp
                            })
                            st.rerun()
                except Exception as e:
                    st.error(f"⚠️ Lỗi khi gửi lại: {e}")
    else:
        st.caption("Chưa có câu hỏi nào.")

    st.markdown("</div>", unsafe_allow_html=True)

    # === Thông tin phiên
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### ℹ️ Thông tin phiên")
    st.caption(f"🧵 ID phiên: `{st.session_state.thread_id}`")
    st.caption(f"💬 Số tin nhắn: {len(st.session_state.messages)}")
    st.caption(f"🕒 Thời gian: {datetime.now().strftime('%H:%M:%S')}")
    st.markdown("</div>", unsafe_allow_html=True)

# === Thêm shortcut
if st.session_state.get("user_input"):
    st.markdown("""
    <script>
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                document.querySelector('button[type="submit"]').click();
            }
        });
    </script>
    """, unsafe_allow_html=True)