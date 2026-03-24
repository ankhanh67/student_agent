import os
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
    interations : str
llm = init_chat_model(
    "google_genai:gemini-3.1-flash-lite-preview",  
    temperature=0
)

tools = [db_query_tool, plot_chart_tool]
llm_with_tools = llm.bind_tools(tools)
# CHATBOT NODE
async def chatbot_node(state: State):

    messages = state.get("messages", [])

    if not messages:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content="Xin chào")
        ]

    response = await llm_with_tools.ainvoke(messages)

    return {
        "messages": messages + [response]
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
    """
    Node này đóng vai trò 'phản tỉnh'. Nó nhìn vào kết quả của Tool 
    để quyết định xem có cần sửa lại hay không.
    """
    messages = state["messages"]
    messages.append(SystemMessage(content="Kiểm tra kết quả trên. Nếu có lỗi SQL hoặc kết quả không logic, hãy sửa lại tool call. Nếu đã ổn, hãy trả lời người dùng."))
    response = await llm_with_tools.ainvoke(messages)
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

    if state.get('interations',0) >3:
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
