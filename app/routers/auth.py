# File: app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TaiKhoan
from app.services.auth_service import create_access_token
from passlib.context import CryptContext

# Công cụ băm để kiểm tra mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(tags=["Authentication"])

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Tìm user trong DB bằng username
    user = db.query(TaiKhoan).filter(TaiKhoan.username == form_data.username).first()
    
    # 2. So sánh mật khẩu người dùng gõ với mật khẩu băm trong DB
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Tạo thẻ Token nhét sẵn thông tin vào Payload
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    
    # 4. Trả thẻ về cho Streamlit
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role,           
        "username": user.username
    }
