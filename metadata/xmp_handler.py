# metadata/xmp_handler.py 📝
from PIL import Image
import piexif
import io

def get_xmp_description(image_path):
	"""Extract XMP metadata from an image."""
	try:
		with Image.open(image_path) as img:
			xmp_data = img.info.get("xmp", b"").decode("utf-8", errors="ignore")
			return xmp_data
	except Exception as e:
		print(f"XMP Read Error: {e}")
		return ""

def set_xmp_description(image_path, description):
	"""Write XMP metadata to an image."""
	try:
		with Image.open(image_path) as img:
			# Ensure XMP data is properly encoded
			xmp_bytes = f'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF><rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:description>{description}</dc:description></rdf:Description></rdf:RDF></x:xmpmeta>'.encode("utf-8")

			# Save the image with updated XMP metadata
			new_img = io.BytesIO()
			img.save(new_img, format=img.format, xmp=xmp_bytes)

			# Overwrite the original image with the updated one
			with open(image_path, "wb") as f:
				f.write(new_img.getvalue())

	except Exception as e:
		print(f"XMP Write Error: {e}")
