from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas

class FactDiemRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.FactDiem]:
        return self.db.query(models.FactDiem).all()

    def get_by_id(self, id: str) -> Optional[models.FactDiem]:
        return self.db.query(models.FactDiem).filter(
            models.FactDiem.id == id
        ).first()

    def get_by_sinh_vien(self, id_sinh_vien: str) -> List[models.FactDiem]:
        return self.db.query(models.FactDiem).filter(
            models.FactDiem.id_sinh_vien == id_sinh_vien
        ).all()

    def get_by_hoc_ky(self, id_hocky: str) -> List[models.FactDiem]:
        return self.db.query(models.FactDiem).filter(
            models.FactDiem.id_hocky == id_hocky
        ).all()

    def create(self, data: schemas.FactDiemCreate) -> models.FactDiem:
        fd = models.FactDiem(
            id=data.id,
            id_sinh_vien=data.id_sinh_vien,
            id_mon_hoc=data.id_mon_hoc,
            id_khoa=data.id_khoa,
            id_nganh=data.id_nganh,
            id_hocky=data.id_hocky,
            diemHe10=data.diemHe10,
            diemChu=data.diemChu,
            soLanHoc=data.soLanHoc or 1,
            soTinChiDat=data.soTinChiDat,
            ketQua=data.ketQua,
        )
        self.db.add(fd)
        self.db.commit()
        self.db.refresh(fd)
        return fd

    def update(self, id: str, data: schemas.FactDiemUpdate) -> Optional[models.FactDiem]:
        fd = self.get_by_id(id)
        if not fd:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(fd, field, value)
        self.db.commit()
        self.db.refresh(fd)
        return fd

    def delete(self, id: str) -> bool:
        fd = self.get_by_id(id)
        if not fd:
            return False
        self.db.delete(fd)
        self.db.commit()
        return True