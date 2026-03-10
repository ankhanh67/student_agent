from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas

class MonHocRepository:
    
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.MonHoc]:
        return self.db.query(models.MonHoc).all()

    def get_by_id(self, id_mon_hoc: str) -> Optional[models.MonHoc]:
        return self.db.query(models.MonHoc).filter(
            models.MonHoc.id_mon_hoc == id_mon_hoc
        ).first()

    def create(self, data: schemas.MonHocCreate) -> models.MonHoc:
        mh = models.MonHoc(
            id_mon_hoc=data.id_mon_hoc,
            tenMon=data.tenMon,
            soTinchi=data.soTinchi,
            loaiMon=data.loaiMon,
        )
        self.db.add(mh)
        self.db.commit()
        self.db.refresh(mh)
        return mh

    def update(self, id_mon_hoc: str, data: schemas.MonHocUpdate) -> Optional[models.MonHoc]:
        mh = self.get_by_id(id_mon_hoc)
        if not mh:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(mh, field, value)
        self.db.commit()
        self.db.refresh(mh)
        return mh

    def delete(self, id_mon_hoc: str) -> bool:
        mh = self.get_by_id(id_mon_hoc)
        if not mh:
            return False
        self.db.delete(mh)
        self.db.commit()
        return True