# app/services/id_generator.py
from __future__ import annotations
from sqlalchemy.orm import Session

def next_code(
    db: Session,
    *,
    model,
    id_attr: str,
    prefix: str,
    width: int = 3,
) -> str:
    """
    Sinh mã dạng PREFIX001, PREFIX002...
    Dựa trên các ID hiện có bắt đầu bằng prefix.
    
    Args:
        db: Session database
        model: Model class (VD: models.Khoa)
        id_attr: Tên cột ID (VD: 'id_khoa')
        prefix: Tiền tố mã (VD: 'K', 'N', 'SV')
        width: Độ rộng phần số (VD: 3 -> 001, 002)
    
    Returns:
        Mã mới dạng PREFIX + số (VD: K004, N005, SV006)
    """
    col = getattr(model, id_attr)
    rows = db.query(col).filter(col.like(f"{prefix}%")).all()

    max_num = 0
    for (val,) in rows:
        if not isinstance(val, str) or not val.startswith(prefix):
            continue
        suffix = val[len(prefix):]
        if suffix.isdigit():
            max_num = max(max_num, int(suffix))

    return f"{prefix}{max_num + 1:0{width}d}"

# Các hàm tiện ích bổ sung
def generate_khoa_code(db: Session) -> str:
    """Sinh mã khoa mới (K001, K002...)"""
    from app import models
    return next_code(db, model=models.Khoa, id_attr='id_khoa', prefix='K', width=3)

def generate_nganh_code(db: Session) -> str:
    """Sinh mã ngành mới (N001, N002...)"""
    from app import models
    return next_code(db, model=models.Nganh, id_attr='id_nganh', prefix='N', width=3)

def generate_lop_code(db: Session) -> str:
    """Sinh mã lớp mới (L001, L002...)"""
    from app import models
    return next_code(db, model=models.LopHoc, id_attr='id_lop', prefix='L', width=3)

def generate_sinh_vien_code(db: Session) -> str:
    """Sinh mã sinh viên mới (SV001, SV002...)"""
    from app import models
    return next_code(db, model=models.SinhVien, id_attr='id_sinh_vien', prefix='SV', width=3)

def generate_giang_vien_code(db: Session) -> str:
    """Sinh mã giảng viên mới (GV001, GV002...)"""
    from app import models
    return next_code(db, model=models.GiangVien, id_attr='id_giang_vien', prefix='GV', width=3)

def generate_mon_hoc_code(db: Session) -> str:
    """Sinh mã môn học mới (MH001, MH002...)"""
    from app import models
    return next_code(db, model=models.MonHoc, id_attr='id_mon_hoc', prefix='MH', width=3)

def generate_dang_ky_code(db: Session) -> str:
    """Sinh mã đăng ký mới (DK001, DK002...)"""
    from app import models
    return next_code(db, model=models.DangKyMon, id_attr='id_dang_ky', prefix='DK', width=3)

def generate_lop_mon_code(db: Session) -> str:
    """Sinh mã lớp học phần mới (LM001, LM002...)"""
    from app import models
    return next_code(db, model=models.LopMonHoc, id_attr='id_lop_mon', prefix='LM', width=3)