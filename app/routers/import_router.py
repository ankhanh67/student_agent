# app/routers/import_router.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.import_service import ImportService

router = APIRouter(prefix="/import", tags=["Import dữ liệu"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload file Excel/CSV để import dữ liệu vào database
    """
    
    # Kiểm tra định dạng file
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(400, "Chỉ hỗ trợ file Excel (.xlsx, .xls) hoặc CSV")
    
    try:
        # Đọc file
        contents = await file.read()
        
        # Gọi service xử lý
        service = ImportService(db)
        result = service.import_from_file(contents, file.filename)
        
        return result
        
    except Exception as e:
        raise HTTPException(500, f"Lỗi xử lý: {str(e)}")