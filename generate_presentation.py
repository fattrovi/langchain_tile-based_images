from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
import os,sys
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory

def save_to_file(directory, filename, content):
    os.makedirs(directory, exist_ok=True)
    try:
        with open(os.path.join(directory, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"文件已成功寫入：{directory}{filename}")
    except Exception as e:
        print(f"寫入 {filename} 時發生錯誤: {e}")

def read_markdown_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"讀取文件md檔時發生錯誤: {e}")
        return None
store = {}   
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]    

def generate_langchain(markdown_content):

    os.environ['OPENAI_API_KEY'] = 'API_KEY'

    output_parser = StrOutputParser()

    # Create the agent
    memory = MemorySaver()

    #設置 OpenAI API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("API Key 未設置。請將 API Key 設置為環境變數 'OPENAI_API_KEY'。")
    os.environ["OPENAI_API_KEY"] = api_key

    config = {"configurable": {"thread_id": "abc123"}}
    # 設置模型
    model = ChatOpenAI(model_name="gpt-4o", api_key=api_key)
    

    prompthtml = ChatPromptTemplate.from_messages([
        ("system", """
        請根據以下 Markdown 內容生成一個符合 Bento Grid 風格的 HTML 文件。
        
        需求：
        1. 網頁包含兩部分：
            - **按鈕區域**：位於頁面底部，使用 `<div id="button-container">` 容器，包含 `<button id="capture-btn">`。
            - **內容區域**：主體使用 `<div class="bento-grid">` 容器，並分為若干獨立區塊，每個區塊用 `<div class="grid-item">` 容納。
        2. HTML 應遵循以下結構：
            - 頂部添加 `<head>`，包含 meta 信息、標題、樣式表鏈接和必要的腳本。
            - 主內容使用 Grid 布局，確保所有區塊充滿 16:9 的比例。
        3. 內容區域細分為多個區塊：
            - 標題（使用 `<h1>` 或 `<h2>`）；
            - 段落（使用 `<p>`）；
            - 若內容過長，請動態調整格子大小，確保顯示完整。
        4. 代碼格式要求：
            - 縮排使用兩個空格；
            - 添加必要註解，描述區域結構。

        請直接輸出完整的 HTML 文件，不需要外部代碼塊標記。
        
        Markdown 內容如下：
        {markdown_content}
        """),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "{markdown_content}"),

    ])
    chainhtml = prompthtml | model | output_parser

    config_html = {"configurable": {"session_id": "html_agent"}}

    with_message_html_history = RunnableWithMessageHistory(chainhtml, get_session_history, input_messages_key="messages")

    html_content = with_message_html_history.invoke(
        {"messages": [HumanMessage(content="請依照上述要求，生成 HTML 結構")],
        "markdown_content": markdown_content},
        config=config_html,
    )

    html_content

    # 檔案存儲位置
    output_dir = "./output_files/"
    os.makedirs(output_dir, exist_ok=True)

    save_to_file(output_dir, "test.html", html_content)

    html_content = with_message_html_history.invoke(
        {"messages": [HumanMessage(content="請輸出空白的html")],
        "markdown_content": markdown_content},
        config=config_html,
    )

    save_to_file(output_dir, "test.html", html_content)

    promptcss = ChatPromptTemplate.from_messages([
        ("system", """
        根據以下 HTML 結構，生成符合 Bento Grid 排版的 CSS 文件。
        要求：
        1. 對 .bento-grid：
        - 使用 `display: grid` 排版。
        - 自適應內容區塊大小，整體填滿 16:9 的比例。
        - 適當設置區塊間距（如 1rem）。
        2. 對 .grid-item：
        - 根據內容動態調整大小，寬高比保持合適，使用 `minmax` 和 `auto` 實現靈活布局。
        - 增加背景陰影、圓角等樣式，提升簡報風格。
        3. 動態調整 `grid-auto-rows`，確保每個區塊大小與內容匹配。
        4. 確保 `.bento-grid` 填滿父容器，無多餘空間。
        5. 對 #button-container 和 #capture-btn：
        - 按鈕置於頁面底部中央，適配整體風格。
        6. 顏色上請參考深色模式為內文、配色主題。
        7. 直接生成CSS檔即可，若有需要另外的文字描述，請使用備註，不要顯示上去
        HTML 結構如下：
        {html_content}

        請輸出完整的 CSS 文件。
        """),
        MessagesPlaceholder(variable_name="messages"),


    ])
    chaincss = promptcss | model | output_parser

    config_css = {"configurable": {"session_id": "css_agent"}}

    with_message_css_history = RunnableWithMessageHistory(chaincss, get_session_history, input_messages_key="messages")

    css_content = with_message_css_history.invoke(
        {"messages": [HumanMessage(content="請依照上述要求，生成 css 結構")],
        "html_content": html_content},
        config=config_css,
    )

    css_content
    save_to_file(output_dir, "test.css", css_content)

    css_content = with_message_css_history.invoke(
        {"messages": [HumanMessage(content="請生成空白的 css  結構")],
        "html_content": html_content},
        config=config_css,
    )

    css_content
    save_to_file(output_dir, "test.css", css_content)

    promptjs = ChatPromptTemplate.from_messages([
        ("system", """
        根據以下 HTML 和 CSS，撰寫 JavaScript 代碼。
        功能需求：
        1. 選取需要截圖的區域為 .bento-grid，並使用 `html2canvas` 將其轉換為 PNG。
        2. 在截圖過程中，暫時隱藏 #capture-btn 按鈕，截圖完成後恢復顯示。
        3. 確保圖片解析度足夠高（使用 `scale: 3`）。
        4. 增加錯誤處理，捕捉任何異常並提示用戶。
        5. 按鈕樣式應適配截圖功能，並與頁面整體風格一致。
        6. 確保正確引用 html2canvas 並選取 .bento-grid 作為截圖對象，按鈕 (id="capture-btn") 點擊後執行截圖，隱藏按鈕並恢復。
        HTML 結構：
        {html_content}

        CSS 樣式：
        {css_content}

        請輸出完整的 JavaScript 文件。
        """),
        MessagesPlaceholder(variable_name="messages"),


    ])
    chainjs = promptjs | model | output_parser

    config_js = {"configurable": {"session_id": "js_agent"}}

    with_message_js_history = RunnableWithMessageHistory(chainjs, get_session_history, input_messages_key="messages")

    js_content = with_message_js_history.invoke(
        {"messages": [HumanMessage(content="請依照上述要求，生成 js 結構")],
        "html_content": html_content,
        "css_content": css_content},
        config=config_js,
    )

    js_content
    save_to_file(output_dir, "test.js", js_content)

    s_content = with_message_js_history.invoke(
        {"messages": [HumanMessage(content="請生成空白的 js 結構")],
        "html_content": html_content,
        "css_content": css_content},
        config=config_js,
    )

    js_content
    save_to_file(output_dir, "test.js", js_content)

    html_content = with_message_html_history.invoke(
        {"messages": [HumanMessage(content="按照我上次叫你的輸出，但在第一格輸出topic")],
        "markdown_content": markdown_content},
        config=config_html,
    )

    save_to_file(output_dir, "test.html", html_content)
def generate_presentation(file_path):
    if not os.path.exists(file_path):
        print("檔案不存在", file=sys.stderr)
        sys.exit(1)

    # 假設這裡是你原始的生成邏輯，將生成的簡報儲存為一個新檔案
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 這裡放入簡報生成的邏輯
        file_path = file_path.split("\\")[-1].replace('.md', '_presentation.html')
        generated_file_path = f"./generated/{file_path}"
        with open(generated_file_path, 'w', encoding='utf-8') as f:
            f.write(f'<html><body><h1>這是生成的簡報</h1><pre>{content}</pre></body></html>')

        print(f'生成成功，檔案位於 {generated_file_path}')
    except Exception as e:
        print(f'生成失敗3: {e}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("請提供檔案路徑", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    markdown_content = read_markdown_file(file_path)
    generate_langchain(markdown_content)
    
    
    
