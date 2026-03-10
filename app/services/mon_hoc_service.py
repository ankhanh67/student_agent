# app/services/mon_hoc_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas
from app.repositories.mon_hoc_repository import MonHocRepository

class MonHocService:
    
    def __init__(self, db: Session):
        self.repo = MonHocRepository(db)
    
    def get_all_mon_hoc(self) -> List[schemas.MonHoc]:
        mon_list = self.repo.get_all()
        return [schemas.MonHoc.model_validate(m) for m in mon_list]
    
    def get_mon_hoc_by_id(self, id_mon_hoc: str) -> Optional[schemas.MonHoc]:
        mon = self.repo.get_by_id(id_mon_hoc)
        if mon:
            return schemas.MonHoc.model_validate(mon)
        return None
    
    def get_mon_tien_quyet(self, id_mon_hoc: str) -> Optional[schemas.MonHoc]:
        mon = self.repo.get_mon_tien_quyet(id_mon_hoc)
        if mon:
            return schemas.MonHoc.model_validate(mon)
        return None
    
    def create_mon_hoc(self, data: schemas.MonHocCreate) -> schemas.MonHoc:
        mon = self.repo.create(data)
        return schemas.MonHoc.model_validate(mon)
    
    def update_mon_hoc(self, id_mon_hoc: str, data: schemas.MonHocUpdate) -> Optional[schemas.MonHoc]:
        mon = self.repo.update(id_mon_hoc, data)
        if mon:
            return schemas.MonHoc.model_validate(mon)
        return None
    
    def delete_mon_hoc(self, id_mon_hoc: str) -> bool:
        return self.repo.delete(id_mon_hoc)