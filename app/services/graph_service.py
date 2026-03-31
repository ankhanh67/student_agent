import io
import ast
import base64
import pandas as pd
from typing import Annotated, List
from typing_extensions import TypedDict
from datetime import date, datetime
from sqlalchemy import text
from app.database import SessionLocal
from app.prompts.prompts import SYSTEM_PROMPT
from langchain_core.messages import (
    BaseMessage,
    ToolMessage,
    HumanMessage,
    SystemMessage,
    AIMessage
)
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver  
import asyncio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# LOAD SCHEMA
with open("app/docs/schema_database.md", "r", encoding="utf-8") as f:
    DB_SCHEMA = f.read()

# SQL TOOL
def execute_read_only_query(sql_query: str):
    if not sql_query.strip().lower().startswith("select"):
        return "Lỗi: Chỉ cho phép SELECT."

    db = SessionLocal()

    try:
        result = db.execute(text(sql_query.strip().rstrip(";")))
        columns = result.keys()
        rows = result.fetchall()

        if not rows:
            return []

        data = []
        for row in rows:
            row_dict = dict(zip(columns, row))

            for k, v in row_dict.items():
                if isinstance(v, (date, datetime)):
                    row_dict[k] = v.isoformat()

            data.append(row_dict)

        return data

    except Exception as e:
        return f"Lỗi SQL: {str(e)}"

    finally:
        db.close()


@tool
def db_query_tool(sql_query: str) -> str:
    """Chạy SQL SELECT"""
    return str(execute_read_only_query(sql_query))

# CHART TOOL
@tool
def plot_chart_tool(data: str) -> str:
    """Vẽ chart từ data"""

    try:
        data = ast.literal_eval(data)
        df = pd.DataFrame(data)

        if df.empty or len(df.columns) < 2:
            return ""

        x = df.columns[0]
        y = df.columns[1]

        plt.figure()

        if len(df) <= 6:
            plt.pie(df[y], labels=df[x], autopct="%1.1f%%")
        else:
            plt.bar(df[x], df[y])

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)

        img = base64.b64encode(buf.read()).decode()
        plt.close()

        return img

    except Exception:
        return ""

# STATE

class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    answer: str
    chart_img: str
    iterations : int
    user_role: str
    user_id: str
llm = init_chat_model(
    "google_genai:gemini-3.1-flash-lite-preview",  
    temperature=0
)

tools = [db_query_tool, plot_chart_tool]
llm_with_tools = llm.bind_tools(tools)
# CHATBOT NODE
async def chatbot_node(state: State):
    messages = state.get("messages", [])
    
    # Lấy thông tin người dùng từ State
    user_role = state.get("user_role", "Khach") 
    user_id = state.get("user_id", "")

    # 1. 🛡️ XÂY DỰNG LỆNH TỐI CAO (Động theo từng User)
    security_rules = ""
    if user_role == "SinhVien":
        security_rules = f"""
        [LỆNH TỐI CAO - BẢO MẬT HỆ THỐNG]
        Người dùng hiện tại là SINH VIÊN, mã số: '{user_id}'.
        1. Bạn BẮT BUỘC chèn điều kiện `id_sinh_vien = '{user_id}'` vào MỌI CÂU LỆNH SQL mà bạn sinh ra.
        2. NẾU người dùng yêu cầu thông tin (tên, điểm, mã, sđt...) của BẤT KỲ AI KHÁC ngoài '{user_id}', BẠN PHẢI TỪ CHỐI NGAY LẬP TỨC và KHÔNG được sinh ra câu lệnh SQL.
        3. Câu trả lời mẫu khi từ chối: "Xin lỗi, vì lý do bảo mật, bạn chỉ được phép truy cập dữ liệu của chính mình (Mã: {user_id})."
        """
    elif user_role == "GiangVien":
        security_rules = f"""
        [LỆNH TỐI CAO - BẢO MẬT HỆ THỐNG]
        Người dùng hiện tại là GIẢNG VIÊN, mã số: '{user_id}'.
        1. BẠN BẮT BUỘC PHẢI THÊM ĐIỀU KIỆN `id_giang_vien = '{user_id}'` vào TẤT CẢ các truy vấn SQL (JOIN nếu cần).
        2. TUYỆT ĐỐI TỪ CHỐI cung cấp dữ liệu của các lớp học phần do giảng viên khác phụ trách.
        """
    else:
        security_rules = "Tình trạng: Admin. Bạn có toàn quyền truy vấn và thống kê mọi dữ liệu."

    # 2. TỔNG HỢP PROMPT HOÀN CHỈNH
    full_system_prompt = f"{SYSTEM_PROMPT}\n\nSchema Database:\n{DB_SCHEMA}\n\n{security_rules}"
    system_msg = SystemMessage(content=full_system_prompt)

    # 3. LỌC BỎ RÁC TRONG BỘ NHỚ
    # Xóa các SystemMessage cũ trong lịch sử để tránh AI bị bối rối/chồng chéo luật
    filtered_messages = [m for m in messages if not isinstance(m, SystemMessage)]
    
    # Ép luật mới nhất lên đầu danh sách tin nhắn gửi đi
    messages_to_llm = [system_msg] + filtered_messages

    # Gọi AI
    response = await llm_with_tools.ainvoke(messages_to_llm)
    
    return {
        "messages": [response], # Chỉ lưu câu trả lời của AI vào State
        "iterations": 0 
    }
# TOOL NODE
class ToolNode:

    def __init__(self, tools: list):
        self.tools_by_name = {tool.name: tool for tool in tools}

    async def __call__(self, state: State):

        last_message = state["messages"][-1]

        outputs = []

        for tool_call in last_message.tool_calls:

            name = tool_call["name"]
            args = tool_call["args"]

            result = await asyncio.to_thread(
                self.tools_by_name[name].invoke,
                args
            )

            outputs.append(
                ToolMessage(
                    content=str(result),
                    name=name,
                    tool_call_id=tool_call["id"],
                )
            )

        return {"messages": outputs}
# Reflection
async def revise_node(state: State):
    messages = state["messages"]
    messages_to_llm = state["messages"] + [
        SystemMessage(content="Kiểm tra kết quả trên. Nếu có lỗi SQL hoặc kết quả không logic, hãy sửa lại tool call bằng công cụ. Nếu đã ổn, hãy tóm tắt và trả lời người dùng.")
    ]
    response = await llm_with_tools.ainvoke(messages_to_llm)
    return {
        "messages": [response],
        "iterations": state.get("iterations", 0) + 1
    }

# ROUTER
def route_tools(state:State):
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return 'tools'
    return 'final'
def route_after_tools(state: State):

    last_message = state["messages"][-1]

    if state.get('iterations',0) >2:
        return "final"
    return "revise"
def route_after_revise(state:State):
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return 'tools'
    return 'final'
# FINAL NODE 
def final_node(state: State):
    messages = state["messages"]
    last_msg = messages[-1]
    answer = ""
    chart_img = ""
        
    if isinstance(last_msg, AIMessage):

        content = last_msg.content

        if isinstance(content, str):
            answer = content

        elif isinstance(content, list):
        
            texts = [c.get("text", "") for c in content if c.get("type") == "text"]
            answer = " ".join(texts)

    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            break
            
        if isinstance(msg, ToolMessage) and msg.name == "plot_chart_tool":
            chart_img = msg.content
            break

    return {
        "answer": answer,
        "chart_img": chart_img
    }
# BUILD GRAPH
def build_graph():
    graph = StateGraph(State)
    graph.add_node("chatbot", chatbot_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node('revise', revise_node)
    graph.add_node("final", final_node)
    graph.add_edge(START, "chatbot")
    graph.add_conditional_edges(
        "chatbot",
        route_tools,
        {
            "tools": "tools",
            "final": "final"
        }
    )
    graph.add_conditional_edges(
        "tools",
        route_after_tools,
        {"revise":"revise",
         "final":"final"}
    )
    graph.add_conditional_edges(
        "revise",
        route_after_revise,
        {"tools":"tools",
         "final":"final"}
    )
    graph.add_edge("final", END)
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)
student_graph = build_graph()
