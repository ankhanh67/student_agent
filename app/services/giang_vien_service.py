# app/services/giang_vien_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas
from app.repositories.giang_vien_repository import GiangVienRepository

class GiangVienService:
    
    def __init__(self, db: Session):
        self.repo = GiangVienRepository(db)
    
    def get_all_giang_vien(self) -> List[schemas.GiangVien]:
        gv_list = self.repo.get_all()
        return [schemas.GiangVien.model_validate(g) for g in gv_list]
    
    def get_giang_vien_by_id(self, id_giang_vien: str) -> Optional[schemas.GiangVien]:
        gv = self.repo.get_by_id(id_giang_vien)
        if gv:
            return schemas.GiangVien.model_validate(gv)
        return None
    
    def get_giang_vien_by_khoa(self, id_khoa: str) -> List[schemas.GiangVien]:
        gv_list = self.repo.get_by_khoa(id_khoa)
        return [schemas.GiangVien.model_validate(g) for g in gv_list]
    
    def create_giang_vien(self, data: schemas.GiangVienCreate) -> schemas.GiangVien:
        gv = self.repo.create(data)
        return schemas.GiangVien.model_validate(gv)
    
    def update_giang_vien(self, id_giang_vien: str, data: schemas.GiangVienUpdate) -> Optional[schemas.GiangVien]:
        gv = self.repo.update(id_giang_vien, data)
        if gv:
            return schemas.GiangVien.model_validate(gv)
        return None
    
    def delete_giang_vien(self, id_giang_vien: str) -> bool:
        return self.repo.delete(id_giang_vien)