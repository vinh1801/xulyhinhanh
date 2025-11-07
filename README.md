# OCR Translate App

Ứng dụng giao diện Tkinter hỗ trợ nhận dạng văn bản từ ảnh (OCR) bằng Tesseract, tiền xử lý ảnh với OpenCV và dịch tự động sang tiếng Việt bằng Google Translate.

## 1. Chuẩn bị môi trường

- **Yêu cầu hệ thống**

  - Windows 10 trở lên.
  - Python 3.10+ (khuyến nghị [Python.org](https://www.python.org/downloads/)).
  - Kết nối Internet (để dịch Google Translate).

- **Tesseract OCR**

  1. Tải bản cài đặt Windows tại: https://github.com/UB-Mannheim/tesseract/wiki
  2. Cài đặt theo hướng dẫn (đường dẫn mặc định được khuyến nghị: `C:\Program Files\Tesseract-OCR`).
  3. Sau khi cài đặt, mở `cmd` và kiểm tra:

     tesseract --version 4. Nếu không cài ở đường dẫn mặc định, cập nhật biến `tesseract_path` trong `app_gui.py`.

## 2. Tạo môi trường ảo và cài thư viện

cd vào thư mục gốc
python -m venv .venv
.\.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

## 3. Chạy ứng dụng

# Nếu chưa kích hoạt môi trường ảo:

.\.venv\Scripts\activate

python app_gui.py

Giao diện sẽ mở ra. Chọn ảnh (`PNG/JPG/JPEG/BMP/TIFF`) có chứa tiếng Anh để ứng dụng:

1. Tiền xử lý ảnh.
2. Nhận dạng chữ bằng Tesseract.
3. Dịch sang tiếng Việt.
