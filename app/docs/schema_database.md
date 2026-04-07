# Database Schema

---


### Table: khoa
Stores information about the various faculties/departments within the university.

| column | type | description |
| id_khoa | string | Unique identifier for the faculty (Primary Key) |
| ten_khoa | string | Full name of the faculty (e.g., 'Information Technology') |

### Table: nganh
Details regarding academic majors/programs managed by specific faculties.

| column | type | description |
| id_nganh | string | Unique identifier for the academic major (Primary Key) |
| ten_nganh | string | "Full name of the major (e.g., 'Software Engineering')" |
| id_khoa | string | ID of the managing faculty (Foreign Key -> khoa.id_khoa) |

### Table: lop_hoc
Information about administrative classes (home rooms) for students.

| column | type | description |
| id_lop | string | Unique identifier for the class (Primary Key) |
| ten_lop | string | "Name of the administrative class (e.g., 'K61_CNTT1')" |
| khoa_hoc | string | "Training cohort/batch (e.g., 'K61')" |
| nam_nhap_hoc | integer | Enrollment year |
| si_so_toi_da | integer | Maximum student capacity (Default: 50) |
| id_khoa | string | ID of the associated faculty (Foreign Key -> khoa.id_khoa) |
| id_nganh | string | ID of the associated major (Foreign Key -> nganh.id_nganh) |

### Table: sinh_vien
Detailed personal and academic records of every student.

| column | type | description |
| id_sinh_vien | string | Student ID number (Primary Key) |
| ho_ten | string | Full name of the student |
| ngay_sinh | date | Student's date of birth (ISO format) |
| gioi_tinh | string | "Gender (Values: 'Nam' for Male, 'Nữ' for Female)" |
| email | string | Personal or academic email address |
| so_dien_thoai | string | Contact phone number |
| dia_chi | string | Permanent or temporary address |
| id_nganh | string | ID of the student's major (Foreign Key -> nganh.id_nganh) |
| id_lop | string | ID of the student's administrative class (Foreign Key -> lop_hoc.id_lop) |
### Table: giang_vien
Comprehensive information about university lecturers and professors.

| column | type | description |
| id_giang_vien | string | Unique identifier for the lecturer (Primary Key) |
| ho_ten | string | Full name of the lecturer (Supports Unicode) |
| email | string | Work email address |
| so_dien_thoai | string | Contact phone number | 
| hoc_ham | string | "Academic title (e.g., 'PGS', 'TS', 'ThS')" |
| id_khoa | string | ID of the faculty they belong to (Foreign Key -> khoa.id_khoa) |

### Table: mon_hoc
The catalog of subjects/courses within the curriculum.

| column | type | description | 
| id_mon_hoc | string | Unique identifier for the subject (Primary Key) |
| ten_mon | string | Full name of the subject |
| so_tin_chi | integer | Number of credits for the course |
| loai_mon | string,"Category (e.g., 'General', 'Core', 'Specialization')" |
| mo_ta | string | Detailed description of the course content |
| he_so | float | Weighting factor for grade calculation |
| id_mon_tien_quyet | string | ID of the required prerequisite course (Self-ref -> mon_hoc.id_mon_hoc) |

### Table: hoc_ky
Timeline management for academic semesters and years.

| column | type | description |
| id_hoc_ky | string | Unique identifier for the semester (Primary Key) | 
| ten_hoc_ky | string | "Display name (e.g., 'Semester 1')" |
| nam_hoc | string | "Academic year period (e.g., '2024-2025')" |
| ky_hoc | integer | "Semester number within the year (1, 2, or 3)" |

### Table: lop_mon_hoc
Specific course sections/classes opened in a given semester.

| column | type | description |
| id_lop_mon | string | Unique identifier for the course section (Primary Key) |
| id_mon_hoc | string | ID of the related subject (Foreign Key -> mon_hoc.id_mon_hoc) |
| id_giang_vien | string | ID of the assigned lecturer (Foreign Key -> giang_vien.id_giang_vien) |
| id_hoc_ky | string | ID of the semester when opened (Foreign Key -> hoc_ky.id_hoc_ky) |
| si_so_toi_da | integer | Enrollment limit (Default: 50) |
| phong_hoc | string | Assigned classroom name |
| lich_hoc | string | "Schedule (e.g., 'Monday, Period 1-3')" |

### Table: dang_ky_mon
Transaction log of student course registrations.

| column | type | description |
| id_dang_ky | string | Unique identifier for the registration record (Primary Key) |
| id_sinh_vien | string | ID of the registering student (Foreign Key -> sinh_vien.id_sinh_vien) |
| id_lop_mon | string | ID of the course section (Foreign Key -> lop_mon_hoc.id_lop_mon) |
| ngay_dang_ky | date | Date of the registration transaction
| trang_thai | string | "Registration status (e.g., 'Approved', 'Cancelled')" |

### Table: fact_diem
The central fact table containing detailed academic results and student grades.

| column | type | description |
| id_diem | string | Unique identifier for the grade record (Primary Key) |
| id_dang_ky | string | Related registration ID (Foreign Key -> dang_ky_mon.id_dang_ky) |
| id_sinh_vien | string | ID of the student (Foreign Key -> sinh_vien.id_sinh_vien) |
| id_mon_hoc | string | ID of the subject (Foreign Key -> mon_hoc.id_mon_hoc) |
| id_lop_mon | string | ID of the specific class section (Foreign Key -> lop_mon_hoc.id_lop_mon) |
| id_giang_vien | string | ID of the lecturer who graded (Foreign Key -> giang_vien.id_giang_vien) |
| id_hoc_ky | string | ID of the semester for the grade (Foreign Key -> hoc_ky.id_hoc_ky) |
| diem_chuyen_can | float | Attendance score |
| diem_giua_ky | float | Midterm exam score |
| diem_cuoi_ky | float | Final exam score |
| diem_trung_binh | float | Final weighted average (Scale of 10.0) | 
| diem_chustring | "Letter grade conversion (A, B, C, D, F)" |
| so_lan_hoc | integer | Number of times the student attempted the course (Default: 1) |
| so_tin_chi_dat | integer | Earned credits awarded upon successful completion |
| ket_qua | boolean | "Final outcome (True: Pass, False: Fail)" |




