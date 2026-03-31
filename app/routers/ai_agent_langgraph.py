from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.graph_service import student_graph 
from langchain_core.messages import HumanMessage
from app.services.auth_service import get_current_user
from app.models import TaiKhoan

router = APIRouter(prefix="/ai", tags=["AI Agent"])

class ChatRequest(BaseModel):
    question: str
    thread_id: str

# 2. Yêu cầu nộp thẻ bằng Depends(get_current_user)
@router.post("/chat")
async def chat_with_student_data(
    request: ChatRequest,
    current_user: TaiKhoan = Depends(get_current_user) 
):
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # 3. Gửi câu hỏi kèm theo thông tin User (Tên + Quyền) vào Graph
        inputs = {
            "messages": [
                HumanMessage(content=request.question)
            ],
            "user_role": current_user.role,       
            "user_id": current_user.username      
        }
        
        result = await student_graph.ainvoke(inputs, config=config)
        
        return {
            "answer": result.get("answer"),
            "chart": result.get("chart_img")
        }
    except Exception as e:
        print(f"Lỗi thực thi Graph: {str(e)}")
        raise HTTPException(status_code=500, detail="Hệ thống AI đang bận, vui lòng thử lại sau.")
