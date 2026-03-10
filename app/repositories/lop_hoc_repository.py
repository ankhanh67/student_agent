# app/repositories/lop_hoc_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas

class LopHocRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[models.LopHoc]:
        return self.db.query(models.LopHoc).all()
    
    def get_by_id(self, id_lop: str) -> Optional[models.LopHoc]:
        return self.db.query(models.LopHoc).filter(models.LopHoc.id_lop == id_lop).first()
    
    def get_by_khoa(self, id_khoa: str) -> List[models.LopHoc]:
        return self.db.query(models.LopHoc).filter(models.LopHoc.id_khoa == id_khoa).all()
    
    def get_by_nganh(self, id_nganh: str) -> List[models.LopHoc]:
        return self.db.query(models.LopHoc).filter(models.LopHoc.id_nganh == id_nganh).all()
    
    def create(self, data: schemas.LopHocCreate) -> models.LopHoc:
        lop = models.LopHoc(**data.model_dump())
        self.db.add(lop)
        self.db.commit()
        self.db.refresh(lop)
        return lop
    
    def update(self, id_lop: str, data: schemas.LopHocUpdate) -> Optional[models.LopHoc]:
        lop = self.get_by_id(id_lop)
        if not lop:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lop, field, value)
        self.db.commit()
        self.db.refresh(lop)
        return lop
    
    def delete(self, id_lop: str) -> bool:
        lop = self.get_by_id(id_lop)
        if not lop:
            return False
        self.db.delete(lop)
        self.db.commit()
        return True