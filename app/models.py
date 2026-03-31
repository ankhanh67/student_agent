# app/models.py
from sqlalchemy import Column, String, Integer, Float, Date, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Khoa(Base):
    __tablename__ = "khoa"
    
    id_khoa = Column(String, primary_key=True, index=True)  
    ten_khoa = Column(String, nullable=False)
    
    # Relationships
    nganhs = relationship("Nganh", back_populates="khoa")
    lop_hocs = relationship("LopHoc", back_populates="khoa")
    giang_viens = relationship("GiangVien", back_populates="khoa")


class Nganh(Base):
    __tablename__ = "nganh"
    
    id_nganh = Column(String, primary_key=True, index=True)  
    ten_nganh = Column(String, nullable=False)
    id_khoa = Column(String, ForeignKey("khoa.id_khoa"), nullable=False)
    
    # Relationships
    khoa = relationship("Khoa", back_populates="nganhs")
    lop_hocs = relationship("LopHoc", back_populates="nganh")
    sinh_viens = relationship("SinhVien", back_populates="nganh")


class LopHoc(Base):
    __tablename__ = "lop_hoc"
    
    id_lop = Column(String, primary_key=True, index=True) 
    ten_lop = Column(String, nullable=False) 
    khoa_hoc = Column(String, nullable=True)  
    nam_nhap_hoc = Column(Integer, nullable=True)
    si_so_toi_da = Column(Integer, default=50)
    id_khoa = Column(String, ForeignKey("khoa.id_khoa"), nullable=False)
    id_nganh = Column(String, ForeignKey("nganh.id_nganh"), nullable=False)
    
    # Relationships
    khoa = relationship("Khoa", back_populates="lop_hocs")
    nganh = relationship("Nganh", back_populates="lop_hocs")
    sinh_viens = relationship("SinhVien", back_populates="lop_hoc")


class SinhVien(Base):
    __tablename__ = "sinh_vien"
    
    id_sinh_vien = Column(String, primary_key=True, index=True) 
    ho_ten = Column(String, nullable=False)
    ngay_sinh = Column(Date, nullable=True)
    gioi_tinh = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)
    so_dien_thoai = Column(String, nullable=True)
    dia_chi = Column(String, nullable=True)
    id_nganh = Column(String, ForeignKey("nganh.id_nganh"), nullable=False)
    id_lop = Column(String, ForeignKey("lop_hoc.id_lop"), nullable=False)
    
    # Relationships
    nganh = relationship("Nganh", back_populates="sinh_viens")
    lop_hoc = relationship("LopHoc", back_populates="sinh_viens")
    dang_ky_mons = relationship("DangKyMon", back_populates="sinh_vien")
    fact_diems = relationship("FactDiem", back_populates="sinh_vien")


class GiangVien(Base):
    __tablename__ = "giang_vien"
    
    id_giang_vien = Column(String, primary_key=True, index=True)  
    ho_ten = Column(String, nullable=False)
    email = Column(String, nullable=True, unique=True)
    so_dien_thoai = Column(String, nullable=True)
    hoc_ham = Column(String, nullable=True) 
    id_khoa = Column(String, ForeignKey("khoa.id_khoa"), nullable=False)
    
    # Relationships
    khoa = relationship("Khoa", back_populates="giang_viens")
    lop_mon_hocs = relationship("LopMonHoc", back_populates="giang_vien")


class MonHoc(Base):
    __tablename__ = "mon_hoc"
    
    id_mon_hoc = Column(String, primary_key=True, index=True) 
    ten_mon = Column(String, nullable=False)
    so_tin_chi = Column(Integer, nullable=False)
    loai_mon = Column(String, nullable=True)  
    mo_ta = Column(Text, nullable=True)
    he_so = Column(Float, default=1.0)
    id_mon_tien_quyet = Column(String, ForeignKey("mon_hoc.id_mon_hoc"), nullable=True)
    
    # Relationships
    mon_tien_quyet = relationship("MonHoc", remote_side=[id_mon_hoc])
    lop_mon_hocs = relationship("LopMonHoc", back_populates="mon_hoc")
    fact_diems = relationship("FactDiem", back_populates="mon_hoc")


class HocKy(Base):
    __tablename__ = "hoc_ky"
    
    id_hoc_ky = Column(String, primary_key=True, index=True) 
    ten_hoc_ky = Column(String, nullable=False) 
    nam_hoc = Column(String, nullable=False)  
    ky_hoc = Column(String, nullable=False)  
    
    # Relationships
    lop_mon_hocs = relationship("LopMonHoc", back_populates="hoc_ky")
    fact_diems = relationship("FactDiem", back_populates="hoc_ky")


class LopMonHoc(Base):
    __tablename__ = "lop_mon_hoc"  # Lớp học phần
    
    id_lop_mon = Column(String, primary_key=True, index=True) 
    id_mon_hoc = Column(String, ForeignKey("mon_hoc.id_mon_hoc"), nullable=False)
    id_giang_vien = Column(String, ForeignKey("giang_vien.id_giang_vien"), nullable=False)
    id_hoc_ky = Column(String, ForeignKey("hoc_ky.id_hoc_ky"), nullable=False)
    si_so_toi_da = Column(Integer, default=50)
    phong_hoc = Column(String, nullable=True)
    lich_hoc = Column(String, nullable=True) 
    
    # Relationships
    mon_hoc = relationship("MonHoc", back_populates="lop_mon_hocs")
    giang_vien = relationship("GiangVien", back_populates="lop_mon_hocs")
    hoc_ky = relationship("HocKy", back_populates="lop_mon_hocs")
    dang_ky_mons = relationship("DangKyMon", back_populates="lop_mon_hoc")


class DangKyMon(Base):
    __tablename__ = "dang_ky_mon"
    
    id_dang_ky = Column(String, primary_key=True, index=True)
    id_sinh_vien = Column(String, ForeignKey("sinh_vien.id_sinh_vien"), nullable=False)
    id_lop_mon = Column(String, ForeignKey("lop_mon_hoc.id_lop_mon"), nullable=False)
    ngay_dang_ky = Column(Date, nullable=False)
    trang_thai = Column(String, default='Đã duyệt')  # 'Chờ duyệt', 'Đã duyệt', 'Hủy'
    
    # Relationships
    sinh_vien = relationship("SinhVien", back_populates="dang_ky_mons")
    lop_mon_hoc = relationship("LopMonHoc", back_populates="dang_ky_mons")
    fact_diems = relationship("FactDiem", back_populates="dang_ky")


class FactDiem(Base):
    __tablename__ = "fact_diem"
    
    id_diem = Column(String, primary_key=True, index=True) 
    id_dang_ky = Column(String, ForeignKey("dang_ky_mon.id_dang_ky"), nullable=False)
    id_sinh_vien = Column(String, ForeignKey("sinh_vien.id_sinh_vien"), nullable=False)
    id_mon_hoc = Column(String, ForeignKey("mon_hoc.id_mon_hoc"), nullable=False)
    id_lop_mon = Column(String, ForeignKey("lop_mon_hoc.id_lop_mon"), nullable=False)
    id_giang_vien = Column(String, ForeignKey("giang_vien.id_giang_vien"), nullable=False)
    id_hoc_ky = Column(String, ForeignKey("hoc_ky.id_hoc_ky"), nullable=False)
    
    # Các cột điểm
    diem_chuyen_can = Column(Float, nullable=True)
    diem_giua_ky = Column(Float, nullable=True)
    diem_cuoi_ky = Column(Float, nullable=True)
    diem_trung_binh = Column(Float, nullable=True)
    diem_chu = Column(String, nullable=True)
    so_lan_hoc = Column(Integer, default=1)
    so_tin_chi_dat = Column(Integer, default=0)
    ket_qua = Column(Boolean, nullable=True) 
    
    # Relationships
    dang_ky = relationship("DangKyMon", back_populates="fact_diems")
    sinh_vien = relationship("SinhVien", back_populates="fact_diems")
    mon_hoc = relationship("MonHoc", back_populates="fact_diems")
    lop_mon_hoc = relationship("LopMonHoc")
    giang_vien = relationship("GiangVien")
    hoc_ky = relationship("HocKy", back_populates="fact_diems")

class TaiKhoan(Base):
    __tablename__ = "tai_khoan"
    
    id_tai_khoan = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  
