# app_gui.py (Bản nâng cấp giao diện - Đã sửa màu nút)
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk  # Sử dụng theme widgets
from tkinter.scrolledtext import ScrolledText  # Text box có thanh cuộn
from PIL import Image, ImageTk
import pytesseract
import os
import re
from deep_translator import GoogleTranslator
from image_preprocessing import preprocess_image_for_ocr  # Import hàm tiền xử lý

# --- Cấu hình đường dẫn Tesseract ---
tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    # Thử tìm tự động hoặc yêu cầu người dùng cấu hình
    print(f"Cảnh báo: Không tìm thấy Tesseract tại {tesseract_path}")
    print("Vui lòng cài đặt Tesseract OCR hoặc cập nhật đường dẫn trong code.")

# --- Hàm làm sạch text: chỉ xuống dòng khi hết câu VÀ ảnh gốc có line break ---
def clean_text_format(text):
    """
    Làm sạch text: chỉ xuống dòng khi:
    - Dòng kết thúc bằng dấu câu (.!?)
    - VÀ dòng tiếp theo là dòng mới (có line break trong OCR output)
    
    Nếu dòng kết thúc bằng dấu câu nhưng vẫn có chữ sau đó trên cùng dòng → gộp lại
    """
    if not text:
        return ""
    
    # Chia thành các dòng từ OCR output
    lines = text.split('\n')
    cleaned_lines = [line.rstrip() for line in lines]  # Xóa khoảng trắng cuối dòng
    
    # Xóa các dòng trống ở đầu và cuối
    while cleaned_lines and not cleaned_lines[0].strip():
        cleaned_lines.pop(0)
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()
    
    # Xử lý: gộp các dòng không hết câu, chỉ giữ line break khi hết câu VÀ có line break trong OCR
    result = []
    i = 0
    
    while i < len(cleaned_lines):
        current_line = cleaned_lines[i].strip()
        
        if not current_line:
            # Dòng trống: giữ nguyên (paragraph break)
            result.append('')
            i += 1
            continue
        
        # Bắt đầu với dòng hiện tại
        merged_line = current_line
        j = i + 1
        
        # Kiểm tra xem dòng hiện tại có kết thúc bằng dấu câu không
        ends_with_punctuation = merged_line and merged_line[-1] in '.!?'
        
        # Nếu dòng kết thúc bằng dấu câu
        if ends_with_punctuation:
            # Kiểm tra dòng tiếp theo
            if j < len(cleaned_lines) and cleaned_lines[j].strip():
                # Có dòng tiếp theo (có line break trong OCR)
                # → Ảnh gốc có line break ở đây → xuống dòng
                result.append(merged_line)
                i = j  # Nhảy đến dòng tiếp theo
                continue
            else:
                # Không có dòng tiếp theo → dòng cuối cùng, giữ nguyên
                result.append(merged_line)
                i += 1
                continue
        
        # Nếu dòng KHÔNG kết thúc bằng dấu câu → gộp với các dòng tiếp theo
        while j < len(cleaned_lines):
            next_line = cleaned_lines[j].strip()
            
            # Dừng nếu gặp dòng trống (paragraph break)
            if not next_line:
                break
            
            # Gộp dòng tiếp theo vào
            merged_line = merged_line + ' ' + next_line
            
            # Kiểm tra xem dòng đã gộp có kết thúc bằng dấu câu chưa
            if merged_line and merged_line[-1] in '.!?':
                # Đã hết câu, kiểm tra dòng tiếp theo
                if j + 1 < len(cleaned_lines) and cleaned_lines[j + 1].strip():
                    # Có dòng tiếp theo (có line break trong OCR)
                    # → Ảnh gốc có line break ở đây → xuống dòng
                    break
                else:
                    # Không có dòng tiếp theo → dòng cuối cùng
                    break
            
            j += 1
        
        # Thêm dòng đã gộp vào kết quả
        result.append(merged_line)
        i = j + 1  # Nhảy đến dòng tiếp theo chưa xử lý
    
    # Xóa khoảng trắng thừa trong mỗi dòng (nhiều hơn 2 khoảng trắng liên tiếp)
    result = [re.sub(r' {2,}', ' ', line) for line in result]
    
    # Gộp lại: giữ line break giữa các dòng
    cleaned_text = '\n'.join(result)
    
    return cleaned_text

# --- Hàm xử lý chính ---
def process_image_and_translate():
    file_path = filedialog.askopenfilename(
        title="Chọn ảnh để OCR",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")]
    )

    if not file_path:
        return

    # 1. Hiển thị ảnh
    try:
        img = Image.open(file_path)
        img.thumbnail((450, 400))
        img_tk = ImageTk.PhotoImage(img)
        image_label.config(image=img_tk, text="")  # Xóa chữ "Chưa chọn ảnh"
        image_label.image = img_tk
    except Exception as e:
        text_original.delete("1.0", tk.END)
        text_original.insert(tk.END, f"Lỗi mở ảnh: {e}")
        return

    # 2. Xóa văn bản cũ và thông báo
    text_original.delete("1.0", tk.END)
    text_translated.delete("1.0", tk.END)

    text_original.insert(tk.END, "Đang xử lý OCR...")
    text_translated.insert(tk.END, "Đang dịch...")
    notebook.select(tab_original)  # Chuyển về tab gốc
    root.update_idletasks()

    # 3. Tiền xử lý ảnh trước OCR
    try:
        # Mở lại ảnh gốc (không resize) để xử lý
        img_for_ocr = Image.open(file_path)
        # Áp dụng tiền xử lý từ module riêng (tự động phát hiện chữ sáng)
        processed_img = preprocess_image_for_ocr(img_for_ocr, auto_invert=True)
    except ImportError:
        # Nếu không có OpenCV, dùng phương pháp đơn giản
        try:
            from image_preprocessing import preprocess_image_simple
            img_for_ocr = Image.open(file_path)
            processed_img = preprocess_image_simple(img_for_ocr)
        except Exception as e:
            text_original.delete("1.0", tk.END)
            text_original.insert(tk.END, f"Lỗi tiền xử lý ảnh: {e}")
            return
    except Exception as e:
        text_original.delete("1.0", tk.END)
        text_original.insert(tk.END, f"Lỗi tiền xử lý ảnh: {e}")
        return

    # 4. OCR
    extracted_text = None
    try:
        # Sử dụng ảnh đã được tiền xử lý
        raw_text = pytesseract.image_to_string(processed_img, lang='eng')
        # Làm sạch text: chỉ xuống dòng khi có dấu kết thúc câu
        extracted_text = clean_text_format(raw_text)

        text_original.delete("1.0", tk.END)
        if not extracted_text.strip():
            text_original.insert(tk.END, "Không phát hiện được văn bản nào.")
            text_translated.delete("1.0", tk.END)
            return
        else:
            text_original.insert(tk.END, extracted_text)

    except Exception as e:
        text_original.delete("1.0", tk.END)
        text_original.insert(tk.END, f"Lỗi OCR: {e}\n\nVui lòng kiểm tra:\n1. Tesseract OCR đã được cài đặt\n2. Đường dẫn Tesseract đúng trong code")
        text_translated.delete("1.0", tk.END)
        return

    # 5. Dịch
    if extracted_text:  # Chỉ dịch nếu OCR thành công
        try:
            raw_translated = GoogleTranslator(source='auto', target='vi').translate(extracted_text)
            # Áp dụng cùng cách làm sạch cho bản dịch
            translated = clean_text_format(raw_translated)

            text_translated.delete("1.0", tk.END)
            text_translated.insert(tk.END, translated)
            notebook.select(tab_translated)  # Tự động chuyển sang tab dịch

        except Exception as e:
            text_translated.delete("1.0", tk.END)
            text_translated.insert(tk.END, f"Lỗi dịch: {e}\n\nCó thể do mất kết nối internet hoặc API Google Translate có vấn đề.")


# --- Thiết kế Giao diện (GUI) ---
root = tk.Tk()
root.title("Chương trình OCR và Dịch thuật")
root.geometry("1000x650")  # Kích thước cửa sổ lớn hơn
root.resizable(False, False)

# Sử dụng style của ttk
style = ttk.Style(root)

# === THAY ĐỔI DUY NHẤT Ở ĐÂY ===
# Đổi 'vista' thành 'clam' để cho phép tùy chỉnh màu nút
style.theme_use('clam')
# ================================

# --- Khung chính chia 2 cột ---
main_frame = ttk.Frame(root, padding="10 10 10 10")
main_frame.pack(fill="both", expand=True)

# Cấu hình grid cho 2 cột cân đối
main_frame.columnconfigure(0, weight=1)  # Cột trái
main_frame.columnconfigure(1, weight=1)  # Cột phải
main_frame.rowconfigure(0, weight=1)

# --- CỘT TRÁI (Ảnh và Nút) ---
left_frame = ttk.Frame(main_frame, padding="10")
left_frame.grid(row=0, column=0, sticky="nsew", padx=10)

btn_load = ttk.Button(
    left_frame,
    text="📂 Chọn ảnh để trích xuất & dịch",
    command=process_image_and_translate,
    style="Accent.TButton"  # Style cho nút nổi bật
)
btn_load.pack(pady=10, fill="x", ipady=10)  # ipady = padding bên trong nút

# Style này giờ sẽ hoạt động với theme 'clam'
# Mã màu #4CAF50 chính là màu xanh lá trong hình bạn gửi
style.configure("Accent.TButton", font=("Arial", 12, "bold"), foreground="white", background="#4CAF50")
# Thêm style khi di chuột vào
style.map("Accent.TButton",
          background=[('active', '#45a049')]  # Màu xanh đậm hơn khi nhấn
          )

image_label = ttk.Label(
    left_frame,
    text="Chưa chọn ảnh",
    anchor="center",
    background="#ffffff",
    relief="solid",
    borderwidth=1
)
image_label.pack(pady=10, fill="both", expand=True)

# --- CỘT PHẢI (Tabs Văn bản) ---
right_frame = ttk.Frame(main_frame)
right_frame.grid(row=0, column=1, sticky="nsew", padx=10)

# Tạo Notebook (Tabs)
notebook = ttk.Notebook(right_frame)
notebook.pack(fill="both", expand=True, pady=10)

# Khung cho tab 1
tab_original = ttk.Frame(notebook, padding="10")
notebook.add(tab_original, text='📝 Văn bản gốc (OCR)')

text_original = ScrolledText(tab_original, height=15, width=60, wrap="word", font=("Arial", 10))
text_original.pack(fill="both", expand=True)

# Khung cho tab 2
tab_translated = ttk.Frame(notebook, padding="10")
notebook.add(tab_translated, text='🌐 Bản dịch tiếng Việt')

text_translated = ScrolledText(tab_translated, height=15, width=60, wrap="word", font=("Arial", 10), bg="#f9f9f9")
text_translated.pack(fill="both", expand=True)

# --- Khởi chạy ---
root.mainloop()