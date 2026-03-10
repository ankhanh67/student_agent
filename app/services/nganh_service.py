from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.repositories import nganh_repository
from app.services.id_generator import next_code


def list_nganh(db: Session) -> List[schemas.NganhOut]:
    return nganh_repository.get_all(db)


def get_nganh(db: Session, id_nganh: str):
    return nganh_repository.get_by_id(db, id_nganh)


def get_nganh_by_khoa(db: Session, id_khoa: str) -> List[schemas.NganhOut]:
    return nganh_repository.get_by_khoa(db, id_khoa)


def create_nganh(db: Session, data: schemas.NganhCreate):
    id_nganh = data.id_nganh or next_code(db, model=models.Nganh, id_attr="id_nganh", prefix="NGANH")
    return nganh_repository.create(db, id_nganh=id_nganh, data=data)


def update_nganh(db: Session, id_nganh: str, data: schemas.NganhUpdate):
    return nganh_repository.update(db, id_nganh, data)


def delete_nganh(db: Session, id_nganh: str) -> bool:
    return nganh_repository.delete(db, id_nganh)