from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.repositories import fact_diem_repository
import uuid


def list_fact_diem(db: Session) -> List[schemas.FactDiemOut]:
    return fact_diem_repository.get_all(db)


def get_fact_diem(db: Session, id: str):
    return fact_diem_repository.get_by_id(db, id)


def get_fact_diem_by_sinh_vien(db: Session, id_sinh_vien: str) -> List[schemas.FactDiemOut]:
    return fact_diem_repository.get_by_sinh_vien(db, id_sinh_vien)


def get_fact_diem_by_hoc_ky(db: Session, id_hocky: str) -> List[schemas.FactDiemOut]:
    return fact_diem_repository.get_by_hoc_ky(db, id_hocky)


def create_fact_diem(db: Session, data: schemas.FactDiemCreate):
    id_fact = data.id or f"FD{uuid.uuid4().hex[:12].upper()}"
    return fact_diem_repository.create(db, id=id_fact, data=data)


def update_fact_diem(db: Session, id: str, data: schemas.FactDiemUpdate):
    return fact_diem_repository.update(db, id, data)


def delete_fact_diem(db: Session, id: str) -> bool:
    return fact_diem_repository.delete(db, id)