from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas
from app.services import khoa_service

router = APIRouter(prefix="/khoa", tags=["Khoa"])


@router.get("/", response_model=List[schemas.KhoaOut])
def list_khoa(db: Session = Depends(get_db)):
    return khoa_service.list_khoa(db)


@router.get("/{id_khoa}", response_model=schemas.KhoaOut)
def get_khoa(id_khoa: str, db: Session = Depends(get_db)):
    khoa = khoa_service.get_khoa(db, id_khoa)
    if not khoa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khoa",
        )
    return khoa


@router.post("/", response_model=schemas.KhoaOut, status_code=status.HTTP_201_CREATED)
def create_khoa(data: schemas.KhoaCreate, db: Session = Depends(get_db)):
    return khoa_service.create_khoa(db, data)


@router.put("/{id_khoa}", response_model=schemas.KhoaOut)
def update_khoa(id_khoa: str, data: schemas.KhoaUpdate, db: Session = Depends(get_db)):
    khoa = khoa_service.update_khoa(db, id_khoa, data)
    if not khoa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khoa",
        )
    return khoa


@router.delete("/{id_khoa}", status_code=status.HTTP_204_NO_CONTENT)
def delete_khoa(id_khoa: str, db: Session = Depends(get_db)):
    ok = khoa_service.delete_khoa(db, id_khoa)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khoa",
        )
    return