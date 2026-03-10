from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas
from app.services import mon_hoc_service

router = APIRouter(prefix="/mon-hoc", tags=["Mon Hoc"])


@router.get("/", response_model=List[schemas.MonHocOut])
def list_mon_hoc(db: Session = Depends(get_db)):
    return mon_hoc_service.list_mon_hoc(db)


@router.get("/{id_mon_hoc}", response_model=schemas.MonHocOut)
def get_mon_hoc(id_mon_hoc: str, db: Session = Depends(get_db)):
    mh = mon_hoc_service.get_mon_hoc(db, id_mon_hoc)
    if not mh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học",
        )
    return mh


@router.post("/", response_model=schemas.MonHocOut, status_code=status.HTTP_201_CREATED)
def create_mon_hoc(data: schemas.MonHocCreate, db: Session = Depends(get_db)):
    return mon_hoc_service.create_mon_hoc(db, data)


@router.put("/{id_mon_hoc}", response_model=schemas.MonHocOut)
def update_mon_hoc(id_mon_hoc: str, data: schemas.MonHocUpdate, db: Session = Depends(get_db)):
    mh = mon_hoc_service.update_mon_hoc(db, id_mon_hoc, data)
    if not mh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học",
        )
    return mh


@router.delete("/{id_mon_hoc}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mon_hoc(id_mon_hoc: str, db: Session = Depends(get_db)):
    ok = mon_hoc_service.delete_mon_hoc(db, id_mon_hoc)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy môn học",
        )
    return