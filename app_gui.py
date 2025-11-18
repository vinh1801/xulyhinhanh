import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk
import pytesseract
import os
import re
from deep_translator import GoogleTranslator
from image_preprocessing import preprocess_image_for_ocr

tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    print(f"Cảnh báo: Không tìm thấy Tesseract tại {tesseract_path}")
    print("Vui lòng cài đặt Tesseract OCR hoặc cập nhật đường dẫn trong code.")

def clean_text_format(text):
    if not text:
        return ""
    
    lines = text.split('\n')
    cleaned_lines = [line.rstrip() for line in lines]
    
    while cleaned_lines and not cleaned_lines[0].strip():
        cleaned_lines.pop(0)
    while cleaned_lines and not cleaned_lines[-1].strip():
        cleaned_lines.pop()
    
    result = []
    i = 0
    
    while i < len(cleaned_lines):
        current_line = cleaned_lines[i].strip()
        
        if not current_line:
            result.append('')
            i += 1
            continue
        
        merged_line = current_line
        j = i + 1
        
        ends_with_punctuation = merged_line and merged_line[-1] in '.!?'
        
        if ends_with_punctuation:
            if j < len(cleaned_lines) and cleaned_lines[j].strip():
                result.append(merged_line)
                i = j
                continue
            else:
                result.append(merged_line)
                i += 1
                continue
        
        while j < len(cleaned_lines):
            next_line = cleaned_lines[j].strip()
            
            if not next_line:
                break
            
            merged_line = merged_line + ' ' + next_line
            
            if merged_line and merged_line[-1] in '.!?':
                if j + 1 < len(cleaned_lines) and cleaned_lines[j + 1].strip():
                    break
                else:
                    break
            
            j += 1
        
        result.append(merged_line)
        i = j + 1
    
    result = [re.sub(r' {2,}', ' ', line) for line in result]
    
    cleaned_text = '\n'.join(result)
    
    return cleaned_text

def process_image_and_translate():
    file_path = filedialog.askopenfilename(
        title="Chọn ảnh để OCR",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")]
    )

    if not file_path:
        return

    try:
        img = Image.open(file_path)
        img.thumbnail((450, 400))
        img_tk = ImageTk.PhotoImage(img)
        image_label.config(image=img_tk, text="")
        image_label.image = img_tk
    except Exception as e:
        text_original.delete("1.0", tk.END)
        text_original.insert(tk.END, f"Lỗi mở ảnh: {e}")
        return

    text_original.delete("1.0", tk.END)
    text_translated.delete("1.0", tk.END)

    text_original.insert(tk.END, "Đang xử lý OCR...")
    text_translated.insert(tk.END, "Đang dịch...")
    notebook.select(tab_original)
    root.update_idletasks()

    try:
        img_for_ocr = Image.open(file_path)
        processed_img = preprocess_image_for_ocr(img_for_ocr, auto_invert=True)
    except ImportError:
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

    extracted_text = None
    try:
        raw_text = pytesseract.image_to_string(processed_img, lang='eng')
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

    if extracted_text:
        try:
            raw_translated = GoogleTranslator(source='auto', target='vi').translate(extracted_text)
            translated = clean_text_format(raw_translated)

            text_translated.delete("1.0", tk.END)
            text_translated.insert(tk.END, translated)
            notebook.select(tab_translated)

        except Exception as e:
            text_translated.delete("1.0", tk.END)
            text_translated.insert(tk.END, f"Lỗi dịch: {e}\n\nCó thể do mất kết nối internet hoặc API Google Translate có vấn đề.")



root = tk.Tk()
root.title("Dịch Thuật Văn Bản Từ Hình Ảnh Nhóm 12")
root.geometry("1150x720")
root.configure(bg="#F0F0EE")
root.resizable(False, False)

# ========= HEADER ==========
header = tk.Frame(root, bg="#E5E5E3", height=90)
header.pack(fill="x")

title = tk.Label(
    header,
    text="DỊCH THUẬT VĂN BẢN TỪ HÌNH ẢNH",
    font=("Segoe UI", 22, "bold"),
    bg="#E5E5E3",
    fg="#333"
)
title.place(relx=0.5, rely=0.5, anchor="center")


# ========= MAIN FRAME ==========
main_container = tk.Frame(root, bg="#F0F0EE")
main_container.pack(fill="both", expand=True, pady=10)

# Căn giữa nội dung
main_container.grid_rowconfigure(0, weight=1)
main_container.grid_columnconfigure(0, weight=1)

main_frame = tk.Frame(main_container, bg="#F0F0EE")
main_frame.grid(row=0, column=0)

# Set tỉ lệ để trái & phải cân đối
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_columnconfigure(1, weight=1)

# ========= LEFT AREA (IMAGE + BUTTON) ==========
left_frame = tk.Frame(main_frame, bg="#F0F0EE")
left_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=20)

btn_load = tk.Button(
    left_frame,
    text="📂  Chọn ảnh để trích xuất & dịch",
    command=process_image_and_translate,
    bg="#4A90E2",
    fg="white",
    font=("Segoe UI", 12, "bold"),
    relief="flat",
    padx=10,
    pady=8
)
btn_load.pack(pady=(0, 20), fill="x")

image_label = tk.Label(
    left_frame,
    text="Chưa chọn ảnh",
    bg="white",
    fg="#555",
    relief="solid",
    borderwidth=1,
    font=("Segoe UI", 10),
    width=45,
    height=20
)
image_label.pack(fill="both", expand=True)


# ========= RIGHT AREA (NOTEBOOK) ==========
right_frame = tk.Frame(main_frame, bg="#F0F0EE")
right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

notebook = ttk.Notebook(right_frame)
notebook.pack(fill="both", expand=True)

# STYLE TAB
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TNotebook.Tab",
    padding=[15, 8],
    font=("Segoe UI", 11),
)
style.map(
    "TNotebook.Tab",
    background=[("selected", "#ffffff")],
    foreground=[("selected", "#000")]
)

# Tabs
tab_original = ttk.Frame(notebook)
tab_translated = ttk.Frame(notebook)

notebook.add(tab_original, text="📝  Văn bản gốc (OCR)")
notebook.add(tab_translated, text="🌐  Bản dịch tiếng Việt")

text_original = ScrolledText(tab_original, wrap="word",
                             font=("Segoe UI", 10), bg="#ffffff")
text_original.pack(fill="both", expand=True, padx=12, pady=12)

text_translated = ScrolledText(tab_translated, wrap="word",
                               font=("Segoe UI", 10), bg="#ffffff")
text_translated.pack(fill="both", expand=True, padx=12, pady=12)

root.mainloop()