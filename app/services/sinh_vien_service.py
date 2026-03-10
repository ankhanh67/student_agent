# app/services/sinh_vien_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas
from app.repositories.sinh_vien_repository import SinhVienRepository

class SinhVienService:
    
    def __init__(self, db: Session):
        self.repo = SinhVienRepository(db)
    
    def get_all_sinh_vien(self) -> List[schemas.SinhVien]:
        sv_list = self.repo.get_all()
        return [schemas.SinhVien.model_validate(s) for s in sv_list]
    
    def get_sinh_vien_by_id(self, id_sinh_vien: str) -> Optional[schemas.SinhVien]:
        sv = self.repo.get_by_id(id_sinh_vien)
        if sv:
            return schemas.SinhVien.model_validate(sv)
        return None
    
    def get_sinh_vien_by_lop(self, id_lop: str) -> List[schemas.SinhVien]:
        sv_list = self.repo.get_by_lop(id_lop)
        return [schemas.SinhVien.model_validate(s) for s in sv_list]
    
    def get_sinh_vien_by_nganh(self, id_nganh: str) -> List[schemas.SinhVien]:
        sv_list = self.repo.get_by_nganh(id_nganh)
        return [schemas.SinhVien.model_validate(s) for s in sv_list]
    
    def create_sinh_vien(self, data: schemas.SinhVienCreate) -> schemas.SinhVien:
        sv = self.repo.create(data)
        return schemas.SinhVien.model_validate(sv)
    
    def update_sinh_vien(self, id_sinh_vien: str, data: schemas.SinhVienUpdate) -> Optional[schemas.SinhVien]:
        sv = self.repo.update(id_sinh_vien, data)
        if sv:
            return schemas.SinhVien.model_validate(sv)
        return None
    
    def delete_sinh_vien(self, id_sinh_vien: str) -> bool:
        return self.repo.delete(id_sinh_vien)