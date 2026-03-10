from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.repositories import sinh_vien_repository
from app.services.id_generator import next_code


def list_sinh_vien(db: Session) -> List[schemas.SinhVienOut]:
    return sinh_vien_repository.get_all(db)


def get_sinh_vien(db: Session, id_sinh_vien: str):
    return sinh_vien_repository.get_by_id(db, id_sinh_vien)


def get_sinh_vien_by_nganh(db: Session, id_nganh: str) -> List[schemas.SinhVienOut]:
    return sinh_vien_repository.get_by_nganh(db, id_nganh)


def create_sinh_vien(db: Session, data: schemas.SinhVienCreate):
    id_sinh_vien = data.id_sinh_vien or next_code(db, model=models.SinhVien, id_attr="id_sinh_vien", prefix="SV")
    return sinh_vien_repository.create(db, id_sinh_vien=id_sinh_vien, data=data)


def update_sinh_vien(db: Session, id_sinh_vien: str, data: schemas.SinhVienUpdate):
    return sinh_vien_repository.update(db, id_sinh_vien, data)


def delete_sinh_vien(db: Session, id_sinh_vien: str) -> bool:
    return sinh_vien_repository.delete(db, id_sinh_vien)