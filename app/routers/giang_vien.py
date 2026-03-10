# app/routers/giang_vien.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas
from app.services.giang_vien_service import GiangVienService

router = APIRouter(prefix="/giang-vien", tags=["Giảng viên"])

def get_giang_vien_service(db: Session = Depends(get_db)):
    return GiangVienService(db)

@router.post("/", response_model=schemas.GiangVien)
def create_giang_vien(
    gv: schemas.GiangVienCreate,
    service: GiangVienService = Depends(get_giang_vien_service)
):
    """Thêm giảng viên mới"""
    return service.create_giang_vien(gv)

@router.get("/", response_model=List[schemas.GiangVien])
def read_all_giang_vien(
    service: GiangVienService = Depends(get_giang_vien_service)
):
    """Lấy danh sách tất cả giảng viên"""
    return service.get_all_giang_vien()

@router.get("/khoa/{id_khoa}", response_model=List[schemas.GiangVien])
def read_giang_vien_by_khoa(
    id_khoa: str,
    service: GiangVienService = Depends(get_giang_vien_service)
):
    """Lấy danh sách giảng viên theo khoa"""
    return service.get_giang_vien_by_khoa(id_khoa)

@router.get("/{id_giang_vien}", response_model=schemas.GiangVien)
def read_giang_vien(
    id_giang_vien: str,
    service: GiangVienService = Depends(get_giang_vien_service)
):
    """Lấy thông tin giảng viên theo ID"""
    gv = service.get_giang_vien_by_id(id_giang_vien)
    if not gv:
        raise HTTPException(status_code=404, detail="Không tìm thấy giảng viên")
    return gv

@router.put("/{id_giang_vien}", response_model=schemas.GiangVien)
def update_giang_vien(
    id_giang_vien: str,
    gv: schemas.GiangVienUpdate,
    service: GiangVienService = Depends(get_giang_vien_service)
):
    """Cập nhật thông tin giảng viên"""
    updated = service.update_giang_vien(id_giang_vien, gv)
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy giảng viên")
    return updated

@router.delete("/{id_giang_vien}")
def delete_giang_vien(
    id_giang_vien: str,
    service: GiangVienService = Depends(get_giang_vien_service)
):
    """Xóa giảng viên"""
    if not service.delete_giang_vien(id_giang_vien):
        raise HTTPException(status_code=404, detail="Không tìm thấy giảng viên")
    return {"message": "Đã xóa giảng viên thành công"}