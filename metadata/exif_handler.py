# metadata/exif_handler.py 📝
import piexif
from PIL import Image

def get_exif_description(image_path):
    """Extract EXIF description from an image."""
    try:
        img = Image.open(image_path)
        exif_data = piexif.load(img.info.get("exif", b""))
        description = exif_data["0th"].get(piexif.ImageIFD.ImageDescription, b"").decode("utf-8", errors="ignore")
        return description
    except Exception as e:
        print(f"EXIF Read Error: {e}")
        return ""

def set_exif_description(image_path, description):
    """Write EXIF description (ASCII only)."""
    try:
        img = Image.open(image_path)
        exif_data = piexif.load(img.info.get("exif", b""))

        exif_data["0th"][piexif.ImageIFD.ImageDescription] = description.encode("ascii", errors="ignore")

        exif_bytes = piexif.dump(exif_data)
        img.save(image_path, "jpeg", exif=exif_bytes)
    except Exception as e:
        print(f"EXIF Write Error: {e}")
