"""
Module tiền xử lý ảnh trước OCR
Chứa các hàm xử lý ảnh để cải thiện độ chính xác OCR
"""
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


def preprocess_image_for_ocr(img, auto_invert=True):
    """
    Tiền xử lý ảnh đơn giản để OCR dễ đọc hơn
    - Chữ tối nền sáng: giữ nguyên
    - Chữ sáng nền tối: đảo lại
    - Giữ nguyên bố cục, không làm mất chi tiết
    
    Args:
        img (PIL.Image): Ảnh đầu vào
        auto_invert (bool): Tự động đảo ngược màu nếu phát hiện chữ sáng trên nền tối
        
    Returns:
        PIL.Image: Ảnh đã được tiền xử lý
    """
    # Convert PIL Image sang numpy array
    img_array = np.array(img)
    
    # 1. Scale up ảnh nếu quá nhỏ (Tesseract hoạt động tốt hơn với ảnh lớn)
    # Nhưng chỉ scale nếu thực sự cần, để giữ nguyên bố cục
    width, height = img.size
    if width < 300 or height < 300:
        new_size = (width * 2, height * 2)
        img = img.resize(new_size, Image.LANCZOS)
        img_array = np.array(img)
    
    # 2. Convert sang grayscale nếu là ảnh màu
    # Tesseract hoạt động tốt với grayscale
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    # 3. Tự động phát hiện và đảo ngược màu nếu chữ sáng trên nền tối
    # Chỉ làm điều này để OCR có thể đọc được
    if auto_invert:
        mean_value = np.mean(gray)
        # Nếu mean < 127: nền tối, chữ sáng -> cần đảo
        # Nếu mean >= 127: nền sáng, chữ tối -> giữ nguyên
        if mean_value < 127:
            gray = cv2.bitwise_not(gray)  # Đảo ngược: chữ sáng -> chữ tối
    
    # KHÔNG làm gì thêm: không blur, không CLAHE, không thresholding, không morphology
    # Để giữ nguyên bố cục và chi tiết của ảnh gốc
    
    # Convert lại sang PIL Image
    processed_img = Image.fromarray(gray)
    
    return processed_img


def preprocess_image_gentle(img):
    """
    Tiền xử lý nhẹ nhàng - chỉ cải thiện chất lượng cơ bản
    Phù hợp với ảnh đã có chất lượng tốt hoặc ảnh scan
    """
    img_array = np.array(img)
    
    # Scale up nếu ảnh nhỏ
    width, height = img.size
    if width < 300 or height < 300:
        img = img.resize((width * 2, height * 2), Image.LANCZOS)
        img_array = np.array(img)
    
    # Convert sang grayscale
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    # Chỉ tăng độ tương phản nhẹ
    clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Chuyển sang PIL Image
    processed_img = Image.fromarray(enhanced)
    
    return processed_img


def preprocess_image_for_ocr_advanced(img):
    """
    Phiên bản nâng cao: thử nhiều phương pháp và chọn tốt nhất
    """
    # Phương pháp 1: Tiền xử lý nhẹ (khuyến nghị)
    img1 = preprocess_image_gentle(img)
    
    # Phương pháp 2: Tiền xử lý không binary
    img2 = preprocess_image_for_ocr(img, auto_invert=True)
    
    # Trả về phương pháp đơn giản nhất
    return img2


def preprocess_image_simple(img):
    """
    Phiên bản tiền xử lý đơn giản hơn (nếu không có OpenCV)
    Chỉ làm những gì cần thiết: scale, grayscale, invert nếu cần
    """
    # Scale up nếu ảnh nhỏ
    width, height = img.size
    if width < 300 or height < 300:
        img = img.resize((width * 2, height * 2), Image.LANCZOS)
    
    # Convert sang grayscale
    if img.mode != 'L':
        img = img.convert('L')
    
    # Kiểm tra nếu cần đảo ngược màu (chữ sáng trên nền tối)
    img_array = np.array(img)
    mean_value = np.mean(img_array)
    if mean_value < 127:
        # Đảo ngược màu: chữ sáng -> chữ tối
        img_array = 255 - img_array
        img = Image.fromarray(img_array)
    
    # KHÔNG làm gì thêm để giữ nguyên bố cục
    
    return img