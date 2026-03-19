from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.services.graph_service import student_graph 
from langchain_core.messages import HumanMessage, SystemMessage
from app.prompts.prompts import SYSTEM_PROMPT
router = APIRouter(prefix="/ai", tags=["AI Agent"])

class ChatRequest(BaseModel):
    question: str
    thread_id: str

@router.post("/chat")
async def chat_with_student_data(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        # Kết quả trả về là toàn bộ State cuối cùng của Graph
        inputs = {
    "messages": [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=request.question)
    ]
}
        result = await student_graph.ainvoke(inputs, config = config)
        
        return {"answer": result.get("answer"),
                "chart": result.get("chart_img")}
    except Exception as e:
        print(f"Lỗi thực thi Graph: {str(e)}")
        raise HTTPException(status_code=500, detail="Hệ thống AI đang bận, vui lòng thử lại sau.")
