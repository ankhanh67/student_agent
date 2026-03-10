# app/repositories/giang_vien_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas

class GiangVienRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[models.GiangVien]:
        return self.db.query(models.GiangVien).all()
    
    def get_by_id(self, id_giang_vien: str) -> Optional[models.GiangVien]:
        return self.db.query(models.GiangVien).filter(models.GiangVien.id_giang_vien == id_giang_vien).first()
    
    def get_by_khoa(self, id_khoa: str) -> List[models.GiangVien]:
        return self.db.query(models.GiangVien).filter(models.GiangVien.id_khoa == id_khoa).all()
    
    def create(self, data: schemas.GiangVienCreate) -> models.GiangVien:
        gv = models.GiangVien(**data.model_dump())
        self.db.add(gv)
        self.db.commit()
        self.db.refresh(gv)
        return gv
    
    def update(self, id_giang_vien: str, data: schemas.GiangVienUpdate) -> Optional[models.GiangVien]:
        gv = self.get_by_id(id_giang_vien)
        if not gv:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(gv, field, value)
        self.db.commit()
        self.db.refresh(gv)
        return gv
    
    def delete(self, id_giang_vien: str) -> bool:
        gv = self.get_by_id(id_giang_vien)
        if not gv:
            return False
        self.db.delete(gv)
        self.db.commit()
        return True