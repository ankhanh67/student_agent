# app/repositories/dang_ky_mon_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas

class DangKyMonRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[models.DangKyMon]:
        return self.db.query(models.DangKyMon).all()
    
    def get_by_id(self, id_dang_ky: str) -> Optional[models.DangKyMon]:
        return self.db.query(models.DangKyMon).filter(models.DangKyMon.id_dang_ky == id_dang_ky).first()
    
    def get_by_sinh_vien(self, id_sinh_vien: str) -> List[models.DangKyMon]:
        return self.db.query(models.DangKyMon).filter(models.DangKyMon.id_sinh_vien == id_sinh_vien).all()
    
    def get_by_lop_mon(self, id_lop_mon: str) -> List[models.DangKyMon]:
        return self.db.query(models.DangKyMon).filter(models.DangKyMon.id_lop_mon == id_lop_mon).all()
    
    def get_by_hoc_ky(self, id_hoc_ky: str) -> List[models.DangKyMon]:
        return self.db.query(models.DangKyMon).join(
            models.LopMonHoc, models.DangKyMon.id_lop_mon == models.LopMonHoc.id_lop_mon
        ).filter(models.LopMonHoc.id_hoc_ky == id_hoc_ky).all()
    
    def create(self, data: schemas.DangKyMonCreate) -> models.DangKyMon:
        dk = models.DangKyMon(**data.model_dump())
        self.db.add(dk)
        self.db.commit()
        self.db.refresh(dk)
        return dk
    
    def update(self, id_dang_ky: str, data: schemas.DangKyMonUpdate) -> Optional[models.DangKyMon]:
        dk = self.get_by_id(id_dang_ky)
        if not dk:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(dk, field, value)
        self.db.commit()
        self.db.refresh(dk)
        return dk
    
    def delete(self, id_dang_ky: str) -> bool:
        dk = self.get_by_id(id_dang_ky)
        if not dk:
            return False
        self.db.delete(dk)
        self.db.commit()
        return True