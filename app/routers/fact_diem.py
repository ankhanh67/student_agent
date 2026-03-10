# app/routers/fact_diem.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas
from app.services.fact_diem_service import FactDiemService

router = APIRouter(prefix="/diem", tags=["Điểm số"])

def get_diem_service(db: Session = Depends(get_db)):
    return FactDiemService(db)

@router.post("/", response_model=schemas.FactDiem)
def create_diem(
    diem: schemas.FactDiemCreate,
    service: FactDiemService = Depends(get_diem_service)
):
    """Thêm điểm mới"""
    return service.create_diem(diem)

@router.get("/", response_model=List[schemas.FactDiem])
def read_all_diem(
    service: FactDiemService = Depends(get_diem_service)
):
    """Lấy danh sách tất cả điểm"""
    return service.get_all_diem()

@router.get("/sinh-vien/{id_sinh_vien}", response_model=List[schemas.FactDiem])
def read_diem_by_sinh_vien(
    id_sinh_vien: str,
    service: FactDiemService = Depends(get_diem_service)
):
    """Lấy điểm của sinh viên"""
    return service.get_diem_by_sinh_vien(id_sinh_vien)

@router.get("/mon-hoc/{id_mon_hoc}", response_model=List[schemas.FactDiem])
def read_diem_by_mon_hoc(
    id_mon_hoc: str,
    service: FactDiemService = Depends(get_diem_service)
):
    """Lấy điểm theo môn học"""
    return service.get_diem_by_mon_hoc(id_mon_hoc)

@router.get("/lop-mon/{id_lop_mon}", response_model=List[schemas.FactDiem])
def read_diem_by_lop_mon(
    id_lop_mon: str,
    service: FactDiemService = Depends(get_diem_service)
):
    """Lấy điểm theo lớp học phần"""
    return service.get_diem_by_lop_mon(id_lop_mon)

@router.get("/giang-vien/{id_giang_vien}", response_model=List[schemas.FactDiem])
def read_diem_by_giang_vien(
    id_giang_vien: str,
    service: FactDiemService = Depends(get_diem_service)
):
    """Lấy điểm do giảng viên chấm"""
    return service.get_diem_by_giang_vien(id_giang_vien)

@router.get("/hoc-ky/{id_hoc_ky}", response_model=List[schemas.FactDiem])
def read_diem_by_hoc_ky(
    id_hoc_ky: str,
    service: FactDiemService = Depends(get_diem_service)
):
    """Lấy điểm theo học kỳ"""
    return service.get_diem_by_hoc_ky(id_hoc_ky)

@router.get("/sinh-vien/{id_sinh_vien}/diem-tb")
def get_diem_trung_binh(
    id_sinh_vien: str,
    service: FactDiemService = Depends(get_diem_service)
):
    """Tính điểm trung bình của sinh viên"""
    diem_tb = service.get_diem_trung_binh_sinh_vien(id_sinh_vien)
    tong_tin_chi = service.get_tong_tin_chi_dat(id_sinh_vien)
    return {
        "id_sinh_vien": id_sinh_vien,
        "diem_trung_binh": round(diem_tb, 2),
        "tong_tin_chi_dat": tong_tin_chi
    }

@router.get("/thong-ke/khoa/{id_khoa}")
def thong_ke_diem_theo_khoa(
    id_khoa: str,
    service: FactDiemService = Depends(get_diem_service)
):
    """Thống kê điểm theo khoa"""
    return service.thong_ke_diem_theo_khoa(id_khoa)

@router.get("/thong-ke/nganh/{id_nganh}")
def thong_ke_diem_theo_nganh(
    id_nganh: str,
    service: FactDiemService = Depends(get_diem_service)
):
    """Thống kê điểm theo ngành"""
    return service.thong_ke_diem_theo_nganh(id_nganh)

@router.get("/{id_diem}", response_model=schemas.FactDiem)
def read_diem(
    id_diem: str,
    service: FactDiemService = Depends(get_diem_service)
):
    """Lấy thông tin điểm theo ID"""
    diem = service.get_diem_by_id(id_diem)
    if not diem:
        raise HTTPException(status_code=404, detail="Không tìm thấy điểm")
    return diem

@router.put("/{id_diem}", response_model=schemas.FactDiem)
def update_diem(
    id_diem: str,
    diem: schemas.FactDiemUpdate,
    service: FactDiemService = Depends(get_diem_service)
):
    """Cập nhật điểm"""
    updated = service.update_diem(id_diem, diem)
    if not updated:
        raise HTTPException(status_code=404, detail="Không tìm thấy điểm")
    return updated

@router.delete("/{id_diem}")
def delete_diem(
    id_diem: str,
    service: FactDiemService = Depends(get_diem_service)
):
    """Xóa điểm"""
    if not service.delete_diem(id_diem):
        raise HTTPException(status_code=404, detail="Không tìm thấy điểm")
    return {"message": "Đã xóa điểm thành công"}