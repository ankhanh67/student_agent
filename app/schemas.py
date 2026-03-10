from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

# ------------------- Khoa -------------------
class KhoaBase(BaseModel):
    id_khoa: str
    ten_khoa: str

class KhoaCreate(KhoaBase):
    pass

class KhoaUpdate(BaseModel):
    ten_khoa: Optional[str] = None

class Khoa(KhoaBase):
    class Config:
        from_attributes = True

# ------------------- Nganh -------------------
class NganhBase(BaseModel):
    id_nganh: str
    ten_nganh: str
    id_khoa: str

class NganhCreate(NganhBase):
    pass

class NganhUpdate(BaseModel):
    ten_nganh: Optional[str] = None
    id_khoa: Optional[str] = None

class Nganh(NganhBase):
    class Config:
        from_attributes = True

# ------------------- LopHoc -------------------
class LopHocBase(BaseModel):
    id_lop: str
    ten_lop: str
    khoa_hoc: Optional[str] = None
    nam_nhap_hoc: Optional[int] = None
    si_so_toi_da: Optional[int] = 50
    id_khoa: str
    id_nganh: str

class LopHocCreate(LopHocBase):
    pass

class LopHocUpdate(BaseModel):
    ten_lop: Optional[str] = None
    khoa_hoc: Optional[str] = None
    nam_nhap_hoc: Optional[int] = None
    si_so_toi_da: Optional[int] = None
    id_khoa: Optional[str] = None
    id_nganh: Optional[str] = None

class LopHoc(LopHocBase):
    class Config:
        from_attributes = True

# ------------------- SinhVien -------------------
class SinhVienBase(BaseModel):
    id_sinh_vien: str
    ho_ten: str
    ngay_sinh: Optional[date] = None
    gioi_tinh: Optional[str] = None
    email: Optional[EmailStr] = None
    so_dien_thoai: Optional[str] = None
    dia_chi: Optional[str] = None
    id_nganh: str
    id_lop: str

class SinhVienCreate(SinhVienBase):
    pass

class SinhVienUpdate(BaseModel):
    ho_ten: Optional[str] = None
    ngay_sinh: Optional[date] = None
    gioi_tinh: Optional[str] = None
    email: Optional[EmailStr] = None
    so_dien_thoai: Optional[str] = None
    dia_chi: Optional[str] = None
    id_nganh: Optional[str] = None
    id_lop: Optional[str] = None

class SinhVien(SinhVienBase):
    class Config:
        from_attributes = True

# ------------------- GiangVien -------------------
class GiangVienBase(BaseModel):
    id_giang_vien: str
    ho_ten: str
    email: Optional[EmailStr] = None
    so_dien_thoai: Optional[str] = None
    hoc_ham: Optional[str] = None
    id_khoa: str

class GiangVienCreate(GiangVienBase):
    pass

class GiangVienUpdate(BaseModel):
    ho_ten: Optional[str] = None
    email: Optional[EmailStr] = None
    so_dien_thoai: Optional[str] = None
    hoc_ham: Optional[str] = None
    id_khoa: Optional[str] = None

class GiangVien(GiangVienBase):
    class Config:
        from_attributes = True

# ------------------- MonHoc -------------------
class MonHocBase(BaseModel):
    id_mon_hoc: str
    ten_mon: str
    so_tin_chi: int
    loai_mon: Optional[str] = None
    mo_ta: Optional[str] = None
    he_so: Optional[float] = 1.0
    id_mon_tien_quyet: Optional[str] = None

class MonHocCreate(MonHocBase):
    pass

class MonHocUpdate(BaseModel):
    ten_mon: Optional[str] = None
    so_tin_chi: Optional[int] = None
    loai_mon: Optional[str] = None
    mo_ta: Optional[str] = None
    he_so: Optional[float] = None
    id_mon_tien_quyet: Optional[str] = None

class MonHoc(MonHocBase):
    class Config:
        from_attributes = True

# ------------------- HocKy -------------------
class HocKyBase(BaseModel):
    id_hoc_ky: str
    ten_hoc_ky: str
    nam_hoc: str
    ky_hoc: str

class HocKyCreate(HocKyBase):
    pass

class HocKyUpdate(BaseModel):
    ten_hoc_ky: Optional[str] = None
    nam_hoc: Optional[str] = None
    ky_hoc: Optional[str] = None

class HocKy(HocKyBase):
    class Config:
        from_attributes = True

# ------------------- LopMonHoc -------------------
class LopMonHocBase(BaseModel):
    id_lop_mon: str
    id_mon_hoc: str
    id_giang_vien: str
    id_hoc_ky: str
    si_so_toi_da: Optional[int] = 50
    phong_hoc: Optional[str] = None
    lich_hoc: Optional[str] = None

class LopMonHocCreate(LopMonHocBase):
    pass

class LopMonHocUpdate(BaseModel):
    si_so_toi_da: Optional[int] = None
    phong_hoc: Optional[str] = None
    lich_hoc: Optional[str] = None

class LopMonHoc(LopMonHocBase):
    class Config:
        from_attributes = True

# ------------------- DangKyMon -------------------
class DangKyMonBase(BaseModel):
    id_dang_ky: str
    id_sinh_vien: str
    id_lop_mon: str
    ngay_dang_ky: date
    trang_thai: Optional[str] = 'Đã duyệt'

class DangKyMonCreate(DangKyMonBase):
    pass

class DangKyMonUpdate(BaseModel):
    trang_thai: Optional[str] = None

class DangKyMon(DangKyMonBase):
    class Config:
        from_attributes = True

# ------------------- FactDiem (QUAN TRỌNG NHẤT) -------------------
class FactDiemBase(BaseModel):
    id_diem: str
    id_dang_ky: str
    id_sinh_vien: str
    id_mon_hoc: str
    id_lop_mon: str
    id_giang_vien: str
    id_hoc_ky: str
    diem_chuyen_can: Optional[float] = None
    diem_giua_ky: Optional[float] = None
    diem_cuoi_ky: Optional[float] = None
    diem_trung_binh: Optional[float] = None
    diem_chu: Optional[str] = None
    so_lan_hoc: Optional[int] = 1
    so_tin_chi_dat: Optional[int] = 0
    ket_qua: Optional[bool] = None

class FactDiemCreate(FactDiemBase):
    pass

class FactDiemUpdate(BaseModel):
    diem_chuyen_can: Optional[float] = None
    diem_giua_ky: Optional[float] = None
    diem_cuoi_ky: Optional[float] = None
    diem_trung_binh: Optional[float] = None
    diem_chu: Optional[str] = None
    so_lan_hoc: Optional[int] = None
    so_tin_chi_dat: Optional[int] = None
    ket_qua: Optional[bool] = None

class FactDiem(FactDiemBase):
    class Config:
        from_attributes = True