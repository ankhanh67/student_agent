# app/repositories/mon_hoc_repository.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas

class MonHocRepository:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[models.MonHoc]:
        return self.db.query(models.MonHoc).all()
    
    def get_by_id(self, id_mon_hoc: str) -> Optional[models.MonHoc]:
        return self.db.query(models.MonHoc).filter(models.MonHoc.id_mon_hoc == id_mon_hoc).first()
    
    def get_mon_tien_quyet(self, id_mon_hoc: str) -> Optional[models.MonHoc]:
        mon = self.get_by_id(id_mon_hoc)
        if mon and mon.id_mon_tien_quyet:
            return self.get_by_id(mon.id_mon_tien_quyet)
        return None
    
    def create(self, data: schemas.MonHocCreate) -> models.MonHoc:
        mon = models.MonHoc(**data.model_dump())
        self.db.add(mon)
        self.db.commit()
        self.db.refresh(mon)
        return mon
    
    def update(self, id_mon_hoc: str, data: schemas.MonHocUpdate) -> Optional[models.MonHoc]:
        mon = self.get_by_id(id_mon_hoc)
        if not mon:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(mon, field, value)
        self.db.commit()
        self.db.refresh(mon)
        return mon
    
    def delete(self, id_mon_hoc: str) -> bool:
        mon = self.get_by_id(id_mon_hoc)
        if not mon:
            return False
        self.db.delete(mon)
        self.db.commit()
        return True