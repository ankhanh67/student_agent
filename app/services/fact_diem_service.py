# app/services/fact_diem_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas
from app.repositories.fact_diem_repository import FactDiemRepository

class FactDiemService:
    
    def __init__(self, db: Session):
        self.repo = FactDiemRepository(db)
    
    def get_all_diem(self) -> List[schemas.FactDiem]:
        diem_list = self.repo.get_all()
        return [schemas.FactDiem.model_validate(d) for d in diem_list]
    
    def get_diem_by_id(self, id_diem: str) -> Optional[schemas.FactDiem]:
        diem = self.repo.get_by_id(id_diem)
        if diem:
            return schemas.FactDiem.model_validate(diem)
        return None
    
    def get_diem_by_sinh_vien(self, id_sinh_vien: str) -> List[schemas.FactDiem]:
        diem_list = self.repo.get_by_sinh_vien(id_sinh_vien)
        return [schemas.FactDiem.model_validate(d) for d in diem_list]
    
    def get_diem_by_mon_hoc(self, id_mon_hoc: str) -> List[schemas.FactDiem]:
        diem_list = self.repo.get_by_mon_hoc(id_mon_hoc)
        return [schemas.FactDiem.model_validate(d) for d in diem_list]
    
    def get_diem_by_lop_mon(self, id_lop_mon: str) -> List[schemas.FactDiem]:
        diem_list = self.repo.get_by_lop_mon(id_lop_mon)
        return [schemas.FactDiem.model_validate(d) for d in diem_list]
    
    def get_diem_by_giang_vien(self, id_giang_vien: str) -> List[schemas.FactDiem]:
        diem_list = self.repo.get_by_giang_vien(id_giang_vien)
        return [schemas.FactDiem.model_validate(d) for d in diem_list]
    
    def get_diem_by_hoc_ky(self, id_hoc_ky: str) -> List[schemas.FactDiem]:
        diem_list = self.repo.get_by_hoc_ky(id_hoc_ky)
        return [schemas.FactDiem.model_validate(d) for d in diem_list]
    
    def get_diem_trung_binh_sinh_vien(self, id_sinh_vien: str) -> float:
        return self.repo.get_diem_trung_binh_sinh_vien(id_sinh_vien)
    
    def get_tong_tin_chi_dat(self, id_sinh_vien: str) -> int:
        return self.repo.get_tong_tin_chi_dat(id_sinh_vien)
    
    def create_diem(self, data: schemas.FactDiemCreate) -> schemas.FactDiem:
        diem = self.repo.create(data)
        return schemas.FactDiem.model_validate(diem)
    
    def update_diem(self, id_diem: str, data: schemas.FactDiemUpdate) -> Optional[schemas.FactDiem]:
        diem = self.repo.update(id_diem, data)
        if diem:
            return schemas.FactDiem.model_validate(diem)
        return None
    
    def delete_diem(self, id_diem: str) -> bool:
        return self.repo.delete(id_diem)
    
    def thong_ke_diem_theo_khoa(self, id_khoa: str) -> dict:
        return self.repo.thong_ke_diem_theo_khoa(id_khoa)
    
    def thong_ke_diem_theo_nganh(self, id_nganh: str) -> dict:
        return self.repo.thong_ke_diem_theo_nganh(id_nganh)