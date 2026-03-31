import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from app.models import TaiKhoan, Base
from dotenv import load_dotenv

# 1. Load cấu hình DB
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Tạo bảng nếu chưa có
Base.metadata.create_all(bind=engine)

# 3. Công cụ băm mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_first_admin():
    db = SessionLocal()
    try:
        # Kiểm tra xem admin đã tồn tại chưa
        admin = db.query(TaiKhoan).filter(TaiKhoan.username == "admin").first()
        if admin:
            print("Tài khoản admin đã tồn tại!")
            return

        # Tạo mật khẩu băm
        mat_khau_goc = "123456"
        mat_khau_bam = pwd_context.hash(mat_khau_goc)

        # Tạo user Admin
        new_admin = TaiKhoan(
            username="admin",
            hashed_password=mat_khau_bam,
            role="Admin"
        )
        db.add(new_admin)
        db.commit()
        print(f"Tạo thành công tài khoản: admin | Mật khẩu: {mat_khau_goc} | Quyền: Admin")
        
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_first_admin()