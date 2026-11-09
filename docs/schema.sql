CREATE TABLE sqlite_sequence(name,seq);

CREATE TABLE "nguoi_dung" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ma_dinh_danh_cong" varchar(50) NOT NULL UNIQUE, "ho_ten" varchar(150) NOT NULL, "email" varchar(150) NULL UNIQUE, "so_dien_thoai" varchar(20) NULL, "loai_nguoi_dung" varchar(20) NOT NULL, "trang_thai" varchar(20) NOT NULL, "lan_dang_nhap_cuoi" datetime NULL, "ngay_tao" datetime NOT NULL);

CREATE TABLE "vai_tro" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ma_vai_tro" varchar(20) NOT NULL UNIQUE, "ten_vai_tro" varchar(100) NOT NULL, "mo_ta" varchar(300) NULL);

CREATE TABLE "khoa" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ma_khoa" varchar(20) NOT NULL UNIQUE, "ten_khoa" varchar(200) NOT NULL, "dang_hoat_dong" bool NOT NULL);

CREATE TABLE "giang_vien" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ma_can_bo" varchar(20) NOT NULL UNIQUE, "hoc_vi" varchar(50) NULL, "bo_mon_id" bigint NULL REFERENCES "bo_mon" ("id") DEFERRABLE INITIALLY DEFERRED, "nguoi_dung_id" bigint NOT NULL UNIQUE REFERENCES "nguoi_dung" ("id") DEFERRABLE INITIALLY DEFERRED, "khoa_id" bigint NOT NULL REFERENCES "khoa" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "sinh_vien" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ma_sinh_vien" varchar(20) NOT NULL UNIQUE, "lop" varchar(50) NULL, "khoa_id" bigint NOT NULL REFERENCES "khoa" ("id") DEFERRABLE INITIALLY DEFERRED, "nguoi_dung_id" bigint NOT NULL UNIQUE REFERENCES "nguoi_dung" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "bo_mon" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ma_bo_mon" varchar(20) NOT NULL, "ten_bo_mon" varchar(200) NOT NULL, "dang_hoat_dong" bool NOT NULL, "khoa_id" bigint NOT NULL REFERENCES "khoa" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "uq_bo_mon_khoa_ma_bo_mon" UNIQUE ("khoa_id", "ma_bo_mon"));

CREATE TABLE "tai_khoan_lien_ket" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nha_cung_cap" varchar(20) NOT NULL, "ma_ngoai" varchar(100) NOT NULL, "email" varchar(150) NULL, "trang_thai_duyet" varchar(20) NOT NULL, "ngay_lien_ket" datetime NOT NULL, "nguoi_dung_id" bigint NOT NULL REFERENCES "nguoi_dung" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "uq_tai_khoan_lien_ket_nha_cung_cap_ma_ngoai" UNIQUE ("nha_cung_cap", "ma_ngoai"));

CREATE TABLE "nguoi_dung_vai_tro" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "hieu_luc_tu" date NOT NULL, "hieu_luc_den" date NULL, "khoa_id" bigint NULL REFERENCES "khoa" ("id") DEFERRABLE INITIALLY DEFERRED, "nguoi_dung_id" bigint NOT NULL REFERENCES "nguoi_dung" ("id") DEFERRABLE INITIALLY DEFERRED, "vai_tro_id" bigint NOT NULL REFERENCES "vai_tro" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "uq_nguoi_dung_vai_tro_khoa" UNIQUE ("nguoi_dung_id", "vai_tro_id", "khoa_id"));

CREATE TABLE "dot" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ma_dot" varchar(30) NOT NULL UNIQUE, "ten_dot" varchar(200) NOT NULL, "loai" varchar(20) NOT NULL, "hoc_ky" smallint unsigned NOT NULL CHECK ("hoc_ky" >= 0), "nam_hoc" varchar(9) NOT NULL, "trang_thai" varchar(20) NOT NULL, "so_sv_toi_da_moi_gv" smallint unsigned NOT NULL CHECK ("so_sv_toi_da_moi_gv" >= 0), "hinh_thuc_cham" varchar(20) NOT NULL, "ngay_tao" datetime NOT NULL, "khoa_id" bigint NOT NULL REFERENCES "khoa" ("id") DEFERRABLE INITIALLY DEFERRED, "nguoi_tao_id" bigint NOT NULL REFERENCES "nguoi_dung" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "dot_moc_thoi_gian" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ma_moc" varchar(30) NOT NULL, "ten_moc" varchar(150) NOT NULL, "loai_moc" varchar(20) NOT NULL, "thu_tu" smallint unsigned NOT NULL CHECK ("thu_tu" >= 0), "han_cuoi" datetime NOT NULL, "dot_id" bigint NOT NULL REFERENCES "dot" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "uq_dot_moc_thoi_gian_dot_ma_moc" UNIQUE ("dot_id", "ma_moc"));

CREATE TABLE "dot_trong_so" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "thanh_phan" varchar(20) NOT NULL, "trong_so" decimal NOT NULL, "dot_id" bigint NOT NULL REFERENCES "dot" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "uq_dot_trong_so_dot_thanh_phan" UNIQUE ("dot_id", "thanh_phan"));

CREATE TABLE "diem_dau_vao" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "diem_tb_he4" decimal NULL, "tin_chi_tich_luy" smallint unsigned NULL CHECK ("tin_chi_tich_luy" >= 0), "ngay_lay" datetime NULL, "nguon" varchar(20) NOT NULL, "ho_so_id" bigint NOT NULL UNIQUE REFERENCES "ho_so" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "lan_lay_diem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nguon" varchar(20) NOT NULL, "ngay_lay" datetime NOT NULL, "so_sv_co_diem" integer NOT NULL, "so_sv_thieu" integer NOT NULL, "trang_thai" varchar(20) NOT NULL, "chi_tiet_loi" text NULL, "dot_id" bigint NOT NULL REFERENCES "dot" ("id") DEFERRABLE INITIALLY DEFERRED, "nguoi_thuc_hien_id" bigint NOT NULL REFERENCES "nguoi_dung" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "lan_nhap_danh_sach" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ten_tep" varchar(255) NOT NULL, "duong_dan" varchar(500) NOT NULL, "tong_dong" integer NOT NULL, "dong_hop_le" integer NOT NULL, "dong_loi" integer NOT NULL, "trang_thai" varchar(20) NOT NULL, "ngay_tai" datetime NOT NULL, "dot_id" bigint NOT NULL REFERENCES "dot" ("id") DEFERRABLE INITIALLY DEFERRED, "nguoi_tai_id" bigint NOT NULL REFERENCES "nguoi_dung" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "dong_nhap_danh_sach" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "so_dong" integer NOT NULL, "ma_sinh_vien" varchar(20) NOT NULL, "ho_ten" varchar(150) NULL, "lop" varchar(50) NULL, "diem_tb" decimal NULL, "trang_thai_dong" varchar(20) NOT NULL, "loi" varchar(300) NULL, "lan_nhap_id" bigint NOT NULL REFERENCES "lan_nhap_danh_sach" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "ho_so" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "trang_thai" varchar(25) NOT NULL, "ngay_tao" datetime NOT NULL, "ngay_cap_nhat" datetime NOT NULL, "de_tai_hien_tai_id" bigint NULL REFERENCES "de_tai" ("id") DEFERRABLE INITIALLY DEFERRED, "dot_id" bigint NOT NULL REFERENCES "dot" ("id") DEFERRABLE INITIALLY DEFERRED, "giang_vien_huong_dan_id" bigint NULL REFERENCES "giang_vien" ("id") DEFERRABLE INITIALLY DEFERRED, "sinh_vien_id" bigint NOT NULL REFERENCES "sinh_vien" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "uq_ho_so_dot_sinh_vien" UNIQUE ("dot_id", "sinh_vien_id"));

CREATE TABLE "ket_qua_ho_so" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "diem_cuoi" decimal NOT NULL, "trong_so_su_dung" text NOT NULL CHECK ((JSON_VALID("trong_so_su_dung") OR "trong_so_su_dung" IS NULL)), "ngay_chot" datetime NOT NULL, "da_luu_tru" bool NOT NULL, "ho_so_id" bigint NOT NULL UNIQUE REFERENCES "ho_so" ("id") DEFERRABLE INITIALLY DEFERRED, "nguoi_chot_id" bigint NOT NULL REFERENCES "nguoi_dung" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "phan_cong_cham" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "loai" varchar(15) NOT NULL, "ngay_phan_cong" datetime NOT NULL, "giang_vien_id" bigint NULL REFERENCES "giang_vien" ("id") DEFERRABLE INITIALLY DEFERRED, "ho_so_id" bigint NOT NULL REFERENCES "ho_so" ("id") DEFERRABLE INITIALLY DEFERRED, "hoi_dong_id" bigint NULL REFERENCES "hoi_dong" ("id") DEFERRABLE INITIALLY DEFERRED, "nguoi_phan_cong_id" bigint NOT NULL REFERENCES "nguoi_dung" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "xac_minh_noi_thuc_tap" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "da_doi_chieu_ban_goc" bool NOT NULL, "ngay_doi_chieu" date NULL, "can_xac_minh" bool NOT NULL, "ly_do_can_xac_minh" varchar(15) NULL, "ket_qua_xac_minh" varchar(15) NULL, "ngay_xac_minh" date NULL, "ghi_chu" varchar(1000) NULL, "ho_so_id" bigint NOT NULL UNIQUE REFERENCES "ho_so" ("id") DEFERRABLE INITIALLY DEFERRED, "nguoi_doi_chieu_id" bigint NULL REFERENCES "giang_vien" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "diem_thanh_phan" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "thanh_phan" varchar(20) NOT NULL, "diem" decimal NULL, "nhan_xet" text NULL, "trang_thai" varchar(10) NOT NULL, "ngay_gui" datetime NULL, "ho_so_id" bigint NOT NULL REFERENCES "ho_so" ("id") DEFERRABLE INITIALLY DEFERRED, "nguoi_cham_id" bigint NOT NULL REFERENCES "giang_vien" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "uq_diem_thanh_phan_ho_so_thanh_phan_nguoi_cham" UNIQUE ("ho_so_id", "thanh_phan", "nguoi_cham_id"));

CREATE TABLE "hoi_dong" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ten_hoi_dong" varchar(150) NOT NULL, "thoi_gian_bao_ve" datetime NULL, "dia_diem" varchar(200) NULL, "dot_id" bigint NOT NULL REFERENCES "dot" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "uq_hoi_dong_dot_ten_hoi_dong" UNIQUE ("dot_id", "ten_hoi_dong"));

CREATE TABLE "thanh_vien_hoi_dong" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "vai_tro_trong_hoi_dong" varchar(30) NULL, "giang_vien_id" bigint NOT NULL REFERENCES "giang_vien" ("id") DEFERRABLE INITIALLY DEFERRED, "hoi_dong_id" bigint NOT NULL REFERENCES "hoi_dong" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "uq_thanh_vien_hoi_dong_hoi_dong_giang_vien" UNIQUE ("hoi_dong_id", "giang_vien_id"));

CREATE TABLE "de_tai" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nguon" varchar(20) NOT NULL, "ten_de_tai" varchar(300) NOT NULL, "mo_ta" text NULL, "trang_thai" varchar(15) NOT NULL, "gop_y_cua_gv" varchar(1000) NULL, "ngay_gui" datetime NOT NULL, "ngay_chot" datetime NULL, "ho_so_id" bigint NOT NULL REFERENCES "ho_so" ("id") DEFERRABLE INITIALLY DEFERRED, "de_tai_goi_y_id" bigint NULL REFERENCES "de_tai_goi_y" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "de_tai_goi_y" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ten_de_tai" varchar(300) NOT NULL, "mo_ta" text NULL, "so_luong_toi_da" smallint unsigned NOT NULL CHECK ("so_luong_toi_da" >= 0), "trang_thai" varchar(10) NOT NULL, "dot_id" bigint NOT NULL REFERENCES "dot" ("id") DEFERRABLE INITIALLY DEFERRED, "giang_vien_id" bigint NOT NULL REFERENCES "giang_vien" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "nhat_ky_he_thong" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "hanh_dong" varchar(100) NOT NULL, "doi_tuong_loai" varchar(50) NOT NULL, "doi_tuong_id" bigint NULL, "mo_ta" text NOT NULL, "dia_chi_ip" varchar(45) NULL, "thoi_gian" datetime NOT NULL, "nguoi_thuc_hien_id" bigint NULL REFERENCES "nguoi_dung" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "thong_bao" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "tieu_de" varchar(200) NOT NULL, "noi_dung" text NOT NULL, "loai" varchar(30) NOT NULL, "duong_dan_dieu_huong" varchar(300) NULL, "da_doc" bool NOT NULL, "ngay_tao" datetime NOT NULL, "nguoi_nhan_id" bigint NOT NULL REFERENCES "nguoi_dung" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "ban_phan_cong" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "trang_thai" varchar(20) NOT NULL, "ngay_gui" datetime NULL, "ngay_cong_bo" datetime NULL, "dot_id" bigint NOT NULL REFERENCES "dot" ("id") DEFERRABLE INITIALLY DEFERRED, "nguoi_tao_id" bigint NOT NULL REFERENCES "nguoi_dung" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "phan_cong_huong_dan" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "trang_thai" varchar(20) NOT NULL, "la_goi_y" bool NOT NULL, "ly_do_tu_choi" varchar(500) NULL, "ngay_phan_hoi" datetime NULL, "ban_phan_cong_id" bigint NOT NULL REFERENCES "ban_phan_cong" ("id") DEFERRABLE INITIALLY DEFERRED, "giang_vien_id" bigint NOT NULL REFERENCES "giang_vien" ("id") DEFERRABLE INITIALLY DEFERRED, "ho_so_id" bigint NOT NULL REFERENCES "ho_so" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "uq_phan_cong_huong_dan_ban_phan_cong_ho_so" UNIQUE ("ban_phan_cong_id", "ho_so_id"));

CREATE TABLE "minh_chung" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "loai" varchar(20) NOT NULL, "ghi_chu" varchar(1000) NULL, "ngay_nop" datetime NOT NULL, "tre_han" bool NOT NULL, "trang_thai" varchar(15) NOT NULL, "ho_so_id" bigint NOT NULL REFERENCES "ho_so" ("id") DEFERRABLE INITIALLY DEFERRED, "moc_id" bigint NULL REFERENCES "dot_moc_thoi_gian" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "nhan_xet_minh_chung" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "noi_dung" text NOT NULL, "ngay_tao" datetime NOT NULL, "giang_vien_id" bigint NOT NULL REFERENCES "giang_vien" ("id") DEFERRABLE INITIALLY DEFERRED, "minh_chung_id" bigint NOT NULL REFERENCES "minh_chung" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "tep_dinh_kem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ten_tep" varchar(255) NOT NULL, "duong_dan" varchar(500) NOT NULL, "loai_mime" varchar(100) NOT NULL, "kich_thuoc" bigint NOT NULL, "ngay_tai" datetime NOT NULL, "minh_chung_id" bigint NOT NULL REFERENCES "minh_chung" ("id") DEFERRABLE INITIALLY DEFERRED, "nguoi_tai_id" bigint NOT NULL REFERENCES "nguoi_dung" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE TABLE "thong_tin_noi_thuc_tap" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "ten_don_vi" varchar(200) NOT NULL, "nguoi_xac_nhan" varchar(150) NOT NULL, "chuc_vu" varchar(100) NULL, "so_dien_thoai" varchar(20) NULL, "email" varchar(150) NULL, "dia_chi" varchar(300) NULL, "ho_so_id" bigint NOT NULL UNIQUE REFERENCES "ho_so" ("id") DEFERRABLE INITIALLY DEFERRED);

