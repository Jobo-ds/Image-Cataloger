import time
import cv2
from PIL import Image
from io import BytesIO
import numpy as np
from utils.dev_tools import measure_execution_time
import base64

image_path = r"test_files\\jpg_large_file.jpg"  # Replace with an actual image

def process_with_pil(image_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img_io = BytesIO()
        img.save(img_io, format="JPEG", quality=50)
        return img_io.getvalue()

def process_with_pil_resize(image_path, max_width=1024):
    """
    Optimized image processing with PIL:
    - Resizes large images for better performance.
    - Converts to RGB.
    - Saves as compressed JPEG in memory.
    """
    with Image.open(image_path) as img:
        img = img.convert("RGB")  # Ensure RGB format
        
        # ✅ Resize image if it's larger than max_width
        w, h = img.size
        if w > max_width:
            scale = max_width / w
            new_size = (int(w * scale), int(h * scale))
            img = img.resize(new_size, Image.LANCZOS)  # ✅ High-quality downscaling
        
        # ✅ Save to in-memory buffer
        img_io = BytesIO()
        img.save(img_io, format="JPEG", quality=50, optimize=True)  # ✅ Optimize compression
        return img_io.getvalue()


def process_with_opencv(image_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    success, img_encoded = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
    return img_encoded.tobytes() if success else None

def process_image_opencv_mozjpeg(image_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # MozJPEG optimized encoding
    success, img_encoded = cv2.imencode(
        ".jpg", img,
        [cv2.IMWRITE_JPEG_QUALITY, 50, cv2.IMWRITE_JPEG_PROGRESSIVE, 1]
    )
    
    return f"data:image/jpeg;base64,{base64.b64encode(img_encoded.tobytes()).decode()}" if success else None

def process_image_resized(image_path, max_width=800):
    img = cv2.imread(image_path)
    h, w = img.shape[:2]

    if w > max_width:
        scale = max_width / w
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

    success, img_encoded = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 50])
    return img_encoded.tobytes() if success else None


# Measure PIL
_, pil_time = measure_execution_time(process_with_pil, image_path)
# Measure Pil (resize)
_, Pil_reize = measure_execution_time(process_with_pil_resize, image_path)
# Measure OpenCV
_, opencv_time = measure_execution_time(process_with_opencv, image_path)
# Measure OpenCV (moz)
_, opencv_time_moz = measure_execution_time(process_image_opencv_mozjpeg, image_path)
# Measure OpenCV (resize)
_, opencv_time_resize = measure_execution_time(process_image_resized, image_path)



print(f"PIL Time: {pil_time:.6f} sec")
print(f"PIL Time (resize): {Pil_reize:.6f} sec")
print(f"OpenCV Time: {opencv_time:.6f} sec")
print(f"OpenCV Time (moz): {opencv_time_moz:.6f} sec")
print(f"OpenCV Time (resize): {opencv_time_resize:.6f} sec")