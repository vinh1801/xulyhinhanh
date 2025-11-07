"""
Module tiền xử lý ảnh trước OCR
Chứa các hàm xử lý ảnh để cải thiện độ chính xác OCR
"""
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


def preprocess_image_for_ocr(img, auto_invert=True):
    """
    Tiền xử lý ảnh để cải thiện độ chính xác OCR
    
    Các bước xử lý:
    1. Convert sang grayscale
    2. Tự động phát hiện và đảo ngược màu nếu chữ sáng trên nền tối
    3. Denoise (giảm nhiễu)
    4. Tăng độ tương phản (CLAHE)
    5. Adaptive Thresholding (chuyển sang binary)
    6. Morphology operations (làm sạch văn bản)
    
    Args:
        img (PIL.Image): Ảnh đầu vào
        auto_invert (bool): Tự động đảo ngược màu nếu phát hiện chữ sáng trên nền tối
        
    Returns:
        PIL.Image: Ảnh đã được tiền xử lý
    """
    # Convert PIL Image sang numpy array
    img_array = np.array(img)
    
    # 1. Convert sang grayscale nếu là ảnh màu
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    # 2. Tự động phát hiện và đảo ngược màu nếu chữ sáng trên nền tối
    if auto_invert:
        # Tính toán mean của pixel values
        mean_value = np.mean(gray)
        # Nếu mean > 127 (nền sáng, chữ tối) thì không cần đảo
        # Nếu mean < 127 (nền tối, chữ sáng) thì đảo ngược
        if mean_value < 127:
            gray = cv2.bitwise_not(gray)  # Đảo ngược: chữ sáng -> chữ tối
    
    # 3. Denoise: Giảm nhiễu bằng Median Blur
    denoised = cv2.medianBlur(gray, 3)
    
    # 4. Tăng độ tương phản bằng CLAHE (trước khi thresholding)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    # 5. Adaptive Thresholding: Chuyển sang binary (đen-trắng)
    # Sử dụng adaptive threshold để xử lý ảnh có ánh sáng không đều
    binary = cv2.adaptiveThreshold(
        enhanced, 
        255,  # Max value
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # Adaptive method
        cv2.THRESH_BINARY,  # Threshold type
        11,  # block size - kích thước vùng để tính toán threshold
        2    # C constant - giá trị trừ đi từ mean
    )
    
    # 6. Morphology: Loại bỏ nhiễu nhỏ và làm đậm văn bản
    kernel = np.ones((1, 1), np.uint8)
    processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    # Convert lại sang PIL Image
    processed_img = Image.fromarray(processed)
    
    return processed_img


def preprocess_image_for_ocr_advanced(img):
    """
    Phiên bản nâng cao với nhiều phương pháp xử lý
    
    Thử nhiều cách và chọn kết quả tốt nhất
    """
    results = []
    
    # Phương pháp 1: Không đảo màu
    img1 = preprocess_image_for_ocr(img, auto_invert=False)
    results.append(("Normal", img1))
    
    # Phương pháp 2: Tự động đảo màu
    img2 = preprocess_image_for_ocr(img, auto_invert=True)
    results.append(("Auto-invert", img2))
    
    # Phương pháp 3: Thử cả 2 và chọn dựa trên độ tương phản
    # (Bạn có thể mở rộng để tự động chọn kết quả tốt nhất)
    
    # Trả về phương pháp auto-invert (thường tốt hơn)
    return img2


def preprocess_image_simple(img):
    """
    Phiên bản tiền xử lý đơn giản hơn (nếu không có OpenCV)
    
    Args:
        img (PIL.Image): Ảnh đầu vào
        
    Returns:
        PIL.Image: Ảnh đã được tiền xử lý
    """
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
    
    # Tăng độ tương phản
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)  # Tăng contrast 1.5 lần
    
    # Làm sắc nét
    img = img.filter(ImageFilter.SHARPEN)
    
    return img