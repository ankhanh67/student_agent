from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Khoa(Base):
    __tablename__ = "khoa"

    id_khoa = Column(String(20), primary_key=True, index=True)
    tenKhoa = Column(String, nullable=False)

    nganhs = relationship("Nganh", back_populates="khoa")
    fact_diems = relationship("FactDiem", back_populates="khoa")


class Nganh(Base):
    __tablename__ = "nganh"

    id_nganh = Column(String(20), primary_key=True, index=True)
    tenNganh = Column(String, nullable=False)
    id_khoa = Column(String(20), ForeignKey("khoa.id_khoa"), nullable=False)

    khoa = relationship("Khoa", back_populates="nganhs")
    sinh_viens = relationship("SinhVien", back_populates="nganh")
    fact_diems = relationship("FactDiem", back_populates="nganh")


class SinhVien(Base):
    __tablename__ = "sinh_vien"

    id_sinh_vien = Column(String(20), primary_key=True, index=True)
    hoTen = Column(String, nullable=False)
    ngaySinh = Column(Date, nullable=True)
    gioiTinh = Column(String, nullable=True)
    email = Column(String, nullable=True)
    soDienthoai = Column(String, nullable=True)
    diaChi = Column(String, nullable=True)
    id_nganh = Column(String(20), ForeignKey("nganh.id_nganh"), nullable=False)

    nganh = relationship("Nganh", back_populates="sinh_viens")
    fact_diems = relationship("FactDiem", back_populates="sinh_vien")


class MonHoc(Base):
    __tablename__ = "mon_hoc"

    id_mon_hoc = Column(String(20), primary_key=True, index=True)
    tenMon = Column(String, nullable=False)
    soTinchi = Column(Integer, nullable=False)
    loaiMon = Column(String, nullable=True)

    fact_diems = relationship("FactDiem", back_populates="mon_hoc")


class HocKy(Base):
    __tablename__ = "hoc_ky"

    id_hocky = Column(String(30), primary_key=True, index=True)
    tenHocky = Column(String, nullable=False)
    namHoc = Column(String, nullable=False)  # ví dụ: "2024-2025"
    kyHoc = Column(String, nullable=False)   # ví dụ: "1", "2", "He"

    fact_diems = relationship("FactDiem", back_populates="hoc_ky")


class FactDiem(Base):
    __tablename__ = "fact_diem"

    id = Column(String(40), primary_key=True, index=True)

    id_sinh_vien = Column(String(20), ForeignKey("sinh_vien.id_sinh_vien"), nullable=False)
    id_mon_hoc = Column(String(20), ForeignKey("mon_hoc.id_mon_hoc"), nullable=False)
    id_khoa = Column(String(20), ForeignKey("khoa.id_khoa"), nullable=False)
    id_nganh = Column(String(20), ForeignKey("nganh.id_nganh"), nullable=False)
    id_hocky = Column(String(30), ForeignKey("hoc_ky.id_hocky"), nullable=False)

    diemHe10 = Column(Float, nullable=True)
    diemChu = Column(String, nullable=True)       # A, B+, ...
    soLanHoc = Column(Integer, nullable=False, default=1)
    soTinChiDat = Column(Integer, nullable=True)  # = 0 nếu rớt
    ketQua = Column(Boolean, nullable=True)       # True = Qua, False = Rớt

    sinh_vien = relationship("SinhVien", back_populates="fact_diems")
    mon_hoc = relationship("MonHoc", back_populates="fact_diems")
    khoa = relationship("Khoa", back_populates="fact_diems")
    nganh = relationship("Nganh", back_populates="fact_diems")
    hoc_ky = relationship("HocKy", back_populates="fact_diems")