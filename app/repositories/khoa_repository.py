# app/repositories/khoa_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas

class KhoaRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[models.Khoa]:
        return self.db.query(models.Khoa).all()
    
    def get_by_id(self, id_khoa: str) -> Optional[models.Khoa]:
        return self.db.query(models.Khoa).filter(models.Khoa.id_khoa == id_khoa).first()
    
    def create(self, data: schemas.KhoaCreate) -> models.Khoa:
        khoa = models.Khoa(**data.model_dump())
        self.db.add(khoa)
        self.db.commit()
        self.db.refresh(khoa)
        return khoa
    
    def update(self, id_khoa: str, data: schemas.KhoaUpdate) -> Optional[models.Khoa]:
        khoa = self.get_by_id(id_khoa)
        if not khoa:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(khoa, field, value)
        self.db.commit()
        self.db.refresh(khoa)
        return khoa
    
    def delete(self, id_khoa: str) -> bool:
        khoa = self.get_by_id(id_khoa)
        if not khoa:
            return False
        self.db.delete(khoa)
        self.db.commit()
        return True