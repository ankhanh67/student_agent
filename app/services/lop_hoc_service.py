# app/services/lop_hoc_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas
from app.repositories.lop_hoc_repository import LopHocRepository

class LopHocService:
    
    def __init__(self, db: Session):
        self.repo = LopHocRepository(db)
    
    def get_all_lop(self) -> List[schemas.LopHoc]:
        lop_list = self.repo.get_all()
        return [schemas.LopHoc.model_validate(l) for l in lop_list]
    
    def get_lop_by_id(self, id_lop: str) -> Optional[schemas.LopHoc]:
        lop = self.repo.get_by_id(id_lop)
        if lop:
            return schemas.LopHoc.model_validate(lop)
        return None
    
    def get_lop_by_khoa(self, id_khoa: str) -> List[schemas.LopHoc]:
        lop_list = self.repo.get_by_khoa(id_khoa)
        return [schemas.LopHoc.model_validate(l) for l in lop_list]
    
    def get_lop_by_nganh(self, id_nganh: str) -> List[schemas.LopHoc]:
        lop_list = self.repo.get_by_nganh(id_nganh)
        return [schemas.LopHoc.model_validate(l) for l in lop_list]
    
    def create_lop(self, data: schemas.LopHocCreate) -> schemas.LopHoc:
        lop = self.repo.create(data)
        return schemas.LopHoc.model_validate(lop)
    
    def update_lop(self, id_lop: str, data: schemas.LopHocUpdate) -> Optional[schemas.LopHoc]:
        lop = self.repo.update(id_lop, data)
        if lop:
            return schemas.LopHoc.model_validate(lop)
        return None
    
    def delete_lop(self, id_lop: str) -> bool:
        return self.repo.delete(id_lop)