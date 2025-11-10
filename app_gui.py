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
root.title("Chương trình OCR và Dịch thuật")
root.geometry("1000x650")
root.resizable(False, False)

style = ttk.Style(root)

style.theme_use('clam')

main_frame = ttk.Frame(root, padding="10 10 10 10")
main_frame.pack(fill="both", expand=True)

main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)

left_frame = ttk.Frame(main_frame, padding="10")
left_frame.grid(row=0, column=0, sticky="nsew", padx=10)

btn_load = ttk.Button(
    left_frame,
    text="📂 Chọn ảnh để trích xuất & dịch",
    command=process_image_and_translate,
    style="Accent.TButton"
)
btn_load.pack(pady=10, fill="x", ipady=10)

style.configure("Accent.TButton", font=("Arial", 12, "bold"), foreground="white", background="#4CAF50")
style.map("Accent.TButton",
          background=[('active', '#45a049')]
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

right_frame = ttk.Frame(main_frame)
right_frame.grid(row=0, column=1, sticky="nsew", padx=10)

notebook = ttk.Notebook(right_frame)
notebook.pack(fill="both", expand=True, pady=10)

tab_original = ttk.Frame(notebook, padding="10")
notebook.add(tab_original, text='📝 Văn bản gốc (OCR)')

text_original = ScrolledText(tab_original, height=15, width=60, wrap="word", font=("Arial", 10))
text_original.pack(fill="both", expand=True)

tab_translated = ttk.Frame(notebook, padding="10")
notebook.add(tab_translated, text='🌐 Bản dịch tiếng Việt')

text_translated = ScrolledText(tab_translated, height=15, width=60, wrap="word", font=("Arial", 10), bg="#f9f9f9")
text_translated.pack(fill="both", expand=True)

root.mainloop()