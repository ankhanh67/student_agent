from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- KHOA ----------

class KhoaBase(BaseModel):
    tenKhoa: str


class KhoaCreate(KhoaBase):
    id_khoa: Optional[str] = None


class KhoaUpdate(BaseModel):
    tenKhoa: Optional[str] = None


class KhoaOut(ORMModel, KhoaBase):
    id_khoa: str


# ---------- NGANH ----------

class NganhBase(BaseModel):
    tenNganh: str
    id_khoa: str


class NganhCreate(NganhBase):
    id_nganh: Optional[str] = None


class NganhUpdate(BaseModel):
    tenNganh: Optional[str] = None
    id_khoa: Optional[str] = None


class NganhOut(ORMModel, NganhBase):
    id_nganh: str


# ---------- SINH VIEN ----------

class SinhVienBase(BaseModel):
    hoTen: str
    ngaySinh: Optional[date] = None
    gioiTinh: Optional[str] = None
    email: Optional[EmailStr] = None
    soDienthoai: Optional[str] = None
    diaChi: Optional[str] = None
    id_nganh: str


class SinhVienCreate(SinhVienBase):
    id_sinh_vien: Optional[str] = None


class SinhVienUpdate(BaseModel):
    hoTen: Optional[str] = None
    ngaySinh: Optional[date] = None
    gioiTinh: Optional[str] = None
    email: Optional[EmailStr] = None
    soDienthoai: Optional[str] = None
    diaChi: Optional[str] = None
    id_nganh: Optional[str] = None


class SinhVienOut(ORMModel, SinhVienBase):
    id_sinh_vien: str


# ---------- MON HOC ----------

class MonHocBase(BaseModel):
    tenMon: str
    soTinchi: int
    loaiMon: Optional[str] = None


class MonHocCreate(MonHocBase):
    id_mon_hoc: Optional[str] = None


class MonHocUpdate(BaseModel):
    tenMon: Optional[str] = None
    soTinchi: Optional[int] = None
    loaiMon: Optional[str] = None


class MonHocOut(ORMModel, MonHocBase):
    id_mon_hoc: str


# ---------- HOC KY ----------

class HocKyBase(BaseModel):
    tenHocky: str
    namHoc: str
    kyHoc: str


class HocKyCreate(HocKyBase):
    id_hocky: Optional[str] = None


class HocKyUpdate(BaseModel):
    tenHocky: Optional[str] = None
    namHoc: Optional[str] = None
    kyHoc: Optional[str] = None


class HocKyOut(ORMModel, HocKyBase):
    id_hocky: str


# ---------- FACT DIEM ----------

class FactDiemBase(BaseModel):
    id_sinh_vien: str
    id_mon_hoc: str
    id_khoa: str
    id_nganh: str
    id_hocky: str

    diemHe10: Optional[float] = None
    diemChu: Optional[str] = None
    soLanHoc: Optional[int] = 1
    soTinChiDat: Optional[int] = None
    ketQua: Optional[bool] = None


class FactDiemCreate(FactDiemBase):
    id: Optional[str] = None


class FactDiemUpdate(BaseModel):
    id_sinh_vien: Optional[str] = None
    id_mon_hoc: Optional[str] = None
    id_khoa: Optional[str] = None
    id_nganh: Optional[str] = None
    id_hocky: Optional[str] = None

    diemHe10: Optional[float] = None
    diemChu: Optional[str] = None
    soLanHoc: Optional[int] = None
    soTinChiDat: Optional[int] = None
    ketQua: Optional[bool] = None


class FactDiemOut(ORMModel, FactDiemBase):
    id: str