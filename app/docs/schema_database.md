-- Dưới đây là Schema chính xác của hệ thống. TUYỆT ĐỐI CHỈ DÙNG các cột này.

CREATE TABLE khoa (
    id_khoa VARCHAR(50) PRIMARY KEY, -- Ví dụ: 'K01'
    ten_khoa VARCHAR(255)            -- Ví dụ: 'Công nghệ thông tin'
);

CREATE TABLE nganh (
    id_nganh VARCHAR(50) PRIMARY KEY,
    ten_nganh VARCHAR(255),
    id_khoa VARCHAR(50) REFERENCES khoa(id_khoa)
);

CREATE TABLE lop_hoc (
    id_lop VARCHAR(50) PRIMARY KEY,
    ten_lop VARCHAR(255),
    khoa_hoc VARCHAR(50),
    nam_nhap_hoc INTEGER,
    si_so_toi_da INTEGER DEFAULT 50,
    id_khoa VARCHAR(50) REFERENCES khoa(id_khoa),
    id_nganh VARCHAR(50) REFERENCES nganh(id_nganh)
);

CREATE TABLE sinh_vien (
    id_sinh_vien VARCHAR(50) PRIMARY KEY,
    ho_ten VARCHAR(255),
    ngay_sinh DATE,
    gioi_tinh VARCHAR(10), -- 'Nam' hoặc 'Nữ'
    email VARCHAR(255),
    so_dien_thoai VARCHAR(20),
    dia_chi TEXT,
    id_nganh VARCHAR(50) REFERENCES nganh(id_nganh),
    id_lop VARCHAR(50) REFERENCES lop_hoc(id_lop)
);
CREATE TABLE giang_vien (
    id_giang_vien VARCHAR(50) PRIMARY KEY,
    ho_ten NVARCHAR(255),
    email VARCHAR(255),
    so_dien_thoai VARCHAR(20),
    hoc_ham NVARCHAR(50),
    id_khoa VARCHAR(50) REFERENCES khoa(id_khoa)
);

CREATE TABLE mon_hoc (
    id_mon_hoc VARCHAR(50) PRIMARY KEY,
    ten_mon NVARCHAR(255),
    so_tin_chi INT,
    loai_mon NVARCHAR(50),
    mo_ta NVARCHAR(MAX),
    he_so FLOAT,
    id_mon_tien_quyet VARCHAR(50) REFERENCES mon_hoc(id_mon_hoc)
);

CREATE TABLE hoc_ky (
    id_hoc_ky VARCHAR(50) PRIMARY KEY,
    ten_hoc_ky NVARCHAR(255),
    nam_hoc VARCHAR(50),
    ky_hoc INT
);

CREATE TABLE lop_mon_hoc (
    id_lop_mon VARCHAR(50) PRIMARY KEY,
    id_mon_hoc VARCHAR(50) REFERENCES mon_hoc(id_mon_hoc),
    id_giang_vien VARCHAR(50) REFERENCES giang_vien(id_giang_vien),
    id_hoc_ky VARCHAR(50) REFERENCES hoc_ky(id_hoc_ky),
    si_so_toi_da INT DEFAULT 50,
    phong_hoc NVARCHAR(50),
    lich_hoc NVARCHAR(255)
);

CREATE TABLE dang_ky_mon (
    id_dang_ky VARCHAR(50) PRIMARY KEY,
    id_sinh_vien VARCHAR(50) REFERENCES sinh_vien(id_sinh_vien),
    id_lop_mon VARCHAR(50) REFERENCES lop_mon_hoc(id_lop_mon),
    ngay_dang_ky DATE,
    trang_thai NVARCHAR(50)
);

CREATE TABLE fact_diem (
    id_diem VARCHAR(50) PRIMARY KEY,
    id_dang_ky VARCHAR(50) REFERENCES dang_ky_mon(id_dang_ky),
    id_sinh_vien VARCHAR(50) REFERENCES sinh_vien(id_sinh_vien),
    id_mon_hoc VARCHAR(50) REFERENCES mon_hoc(id_mon_hoc),
    id_lop_mon VARCHAR(50) REFERENCES lop_mon_hoc(id_lop_mon),
    id_giang_vien VARCHAR(50) REFERENCES giang_vien(id_giang_vien),
    id_hoc_ky VARCHAR(50) REFERENCES hoc_ky(id_hoc_ky),
    diem_chuyen_can FLOAT,
    diem_giua_ky FLOAT,
    diem_cuoi_ky FLOAT,
    diem_trung_binh FLOAT,
    diem_chu VARCHAR(10),
    so_lan_hoc INT DEFAULT 1,
    so_tin_chi_dat INT,
    ket_qua BIT
);