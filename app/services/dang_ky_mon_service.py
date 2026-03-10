# app/services/dang_ky_mon_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas
from app.repositories.dang_ky_mon_repository import DangKyMonRepository

class DangKyMonService:
    
    def __init__(self, db: Session):
        self.repo = DangKyMonRepository(db)
    
    def get_all_dang_ky(self) -> List[schemas.DangKyMon]:
        dk_list = self.repo.get_all()
        return [schemas.DangKyMon.model_validate(d) for d in dk_list]
    
    def get_dang_ky_by_id(self, id_dang_ky: str) -> Optional[schemas.DangKyMon]:
        dk = self.repo.get_by_id(id_dang_ky)
        if dk:
            return schemas.DangKyMon.model_validate(dk)
        return None
    
    def get_dang_ky_by_sinh_vien(self, id_sinh_vien: str) -> List[schemas.DangKyMon]:
        dk_list = self.repo.get_by_sinh_vien(id_sinh_vien)
        return [schemas.DangKyMon.model_validate(d) for d in dk_list]
    
    def get_dang_ky_by_lop_mon(self, id_lop_mon: str) -> List[schemas.DangKyMon]:
        dk_list = self.repo.get_by_lop_mon(id_lop_mon)
        return [schemas.DangKyMon.model_validate(d) for d in dk_list]
    
    def get_dang_ky_by_hoc_ky(self, id_hoc_ky: str) -> List[schemas.DangKyMon]:
        dk_list = self.repo.get_by_hoc_ky(id_hoc_ky)
        return [schemas.DangKyMon.model_validate(d) for d in dk_list]
    
    def create_dang_ky(self, data: schemas.DangKyMonCreate) -> schemas.DangKyMon:
        dk = self.repo.create(data)
        return schemas.DangKyMon.model_validate(dk)
    
    def update_dang_ky(self, id_dang_ky: str, data: schemas.DangKyMonUpdate) -> Optional[schemas.DangKyMon]:
        dk = self.repo.update(id_dang_ky, data)
        if dk:
            return schemas.DangKyMon.model_validate(dk)
        return None
    
    def delete_dang_ky(self, id_dang_ky: str) -> bool:
        return self.repo.delete(id_dang_ky)