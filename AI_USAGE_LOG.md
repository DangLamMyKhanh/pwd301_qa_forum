# AI Usage Log - Nhat ky su dung AI

- Mon hoc: Python Web Development (PWD301)
- De tai: Topic 5 - Student Q&A Forum
- Muc dich: Ghi chep nhat ky su dung cac cong cu Tri tue Nhan tao (AI Tools) phuc vu qua trinh phat trien du an theo dung Tieu chi 10 trong Rubric danh gia.

---

## 1. Nguyen tac su dung AI cua nhom

1. AI dong vai tro la tro ly lap trinh (Pair Programmer) ho tro:
   - Goi y kien truc thu muc va mo hinh to chuc ma nguon Flask chuan.
   - Ho tro soan thao tai lieu ky thuat, dac ta REST API va schema co so du lieu.
   - Ho tro kiem tra loi, ra soat cac lo hong bao mat pho bien (CSRF, XSS, SQL Injection, IDOR).
2. Cam ket ve tinh trung thuc va chat luong:
   - Tat ca thanh vien trong nhom deu phai doc hieu tung dong ma nguon do AI goi y truoc khi dua vao du an.
   - Thuc hien kiem thu doc lap tren may cuc bo va chiu trach nhiem hoan toan ve san pham cuoi cung.

---

## 2. Nhat ky chi tiet (Prompt & Quality Assessment Log)

| Ngay | Thanh vien | Cong cu AI | Muc dich tuong tac (Prompt/Yeu cau) | Ket qua AI sinh ra (Output) |
| :---: | :---: | :---: | :--- | :--- |
| 03/10/2026 | Truong | Antigravity AI | Su dung AI de ho tro soan thao va chinh sua cau truc Markdown cho tai lieu du an (README.md). | Khung noi dung Markdown chuan: Ten de tai, Mo ta, Tech Stack, va Huong dan cai dat. |
| *(Tiep tuc cap nhat)* | | | | |

---

## 3. Danh gia chat luong ma nguon do AI sinh ra

- Tinh dung dan: Ma nguon va file cau hinh do AI tao ra tuan thu dung cu phap chuan cua Python 3.11, Flask 3.0 va Docker Compose specification.
- Tinh an toan:
  - Khong de lo secret key truc tiep trong ma nguon, khuyen nghi su dung file bien moi truong .env.
  - Form luon co co che bao ve CSRF, du lieu nhap tu nguoi dung duoc kiem tra server-side.
- Kha nang bao tri: Code duoc modul hoa ro rang theo mo hinh Blueprint, giup cac thanh vien phat trien doc lap ma khong gay xung dot ma nguon tren Git.
