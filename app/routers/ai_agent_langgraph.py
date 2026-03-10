from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
# Import graph đã compile từ graph_service
from app.services.graph_service import student_graph 

router = APIRouter(prefix="/ai", tags=["AI Agent"])

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
async def chat_with_student_data(request: ChatRequest):
    try:
        config = {"configurable": {"thread_id": "user_session_001"}}
        # Chạy luồng qua 7 Nodes
        # Kết quả trả về là toàn bộ State cuối cùng của Graph
        inputs = {"question": request.question}
        result = student_graph.invoke(inputs, config = config)
        
        # Trả về câu trả lời cuối cùng từ Node 7
        return {"answer": result["answer"]}

    except Exception as e:
        print(f"Lỗi thực thi Graph: {str(e)}")
        raise HTTPException(status_code=500, detail="Hệ thống AI đang bận, vui lòng thử lại sau.")