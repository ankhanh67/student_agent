# app/repositories/nganh_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas

class NganhRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[models.Nganh]:
        return self.db.query(models.Nganh).all()
    
    def get_by_id(self, id_nganh: str) -> Optional[models.Nganh]:
        return self.db.query(models.Nganh).filter(models.Nganh.id_nganh == id_nganh).first()
    
    def get_by_khoa(self, id_khoa: str) -> List[models.Nganh]:
        return self.db.query(models.Nganh).filter(models.Nganh.id_khoa == id_khoa).all()
    
    def create(self, data: schemas.NganhCreate) -> models.Nganh:
        nganh = models.Nganh(**data.model_dump())
        self.db.add(nganh)
        self.db.commit()
        self.db.refresh(nganh)
        return nganh
    
    def update(self, id_nganh: str, data: schemas.NganhUpdate) -> Optional[models.Nganh]:
        nganh = self.get_by_id(id_nganh)
        if not nganh:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(nganh, field, value)
        self.db.commit()
        self.db.refresh(nganh)
        return nganh
    
    def delete(self, id_nganh: str) -> bool:
        nganh = self.get_by_id(id_nganh)
        if not nganh:
            return False
        self.db.delete(nganh)
        self.db.commit()
        return True