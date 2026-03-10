# app/repositories/lop_mon_hoc_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas

class LopMonHocRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[models.LopMonHoc]:
        return self.db.query(models.LopMonHoc).all()
    
    def get_by_id(self, id_lop_mon: str) -> Optional[models.LopMonHoc]:
        return self.db.query(models.LopMonHoc).filter(models.LopMonHoc.id_lop_mon == id_lop_mon).first()
    
    def get_by_mon_hoc(self, id_mon_hoc: str) -> List[models.LopMonHoc]:
        return self.db.query(models.LopMonHoc).filter(models.LopMonHoc.id_mon_hoc == id_mon_hoc).all()
    
    def get_by_giang_vien(self, id_giang_vien: str) -> List[models.LopMonHoc]:
        return self.db.query(models.LopMonHoc).filter(models.LopMonHoc.id_giang_vien == id_giang_vien).all()
    
    def get_by_hoc_ky(self, id_hoc_ky: str) -> List[models.LopMonHoc]:
        return self.db.query(models.LopMonHoc).filter(models.LopMonHoc.id_hoc_ky == id_hoc_ky).all()
    
    def create(self, data: schemas.LopMonHocCreate) -> models.LopMonHoc:
        lop_mon = models.LopMonHoc(**data.model_dump())
        self.db.add(lop_mon)
        self.db.commit()
        self.db.refresh(lop_mon)
        return lop_mon
    
    def update(self, id_lop_mon: str, data: schemas.LopMonHocUpdate) -> Optional[models.LopMonHoc]:
        lop_mon = self.get_by_id(id_lop_mon)
        if not lop_mon:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lop_mon, field, value)
        self.db.commit()
        self.db.refresh(lop_mon)
        return lop_mon
    
    def delete(self, id_lop_mon: str) -> bool:
        lop_mon = self.get_by_id(id_lop_mon)
        if not lop_mon:
            return False
        self.db.delete(lop_mon)
        self.db.commit()
        return True