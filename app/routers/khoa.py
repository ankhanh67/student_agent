# app/routers/khoa.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas
from app.services.khoa_service import KhoaService

router = APIRouter(prefix="/khoa", tags=["Khoa"])

def get_khoa_service(db: Session = Depends(get_db)):
    return KhoaService(db)

@router.post("/", response_model=schemas.Khoa)
def create_khoa(
    khoa: schemas.KhoaCreate,
    service: KhoaService = Depends(get_khoa_service)
):
    """Tạo khoa mới"""
    return service.create_khoa(khoa)

@router.get("/", response_model=List[schemas.Khoa])
def read_all_khoa(
    service: KhoaService = Depends(get_khoa_service)
):
    """Lấy danh sách tất cả khoa"""
    return service.get_all_khoa()

@router.get("/{id_khoa}", response_model=schemas.Khoa)
def read_khoa(
    id_khoa: str,
    service: KhoaService = Depends(get_khoa_service)
):
    """Lấy thông tin khoa theo ID"""
    khoa = service.get_khoa_by_id(id_khoa)
    if not khoa:
        raise HTTPException(status_code=404, detail="Không tìm thấy khoa")
    return khoa

@router.put("/{id_khoa}", response_model=schemas.Khoa)
def update_khoa(
    id_khoa: str,
    khoa: schemas.KhoaUpdate,
    service: KhoaService = Depends(get_khoa_service)
):
    """Cập nhật thông tin khoa"""
    updated = service.update_khoa(id_khoa, khoa)
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy khoa")
    return updated

@router.delete("/{id_khoa}")
def delete_khoa(
    id_khoa: str,
    service: KhoaService = Depends(get_khoa_service)
):
    """Xóa khoa"""
    if not service.delete_khoa(id_khoa):
        raise HTTPException(status_code=404, detail="Không tìm thấy khoa")
    return {"message": "Đã xóa khoa thành công"}