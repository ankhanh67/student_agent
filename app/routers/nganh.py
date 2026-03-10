from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas
from app.services import nganh_service

router = APIRouter(prefix="/nganh", tags=["Nganh"])


@router.get("/", response_model=List[schemas.NganhOut])
def list_nganh(db: Session = Depends(get_db)):
    return nganh_service.list_nganh(db)


@router.get("/khoa/{id_khoa}", response_model=List[schemas.NganhOut])
def list_nganh_by_khoa(id_khoa: str, db: Session = Depends(get_db)):
    return nganh_service.get_nganh_by_khoa(db, id_khoa)


@router.get("/{id_nganh}", response_model=schemas.NganhOut)
def get_nganh(id_nganh: str, db: Session = Depends(get_db)):
    nganh = nganh_service.get_nganh(db, id_nganh)
    if not nganh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy ngành",
        )
    return nganh


@router.post("/", response_model=schemas.NganhOut, status_code=status.HTTP_201_CREATED)
def create_nganh(data: schemas.NganhCreate, db: Session = Depends(get_db)):
    return nganh_service.create_nganh(db, data)


@router.put("/{id_nganh}", response_model=schemas.NganhOut)
def update_nganh(id_nganh: str, data: schemas.NganhUpdate, db: Session = Depends(get_db)):
    nganh = nganh_service.update_nganh(db, id_nganh, data)
    if not nganh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy ngành",
        )
    return nganh


@router.delete("/{id_nganh}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nganh(id_nganh: str, db: Session = Depends(get_db)):
    ok = nganh_service.delete_nganh(db, id_nganh)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy ngành",
        )
    return