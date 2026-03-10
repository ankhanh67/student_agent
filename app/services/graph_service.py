import json
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.services.agent_service import client, clean_sql
from app.services.tools import get_database_schema, db_query_tool
from app.prompts.prompts import SYSTEM_PROMPT, RESPONSE_PROMPT
from langgraph.checkpoint.memory import MemorySaver
class AgentState(TypedDict):
    question: str
    sql_query: str
    raw_data: Optional[str]
    error: Optional[str]
    retry_count: int
    answer: str
    history: Optional[str]

# --- CÁC NODES ĐÃ TỐI ƯU ---

def node_1_normalize(state: AgentState):
    print("\n" + "="*30)
    print("--- NODE 1: NORMALIZE & FETCH SCHEMA ---")
    # Sử dụng tool trực tiếp để lấy metadata ngay từ bước đầu
    schema = get_database_schema.invoke({}) 
    return {"question": state['question'], "raw_data": schema, "retry_count": 0}

def node_2_generate_sql(state: AgentState):
    print("--- NODE 2: GENERATE SQL ---")
    
    # Kết hợp Schema và Lịch sử vào Prompt
    history_context = f"\nLịch sử cũ: {state.get('history', '')}"
    prompt = f"Schema: {state['raw_data']}{history_context}\nCâu hỏi: {state['question']}"
    
    if state.get('error'):
        prompt += f"\nSửa lỗi: {state['error']}. Phải giữ điều kiện lọc của câu trước."

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", 
        config={"system_instruction": SYSTEM_PROMPT},
        contents=prompt
    )
    sql_query = clean_sql(response.text)
    print(f"SQL: {sql_query}")
    return {"sql_query": sql_query}

# def node_3_validate_sql(state: AgentState):
#     print("--- NODE 3: VALIDATE SQL ---")
#     # Lấy SQL ĐÃ SINH từ Node 2
#     current_sql = state.get('sql_query') 
    
#     # CHỈ KIỂM TRA, KHÔNG SINH LẠI
#     if not current_sql or "SELECT" not in current_sql.upper():
#         return {"error": "SQL không hợp lệ hoặc bị trống!"}
    
#     # Nếu SQL đã có điều kiện WHERE (từ Node 2), hãy giữ nguyên nó
#     print(f"SQL được bảo toàn: {current_sql}")
#     return {"error": None}

def node_4_execute_sql(state: AgentState):
    # Thực thi SQL thông qua tool đã đóng gói
    print("--- NODE 4: EXECUTE SQL ---")
    result = db_query_tool.invoke({"sql_query": state['sql_query']})
    if "Lỗi" in result:
        return {"error": result}
    return {"raw_data": result, "error": None}

def node_5_fix_sql(state: AgentState):
    count = state['retry_count'] + 1
    print(f"--- NODE 5: FIX SQL (Lần thử thứ {count}) ---")
    return {"retry_count": state['retry_count'] + 1}

def node_6_format_result(state: AgentState):
    # Đảm bảo dữ liệu thô được chuẩn hóa thành text sạch
    print("--- NODE 6: FORMAT RESULT ---")
    return {"raw_data": str(state['raw_data'])}

def node_7_generate_answer(state: AgentState):
    print("--- NODE 7: GENERATE ANSWER ---")
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        config={"system_instruction": RESPONSE_PROMPT},
        contents=f"Câu hỏi: {state['question']}\nKết quả: {state['raw_data']}"
    )
    # Lưu vết để câu hỏi sau biết 'họ' là ai
    new_history = f"Q: {state['question']} | SQL: {state['sql_query']}" 
    return {"answer": response.text, "history": new_history}

# --- KHỞI TẠO GRAPH ---
workflow = StateGraph(AgentState)

workflow.add_node("n1", node_1_normalize)
workflow.add_node("n2", node_2_generate_sql)
# Đã xóa n3
workflow.add_node("n4", node_4_execute_sql)
workflow.add_node("n5", node_5_fix_sql)
workflow.add_node("n6", node_6_format_result)
workflow.add_node("n7", node_7_generate_answer)

workflow.set_entry_point("n1")
workflow.add_edge("n1", "n2")
workflow.add_edge("n2", "n4") # Nối thẳng sang Execute

# Điều hướng dựa trên kết quả thực thi
workflow.add_conditional_edges(
    "n4", 
    lambda x: "n5" if x.get("error") and x["retry_count"] < 3 else "n6"
)

workflow.add_edge("n5", "n2")
workflow.add_edge("n6", "n7")
workflow.add_edge("n7", END)

memory = MemorySaver()
student_graph = workflow.compile(checkpointer=memory)