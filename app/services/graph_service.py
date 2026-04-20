from typing import Annotated, List
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, ToolMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver  
from app.prompts.prompts import SYSTEM_PROMPT

# Import MCP Client & contextlib
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
# from mcp.client.stdio import stdio_client

# # Cấu hình kết nối tới MCP Server
# mcp_server_params = StdioServerParameters(
#     command="python",
#     args=["mcp_server/server.py"], 
# )

# STATE
class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    answer: str
    chart_url: str  # <--- Lưu URL thay vì Base64
    iterations : int
    user_role: str
    user_id: str

llm = init_chat_model("google_genai:gemini-2.5-flash", temperature=0)

# --- KHỞI TẠO MCP & MAP TOOLS (PERSISTENT SESSION) ---
DB_SCHEMA = ""
mcp_exit_stack = AsyncExitStack()
mcp_global_session = None

# async def load_mcp_resources():
#     """Hàm này được gọi từ app/main.py lúc startup để thiết lập kết nối duy nhất"""
#     global DB_SCHEMA, mcp_global_session
    
#     # Sử dụng exit_stack để duy trì context ngầm thay vì đóng lại
#     read, write = await mcp_exit_stack.enter_async_context(stdio_client(mcp_server_params))
#     mcp_global_session = await mcp_exit_stack.enter_async_context(ClientSession(read, write))
    
#     await mcp_global_session.initialize()
    
#     # Tải Resource Schema một lần và lưu vào DB_SCHEMA
#     res = await mcp_global_session.read_resource("schema://database")
#     if res:
#         DB_SCHEMA = res.contents[0].text
async def load_mcp_resources():
    """Hàm này được gọi từ app/main.py lúc startup để thiết lập kết nối duy nhất"""
    global DB_SCHEMA, mcp_global_session
    
    # Địa chỉ của MCP Server chạy qua SSE
    sse_url = "http://127.0.0.1:5000/sse"
    
    # Kết nối bằng sse_client thay vì stdio_client
    read, write = await mcp_exit_stack.enter_async_context(sse_client(sse_url))
    mcp_global_session = await mcp_exit_stack.enter_async_context(ClientSession(read, write))
    
    await mcp_global_session.initialize()
    
    # Tải Resource Schema một lần và lưu vào DB_SCHEMA
    res = await mcp_global_session.read_resource("schema://database")
    if res:
        DB_SCHEMA = res.contents[0].text
async def call_mcp_tool(tool_name: str, args: dict):
    """Proxy gọi tool qua Global Session đã kết nối (tốc độ cao)"""
    if not mcp_global_session:
        return "Lỗi: Chưa thiết lập kết nối tới MCP Server."
        
    result = await mcp_global_session.call_tool(tool_name, arguments=args)
    return result.content[0].text

@tool
async def db_query_tool(sql_query: str) -> str:
    """Chạy SQL SELECT qua MCP Server"""
    return await call_mcp_tool("execute_read_only_query", {"sql_query": sql_query})

@tool
async def plot_chart_tool(data: str, chart_type: str = "bar") -> str:
    """Vẽ chart từ data qua MCP Server. Trả về mã Base64 của hình ảnh."""
    return await call_mcp_tool("plot_chart_tool", {"data": data, "chart_type": chart_type})

tools = [db_query_tool, plot_chart_tool]
llm_with_tools = llm.bind_tools(tools)

# --- LANGGRAPH NODES ---

async def chatbot_node(state: State):
    messages = state.get("messages", [])
    user_role = state.get("user_role", "Khach") 
    user_id = state.get("user_id", "")

    security_rules = ""
    if user_role == "SinhVien":
        security_rules = f"""
        [LỆNH TỐI CAO - BẢO MẬT HỆ THỐNG]
        Người dùng hiện tại là SINH VIÊN, mã số: '{user_id}'.
        1. Bạn BẮT BUỘC chèn điều kiện `id_sinh_vien = '{user_id}'` vào MỌI CÂU LỆNH SQL mà bạn sinh ra.
        2. NẾU người dùng yêu cầu thông tin của ai khác, TỪ CHỐI NGAY LẬP TỨC.
        """
    elif user_role == "GiangVien":
        security_rules = f"""
        [LỆNH TỐI CAO - BẢO MẬT HỆ THỐNG]
        Người dùng hiện tại là GIẢNG VIÊN, mã số: '{user_id}'.
        1. BẮT BUỘC THÊM ĐIỀU KIỆN `id_giang_vien = '{user_id}'` vào TẤT CẢ các truy vấn SQL.
        """
    else:
        security_rules = "Tình trạng: Admin. Bạn có toàn quyền truy vấn."

    full_system_prompt = f"{SYSTEM_PROMPT}\n\nSchema Database:\n{DB_SCHEMA}\n\n{security_rules}"
    system_msg = SystemMessage(content=full_system_prompt)
    
    filtered_messages = [m for m in messages if not isinstance(m, SystemMessage)]
    messages_to_llm = [system_msg] + filtered_messages

    response = await llm_with_tools.ainvoke(messages_to_llm)
    return {"messages": [response], "iterations": 0}

class ToolNode:
    def __init__(self, tools: list):
        self.tools_by_name = {tool.name: tool for tool in tools}

    async def __call__(self, state: State):
        last_message = state["messages"][-1]
        outputs = []
        chart_url = ""

        for tool_call in last_message.tool_calls:
            name = tool_call["name"]
            args = tool_call["args"]

            result = await self.tools_by_name[name].ainvoke(args)

            if name == "plot_chart_tool":
                chart_url = result # Lúc này biến result đang chứa nguyên chuỗi Base64
                outputs.append(
                    ToolMessage(
                        content="Đã vẽ biểu đồ thành công. Đã lưu hình ảnh dưới dạng Base64 ẩn.",  
                        name=name,
                        tool_call_id=tool_call["id"],
                    )
                )
            else:
                outputs.append(
                    ToolMessage(
                        content=str(result),
                        name=name,
                        tool_call_id=tool_call["id"],
                    )
                )

        return {"messages": outputs, "chart_url": chart_url}

async def revise_node(state: State):
    messages_to_llm = state["messages"] + [
        SystemMessage(content="Kiểm tra kết quả trên. Nếu có lỗi SQL hãy sửa lại. Nếu đã ổn, hãy tóm tắt và trả lời người dùng.")
    ]
    response = await llm_with_tools.ainvoke(messages_to_llm)
    return {"messages": [response], "iterations": state.get("iterations", 0) + 1}

def route_tools(state:State):
    if state['messages'][-1].tool_calls: return 'tools'
    return 'final'

def route_after_tools(state: State):
    if state.get('iterations',0) > 2: return "final"
    return "revise"

def route_after_revise(state:State):
    if state['messages'][-1].tool_calls: return 'tools'
    return 'final'

def final_node(state: State):
    last_msg = state["messages"][-1]
    answer = ""
    chart_url = state.get("chart_url", "")
        
    if isinstance(last_msg, AIMessage):
        if isinstance(last_msg.content, str):
            answer = last_msg.content
        elif isinstance(last_msg.content, list):
            answer = " ".join([c.get("text", "") for c in last_msg.content if c.get("type") == "text"])

    return {"answer": answer, "chart_url": chart_url}

def build_graph():
    graph = StateGraph(State)
    graph.add_node("chatbot", chatbot_node)
    graph.add_node("tools", ToolNode(tools))
    graph.add_node('revise', revise_node)
    graph.add_node("final", final_node)
    
    graph.add_edge(START, "chatbot")
    graph.add_conditional_edges("chatbot", route_tools, {"tools": "tools", "final": "final"})
    graph.add_conditional_edges("tools", route_after_tools, {"revise":"revise", "final":"final"})
    graph.add_conditional_edges("revise", route_after_revise, {"tools":"tools", "final":"final"})
    graph.add_edge("final", END)
    
    return graph.compile(checkpointer=MemorySaver())

student_graph = build_graph()
