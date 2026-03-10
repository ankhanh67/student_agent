# app/routers/dang_ky_mon.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas
from app.services.dang_ky_mon_service import DangKyMonService

router = APIRouter(prefix="/dang-ky-mon", tags=["Đăng ký môn học"])

def get_dang_ky_mon_service(db: Session = Depends(get_db)):
    return DangKyMonService(db)

@router.post("/", response_model=schemas.DangKyMon)
def create_dang_ky(
    dk: schemas.DangKyMonCreate,
    service: DangKyMonService = Depends(get_dang_ky_mon_service)
):
    """Đăng ký môn học cho sinh viên"""
    return service.create_dang_ky(dk)

@router.get("/", response_model=List[schemas.DangKyMon])
def read_all_dang_ky(
    service: DangKyMonService = Depends(get_dang_ky_mon_service)
):
    """Lấy danh sách tất cả đăng ký"""
    return service.get_all_dang_ky()

@router.get("/sinh-vien/{id_sinh_vien}", response_model=List[schemas.DangKyMon])
def read_dang_ky_by_sinh_vien(
    id_sinh_vien: str,
    service: DangKyMonService = Depends(get_dang_ky_mon_service)
):
    """Lấy danh sách đăng ký của sinh viên"""
    return service.get_dang_ky_by_sinh_vien(id_sinh_vien)

@router.get("/lop-mon/{id_lop_mon}", response_model=List[schemas.DangKyMon])
def read_dang_ky_by_lop_mon(
    id_lop_mon: str,
    service: DangKyMonService = Depends(get_dang_ky_mon_service)
):
    """Lấy danh sách đăng ký của lớp học phần"""
    return service.get_dang_ky_by_lop_mon(id_lop_mon)

@router.get("/hoc-ky/{id_hoc_ky}", response_model=List[schemas.DangKyMon])
def read_dang_ky_by_hoc_ky(
    id_hoc_ky: str,
    service: DangKyMonService = Depends(get_dang_ky_mon_service)
):
    """Lấy danh sách đăng ký theo học kỳ"""
    return service.get_dang_ky_by_hoc_ky(id_hoc_ky)

@router.get("/{id_dang_ky}", response_model=schemas.DangKyMon)
def read_dang_ky(
    id_dang_ky: str,
    service: DangKyMonService = Depends(get_dang_ky_mon_service)
):
    """Lấy thông tin đăng ký theo ID"""
    dk = service.get_dang_ky_by_id(id_dang_ky)
    if not dk:
        raise HTTPException(status_code=404, detail="Không tìm thấy đăng ký")
    return dk

@router.put("/{id_dang_ky}", response_model=schemas.DangKyMon)
def update_dang_ky(
    id_dang_ky: str,
    dk: schemas.DangKyMonUpdate,
    service: DangKyMonService = Depends(get_dang_ky_mon_service)
):
    """Cập nhật trạng thái đăng ký"""
    updated = service.update_dang_ky(id_dang_ky, dk)
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy đăng ký")
    return updated

@router.delete("/{id_dang_ky}")
def delete_dang_ky(
    id_dang_ky: str,
    service: DangKyMonService = Depends(get_dang_ky_mon_service)
):
    """Xóa đăng ký"""
    if not service.delete_dang_ky(id_dang_ky):
        raise HTTPException(status_code=404, detail="Không tìm thấy đăng ký")
    return {"message": "Đã xóa đăng ký thành công"}