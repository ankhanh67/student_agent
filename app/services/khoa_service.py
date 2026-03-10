from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.repositories import khoa_repository
from app.services.id_generator import next_code


def list_khoa(db: Session) -> List[schemas.KhoaOut]:
    return khoa_repository.get_all(db)


def get_khoa(db: Session, id_khoa: str):
    return khoa_repository.get_by_id(db, id_khoa)


def create_khoa(db: Session, data: schemas.KhoaCreate):
    id_khoa = data.id_khoa or next_code(db, model=models.Khoa, id_attr="id_khoa", prefix="KHOA")
    return khoa_repository.create(db, id_khoa=id_khoa, data=data)


def update_khoa(db: Session, id_khoa: str, data: schemas.KhoaUpdate):
    return khoa_repository.update(db, id_khoa, data)


def delete_khoa(db: Session, id_khoa: str) -> bool:
    return khoa_repository.delete(db, id_khoa)