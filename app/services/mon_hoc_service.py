from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.repositories import mon_hoc_repository
from app.services.id_generator import next_code


def list_mon_hoc(db: Session) -> List[schemas.MonHocOut]:
    return mon_hoc_repository.get_all(db)


def get_mon_hoc(db: Session, id_mon_hoc: str):
    return mon_hoc_repository.get_by_id(db, id_mon_hoc)


def create_mon_hoc(db: Session, data: schemas.MonHocCreate):
    id_mon_hoc = data.id_mon_hoc or next_code(db, model=models.MonHoc, id_attr="id_mon_hoc", prefix="MH")
    return mon_hoc_repository.create(db, id_mon_hoc=id_mon_hoc, data=data)


def update_mon_hoc(db: Session, id_mon_hoc: str, data: schemas.MonHocUpdate):
    return mon_hoc_repository.update(db, id_mon_hoc, data)


def delete_mon_hoc(db: Session, id_mon_hoc: str) -> bool:
    return mon_hoc_repository.delete(db, id_mon_hoc)