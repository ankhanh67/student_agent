# app/services/import_service.py
import pandas as pd
import io
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from app import schemas
from app.repositories import (
    khoa_repository,
    nganh_repository,
    lop_hoc_repository,
    sinh_vien_repository,
    giang_vien_repository,
    mon_hoc_repository,
    hoc_ky_repository,
    lop_mon_hoc_repository,
    dang_ky_mon_repository,
    fact_diem_repository
)
from app.services.id_generator import (
    generate_khoa_code, generate_nganh_code, generate_lop_code,
    generate_sinh_vien_code, generate_giang_vien_code, generate_mon_hoc_code,
    generate_dang_ky_code, generate_lop_mon_code
)

class ImportService:
    """
    Dịch vụ import dữ liệu từ file CSV/Excel vào database.
    
    QUY TRÌNH IMPORT CHUẨN:
    1. Đọc và chuẩn hóa dữ liệu
    2. Import các bảng độc lập: khoa, nganh, lop_hoc
    3. Import giảng viên (tạo mapping tên -> id)
    4. Import môn học
    5. Import học kỳ
    6. Import lớp môn học (phụ thuộc môn học, giảng viên, học kỳ)
    7. Import sinh viên
    8. Import đăng ký môn (phụ thuộc sinh viên và lớp môn học)
    9. Import điểm (phụ thuộc tất cả)
    """

    def __init__(self, db: Session):
        self.db = db
        
        # Khởi tạo repositories
        self.khoa_repo = khoa_repository.KhoaRepository(db)
        self.nganh_repo = nganh_repository.NganhRepository(db)
        self.lop_hoc_repo = lop_hoc_repository.LopHocRepository(db)
        self.sinh_vien_repo = sinh_vien_repository.SinhVienRepository(db)
        self.giang_vien_repo = giang_vien_repository.GiangVienRepository(db)
        self.mon_hoc_repo = mon_hoc_repository.MonHocRepository(db)
        self.hoc_ky_repo = hoc_ky_repository.HocKyRepository(db)
        self.lop_mon_hoc_repo = lop_mon_hoc_repository.LopMonHocRepository(db)
        self.dang_ky_mon_repo = dang_ky_mon_repository.DangKyMonRepository(db)
        self.diem_repo = fact_diem_repository.FactDiemRepository(db)
        
        # Cache để lưu mapping giữa các bảng
        self.gv_dict = {}  # Mapping tên giảng viên -> ID
        self.mon_dict = {}  # Mapping mã môn học -> object
        self.hk_dict = {}   # Mapping mã học kỳ -> object
        self.sv_dict = {}   # Mapping mã sinh viên -> object
    
    # -------------------------------------------------------------------------
    # HÀM CHÍNH: IMPORT TỪ FILE
    # -------------------------------------------------------------------------
    def import_from_file(self, file_contents: bytes, filename: str) -> Dict:
        """
        HÀM CHÍNH: Import dữ liệu từ file tổng vào database
        """
        print("\n" + "="*80)
        print("🚀 BẮT ĐẦU QUÁ TRÌNH IMPORT DỮ LIỆU")
        print("="*80)
        
        # Bước 1: Đọc file
        df = self._doc_file(file_contents, filename)
        print(f"📄 Đã đọc file: {len(df)} dòng dữ liệu")
        print(f"📋 Các cột: {list(df.columns)}")
        
        # Bước 2: Chuẩn hóa tên cột
        df = self._chuan_hoa_ten_cot(df)
        print("✅ Đã chuẩn hóa tên cột")
        
        # Bước 3: Chuẩn hóa dữ liệu học kỳ
        df = self._chuan_hoa_hoc_ky(df)
        print("✅ Đã chuẩn hóa học kỳ")
        
        # Bước 4: Import theo đúng thứ tự
        print("\n" + "-"*80)
        print("📦 BẮT ĐẦU IMPORT CÁC BẢNG DỮ LIỆU")
        print("-"*80)
        
        # Dictionary lưu kết quả từng bảng
        ket_qua = {}
        
        # 4.1. Import các bảng độc lập
        ket_qua["khoa"] = self._import_khoa(df)
        ket_qua["nganh"] = self._import_nganh(df)
        ket_qua["lop_hoc"] = self._import_lop_hoc(df)
        
        # 4.2. Import giảng viên (tạo mapping)
        ket_qua["giang_vien"] = self._import_giang_vien(df)
        
        # 4.3. Import môn học (tạo mapping)
        ket_qua["mon_hoc"] = self._import_mon_hoc(df)
        
        # 4.4. Import học kỳ (tạo mapping)
        ket_qua["hoc_ky"] = self._import_hoc_ky(df)
        
        # 4.5. Import lớp môn học (phụ thuộc môn, giảng viên, học kỳ)
        ket_qua["lop_mon_hoc"] = self._import_lop_mon_hoc(df)
        
        # 4.6. Import sinh viên (phụ thuộc lớp, ngành)
        ket_qua["sinh_vien"] = self._import_sinh_vien(df)
        
        # 4.7. Import đăng ký môn (phụ thuộc sinh viên và lớp môn học)
        ket_qua["dang_ky_mon"] = self._import_dang_ky_mon(df)
        
        # 4.8. Import điểm (phụ thuộc tất cả)
        ket_qua["fact_diem"] = self._import_fact_diem(df)
        
        # Bước 5: Commit và hoàn tất
        self.db.commit()
        
        print("\n" + "="*80)
        print("✅ IMPORT HOÀN TẤT!")
        print("="*80)
        
        return {
            "message": "Import dữ liệu thành công!",
            "thong_ke": ket_qua,
            "tong_dong_file": len(df)
        }
    
    # -------------------------------------------------------------------------
    # HÀM ĐỌC FILE
    # -------------------------------------------------------------------------
    def _doc_file(self, file_contents: bytes, filename: str):
        """Đọc file Excel hoặc CSV"""
        try:
            if filename.endswith('.csv'):
                return pd.read_csv(io.BytesIO(file_contents), sep=';', encoding='utf-8')
            else:
                return pd.read_excel(io.BytesIO(file_contents))
        except Exception as e:
            raise ValueError(f"Không thể đọc file: {e}")
    
    # -------------------------------------------------------------------------
    # HÀM CHUẨN HÓA
    # -------------------------------------------------------------------------
    def _chuan_hoa_ten_cot(self, df):
        """
        Chuẩn hóa tên cột: chuyển tên cột trong file thành tên cột code sử dụng
        """
        # Mapping từ tên cột trong file sang tên cột code cần
        column_mapping = {
            'id_sinh_vien': 'id_sinh_vien',
            'ho_ten': 'hoTen',
            'ngay_sinh': 'ngaySinh',
            'gioi_tinh': 'gioiTinh',
            'email': 'email',
            'so_dien_thoai': 'soDienthoai',
            'dia_chi': 'diaChi',
            'id_lop': 'id_lop',
            'ten_lop': 'ten_lop',
            'khoa_hoc': 'khoa_hoc',
            'nam_nhap_hoc': 'nam_nhap_hoc',
            'id_nganh': 'id_nganh',
            'ten_nganh': 'tenNganh',
            'id_khoa': 'id_khoa',
            'ten_khoa': 'tenKhoa',
            'id_hoc_ky': 'id_hocky',
            'ten_hoc_ky': 'tenHocky',
            'nam_hoc': 'namHoc',
            'ky_hoc': 'kyHoc',
            'id_mon_hoc': 'id_mon_hoc',
            'ten_mon': 'tenMon',
            'so_tin_chi': 'soTinChi',
            'loai_mon': 'loaiMon',
            'he_so': 'he_so',
            'id_lop_mon': 'id_lop_mon',
            'phong_hoc': 'phong_hoc',
            'lich_hoc': 'lich_hoc',
            'ten_giang_vien': 'ten_giang_vien',
            'hoc_ham_giang_vien': 'hoc_ham_giang_vien',
            'id_dang_ky': 'id_dang_ky',
            'ngay_dang_ky': 'ngay_dang_ky',
            'trang_thai_dang_ky': 'trang_thai_dang_ky',
            'id_diem': 'id_diem',
            'diem_chuyen_can': 'diem_chuyen_can',
            'diem_giua_ky': 'diem_giua_ky',
            'diem_cuoi_ky': 'diem_cuoi_ky',
            'diem_trung_binh': 'diemHe10',
            'diem_chu': 'diem_chu',
            'so_lan_hoc': 'so_lan_hoc',
            'so_tin_chi_dat': 'so_tin_chi_dat',
            'ket_qua': 'ketQua'
        }
        
        # Tạo mapping chỉ cho những cột tồn tại
        rename_map = {}
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                rename_map[old_col] = new_col
        
        # Đổi tên cột
        if rename_map:
            df.rename(columns=rename_map, inplace=True)
            print(f"  ✅ Đã đổi tên {len(rename_map)} cột")
        
        # Kiểm tra các cột bắt buộc
        required_cols = ['id_sinh_vien', 'hoTen', 'id_khoa', 'id_nganh', 'id_mon_hoc', 'id_hocky', 'diemHe10']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Thiếu cột bắt buộc: {missing_cols}")
        
        return df
    
    def _chuan_hoa_hoc_ky(self, df):
        """Chuẩn hóa mã học kỳ về dạng HK{ky}-{nam} và tính đúng năm học"""
        if 'id_hocky' not in df.columns:
            return df
            
        def chuan_hoa(row):
            id_hocky = str(row.get('id_hocky', '')).strip()
            
            # Nếu đã đúng định dạng HKx-xxxx thì giữ nguyên
            if id_hocky and id_hocky.startswith('HK') and '-' in id_hocky:
                # 🔥 QUAN TRỌNG: Tính lại năm học cho đúng
                # Ví dụ: HK1-2024 -> năm học 2023-2024
                #         HK2-2024 -> năm học 2023-2024
                #         HK1-2025 -> năm học 2024-2025
                parts = id_hocky.split('-')
                ky = parts[0][2:]  # Lấy số sau HK (1, 2, 3)
                nam = parts[1]      # 2024, 2025, 2026
                
                # Năm học bắt đầu từ năm trước
                nam_bat_dau = int(nam) - 1
                nam_ket_thuc = int(nam)
                nam_hoc_dung = f"{nam_bat_dau}-{nam_ket_thuc}"
                
                # Cập nhật lại cột namHoc
                row['namHoc'] = nam_hoc_dung
                return id_hocky
            
            # Nếu là định dạng cũ (HK231, HK232...)
            if id_hocky and id_hocky.startswith('HK') and len(id_hocky) == 5:
                ky = id_hocky[2]
                nam = id_hocky[3:5]
                nam_day_du = f"20{nam}"
                nam_bat_dau = int(nam_day_du) - 1
                nam_ket_thuc = int(nam_day_du)
                
                row['namHoc'] = f"{nam_bat_dau}-{nam_ket_thuc}"
                return f"HK{ky}-20{nam}"
            
            # Tạo mới từ các cột khác
            nam = row.get('namHoc', '2024-2025')
            ky = row.get('kyHoc', '1')
            return f"HK{ky}-{nam[:4]}"
        
        # Áp dụng chuẩn hóa
        for idx, row in df.iterrows():
            df.at[idx, 'id_hocky'] = chuan_hoa(row)
        
        return df
    
    # -------------------------------------------------------------------------
    # HÀM TIỆN ÍCH
    # -------------------------------------------------------------------------
    def _lay_danh_sach_duy_nhat(self, df, columns: List[str], subset: Optional[List[str]] = None) -> pd.DataFrame:
        """Lấy danh sách các dòng duy nhất từ dataframe"""
        available_cols = [col for col in columns if col in df.columns]
        if not available_cols:
            return pd.DataFrame()
        
        if subset:
            return df[available_cols].drop_duplicates(subset=subset)
        return df[available_cols].drop_duplicates()
    
    # -------------------------------------------------------------------------
    # HÀM IMPORT CHO TỪNG BẢNG
    # -------------------------------------------------------------------------
    def _import_khoa(self, df) -> Dict:
        """Import dữ liệu KHOA"""
        them_moi, bo_qua = 0, 0
        
        if 'id_khoa' not in df.columns or 'tenKhoa' not in df.columns:
            print("⚠️ Bỏ qua import KHOA do thiếu cột")
            return {"them_moi": 0, "bo_qua": 0}
        
        khoa_list = self._lay_danh_sach_duy_nhat(df, ['id_khoa', 'tenKhoa'])
        print(f"\n📚 Import KHOA: {len(khoa_list)} khoa")
        
        for _, row in khoa_list.iterrows():
            try:
                if pd.isna(row['id_khoa']) or pd.isna(row['tenKhoa']):
                    continue
                    
                existing = self.khoa_repo.get_by_id(row['id_khoa'])
                if not existing:
                    data = schemas.KhoaCreate(
                        id_khoa=row['id_khoa'],
                        ten_khoa=row['tenKhoa']
                    )
                    self.khoa_repo.create(data)
                    them_moi += 1
                else:
                    bo_qua += 1
            except Exception as e:
                print(f"  ❌ Lỗi import khoa {row.get('id_khoa')}: {e}")
                bo_qua += 1
        
        print(f"  ✅ Thêm mới: {them_moi}, ⏩ Bỏ qua: {bo_qua}")
        return {"them_moi": them_moi, "bo_qua": bo_qua}
    
    def _import_nganh(self, df) -> Dict:
        """Import dữ liệu NGÀNH"""
        them_moi, bo_qua = 0, 0
        
        required = ['id_nganh', 'tenNganh', 'id_khoa']
        if not all(col in df.columns for col in required):
            print("⚠️ Bỏ qua import NGÀNH do thiếu cột")
            return {"them_moi": 0, "bo_qua": 0}
        
        nganh_list = self._lay_danh_sach_duy_nhat(df, required)
        print(f"\n📚 Import NGÀNH: {len(nganh_list)} ngành")
        
        for _, row in nganh_list.iterrows():
            try:
                if pd.isna(row['id_nganh']) or pd.isna(row['tenNganh']) or pd.isna(row['id_khoa']):
                    continue
                    
                existing = self.nganh_repo.get_by_id(row['id_nganh'])
                if not existing:
                    data = schemas.NganhCreate(
                        id_nganh=row['id_nganh'],
                        ten_nganh=row['tenNganh'],
                        id_khoa=row['id_khoa']
                    )
                    self.nganh_repo.create(data)
                    them_moi += 1
                else:
                    bo_qua += 1
            except Exception as e:
                print(f"  ❌ Lỗi import ngành {row.get('id_nganh')}: {e}")
                bo_qua += 1
        
        print(f"  ✅ Thêm mới: {them_moi}, ⏩ Bỏ qua: {bo_qua}")
        return {"them_moi": them_moi, "bo_qua": bo_qua}
    
    def _import_lop_hoc(self, df) -> Dict:
        """Import dữ liệu LỚP HỌC"""
        them_moi, bo_qua, cap_nhat = 0, 0, 0
        
        # Các cột bắt buộc
        required = ['id_lop', 'ten_lop', 'id_khoa', 'id_nganh']
        if not all(col in df.columns for col in required):
            print("⚠️ Bỏ qua import LỚP HỌC do thiếu cột bắt buộc")
            return {"them_moi": 0, "bo_qua": 0}
        
        # Xác định các cột sẽ lấy
        cols_to_get = required.copy()
        if 'khoa_hoc' in df.columns:
            cols_to_get.append('khoa_hoc')
        if 'nam_nhap_hoc' in df.columns:
            cols_to_get.append('nam_nhap_hoc')
        
        # Lấy danh sách lớp duy nhất
        lop_list = self._lay_danh_sach_duy_nhat(df, cols_to_get, subset=['id_lop'])
        print(f"\n📚 Import LỚP HỌC: {len(lop_list)} lớp")
        
        # Tạo dictionary mapping từ file
        file_data = {}
        for _, row in lop_list.iterrows():
            try:
                if any(pd.isna(row[col]) for col in required):
                    continue
                
                # Xử lý khoa_hoc
                khoa_hoc = None
                if 'khoa_hoc' in row and pd.notna(row['khoa_hoc']):
                    khoa_hoc = str(row['khoa_hoc']).strip()
                    if khoa_hoc == '' or khoa_hoc.lower() == 'null':
                        khoa_hoc = None
                
                # Xử lý nam_nhap_hoc
                nam_nhap_hoc = None
                if 'nam_nhap_hoc' in row and pd.notna(row['nam_nhap_hoc']):
                    try:
                        val = row['nam_nhap_hoc']
                        if isinstance(val, str):
                            val = val.replace(',', '').strip()
                        nam_nhap_hoc = int(float(val))
                    except:
                        nam_nhap_hoc = None
                
                file_data[row['id_lop']] = {
                    'ten_lop': row['ten_lop'],
                    'khoa_hoc': khoa_hoc,
                    'nam_nhap_hoc': nam_nhap_hoc,
                    'id_khoa': row['id_khoa'],
                    'id_nganh': row['id_nganh']
                }
            except Exception as e:
                print(f"  ⚠️ Lỗi xử lý dòng: {e}")
        
        # Lấy tất cả các lớp hiện có trong database
        db_lops = self.lop_hoc_repo.get_all()
        db_dict = {lop.id_lop: lop for lop in db_lops}
        
        # Cập nhật từng lớp
        for id_lop, file_row in file_data.items():
            try:
                if id_lop in db_dict:
                    # Lớp đã tồn tại -> UPDATE
                    existing = db_dict[id_lop]
                    update_data = {}
                    
                    # Kiểm tra và cập nhật từng trường
                    if file_row['khoa_hoc'] is not None and existing.khoa_hoc != file_row['khoa_hoc']:
                        update_data['khoa_hoc'] = file_row['khoa_hoc']
                    
                    if file_row['nam_nhap_hoc'] is not None and existing.nam_nhap_hoc != file_row['nam_nhap_hoc']:
                        update_data['nam_nhap_hoc'] = file_row['nam_nhap_hoc']
                    
                    if existing.ten_lop != file_row['ten_lop']:
                        update_data['ten_lop'] = file_row['ten_lop']
                    
                    if existing.id_khoa != file_row['id_khoa']:
                        update_data['id_khoa'] = file_row['id_khoa']
                    
                    if existing.id_nganh != file_row['id_nganh']:
                        update_data['id_nganh'] = file_row['id_nganh']
                    
                    if update_data:
                        from app.schemas import LopHocUpdate
                        update_schema = LopHocUpdate(**update_data)
                        self.lop_hoc_repo.update(id_lop, update_schema)
                        cap_nhat += 1
                        print(f"  🔄 Đã cập nhật lớp {id_lop}: {file_row['khoa_hoc']} - {file_row['nam_nhap_hoc']}")
                    else:
                        bo_qua += 1
                else:
                    # Lớp chưa tồn tại -> INSERT
                    data = schemas.LopHocCreate(
                        id_lop=id_lop,
                        ten_lop=file_row['ten_lop'],
                        khoa_hoc=file_row['khoa_hoc'],
                        nam_nhap_hoc=file_row['nam_nhap_hoc'],
                        id_khoa=file_row['id_khoa'],
                        id_nganh=file_row['id_nganh']
                    )
                    self.lop_hoc_repo.create(data)
                    them_moi += 1
                    print(f"  ✅ Đã thêm lớp {id_lop}")
                    
            except Exception as e:
                print(f"  ❌ Lỗi xử lý lớp {id_lop}: {e}")
                bo_qua += 1
        
        print(f"  ✅ Kết quả: Thêm mới: {them_moi}, Cập nhật: {cap_nhat}, Bỏ qua: {bo_qua}")
        return {"them_moi": them_moi, "bo_qua": bo_qua, "cap_nhat": cap_nhat}
    
    def _import_giang_vien(self, df) -> Dict:
        """Import dữ liệu GIẢNG VIÊN và tạo mapping tên -> id"""
        them_moi, bo_qua = 0, 0
        
        if 'ten_giang_vien' not in df.columns:
            print("⚠️ Bỏ qua import GIẢNG VIÊN do thiếu cột")
            return {"them_moi": 0, "bo_qua": 0}
        
        # Lấy danh sách giảng viên duy nhất
        gv_raw = df[['ten_giang_vien']].drop_duplicates()
        gv_raw = gv_raw[gv_raw['ten_giang_vien'].notna()]
        print(f"\n📚 Import GIẢNG VIÊN: {len(gv_raw)} giảng viên")
        
        # Xóa cache cũ
        self.gv_dict = {}
        
        for _, row in gv_raw.iterrows():
            try:
                ten_gv = row['ten_giang_vien']
                
                # Tìm khoa cho giảng viên này
                khoa_rows = df[df['ten_giang_vien'] == ten_gv]['id_khoa'].dropna()
                if khoa_rows.empty:
                    print(f"  ⚠️ Giảng viên '{ten_gv}' không có khoa, bỏ qua")
                    bo_qua += 1
                    continue
                
                id_khoa = khoa_rows.iloc[0]
                
                # Tạo mã giảng viên mới
                id_gv = generate_giang_vien_code(self.db)
                
                data = schemas.GiangVienCreate(
                    id_giang_vien=id_gv,
                    ho_ten=ten_gv,
                    id_khoa=id_khoa
                )
                self.giang_vien_repo.create(data)
                them_moi += 1
                
                # Lưu mapping
                self.gv_dict[ten_gv] = id_gv
                print(f"  ✅ Đã tạo giảng viên: {id_gv} - {ten_gv}")
                
            except Exception as e:
                print(f"  ❌ Lỗi import giảng viên: {e}")
                bo_qua += 1
        
        # Thêm cột id_giang_vien vào dataframe dựa trên mapping
        if self.gv_dict:
            df['id_giang_vien'] = df['ten_giang_vien'].map(self.gv_dict)
        
        print(f"  ✅ Thêm mới: {them_moi}, ⏩ Bỏ qua: {bo_qua}")
        return {"them_moi": them_moi, "bo_qua": bo_qua}
    
    def _import_mon_hoc(self, df) -> Dict:
        """Import dữ liệu MÔN HỌC và tạo mapping"""
        them_moi, bo_qua = 0, 0
        
        if not all(col in df.columns for col in ['id_mon_hoc', 'tenMon']):
            print("⚠️ Bỏ qua import MÔN HỌC do thiếu cột")
            return {"them_moi": 0, "bo_qua": 0}
        
        mon_list = self._lay_danh_sach_duy_nhat(df, ['id_mon_hoc', 'tenMon'])
        print(f"\n📚 Import MÔN HỌC: {len(mon_list)} môn")
        
        # Xóa cache cũ
        self.mon_dict = {}
        
        for _, row in mon_list.iterrows():
            try:
                if pd.isna(row['id_mon_hoc']) or pd.isna(row['tenMon']):
                    continue
                    
                existing = self.mon_hoc_repo.get_by_id(row['id_mon_hoc'])
                if not existing:
                    # Lấy số tín chỉ nếu có
                    so_tin_chi = 3
                    if 'soTinChi' in df.columns:
                        tc_rows = df[df['id_mon_hoc'] == row['id_mon_hoc']]['soTinChi'].dropna()
                        if not tc_rows.empty:
                            so_tin_chi = int(tc_rows.iloc[0])
                    
                    data = schemas.MonHocCreate(
                        id_mon_hoc=row['id_mon_hoc'],
                        ten_mon=row['tenMon'],
                        so_tin_chi=so_tin_chi
                    )
                    self.mon_hoc_repo.create(data)
                    them_moi += 1
                    
                    # Lưu vào cache
                    self.mon_dict[row['id_mon_hoc']] = data
                else:
                    self.mon_dict[row['id_mon_hoc']] = existing
                    bo_qua += 1
            except Exception as e:
                print(f"  ❌ Lỗi import môn học {row.get('id_mon_hoc')}: {e}")
                bo_qua += 1
        
        print(f"  ✅ Thêm mới: {them_moi}, ⏩ Bỏ qua: {bo_qua}")
        return {"them_moi": them_moi, "bo_qua": bo_qua}
    
    def _import_hoc_ky(self, df) -> Dict:
        """Import dữ liệu HỌC KỲ"""
        them_moi, bo_qua, cap_nhat = 0, 0, 0
        
        required = ['id_hocky', 'tenHocky', 'namHoc']
        if not all(col in df.columns for col in required):
            print("⚠️ Bỏ qua import HỌC KỲ do thiếu cột")
            return {"them_moi": 0, "bo_qua": 0}
        
        hk_list = self._lay_danh_sach_duy_nhat(df, required)
        print(f"\n📚 Import HỌC KỲ: {len(hk_list)} học kỳ")
        
        for _, row in hk_list.iterrows():
            try:
                if any(pd.isna(row[col]) for col in required):
                    continue
                
                existing = self.hoc_ky_repo.get_by_id(row['id_hocky'])
                
                if not existing:
                    # INSERT
                    kyHoc = row['id_hocky'][2] if row['id_hocky'].startswith('HK') else '1'
                    data = schemas.HocKyCreate(
                        id_hoc_ky=row['id_hocky'],
                        ten_hoc_ky=row['tenHocky'],
                        nam_hoc=row['namHoc'],
                        ky_hoc=kyHoc
                    )
                    self.hoc_ky_repo.create(data)
                    them_moi += 1
                else:
                    # UPDATE nếu có thay đổi
                    update_data = {}
                    if existing.ten_hoc_ky != row['tenHocky']:
                        update_data['ten_hoc_ky'] = row['tenHocky']
                    if existing.nam_hoc != row['namHoc']:
                        update_data['nam_hoc'] = row['namHoc']
                        print(f"  🔄 Cập nhật năm học {row['id_hocky']}: {existing.nam_hoc} -> {row['namHoc']}")
                    
                    if update_data:
                        from app.schemas import HocKyUpdate
                        update_schema = HocKyUpdate(**update_data)
                        self.hoc_ky_repo.update(row['id_hocky'], update_schema)
                        cap_nhat += 1
                    else:
                        bo_qua += 1
                        
            except Exception as e:
                print(f"  ❌ Lỗi import học kỳ {row.get('id_hocky')}: {e}")
                bo_qua += 1
        
        print(f"  ✅ Thêm mới: {them_moi}, Cập nhật: {cap_nhat}, Bỏ qua: {bo_qua}")
        return {"them_moi": them_moi, "bo_qua": bo_qua, "cap_nhat": cap_nhat}
    
    def _import_lop_mon_hoc(self, df) -> Dict:
        """Import dữ liệu LỚP HỌC PHẪN"""
        them_moi, bo_qua, cap_nhat = 0, 0, 0
        
        required = ['id_mon_hoc', 'id_hocky']
        if not all(col in df.columns for col in required):
            print("⚠️ Bỏ qua import LỚP HỌC PHẪN do thiếu cột")
            return {"them_moi": 0, "bo_qua": 0}
        
        # Tạo ID lớp môn học nếu chưa có
        if 'id_lop_mon' not in df.columns:
            df['id_lop_mon'] = [generate_lop_mon_code(self.db) for _ in range(len(df))]
        
        # Xác định các cột sẽ lấy
        cols_to_keep = ['id_lop_mon', 'id_mon_hoc', 'id_hocky']
        if 'id_giang_vien' in df.columns:
            cols_to_keep.append('id_giang_vien')
        if 'phong_hoc' in df.columns:
            cols_to_keep.append('phong_hoc')
        if 'lich_hoc' in df.columns:
            cols_to_keep.append('lich_hoc')
        
        lop_mon_list = df[cols_to_keep].drop_duplicates(subset=['id_lop_mon'])
        print(f"\n📚 Import LỚP HỌC PHẪN: {len(lop_mon_list)} lớp")
        
        for _, row in lop_mon_list.iterrows():
            try:
                # Kiểm tra môn học tồn tại
                if row['id_mon_hoc'] not in self.mon_dict:
                    mon = self.mon_hoc_repo.get_by_id(row['id_mon_hoc'])
                    if not mon:
                        print(f"  ⚠️ Môn học {row['id_mon_hoc']} không tồn tại, bỏ qua")
                        bo_qua += 1
                        continue
                    self.mon_dict[row['id_mon_hoc']] = mon
                
                # Kiểm tra học kỳ tồn tại
                if row['id_hocky'] not in self.hk_dict:
                    hk = self.hoc_ky_repo.get_by_id(row['id_hocky'])
                    if not hk:
                        print(f"  ⚠️ Học kỳ {row['id_hocky']} không tồn tại, bỏ qua")
                        bo_qua += 1
                        continue
                    self.hk_dict[row['id_hocky']] = hk
                
                existing = self.lop_mon_hoc_repo.get_by_id(row['id_lop_mon'])
                
                if not existing:
                    # INSERT nếu chưa tồn tại
                    data = schemas.LopMonHocCreate(
                        id_lop_mon=row['id_lop_mon'],
                        id_mon_hoc=row['id_mon_hoc'],
                        id_giang_vien=row.get('id_giang_vien'),
                        id_hoc_ky=row['id_hocky'],
                        phong_hoc=row.get('phong_hoc'),
                        lich_hoc=row.get('lich_hoc')
                    )
                    self.lop_mon_hoc_repo.create(data)
                    them_moi += 1
                else:
                    # 🔥 QUAN TRỌNG: UPDATE nếu đã tồn tại
                    update_data = {}
                    if 'phong_hoc' in row and pd.notna(row['phong_hoc']):
                        update_data['phong_hoc'] = row['phong_hoc']
                    if 'lich_hoc' in row and pd.notna(row['lich_hoc']):
                        update_data['lich_hoc'] = row['lich_hoc']
                    if 'id_giang_vien' in row and pd.notna(row['id_giang_vien']):
                        update_data['id_giang_vien'] = row['id_giang_vien']
                    
                    if update_data:
                        # Tạo đối tượng update
                        from app.schemas import LopMonHocUpdate
                        update_schema = LopMonHocUpdate(**update_data)
                        self.lop_mon_hoc_repo.update(row['id_lop_mon'], update_schema)
                        cap_nhat += 1
                        print(f"  🔄 Đã cập nhật lớp {row['id_lop_mon']}: {row.get('phong_hoc')} - {row.get('lich_hoc')}")
                    else:
                        bo_qua += 1
                    
            except Exception as e:
                print(f"  ❌ Lỗi import lớp học phần {row.get('id_lop_mon')}: {e}")
                bo_qua += 1
        
        print(f"  ✅ Thêm mới: {them_moi}, 🔄 Cập nhật: {cap_nhat}, ⏩ Bỏ qua: {bo_qua}")
        return {"them_moi": them_moi, "bo_qua": bo_qua, "cap_nhat": cap_nhat}
        
    def _import_sinh_vien(self, df) -> Dict:
        """Import dữ liệu SINH VIÊN và tạo mapping"""
        them_moi, bo_qua = 0, 0
        
        if 'id_sinh_vien' not in df.columns or 'hoTen' not in df.columns:
            print("⚠️ Bỏ qua import SINH VIÊN do thiếu cột")
            return {"them_moi": 0, "bo_qua": 0}
        
        # Lấy danh sách sinh viên duy nhất
        sv_cols = ['id_sinh_vien', 'hoTen', 'ngaySinh', 'gioiTinh', 'email', 
                   'soDienthoai', 'diaChi', 'id_nganh', 'id_lop']
        available_cols = [col for col in sv_cols if col in df.columns]
        
        sv_list = df[available_cols].drop_duplicates(subset=['id_sinh_vien'])
        print(f"\n📚 Import SINH VIÊN: {len(sv_list)} sinh viên")
        
        # Xóa cache cũ
        self.sv_dict = {}
        
        for _, row in sv_list.iterrows():
            try:
                if pd.isna(row['id_sinh_vien']) or pd.isna(row['hoTen']):
                    continue
                    
                existing = self.sinh_vien_repo.get_by_id(row['id_sinh_vien'])
                if not existing:
                    # Xử lý ngày sinh
                    ngay_sinh = None
                    if 'ngaySinh' in row and pd.notna(row['ngaySinh']):
                        try:
                            ngay_sinh = pd.to_datetime(row['ngaySinh']).date()
                        except:
                            ngay_sinh = None
                    
                    # Xử lý số điện thoại
                    so_dien_thoai = None
                    if 'soDienthoai' in row and pd.notna(row['soDienthoai']):
                        so_dien_thoai = str(row['soDienthoai'])
                    
                    data = schemas.SinhVienCreate(
                        id_sinh_vien=row['id_sinh_vien'],
                        ho_ten=row['hoTen'],
                        ngay_sinh=ngay_sinh,
                        gioi_tinh=row.get('gioiTinh'),
                        email=row.get('email'),
                        so_dien_thoai=so_dien_thoai,
                        dia_chi=row.get('diaChi'),
                        id_nganh=row.get('id_nganh'),
                        id_lop=row.get('id_lop')
                    )
                    self.sinh_vien_repo.create(data)
                    them_moi += 1
                    self.sv_dict[row['id_sinh_vien']] = data
                else:
                    self.sv_dict[row['id_sinh_vien']] = existing
                    bo_qua += 1
            except Exception as e:
                print(f"  ❌ Lỗi import sinh viên {row.get('id_sinh_vien')}: {e}")
                bo_qua += 1
        
        print(f"  ✅ Thêm mới: {them_moi}, ⏩ Bỏ qua: {bo_qua}")
        return {"them_moi": them_moi, "bo_qua": bo_qua}
    
    def _import_dang_ky_mon(self, df) -> Dict:
        """Import dữ liệu ĐĂNG KÝ MÔN HỌC"""
        them_moi, bo_qua = 0, 0
        
        required = ['id_sinh_vien', 'id_lop_mon']
        if not all(col in df.columns for col in required):
            print("⚠️ Bỏ qua import ĐĂNG KÝ MÔN do thiếu cột")
            return {"them_moi": 0, "bo_qua": 0}
        
        # Tạo ID đăng ký nếu chưa có
        if 'id_dang_ky' not in df.columns:
            df['id_dang_ky'] = [generate_dang_ky_code(self.db) for _ in range(len(df))]
        
        # Lấy danh sách đăng ký duy nhất
        dk_list = df[['id_dang_ky', 'id_sinh_vien', 'id_lop_mon']].drop_duplicates()
        print(f"\n📚 Import ĐĂNG KÝ MÔN: {len(dk_list)} đăng ký")
        
        for _, row in dk_list.iterrows():
            try:
                # Kiểm tra sinh viên tồn tại
                if row['id_sinh_vien'] not in self.sv_dict:
                    sv = self.sinh_vien_repo.get_by_id(row['id_sinh_vien'])
                    if not sv:
                        print(f"  ⚠️ Sinh viên {row['id_sinh_vien']} không tồn tại, bỏ qua")
                        bo_qua += 1
                        continue
                    self.sv_dict[row['id_sinh_vien']] = sv
                
                # Kiểm tra lớp môn học tồn tại
                lop_mon = self.lop_mon_hoc_repo.get_by_id(row['id_lop_mon'])
                if not lop_mon:
                    print(f"  ⚠️ Lớp môn học {row['id_lop_mon']} không tồn tại, bỏ qua")
                    bo_qua += 1
                    continue
                
                existing = self.dang_ky_mon_repo.get_by_id(row['id_dang_ky'])
                if not existing:
                    # Lấy ngày đăng ký nếu có
                    ngay_dang_ky = datetime.now().date()
                    if 'ngay_dang_ky' in df.columns:
                        ngay_rows = df[df['id_dang_ky'] == row['id_dang_ky']]['ngay_dang_ky'].dropna()
                        if not ngay_rows.empty:
                            try:
                                ngay_dang_ky = pd.to_datetime(ngay_rows.iloc[0]).date()
                            except:
                                pass
                    
                    # Lấy trạng thái nếu có
                    trang_thai = 'Đã duyệt'
                    if 'trang_thai_dang_ky' in df.columns:
                        tt_rows = df[df['id_dang_ky'] == row['id_dang_ky']]['trang_thai_dang_ky'].dropna()
                        if not tt_rows.empty:
                            trang_thai = tt_rows.iloc[0]
                    
                    data = schemas.DangKyMonCreate(
                        id_dang_ky=row['id_dang_ky'],
                        id_sinh_vien=row['id_sinh_vien'],
                        id_lop_mon=row['id_lop_mon'],
                        ngay_dang_ky=ngay_dang_ky,
                        trang_thai=trang_thai
                    )
                    self.dang_ky_mon_repo.create(data)
                    them_moi += 1
                else:
                    bo_qua += 1
                    
            except Exception as e:
                print(f"  ❌ Lỗi import đăng ký môn: {e}")
                bo_qua += 1
        
        print(f"  ✅ Thêm mới: {them_moi}, ⏩ Bỏ qua: {bo_qua}")
        return {"them_moi": them_moi, "bo_qua": bo_qua}
    
    def _import_fact_diem(self, df) -> Dict:
        """Import dữ liệu FACT ĐIỂM"""
        them_moi, bo_qua = 0, 0
        
        required = ['id_sinh_vien', 'id_mon_hoc', 'id_hocky', 'diemHe10']
        if not all(col in df.columns for col in required):
            print("⚠️ Thiếu cột dữ liệu điểm, bỏ qua import điểm")
            return {"them_moi": 0, "bo_qua": 0}
        
        print(f"\n📚 Import FACT ĐIỂM: {len(df)} dòng điểm")
        
        for idx, row in df.iterrows():
            try:
                # Kiểm tra sinh viên tồn tại
                if row['id_sinh_vien'] not in self.sv_dict:
                    sv = self.sinh_vien_repo.get_by_id(row['id_sinh_vien'])
                    if not sv:
                        print(f"  ⚠️ Sinh viên {row['id_sinh_vien']} không tồn tại, bỏ qua")
                        bo_qua += 1
                        continue
                    self.sv_dict[row['id_sinh_vien']] = sv
                
                # Kiểm tra môn học tồn tại
                if row['id_mon_hoc'] not in self.mon_dict:
                    mon = self.mon_hoc_repo.get_by_id(row['id_mon_hoc'])
                    if not mon:
                        print(f"  ⚠️ Môn học {row['id_mon_hoc']} không tồn tại, bỏ qua")
                        bo_qua += 1
                        continue
                    self.mon_dict[row['id_mon_hoc']] = mon
                
                # Kiểm tra học kỳ tồn tại
                if row['id_hocky'] not in self.hk_dict:
                    hk = self.hoc_ky_repo.get_by_id(row['id_hocky'])
                    if not hk:
                        print(f"  ⚠️ Học kỳ {row['id_hocky']} không tồn tại, bỏ qua")
                        bo_qua += 1
                        continue
                    self.hk_dict[row['id_hocky']] = hk
                
                # Tạo ID điểm
                diem_id = f"{row['id_sinh_vien']}_{row['id_mon_hoc']}_{row['id_hocky']}"
                
                # Xử lý điểm
                diem_he10 = float(row['diemHe10']) if pd.notna(row['diemHe10']) else None
                ket_qua = diem_he10 >= 5 if diem_he10 is not None else False
                
                # Lấy id_dang_ky tương ứng
                id_dang_ky = None
                if 'id_dang_ky' in df.columns and pd.notna(row.get('id_dang_ky')):
                    id_dang_ky = row['id_dang_ky']
                else:
                    # Tạo id_dang_ky mới
                    id_dang_ky = generate_dang_ky_code(self.db)
                
                existing = self.diem_repo.get_by_id(diem_id)
                if not existing:
                    data = schemas.FactDiemCreate(
                        id_diem=diem_id,
                        id_dang_ky=id_dang_ky,
                        id_sinh_vien=row['id_sinh_vien'],
                        id_mon_hoc=row['id_mon_hoc'],
                        id_lop_mon=row.get('id_lop_mon'),
                        id_giang_vien=row.get('id_giang_vien'),
                        id_hoc_ky=row['id_hocky'],
                        diem_chuyen_can=row.get('diem_chuyen_can'),
                        diem_giua_ky=row.get('diem_giua_ky'),
                        diem_cuoi_ky=row.get('diem_cuoi_ky'),
                        diem_trung_binh=diem_he10,
                        diem_chu=row.get('diem_chu') or self._diem_so_sang_chu(diem_he10),
                        so_lan_hoc=int(row.get('so_lan_hoc', 1)),
                        so_tin_chi_dat=self.mon_dict[row['id_mon_hoc']].so_tin_chi if ket_qua else 0,
                        ket_qua=ket_qua
                    )
                    self.diem_repo.create(data)
                    them_moi += 1
                else:
                    bo_qua += 1
                
            except Exception as e:
                print(f"  ❌ Lỗi dòng {idx}: {e}")
                bo_qua += 1
        
        print(f"  ✅ Thêm mới: {them_moi}, ⏩ Bỏ qua: {bo_qua}")
        return {"them_moi": them_moi, "bo_qua": bo_qua}
    
    # -------------------------------------------------------------------------
    # HÀM TIỆN ÍCH
    # -------------------------------------------------------------------------
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