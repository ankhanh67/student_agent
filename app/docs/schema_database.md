# Schema Cơ Sở Dữ Liệu - Hệ Thống Quản Lý Sinh Viên

Cơ sở dữ liệu này lưu trữ thông tin về sinh viên, giảng viên, môn học, lớp học phần, đăng ký môn và điểm số.

---

# Bảng: khoa
Thông tin khoa trong trường.

Các cột:
- id_khoa (PK) – mã khoa
- ten_khoa – tên khoa

---

# Bảng: nganh
Thông tin ngành học.

Các cột:
- id_nganh (PK) – mã ngành
- ten_nganh – tên ngành
- id_khoa (FK → khoa.id_khoa) – ngành thuộc khoa nào

---

# Bảng: lop_hoc
Thông tin lớp sinh viên.

Các cột:
- id_lop (PK) – mã lớp
- ten_lop – tên lớp
- khoa_hoc – khóa học
- nam_nhap_hoc – năm nhập học
- si_so_toi_da – sĩ số tối đa
- id_khoa (FK → khoa.id_khoa)
- id_nganh (FK → nganh.id_nganh)

---

# Bảng: sinh_vien
Thông tin sinh viên.

Các cột:
- id_sinh_vien (PK) – mã sinh viên
- ho_ten – họ tên sinh viên
- ngay_sinh – ngày sinh
- gioi_tinh – giới tính
- email – email
- so_dien_thoai – số điện thoại
- dia_chi – địa chỉ
- id_nganh (FK → nganh.id_nganh)
- id_lop (FK → lop_hoc.id_lop)

---

# Bảng: giang_vien
Thông tin giảng viên.

Các cột:
- id_giang_vien (PK) – mã giảng viên
- ho_ten – họ tên giảng viên
- email – email
- so_dien_thoai – số điện thoại
- hoc_ham – học hàm / học vị
- id_khoa (FK → khoa.id_khoa)

---

# Bảng: mon_hoc
Thông tin môn học.

Các cột:
- id_mon_hoc (PK) – mã môn học
- ten_mon – tên môn học
- so_tin_chi – số tín chỉ
- loai_mon – loại môn
- mo_ta – mô tả môn học
- he_so – hệ số tính điểm
- id_mon_tien_quyet (FK → mon_hoc.id_mon_hoc) – môn học tiên quyết

---

# Bảng: hoc_ky
Thông tin học kỳ.

Các cột:
- id_hoc_ky (PK) – mã học kỳ
- ten_hoc_ky – tên học kỳ
- nam_hoc – năm học
- ky_hoc – số thứ tự học kỳ

---

# Bảng: lop_mon_hoc
Lớp học phần của một môn học trong một học kỳ.

Các cột:
- id_lop_mon (PK) – mã lớp môn học
- id_mon_hoc (FK → mon_hoc.id_mon_hoc)
- id_giang_vien (FK → giang_vien.id_giang_vien)
- id_hoc_ky (FK → hoc_ky.id_hoc_ky)
- si_so_toi_da – số sinh viên tối đa
- phong_hoc – phòng học
- lich_hoc – lịch học

---

# Bảng: dang_ky_mon
Thông tin sinh viên đăng ký môn học.

Các cột:
- id_dang_ky (PK) – mã đăng ký
- id_sinh_vien (FK → sinh_vien.id_sinh_vien)
- id_lop_mon (FK → lop_mon_hoc.id_lop_mon)
- ngay_dang_ky – ngày đăng ký
- trang_thai – trạng thái đăng ký

---

# Bảng: fact_diem
Bảng lưu điểm của sinh viên cho từng môn học.

Các cột:
- id_diem (PK) – mã bản ghi điểm
- id_dang_ky (FK → dang_ky_mon.id_dang_ky)
- id_sinh_vien (FK → sinh_vien.id_sinh_vien)
- id_mon_hoc (FK → mon_hoc.id_mon_hoc)
- id_lop_mon (FK → lop_mon_hoc.id_lop_mon)
- id_hoc_ky (FK → hoc_ky.id_hoc_ky)

Các cột điểm:
- diem_chuyen_can – điểm chuyên cần
- diem_giua_ky – điểm giữa kỳ
- diem_cuoi_ky – điểm cuối kỳ
- diem_trung_binh – điểm trung bình
- diem_chu – điểm chữ
- so_lan_hoc – số lần học
- so_tin_chi_dat – số tín chỉ đạt
- ket_qua – kết quả (đạt / không đạt)

---

# Tổng Quan Quan Hệ Giữa Các Bảng

khoa  
→ nganh  
→ lop_hoc  
→ sinh_vien  

mon_hoc  
→ lop_mon_hoc  
→ dang_ky_mon  
→ fact_diem  

giang_vien  
→ lop_mon_hoc  

hoc_ky  
→ lop_mon_hoc  
→ fact_diem