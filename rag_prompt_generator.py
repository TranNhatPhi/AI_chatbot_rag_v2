# ✅ rag_prompt_generator.py
from yes_client import call_yescale

def generate_contextual_prompt(user_question: str, history: list[str] = []) -> str:
    """
    Tạo prompt mới thân thiện và có định hướng từ câu hỏi gốc + lịch sử trò chuyện.
    """
    system_prompt = (
        "Bạn là chuyên gia tạo prompt cho chatbot tư vấn tuyển sinh Trường Đại học Luật TP.HCM."
        " Hãy viết lại câu hỏi dưới định dạng hoàn chỉnh, dễ hiểu hơn, thân thiện và mang tính trò chuyện."
        " Đảm bảo chính xác và rõ ràng, không mơ hồ. Nếu có lịch sử câu hỏi, tránh lặp lại nội dung."
        " Thêm 1 câu hỏi mở rộng để khơi gợi người dùng tiếp tục trò chuyện."
    )

    history_block = "\n".join(f"- {q}" for q in history[-3:])  # Lấy 3 câu gần nhất
    user_prompt = f"""
Câu hỏi hiện tại: "{user_question}"
Lịch sử hội thoại trước đó:
{history_block if history_block else "(Không có)"}

➡️ Hãy viết lại câu hỏi tối ưu hơn + thêm 1 câu hỏi mở rộng tự nhiên.
"""
    result = call_yescale(system_prompt, user_prompt)
    return result
