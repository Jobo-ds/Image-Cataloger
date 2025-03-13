# metadata/xmp_handler.py 📜
import re
from PIL import Image

def get_xmp_description(image_path):
    """Extracts XMP metadata from an image."""
    try:
        img = Image.open(image_path)
        xmp_data = img.info.get("XML:com.adobe.xmp", "")
        match = re.search(r'<dc:description><rdf:Alt><rdf:li.*?>(.*?)</rdf:li>', xmp_data)
        return match.group(1) if match else ""
    except Exception as e:
        print(f"XMP Read Error: {e}")
        return ""

def set_xmp_description(image_path, description):
    """Writes XMP description (Unicode supported)."""
    try:
        img = Image.open(image_path)
        xmp_template = f"""<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>
        <x:xmpmeta xmlns:x="adobe:ns:meta/">
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
        <rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:description><rdf:Alt><rdf:li xml:lang="x-default">{description}</rdf:li></rdf:Alt></dc:description>
        </rdf:Description></rdf:RDF></x:xmpmeta>"""
        
        img.save(image_path, "jpeg", icc_profile=img.info.get("icc_profile", ""), exif=img.info.get("exif", b""), xmp=xmp_template)
    except Exception as e:
        print(f"XMP Write Error: {e}")
