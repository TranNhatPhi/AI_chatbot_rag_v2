from agents import function_tool
import webbrowser

@function_tool(name="open_google", description="Mở trang Google trên trình duyệt")
def open_google():
    webbrowser.open("https://www.google.com")
    return "Đã mở trang Google."

@function_tool(name="search_google", description="Tìm kiếm từ khoá trên Google")
def search_google(query: str):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Đã tìm kiếm '{query}' trên Google."
