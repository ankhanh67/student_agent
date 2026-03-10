# app/services/lop_mon_hoc_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas
from app.repositories.lop_mon_hoc_repository import LopMonHocRepository

class LopMonHocService:
    
    def __init__(self, db: Session):
        self.repo = LopMonHocRepository(db)
    
    def get_all_lop_mon(self) -> List[schemas.LopMonHoc]:
        lm_list = self.repo.get_all()
        return [schemas.LopMonHoc.model_validate(l) for l in lm_list]
    
    def get_lop_mon_by_id(self, id_lop_mon: str) -> Optional[schemas.LopMonHoc]:
        lm = self.repo.get_by_id(id_lop_mon)
        if lm:
            return schemas.LopMonHoc.model_validate(lm)
        return None
    
    def get_lop_mon_by_mon_hoc(self, id_mon_hoc: str) -> List[schemas.LopMonHoc]:
        lm_list = self.repo.get_by_mon_hoc(id_mon_hoc)
        return [schemas.LopMonHoc.model_validate(l) for l in lm_list]
    
    def get_lop_mon_by_giang_vien(self, id_giang_vien: str) -> List[schemas.LopMonHoc]:
        lm_list = self.repo.get_by_giang_vien(id_giang_vien)
        return [schemas.LopMonHoc.model_validate(l) for l in lm_list]
    
    def get_lop_mon_by_hoc_ky(self, id_hoc_ky: str) -> List[schemas.LopMonHoc]:
        lm_list = self.repo.get_by_hoc_ky(id_hoc_ky)
        return [schemas.LopMonHoc.model_validate(l) for l in lm_list]
    
    def create_lop_mon(self, data: schemas.LopMonHocCreate) -> schemas.LopMonHoc:
        lm = self.repo.create(data)
        return schemas.LopMonHoc.model_validate(lm)
    
    def update_lop_mon(self, id_lop_mon: str, data: schemas.LopMonHocUpdate) -> Optional[schemas.LopMonHoc]:
        lm = self.repo.update(id_lop_mon, data)
        if lm:
            return schemas.LopMonHoc.model_validate(lm)
        return None
    
    def delete_lop_mon(self, id_lop_mon: str) -> bool:
        return self.repo.delete(id_lop_mon)