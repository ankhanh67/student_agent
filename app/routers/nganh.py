# app/routers/nganh.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas
from app.services.nganh_service import NganhService

router = APIRouter(prefix="/nganh", tags=["Ngành học"])

def get_nganh_service(db: Session = Depends(get_db)):
    return NganhService(db)

@router.post("/", response_model=schemas.Nganh)
def create_nganh(
    nganh: schemas.NganhCreate,
    service: NganhService = Depends(get_nganh_service)
):
    """Tạo ngành học mới"""
    return service.create_nganh(nganh)

@router.get("/", response_model=List[schemas.Nganh])
def read_all_nganh(
    service: NganhService = Depends(get_nganh_service)
):
    """Lấy danh sách tất cả ngành học"""
    return service.get_all_nganh()

@router.get("/khoa/{id_khoa}", response_model=List[schemas.Nganh])
def read_nganh_by_khoa(
    id_khoa: str,
    service: NganhService = Depends(get_nganh_service)
):
    """Lấy danh sách ngành theo khoa"""
    return service.get_nganh_by_khoa(id_khoa)

@router.get("/{id_nganh}", response_model=schemas.Nganh)
def read_nganh(
    id_nganh: str,
    service: NganhService = Depends(get_nganh_service)
):
    """Lấy thông tin ngành theo ID"""
    nganh = service.get_nganh_by_id(id_nganh)
    if not nganh:
        raise HTTPException(status_code=404, detail="Không tìm thấy ngành học")
    return nganh

@router.put("/{id_nganh}", response_model=schemas.Nganh)
def update_nganh(
    id_nganh: str,
    nganh: schemas.NganhUpdate,
    service: NganhService = Depends(get_nganh_service)
):
    """Cập nhật thông tin ngành học"""
    updated = service.update_nganh(id_nganh, nganh)
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy ngành học")
    return updated

@router.delete("/{id_nganh}")
def delete_nganh(
    id_nganh: str,
    service: NganhService = Depends(get_nganh_service)
):
    """Xóa ngành học"""
    if not service.delete_nganh(id_nganh):
        raise HTTPException(status_code=404, detail="Không tìm thấy ngành học")
    return {"message": "Đã xóa ngành học thành công"}