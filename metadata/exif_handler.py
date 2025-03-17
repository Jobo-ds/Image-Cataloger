# metadata/exif_handler.py 📝
from PIL import Image
import piexif
from utils.state import state

def get_exif_description(image_path):
	"""
	Extract EXIF description from an image. Returns an empty string if missing.
	"""
	try:
		with Image.open(image_path) as img:
			# Ensure the image has EXIF data
			exif_data = img.info.get("exif", b"")
			if not exif_data:
				return ""

			# Load EXIF data using piexif
			exif_dict = piexif.load(exif_data)
			description_bytes = exif_dict["0th"].get(piexif.ImageIFD.ImageDescription, b"")

			if not description_bytes:
				return ""

			# Decode EXIF description
			description = description_bytes.decode("utf-8", errors="ignore")
			return description
	except Exception as e:
		state.error_dialog.show(f"Could not read EXIF data.", "The exif data could be corrupted.", f"{e}")
		print(f"EXIF Read Error: {e}")
		return ""

def set_exif_description(image_path, description):
	"""
	Write EXIF description to an image, properly detecting existing EXIF data.
	"""
	try:
		with Image.open(image_path) as img:
			if img.format not in ["JPEG", "TIFF"]:  # EXIF is not supported in PNG
				return

			# Try loading EXIF data correctly
			try:
				exif_data = img.info.get("exif", None)
				exif_dict = piexif.load(exif_data) if exif_data else {"0th": {}, "Exif": {}, "Interop": {}, "GPS": {}, "1st": {}, "thumbnail": None}
			except Exception:
				exif_dict = {"0th": {}, "Exif": {}, "Interop": {}, "GPS": {}, "1st": {}, "thumbnail": None}

			# Ensure the description is bytes-encoded
			exif_dict["0th"][piexif.ImageIFD.ImageDescription] = description.encode("utf-8")

			# Convert the EXIF data back to bytes
			exif_bytes = piexif.dump(exif_dict)

			# Save the image with updated EXIF data
			img.save(image_path, exif=exif_bytes)

			print("EXIF metadata updated successfully!") 

	except Exception as e:
		state.error_dialog.show(f"Could not write EXIF data.", "The app was unable to save the EXIF data to the image.", f"{e}")
		print(f"EXIF Write Error: {e}")
