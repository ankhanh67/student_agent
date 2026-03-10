# app/repositories/hoc_ky_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas

class HocKyRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[models.HocKy]:
        return self.db.query(models.HocKy).all()
    
    def get_by_id(self, id_hoc_ky: str) -> Optional[models.HocKy]:
        return self.db.query(models.HocKy).filter(models.HocKy.id_hoc_ky == id_hoc_ky).first()
    
    def get_hoc_ky_hien_tai(self) -> Optional[models.HocKy]:
        return self.db.query(models.HocKy).order_by(models.HocKy.id_hoc_ky.desc()).first()
    
    def create(self, data: schemas.HocKyCreate) -> models.HocKy:
        hk = models.HocKy(**data.model_dump())
        self.db.add(hk)
        self.db.commit()
        self.db.refresh(hk)
        return hk
    
    def update(self, id_hoc_ky: str, data: schemas.HocKyUpdate) -> Optional[models.HocKy]:
        hk = self.get_by_id(id_hoc_ky)
        if not hk:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(hk, field, value)
        self.db.commit()
        self.db.refresh(hk)
        return hk
    
    def delete(self, id_hoc_ky: str) -> bool:
        hk = self.get_by_id(id_hoc_ky)
        if not hk:
            return False
        self.db.delete(hk)
        self.db.commit()
        return True