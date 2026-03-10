from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas
from app.services import sinh_vien_service

router = APIRouter(prefix="/sinh-vien", tags=["Sinh Vien"])


@router.get("/", response_model=List[schemas.SinhVienOut])
def list_sinh_vien(db: Session = Depends(get_db)):
    return sinh_vien_service.list_sinh_vien(db)


@router.get("/nganh/{id_nganh}", response_model=List[schemas.SinhVienOut])
def list_sinh_vien_by_nganh(id_nganh: str, db: Session = Depends(get_db)):
    return sinh_vien_service.get_sinh_vien_by_nganh(db, id_nganh)


@router.get("/{id_sinh_vien}", response_model=schemas.SinhVienOut)
def get_sinh_vien(id_sinh_vien: str, db: Session = Depends(get_db)):
    sv = sinh_vien_service.get_sinh_vien(db, id_sinh_vien)
    if not sv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sinh viên",
        )
    return sv


@router.post("/", response_model=schemas.SinhVienOut, status_code=status.HTTP_201_CREATED)
def create_sinh_vien(data: schemas.SinhVienCreate, db: Session = Depends(get_db)):
    return sinh_vien_service.create_sinh_vien(db, data)


@router.put("/{id_sinh_vien}", response_model=schemas.SinhVienOut)
def update_sinh_vien(id_sinh_vien: str, data: schemas.SinhVienUpdate, db: Session = Depends(get_db)):
    sv = sinh_vien_service.update_sinh_vien(db, id_sinh_vien, data)
    if not sv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sinh viên",
        )
    return sv


@router.delete("/{id_sinh_vien}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sinh_vien(id_sinh_vien: str, db: Session = Depends(get_db)):
    ok = sinh_vien_service.delete_sinh_vien(db, id_sinh_vien)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy sinh viên",
        )
    return