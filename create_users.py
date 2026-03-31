import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from app.models import TaiKhoan
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_bulk_users():
    db = SessionLocal()
    try:
        danh_sach = []
        
        # 1. Sinh tự động 100 tài khoản Sinh Viên (SV001 -> SV100)
        for i in range(1, 101):
            danh_sach.append({
                "username": f"SV{i:03d}", 
                "password": "123", 
                "role": "SinhVien"
            })
            
        # 2. Sinh tự động 10 tài khoản Giảng Viên (GV001 -> GV010)
        for i in range(1, 11):
            danh_sach.append({
                "username": f"GV{i:03d}", 
                "password": "123", 
                "role": "GiangVien"
            })

        print(f"⏳ Đang xử lý tạo {len(danh_sach)} tài khoản. Vui lòng đợi...")

        for user_data in danh_sach:
            # Kiểm tra xem tài khoản đã tồn tại chưa
            existing_user = db.query(TaiKhoan).filter(TaiKhoan.username == user_data["username"]).first()
            if existing_user:
                print(f"⚠️ Tài khoản {user_data['username']} đã tồn tại!")
                continue

            # Băm mật khẩu và đưa vào phiên giao dịch
            hashed_pw = pwd_context.hash(user_data["password"])
            new_user = TaiKhoan(
                username=user_data["username"],
                hashed_password=hashed_pw,
                role=user_data["role"]
            )
            db.add(new_user)
            print(f"✅ Đã chuẩn bị: {user_data['username']}")
        
        # Commit ĐỒNG LOẠT 1 lần ở cuối cùng để tăng tối đa tốc độ ghi Database
        db.commit()
        print("🎉 HOÀN TẤT TẠO TÀI KHOẢN HÀNG LOẠT VÀO DATABASE!")
        
    except Exception as e:
        print(f"❌ Có lỗi xảy ra: {e}")
        db.rollback() # Quay xe nếu có lỗi để bảo vệ DB
    finally:
        db.close()

if __name__ == "__main__":
    create_bulk_users()
