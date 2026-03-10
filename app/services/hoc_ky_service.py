# app/services/hoc_ky_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas
from app.repositories.hoc_ky_repository import HocKyRepository

class HocKyService:
    
    def __init__(self, db: Session):
        self.repo = HocKyRepository(db)
    
    def get_all_hoc_ky(self) -> List[schemas.HocKy]:
        hk_list = self.repo.get_all()
        return [schemas.HocKy.model_validate(h) for h in hk_list]
    
    def get_hoc_ky_by_id(self, id_hoc_ky: str) -> Optional[schemas.HocKy]:
        hk = self.repo.get_by_id(id_hoc_ky)
        if hk:
            return schemas.HocKy.model_validate(hk)
        return None
    
    def get_hoc_ky_hien_tai(self) -> Optional[schemas.HocKy]:
        hk = self.repo.get_hoc_ky_hien_tai()
        if hk:
            return schemas.HocKy.model_validate(hk)
        return None
    
    def create_hoc_ky(self, data: schemas.HocKyCreate) -> schemas.HocKy:
        hk = self.repo.create(data)
        return schemas.HocKy.model_validate(hk)
    
    def update_hoc_ky(self, id_hoc_ky: str, data: schemas.HocKyUpdate) -> Optional[schemas.HocKy]:
        hk = self.repo.update(id_hoc_ky, data)
        if hk:
            return schemas.HocKy.model_validate(hk)
        return None
    
    def delete_hoc_ky(self, id_hoc_ky: str) -> bool:
        return self.repo.delete(id_hoc_ky)