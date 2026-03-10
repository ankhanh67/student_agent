# app/services/khoa_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas
from app.repositories.khoa_repository import KhoaRepository

class KhoaService:
    
    def __init__(self, db: Session):
        self.repo = KhoaRepository(db)
    
    def get_all_khoa(self) -> List[schemas.Khoa]:
        khoa_list = self.repo.get_all()
        return [schemas.Khoa.model_validate(k) for k in khoa_list]
    
    def get_khoa_by_id(self, id_khoa: str) -> Optional[schemas.Khoa]:
        khoa = self.repo.get_by_id(id_khoa)
        if khoa:
            return schemas.Khoa.model_validate(khoa)
        return None
    
    def create_khoa(self, data: schemas.KhoaCreate) -> schemas.Khoa:
        khoa = self.repo.create(data)
        return schemas.Khoa.model_validate(khoa)
    
    def update_khoa(self, id_khoa: str, data: schemas.KhoaUpdate) -> Optional[schemas.Khoa]:
        khoa = self.repo.update(id_khoa, data)
        if khoa:
            return schemas.Khoa.model_validate(khoa)
        return None
    
    def delete_khoa(self, id_khoa: str) -> bool:
        return self.repo.delete(id_khoa)