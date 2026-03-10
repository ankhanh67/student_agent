# app/routers/lop_mon_hoc.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas
from app.services.lop_mon_hoc_service import LopMonHocService

router = APIRouter(prefix="/lop-mon-hoc", tags=["Lớp học phần"])

def get_lop_mon_hoc_service(db: Session = Depends(get_db)):
    return LopMonHocService(db)

@router.post("/", response_model=schemas.LopMonHoc)
def create_lop_mon(
    lop_mon: schemas.LopMonHocCreate,
    service: LopMonHocService = Depends(get_lop_mon_hoc_service)
):
    """Tạo lớp học phần mới"""
    return service.create_lop_mon(lop_mon)

@router.get("/", response_model=List[schemas.LopMonHoc])
def read_all_lop_mon(
    service: LopMonHocService = Depends(get_lop_mon_hoc_service)
):
    """Lấy danh sách tất cả lớp học phần"""
    return service.get_all_lop_mon()

@router.get("/mon-hoc/{id_mon_hoc}", response_model=List[schemas.LopMonHoc])
def read_lop_mon_by_mon_hoc(
    id_mon_hoc: str,
    service: LopMonHocService = Depends(get_lop_mon_hoc_service)
):
    """Lấy danh sách lớp học phần theo môn học"""
    return service.get_lop_mon_by_mon_hoc(id_mon_hoc)

@router.get("/giang-vien/{id_giang_vien}", response_model=List[schemas.LopMonHoc])
def read_lop_mon_by_giang_vien(
    id_giang_vien: str,
    service: LopMonHocService = Depends(get_lop_mon_hoc_service)
):
    """Lấy danh sách lớp học phần theo giảng viên"""
    return service.get_lop_mon_by_giang_vien(id_giang_vien)

@router.get("/hoc-ky/{id_hoc_ky}", response_model=List[schemas.LopMonHoc])
def read_lop_mon_by_hoc_ky(
    id_hoc_ky: str,
    service: LopMonHocService = Depends(get_lop_mon_hoc_service)
):
    """Lấy danh sách lớp học phần theo học kỳ"""
    return service.get_lop_mon_by_hoc_ky(id_hoc_ky)

@router.get("/{id_lop_mon}", response_model=schemas.LopMonHoc)
def read_lop_mon(
    id_lop_mon: str,
    service: LopMonHocService = Depends(get_lop_mon_hoc_service)
):
    """Lấy thông tin lớp học phần theo ID"""
    lop_mon = service.get_lop_mon_by_id(id_lop_mon)
    if not lop_mon:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học phần")
    return lop_mon

@router.put("/{id_lop_mon}", response_model=schemas.LopMonHoc)
def update_lop_mon(
    id_lop_mon: str,
    lop_mon: schemas.LopMonHocUpdate,
    service: LopMonHocService = Depends(get_lop_mon_hoc_service)
):
    """Cập nhật thông tin lớp học phần"""
    updated = service.update_lop_mon(id_lop_mon, lop_mon)
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học phần")
    return updated

@router.delete("/{id_lop_mon}")
def delete_lop_mon(
    id_lop_mon: str,
    service: LopMonHocService = Depends(get_lop_mon_hoc_service)
):
    """Xóa lớp học phần"""
    if not service.delete_lop_mon(id_lop_mon):
        raise HTTPException(status_code=404, detail="Không tìm thấy lớp học phần")
    return {"message": "Đã xóa lớp học phần thành công"}