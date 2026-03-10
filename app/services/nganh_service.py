# app/services/nganh_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas
from app.repositories.nganh_repository import NganhRepository

class NganhService:
    
    def __init__(self, db: Session):
        self.repo = NganhRepository(db)
    
    def get_all_nganh(self) -> List[schemas.Nganh]:
        nganh_list = self.repo.get_all()
        return [schemas.Nganh.model_validate(n) for n in nganh_list]
    
    def get_nganh_by_id(self, id_nganh: str) -> Optional[schemas.Nganh]:
        nganh = self.repo.get_by_id(id_nganh)
        if nganh:
            return schemas.Nganh.model_validate(nganh)
        return None
    
    def get_nganh_by_khoa(self, id_khoa: str) -> List[schemas.Nganh]:
        nganh_list = self.repo.get_by_khoa(id_khoa)
        return [schemas.Nganh.model_validate(n) for n in nganh_list]
    
    def create_nganh(self, data: schemas.NganhCreate) -> schemas.Nganh:
        nganh = self.repo.create(data)
        return schemas.Nganh.model_validate(nganh)
    
    def update_nganh(self, id_nganh: str, data: schemas.NganhUpdate) -> Optional[schemas.Nganh]:
        nganh = self.repo.update(id_nganh, data)
        if nganh:
            return schemas.Nganh.model_validate(nganh)
        return None
    
    def delete_nganh(self, id_nganh: str) -> bool:
        return self.repo.delete(id_nganh)