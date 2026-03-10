from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.services.agent_service import ask_student_agent

router = APIRouter(prefix="/ai", tags=["AI Agent"])


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
async def chat_with_student_data(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat với dữ liệu sinh viên bằng ngôn ngữ tự nhiên
    """
    try:
        answer = ask_student_agent(request.question, db)
        return {"answer": answer}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))