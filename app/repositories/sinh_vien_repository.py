# app/repositories/sinh_vien_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas

class SinhVienRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[models.SinhVien]:
        return self.db.query(models.SinhVien).all()
    
    def get_by_id(self, id_sinh_vien: str) -> Optional[models.SinhVien]:
        return self.db.query(models.SinhVien).filter(models.SinhVien.id_sinh_vien == id_sinh_vien).first()
    
    def get_by_lop(self, id_lop: str) -> List[models.SinhVien]:
        return self.db.query(models.SinhVien).filter(models.SinhVien.id_lop == id_lop).all()
    
    def get_by_nganh(self, id_nganh: str) -> List[models.SinhVien]:
        return self.db.query(models.SinhVien).filter(models.SinhVien.id_nganh == id_nganh).all()
    
    def create(self, data: schemas.SinhVienCreate) -> models.SinhVien:
        sv = models.SinhVien(**data.model_dump())
        self.db.add(sv)
        self.db.commit()
        self.db.refresh(sv)
        return sv
    
    def update(self, id_sinh_vien: str, data: schemas.SinhVienUpdate) -> Optional[models.SinhVien]:
        sv = self.get_by_id(id_sinh_vien)
        if not sv:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sv, field, value)
        self.db.commit()
        self.db.refresh(sv)
        return sv
    
    def delete(self, id_sinh_vien: str) -> bool:
        sv = self.get_by_id(id_sinh_vien)
        if not sv:
            return False
        self.db.delete(sv)
        self.db.commit()
        return True