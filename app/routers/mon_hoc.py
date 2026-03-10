# app/routers/mon_hoc.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas
from app.services.mon_hoc_service import MonHocService

router = APIRouter(prefix="/mon-hoc", tags=["Môn học"])

def get_mon_hoc_service(db: Session = Depends(get_db)):
    return MonHocService(db)

@router.post("/", response_model=schemas.MonHoc)
def create_mon_hoc(
    mon: schemas.MonHocCreate,
    service: MonHocService = Depends(get_mon_hoc_service)
):
    """Thêm môn học mới"""
    return service.create_mon_hoc(mon)

@router.get("/", response_model=List[schemas.MonHoc])
def read_all_mon_hoc(
    service: MonHocService = Depends(get_mon_hoc_service)
):
    """Lấy danh sách tất cả môn học"""
    return service.get_all_mon_hoc()

@router.get("/{id_mon_hoc}/tien-quyet", response_model=schemas.MonHoc)
def read_mon_tien_quyet(
    id_mon_hoc: str,
    service: MonHocService = Depends(get_mon_hoc_service)
):
    """Lấy môn tiên quyết của môn học"""
    mon = service.get_mon_tien_quyet(id_mon_hoc)
    if not mon:
        raise HTTPException(status_code=404, detail="Không có môn tiên quyết")
    return mon

@router.get("/{id_mon_hoc}", response_model=schemas.MonHoc)
def read_mon_hoc(
    id_mon_hoc: str,
    service: MonHocService = Depends(get_mon_hoc_service)
):
    """Lấy thông tin môn học theo ID"""
    mon = service.get_mon_hoc_by_id(id_mon_hoc)
    if not mon:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
    return mon

@router.put("/{id_mon_hoc}", response_model=schemas.MonHoc)
def update_mon_hoc(
    id_mon_hoc: str,
    mon: schemas.MonHocUpdate,
    service: MonHocService = Depends(get_mon_hoc_service)
):
    """Cập nhật thông tin môn học"""
    updated = service.update_mon_hoc(id_mon_hoc, mon)
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
    return updated

@router.delete("/{id_mon_hoc}")
def delete_mon_hoc(
    id_mon_hoc: str,
    service: MonHocService = Depends(get_mon_hoc_service)
):
    """Xóa môn học"""
    if not service.delete_mon_hoc(id_mon_hoc):
        raise HTTPException(status_code=404, detail="Không tìm thấy môn học")
    return {"message": "Đã xóa môn học thành công"}