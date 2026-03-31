# app/main.py
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import (
    khoa, nganh, sinh_vien, mon_hoc, hoc_ky, fact_diem,
    import_router, ai_agent_langgraph, auth
)

# Tạo bảng
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quản lý sinh viên")

# Đăng ký routers
app.include_router(khoa.router)
app.include_router(nganh.router)
app.include_router(sinh_vien.router)
app.include_router(mon_hoc.router)
app.include_router(hoc_ky.router)
app.include_router(fact_diem.router)
app.include_router(import_router.router)
app.include_router(ai_agent_langgraph.router)
app.include_router(auth.router)
@app.get("/")
def root():
    return {
        "message": "Hệ thống quản lý sinh viên",
        "endpoints": {
            "import": "POST /import/upload - Upload file Excel",
            "docs": "/docs - Tài liệu API"
        }
    }
