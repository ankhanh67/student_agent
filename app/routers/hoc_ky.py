# app/routers/hoc_ky.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas
from app.services.hoc_ky_service import HocKyService

router = APIRouter(prefix="/hoc-ky", tags=["Học kỳ"])

def get_hoc_ky_service(db: Session = Depends(get_db)):
    return HocKyService(db)

@router.post("/", response_model=schemas.HocKy)
def create_hoc_ky(
    hk: schemas.HocKyCreate,
    service: HocKyService = Depends(get_hoc_ky_service)
):
    """Thêm học kỳ mới"""
    return service.create_hoc_ky(hk)

@router.get("/", response_model=List[schemas.HocKy])
def read_all_hoc_ky(
    service: HocKyService = Depends(get_hoc_ky_service)
):
    """Lấy danh sách tất cả học kỳ"""
    return service.get_all_hoc_ky()

@router.get("/hien-tai", response_model=schemas.HocKy)
def read_hoc_ky_hien_tai(
    service: HocKyService = Depends(get_hoc_ky_service)
):
    """Lấy học kỳ hiện tại"""
    hk = service.get_hoc_ky_hien_tai()
    if not hk:
        raise HTTPException(status_code=404, detail="Không có học kỳ hiện tại")
    return hk

@router.get("/{id_hoc_ky}", response_model=schemas.HocKy)
def read_hoc_ky(
    id_hoc_ky: str,
    service: HocKyService = Depends(get_hoc_ky_service)
):
    """Lấy thông tin học kỳ theo ID"""
    hk = service.get_hoc_ky_by_id(id_hoc_ky)
    if not hk:
        raise HTTPException(status_code=404, detail="Không tìm thấy học kỳ")
    return hk

@router.put("/{id_hoc_ky}", response_model=schemas.HocKy)
def update_hoc_ky(
    id_hoc_ky: str,
    hk: schemas.HocKyUpdate,
    service: HocKyService = Depends(get_hoc_ky_service)
):
    """Cập nhật thông tin học kỳ"""
    updated = service.update_hoc_ky(id_hoc_ky, hk)
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy học kỳ")
    return updated

@router.delete("/{id_hoc_ky}")
def delete_hoc_ky(
    id_hoc_ky: str,
    service: HocKyService = Depends(get_hoc_ky_service)
):
    """Xóa học kỳ"""
    if not service.delete_hoc_ky(id_hoc_ky):
        raise HTTPException(status_code=404, detail="Không tìm thấy học kỳ")
    return {"message": "Đã xóa học kỳ thành công"}