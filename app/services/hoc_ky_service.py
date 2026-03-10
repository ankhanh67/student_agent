from sqlalchemy.orm import Session
from typing import List

from app import schemas
from app.repositories import hoc_ky_repository


def list_hoc_ky(db: Session) -> List[schemas.HocKyOut]:
    return hoc_ky_repository.get_all(db)


def get_hoc_ky(db: Session, id_hocky: str):
    return hoc_ky_repository.get_by_id(db, id_hocky)


def create_hoc_ky(db: Session, data: schemas.HocKyCreate):
    id_hocky = data.id_hocky
    if not id_hocky:
        # ví dụ: namHoc="2024-2025", kyHoc="1" -> "HK20242025_1"
        nam = data.namHoc.replace("-", "").replace(" ", "")
        ky = str(data.kyHoc).strip()
        id_hocky = f"HK{nam}_{ky}"
    return hoc_ky_repository.create(db, id_hocky=id_hocky, data=data)


def update_hoc_ky(db: Session, id_hocky: str, data: schemas.HocKyUpdate):
    return hoc_ky_repository.update(db, id_hocky, data)


def delete_hoc_ky(db: Session, id_hocky: str) -> bool:
    return hoc_ky_repository.delete(db, id_hocky)