# app/repositories/fact_diem_repository.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app import models, schemas

class FactDiemRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[models.FactDiem]:
        return self.db.query(models.FactDiem).all()
    
    def get_by_id(self, id_diem: str) -> Optional[models.FactDiem]:
        return self.db.query(models.FactDiem).filter(models.FactDiem.id_diem == id_diem).first()
    
    def get_by_sinh_vien(self, id_sinh_vien: str) -> List[models.FactDiem]:
        return self.db.query(models.FactDiem).filter(models.FactDiem.id_sinh_vien == id_sinh_vien).all()
    
    def get_by_mon_hoc(self, id_mon_hoc: str) -> List[models.FactDiem]:
        return self.db.query(models.FactDiem).filter(models.FactDiem.id_mon_hoc == id_mon_hoc).all()
    
    def get_by_lop_mon(self, id_lop_mon: str) -> List[models.FactDiem]:
        return self.db.query(models.FactDiem).filter(models.FactDiem.id_lop_mon == id_lop_mon).all()
    
    def get_by_giang_vien(self, id_giang_vien: str) -> List[models.FactDiem]:
        return self.db.query(models.FactDiem).filter(models.FactDiem.id_giang_vien == id_giang_vien).all()
    
    def get_by_hoc_ky(self, id_hoc_ky: str) -> List[models.FactDiem]:
        return self.db.query(models.FactDiem).filter(models.FactDiem.id_hoc_ky == id_hoc_ky).all()
    
    def get_diem_trung_binh_sinh_vien(self, id_sinh_vien: str) -> float:
        result = self.db.query(
            func.avg(models.FactDiem.diem_trung_binh).label('diem_tb')
        ).filter(
            models.FactDiem.id_sinh_vien == id_sinh_vien,
            models.FactDiem.ketQua == True
        ).first()
        return result.diem_tb or 0
    
    def get_tong_tin_chi_dat(self, id_sinh_vien: str) -> int:
        result = self.db.query(
            func.sum(models.FactDiem.so_tin_chi_dat).label('tong_tc')
        ).filter(
            models.FactDiem.id_sinh_vien == id_sinh_vien,
            models.FactDiem.ketQua == True
        ).first()
        return result.tong_tc or 0
    
    def create(self, data: schemas.FactDiemCreate) -> models.FactDiem:
        diem = models.FactDiem(**data.model_dump())
        self.db.add(diem)
        self.db.commit()
        self.db.refresh(diem)
        return diem
    
    def update(self, id_diem: str, data: schemas.FactDiemUpdate) -> Optional[models.FactDiem]:
        diem = self.get_by_id(id_diem)
        if not diem:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(diem, field, value)
        self.db.commit()
        self.db.refresh(diem)
        return diem
    
    def delete(self, id_diem: str) -> bool:
        diem = self.get_by_id(id_diem)
        if not diem:
            return False
        self.db.delete(diem)
        self.db.commit()
        return True
    
    def thong_ke_diem_theo_khoa(self, id_khoa: str) -> dict:
        """Thống kê điểm trung bình theo khoa"""
        result = self.db.query(
            func.avg(models.FactDiem.diem_trung_binh).label('diem_tb'),
            func.count(models.FactDiem.id_diem).label('so_luong'),
            func.sum(models.FactDiem.so_tin_chi_dat).label('tong_tin_chi')
        ).filter(models.FactDiem.id_khoa == id_khoa).first()
        
        return {
            "diem_trung_binh": result.diem_tb or 0,
            "so_luong_diem": result.so_luong or 0,
            "tong_tin_chi_dat": result.tong_tin_chi or 0
        }
    
    def thong_ke_diem_theo_nganh(self, id_nganh: str) -> dict:
        """Thống kê điểm trung bình theo ngành"""
        result = self.db.query(
            func.avg(models.FactDiem.diem_trung_binh).label('diem_tb'),
            func.count(models.FactDiem.id_diem).label('so_luong')
        ).filter(models.FactDiem.id_nganh == id_nganh).first()
        
        return {
            "diem_trung_binh": result.diem_tb or 0,
            "so_luong_diem": result.so_luong or 0
        }