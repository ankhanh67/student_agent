from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas
from app.services import fact_diem_service

router = APIRouter(prefix="/fact-diem", tags=["Fact Diem"])


@router.get("/", response_model=List[schemas.FactDiemOut])
def list_fact_diem(db: Session = Depends(get_db)):
    return fact_diem_service.list_fact_diem(db)


@router.get("/sinh-vien/{id_sinh_vien}", response_model=List[schemas.FactDiemOut])
def list_fact_diem_by_sinh_vien(id_sinh_vien: str, db: Session = Depends(get_db)):
    return fact_diem_service.get_fact_diem_by_sinh_vien(db, id_sinh_vien)


@router.get("/hoc-ky/{id_hocky}", response_model=List[schemas.FactDiemOut])
def list_fact_diem_by_hoc_ky(id_hocky: str, db: Session = Depends(get_db)):
    return fact_diem_service.get_fact_diem_by_hoc_ky(db, id_hocky)


@router.get("/{id}", response_model=schemas.FactDiemOut)
def get_fact_diem(id: str, db: Session = Depends(get_db)):
    fd = fact_diem_service.get_fact_diem(db, id)
    if not fd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bản ghi điểm",
        )
    return fd


@router.post("/", response_model=schemas.FactDiemOut, status_code=status.HTTP_201_CREATED)
def create_fact_diem(data: schemas.FactDiemCreate, db: Session = Depends(get_db)):
    return fact_diem_service.create_fact_diem(db, data)


@router.put("/{id}", response_model=schemas.FactDiemOut)
def update_fact_diem(id: str, data: schemas.FactDiemUpdate, db: Session = Depends(get_db)):
    fd = fact_diem_service.update_fact_diem(db, id, data)
    if not fd:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bản ghi điểm",
        )
    return fd


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fact_diem(id: str, db: Session = Depends(get_db)):
    ok = fact_diem_service.delete_fact_diem(db, id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy bản ghi điểm",
        )
    return