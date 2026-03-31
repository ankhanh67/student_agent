from datetime import datetime, timedelta
from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import TaiKhoan

SECRET_KEY = "HETHONG_QUANLY_SINHVIEN_BI_MAT_SIEU_CAP" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 1. Hàm tạo Thẻ từ (Sinh JWT)
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 2. Hàm kiểm tra Thẻ (Xác thực người dùng)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Không thể xác thực thông tin thẻ (Token không hợp lệ hoặc đã hết hạn)",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if username is None or role is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # Kiểm tra xem người này còn tồn tại trong DB không
    user = db.query(TaiKhoan).filter(TaiKhoan.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# 3. Class kiểm tra Quyền
class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: TaiKhoan = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Quyền của bạn ({user.role}) không được phép thực hiện thao tác này."
            )
        return user
