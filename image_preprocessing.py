import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


def preprocess_image_for_ocr(img, auto_invert=True):
    img_array = np.array(img)
    
    width, height = img.size
    if width < 300 or height < 300:
        new_size = (width * 2, height * 2)
        img = img.resize(new_size, Image.LANCZOS)
        img_array = np.array(img)
    
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    if auto_invert:
        mean_value = np.mean(gray)
        if mean_value < 127:
            gray = cv2.bitwise_not(gray)
    
    processed_img = Image.fromarray(gray)
    
    return processed_img


def preprocess_image_gentle(img):
    img_array = np.array(img)
    
    width, height = img.size
    if width < 300 or height < 300:
        img = img.resize((width * 2, height * 2), Image.LANCZOS)
        img_array = np.array(img)
    
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    clahe = cv2.createCLAHE(clipLimit=1.2, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    processed_img = Image.fromarray(enhanced)
    
    return processed_img


def preprocess_image_for_ocr_advanced(img):
    img1 = preprocess_image_gentle(img)
    
    img2 = preprocess_image_for_ocr(img, auto_invert=True)
    
    return img2


def preprocess_image_simple(img):
    width, height = img.size
    if width < 300 or height < 300:
        img = img.resize((width * 2, height * 2), Image.LANCZOS)
    
    if img.mode != 'L':
        img = img.convert('L')
    
    img_array = np.array(img)
    mean_value = np.mean(img_array)
    if mean_value < 127:
        img_array = 255 - img_array
        img = Image.fromarray(img_array)
    
    return img