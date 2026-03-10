# app/routers/lop_hoc.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas
from app.services.lop_hoc_service import LopHocService

router = APIRouter(prefix="/lop-hoc", tags=["Lớp học"])

def get_lop_hoc_service(db: Session = Depends(get_db)):
    return LopHocService(db)

@router.post("/", response_model=schemas.LopHoc)
def create_lop(
    lop: schemas.LopHocCreate,
    service: LopHocService = Depends(get_lop_hoc_service)
):
    """Tạo lớp học mới"""
    return service.create_lop(lop)

@router.get("/", response_model=List[schemas.LopHoc])
def read_all_lop(
    service: LopHocService = Depends(get_lop_hoc_service)
):
    """Lấy danh sách tất cả lớp học"""
    return service.get_all_lop()

@router.get("/khoa/{id_khoa}", response_model=List[schemas.LopHoc])
def read_lop_by_khoa(
    id_khoa: str,
    service: LopHocService = Depends(get_lop_hoc_service)
):
    """Lấy danh sách lớp theo khoa"""
    return service.get_lop_by_khoa(id_khoa)

@router.get("/nganh/{id_nganh}", response_model=List[schemas.LopHoc])
def read_lop_by_nganh(
    id_nganh: str,
    service: LopHocService = Depends(get_lop_hoc_service)
):
    """Lấy danh sách lớp theo ngành"""
    return service.get_lop_by_nganh(id_nganh)

@router.get("/{id_lop}", response_model=schemas.LopHoc)
def read_lop(
    id_lop: str,
    service: LopHocService = Depends(get_lop_hoc_service)
):
    """Lấy thông tin lớp học theo ID"""
    lop = service.get_lop_by_id(id_lop)
    if not lop:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    return lop

@router.put("/{id_lop}", response_model=schemas.LopHoc)
def update_lop(
    id_lop: str,
    lop: schemas.LopHocUpdate,
    service: LopHocService = Depends(get_lop_hoc_service)
):
    """Cập nhật thông tin lớp học"""
    updated = service.update_lop(id_lop, lop)
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    return updated

@router.delete("/{id_lop}")
def delete_lop(
    id_lop: str,
    service: LopHocService = Depends(get_lop_hoc_service)
):
    """Xóa lớp học"""
    if not service.delete_lop(id_lop):
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học")
    return {"message": "Đã xóa lớp học thành công"}