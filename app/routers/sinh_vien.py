# app/routers/sinh_vien.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas
from app.services.sinh_vien_service import SinhVienService

router = APIRouter(prefix="/sinh-vien", tags=["Sinh viên"])

def get_sinh_vien_service(db: Session = Depends(get_db)):
    return SinhVienService(db)

@router.post("/", response_model=schemas.SinhVien)
def create_sinh_vien(
    sv: schemas.SinhVienCreate,
    service: SinhVienService = Depends(get_sinh_vien_service)
):
    """Thêm sinh viên mới"""
    return service.create_sinh_vien(sv)

@router.get("/", response_model=List[schemas.SinhVien])
def read_all_sinh_vien(
    service: SinhVienService = Depends(get_sinh_vien_service)
):
    """Lấy danh sách tất cả sinh viên"""
    return service.get_all_sinh_vien()

@router.get("/lop/{id_lop}", response_model=List[schemas.SinhVien])
def read_sinh_vien_by_lop(
    id_lop: str,
    service: SinhVienService = Depends(get_sinh_vien_service)
):
    """Lấy danh sách sinh viên theo lớp"""
    return service.get_sinh_vien_by_lop(id_lop)

@router.get("/nganh/{id_nganh}", response_model=List[schemas.SinhVien])
def read_sinh_vien_by_nganh(
    id_nganh: str,
    service: SinhVienService = Depends(get_sinh_vien_service)
):
    """Lấy danh sách sinh viên theo ngành"""
    return service.get_sinh_vien_by_nganh(id_nganh)

@router.get("/{id_sinh_vien}", response_model=schemas.SinhVien)
def read_sinh_vien(
    id_sinh_vien: str,
    service: SinhVienService = Depends(get_sinh_vien_service)
):
    """Lấy thông tin sinh viên theo ID"""
    sv = service.get_sinh_vien_by_id(id_sinh_vien)
    if not sv:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    return sv

@router.put("/{id_sinh_vien}", response_model=schemas.SinhVien)
def update_sinh_vien(
    id_sinh_vien: str,
    sv: schemas.SinhVienUpdate,
    service: SinhVienService = Depends(get_sinh_vien_service)
):
    """Cập nhật thông tin sinh viên"""
    updated = service.update_sinh_vien(id_sinh_vien, sv)
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    return updated

@router.delete("/{id_sinh_vien}")
def delete_sinh_vien(
    id_sinh_vien: str,
    service: SinhVienService = Depends(get_sinh_vien_service)
):
    """Xóa sinh viên"""
    if not service.delete_sinh_vien(id_sinh_vien):
        raise HTTPException(status_code=404, detail="Không tìm thấy sinh viên")
    return {"message": "Đã xóa sinh viên thành công"}