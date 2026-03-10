from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas
from app.services import hoc_ky_service

router = APIRouter(prefix="/hoc-ky", tags=["Hoc Ky"])


@router.get("/", response_model=List[schemas.HocKyOut])
def list_hoc_ky(db: Session = Depends(get_db)):
    return hoc_ky_service.list_hoc_ky(db)


@router.get("/{id_hocky}", response_model=schemas.HocKyOut)
def get_hoc_ky(id_hocky: str, db: Session = Depends(get_db)):
    hk = hoc_ky_service.get_hoc_ky(db, id_hocky)
    if not hk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy học kỳ",
        )
    return hk


@router.post("/", response_model=schemas.HocKyOut, status_code=status.HTTP_201_CREATED)
def create_hoc_ky(data: schemas.HocKyCreate, db: Session = Depends(get_db)):
    return hoc_ky_service.create_hoc_ky(db, data)


@router.put("/{id_hocky}", response_model=schemas.HocKyOut)
def update_hoc_ky(id_hocky: str, data: schemas.HocKyUpdate, db: Session = Depends(get_db)):
    hk = hoc_ky_service.update_hoc_ky(db, id_hocky, data)
    if not hk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy học kỳ",
        )
    return hk


@router.delete("/{id_hocky}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hoc_ky(id_hocky: str, db: Session = Depends(get_db)):
    ok = hoc_ky_service.delete_hoc_ky(db, id_hocky)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy học kỳ",
        )
    return