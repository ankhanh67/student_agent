# app/services/import_service.py
import pandas as pd
import io
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime

from app import schemas
from app.repositories import (
    khoa_repository,
    nganh_repository,
    sinh_vien_repository,
    mon_hoc_repository,
    hoc_ky_repository,
    fact_diem_repository
)

class ImportService:

    def __init__(self, db: Session):
        self.db = db
        self.khoa_repo = khoa_repository.KhoaRepository(db)
        self.nganh_repo = nganh_repository.NganhRepository(db)
        self.sinh_vien_repo = sinh_vien_repository.SinhVienRepository(db)
        self.mon_hoc_repo = mon_hoc_repository.MonHocRepository(db)
        self.hoc_ky_repo = hoc_ky_repository.HocKyRepository(db)
        self.diem_repo = fact_diem_repository.FactDiemRepository(db)
    
    def import_from_file(self, file_contents: bytes, filename: str) -> Dict:
        """
        HÀM CHÍNH: Import dữ liệu từ file tổng vào database
        """
        
        # Read file
        df = self._doc_file(file_contents, filename)
        
        # Checking data
        self._kiem_tra_du_lieu(df)
        
        # 🟢 Chuẩn hóa dữ liệu học kỳ trước khi xử lý
        df = self._chuan_hoa_hoc_ky(df)
        
        # Import theo đúng thứ tự
        ket_qua = {
            "khoa": self._import_khoa(df),
            "nganh": self._import_nganh(df),
            "mon_hoc": self._import_mon_hoc(df),
            "hoc_ky": self._import_hoc_ky(df),
        }
        
        ket_qua["sinh_vien"] = self._import_sinh_vien(df)
        ket_qua["fact_diem"] = self._import_fact_diem(df)
        
        self.db.commit()
        
        return {
            "message": "Import dữ liệu thành công!",
            "thong_ke": ket_qua,
            "tong_dong_file": len(df)
        }
    
    def _doc_file(self, file_contents: bytes, filename: str):
        """Đọc file Excel hoặc CSV"""
        if filename.endswith('.csv'):
            return pd.read_csv(io.BytesIO(file_contents))
        else:
            return pd.read_excel(io.BytesIO(file_contents))
    
    def _kiem_tra_du_lieu(self, df):
        """Kiểm tra các cột bắt buộc"""
        cot_bat_buoc = ['id_sinh_vien', 'hoTen', 'id_khoa', 'id_nganh', 'id_mon_hoc', 'id_hocky', 'diemHe10']
        for cot in cot_bat_buoc:
            if cot not in df.columns:
                raise ValueError(f"Thiếu cột bắt buộc: {cot}")
    
    # 🟢 HÀM MỚI: Chuẩn hóa mã học kỳ
    def _chuan_hoa_hoc_ky(self, df):
        """Chuẩn hóa mã học kỳ về dạng HK{ky}-{nam}"""
        
        def chuan_hoa_mot_dong(row):
            id_hocky = str(row['id_hocky']).strip()
            ten_hocky = row.get('tenHocky', '')
            nam_hoc = row.get('namHoc', '')
            
            # Nếu đã đúng định dạng HK{ky}-{nam} thì giữ nguyên
            if id_hocky.startswith('HK') and '-' in id_hocky:
                return id_hocky
            
            # Xử lý các trường hợp đặc biệt
            if id_hocky == 'K001' and nam_hoc == '2025-2026':
                return 'HK1-2025'
            
            # Xử lý mã dạng HKxyz (HK261, HK262, ...)
            if id_hocky.startswith('HK') and len(id_hocky) == 5:
                # HK261: năm 2026, học kỳ 1
                nam = id_hocky[2:4]  # '26'
                ky = id_hocky[4]     # '1'
                return f"HK{ky}-20{nam}"
            
            # Xử lý mã dạng HK231, HK232...
            if id_hocky.startswith('HK') and len(id_hocky) == 5:
                nam = id_hocky[2:4]
                ky = id_hocky[4]
                return f"HK{ky}-20{nam}"
            
            # Mặc định trả về nguyên bản
            return id_hocky
        
        # Áp dụng hàm chuẩn hóa
        df['id_hocky_chuan'] = df.apply(chuan_hoa_mot_dong, axis=1)
        df['id_hocky'] = df['id_hocky_chuan']
        df.drop(columns=['id_hocky_chuan'], inplace=True)
        
        return df
    
    def _import_khoa(self, df) -> Dict:
        """Import dữ liệu KHOA"""
        them_moi = 0
        bo_qua = 0
        
        khoa_list = df[['id_khoa', 'tenKhoa']].drop_duplicates()
        
        for _, row in khoa_list.iterrows():
            try:
                existing = self.khoa_repo.get_by_id(row['id_khoa'])
                if not existing:
                    khoa_data = schemas.KhoaCreate(
                        id_khoa=row['id_khoa'],
                        tenKhoa=row['tenKhoa']
                    )
                    self.khoa_repo.create(khoa_data)
                    them_moi += 1
                else:
                    bo_qua += 1
            except Exception as e:
                print(f"Lỗi import khoa {row['id_khoa']}: {e}")
                bo_qua += 1
        
        return {"them_moi": them_moi, "bo_qua": bo_qua}
    
    def _import_nganh(self, df) -> Dict:
        """Import dữ liệu NGÀNH"""
        them_moi = 0
        bo_qua = 0
        
        nganh_list = df[['id_nganh', 'tenNganh', 'id_khoa']].drop_duplicates()
        
        for _, row in nganh_list.iterrows():
            try:
                existing = self.nganh_repo.get_by_id(row['id_nganh'])
                if not existing:
                    nganh_data = schemas.NganhCreate(
                        id_nganh=row['id_nganh'],
                        tenNganh=row['tenNganh'],
                        id_khoa=row['id_khoa']
                    )
                    self.nganh_repo.create(nganh_data)
                    them_moi += 1
                else:
                    bo_qua += 1
            except Exception as e:
                print(f"Lỗi import ngành {row['id_nganh']}: {e}")
                bo_qua += 1
        
        return {"them_moi": them_moi, "bo_qua": bo_qua}
    
    def _import_mon_hoc(self, df) -> Dict:
        """Import dữ liệu MÔN HỌC"""
        them_moi = 0
        bo_qua = 0
        
        monhoc_list = df[['id_mon_hoc', 'tenMon', 'soTinChi']].drop_duplicates()
        
        for _, row in monhoc_list.iterrows():
            try:
                existing = self.mon_hoc_repo.get_by_id(row['id_mon_hoc'])
                if not existing:
                    monhoc_data = schemas.MonHocCreate(
                        id_mon_hoc=row['id_mon_hoc'],
                        tenMon=row['tenMon'],
                        soTinchi=int(row['soTinChi']) if pd.notna(row['soTinChi']) else 0
                    )
                    self.mon_hoc_repo.create(monhoc_data)
                    them_moi += 1
                else:
                    bo_qua += 1
            except Exception as e:
                print(f"Lỗi import môn học {row['id_mon_hoc']}: {e}")
                bo_qua += 1
        
        return {"them_moi": them_moi, "bo_qua": bo_qua}
    
    def _import_hoc_ky(self, df) -> Dict:
        """Import dữ liệu HỌC KỲ - ĐÃ CHUẨN HÓA"""
        them_moi = 0
        bo_qua = 0
        
        # Lấy danh sách học kỳ duy nhất từ file
        hocky_list = df[['id_hocky', 'tenHocky', 'namHoc']].drop_duplicates()
        
        for _, row in hocky_list.iterrows():
            try:
                # Tách thông tin từ mã học kỳ đã chuẩn hóa
                id_hocky = row['id_hocky']
                
                # Xác định kyHoc từ mã
                kyHoc = '1'
                if id_hocky.startswith('HK'):
                    kyHoc = id_hocky[2]  # Lấy ký tự sau 'HK'
                
                existing = self.hoc_ky_repo.get_by_id(id_hocky)
                if not existing:
                    hocky_data = schemas.HocKyCreate(
                        id_hocky=id_hocky,
                        tenHocky=row.get('tenHocky', f"Học kỳ {kyHoc}"),
                        namHoc=row.get('namHoc', f"20{id_hocky[3:5]}-20{int(id_hocky[3:5])+1}"),
                        kyHoc=kyHoc
                    )
                    self.hoc_ky_repo.create(hocky_data)
                    them_moi += 1
                else:
                    bo_qua += 1
            except Exception as e:
                print(f"Lỗi import học kỳ {row['id_hocky']}: {e}")
                bo_qua += 1
        
        return {"them_moi": them_moi, "bo_qua": bo_qua}
    
    def _import_sinh_vien(self, df) -> Dict:
        """Import dữ liệu SINH VIÊN"""
        them_moi = 0
        bo_qua = 0
        
        sv_list = df[['id_sinh_vien', 'hoTen', 'ngaySinh', 'gioiTinh', 'email', 'soDienthoai', 'diaChi', 'id_nganh']].drop_duplicates()
        
        for _, row in sv_list.iterrows():
            try:
                existing = self.sinh_vien_repo.get_by_id(row['id_sinh_vien'])
                if not existing:
                    ngay_sinh = None
                    if pd.notna(row.get('ngaySinh')):
                        ngay_sinh = pd.to_datetime(row['ngaySinh']).date()
                    
                    # Xử lý số điện thoại
                    so_dien_thoai_str = None
                    if pd.notna(row.get('soDienthoai')):
                        so_dien_thoai_str = str(row['soDienthoai'])
                    
                    sv_data = schemas.SinhVienCreate(
                        id_sinh_vien=row['id_sinh_vien'],
                        hoTen=row['hoTen'],
                        ngaySinh=ngay_sinh,
                        gioiTinh=row.get('gioiTinh'),
                        email=row.get('email'),
                        soDienthoai=so_dien_thoai_str,
                        diaChi=row.get('diaChi'),
                        id_nganh=row['id_nganh']
                    )
                    self.sinh_vien_repo.create(sv_data)
                    them_moi += 1
                else:
                    bo_qua += 1
            except Exception as e:
                print(f"Lỗi import sinh viên {row['id_sinh_vien']}: {e}")
                bo_qua += 1
        
        return {"them_moi": them_moi, "bo_qua": bo_qua}
    
    def _import_fact_diem(self, df) -> Dict:
        """Import dữ liệu FACT ĐIỂM"""
        them_moi = 0
        bo_qua = 0
        sv_moi_tao = 0
        
        for idx, row in df.iterrows():
            try:
                # Đảm bảo sinh viên tồn tại
                sinh_vien = self.sinh_vien_repo.get_by_id(row['id_sinh_vien'])
                
                if not sinh_vien:
                    print(f"Sinh viên {row['id_sinh_vien']} chưa tồn tại. Đang tạo mới...")
                    try:
                        ngay_sinh = None
                        if pd.notna(row.get('ngaySinh')):
                            ngay_sinh = pd.to_datetime(row['ngaySinh']).date()
                        
                        # Xử lý số điện thoại
                        so_dien_thoai_str = None
                        if pd.notna(row.get('soDienthoai')):
                            so_dien_thoai_str = str(row['soDienthoai'])
                        
                        sv_data = schemas.SinhVienCreate(
                            id_sinh_vien=row['id_sinh_vien'],
                            hoTen=row.get('hoTen', f"Sinh viên {row['id_sinh_vien']}"),
                            ngaySinh=ngay_sinh,
                            gioiTinh=row.get('gioiTinh'),
                            email=row.get('email'),
                            soDienthoai=so_dien_thoai_str,
                            diaChi=row.get('diaChi'),
                            id_nganh=row['id_nganh']
                        )
                        self.sinh_vien_repo.create(sv_data)
                        self.db.flush()
                        sv_moi_tao += 1
                    except Exception as e_sv:
                        print(f"  ⚠️ Không thể tạo sinh viên: {e_sv}")
                        bo_qua += 1
                        continue
                
                # Xử lý điểm
                diem_id = f"{row['id_sinh_vien']}_{row['id_mon_hoc']}_{row['id_hocky']}"
                diem_he10 = float(row['diemHe10']) if pd.notna(row['diemHe10']) else None
                
                # Xử lý kết quả
                ket_qua_value = row.get('ketQua')
                if isinstance(ket_qua_value, str):
                    ket_qua_bool = ket_qua_value.lower() == 'pass'
                else:
                    ket_qua_bool = diem_he10 >= 5 if diem_he10 is not None else False
                
                mon_hoc = self.mon_hoc_repo.get_by_id(row['id_mon_hoc'])
                so_tin_chi = mon_hoc.soTinchi if mon_hoc else 0
                
                existing = self.diem_repo.get_by_id(diem_id)
                if not existing:
                    diem_data = schemas.FactDiemCreate(
                        id=diem_id,
                        id_sinh_vien=row['id_sinh_vien'],
                        id_mon_hoc=row['id_mon_hoc'],
                        id_khoa=row['id_khoa'],
                        id_nganh=row['id_nganh'],
                        id_hocky=row['id_hocky'],
                        gioiTinh = row['gioiTinh'],
                        diemHe10=diem_he10,
                        diemChu=row.get('diemChu') or self._diem_so_sang_chu(diem_he10),
                        soLanHoc=int(row.get('soLanHoc', 1)),
                        soTinChiDat=row.get('soTinChiDat', so_tin_chi if ket_qua_bool else 0),
                        tenMon = row['tenMon'],
                        loaiMon = row['loaiMon'],
                        ketQua=ket_qua_bool
                    )
                    self.diem_repo.create(diem_data)
                    them_moi += 1
                else:
                    bo_qua += 1
                
                if (idx + 1) % 100 == 0:
                    self.db.flush()
                    
            except Exception as e:
                print(f"❌ Lỗi dòng {idx}: {e}")
                bo_qua += 1
        
        if sv_moi_tao > 0:
            print(f"📝 Đã tự động tạo {sv_moi_tao} sinh viên mới")
        
        return {"them_moi": them_moi, "bo_qua": bo_qua}
    
    def _diem_so_sang_chu(self, diem):
        """Chuyển điểm số sang điểm chữ"""
        if pd.isna(diem) or diem is None:
            return None
        if diem >= 9.0:
            return "A"
        elif diem >= 8.0:
            return "B+"
        elif diem >= 7.0:
            return "B"
        elif diem >= 6.0:
            return "C+"
        elif diem >= 5.0:
            return "C"
        elif diem >= 4.0:
            return "D+"
        else:
            return "F"