# metadata/exif_handler.py 
import asyncio
import os
import sys
from utils.state import state
import exiftool

async def get_exif_description(image_path):
	"""
	Extract EXIF description asynchronously using ExifTool.
	"""
	try:
		if state.exiftool_process is None:
			state.exiftool_process = exiftool.ExifToolHelper(executable=str(state.exiftool_path))

		# Ensure the file actually exists before calling subprocess
		if not os.path.isfile(state.exiftool_path) or not os.path.isfile(image_path):
			raise FileNotFoundError(f"A required file was not found at either {state.exiftool_path} or {image_path}.")

		metadata = state.exiftool_process.get_tags(image_path, ["EXIF:ImageDescription"])
		return metadata[0].get("ImageDescription", False)

	except Exception as e:
		state.error_dialog.show(
			"ExifTool Execution Failed",
			"An error occured when attemping to get the EXIF ImageDescription through ExifTool.",
			str(e)
		)
	except FileNotFoundError as e:
		state.error_dialog.show(
			"Missing required file.",
			"An error occured when attemping to get the EXIF ImageDescription through ExifTool. Either ExifTool or the image file is missing.",
			str(e)
		)


async def set_exif_description(image_path, new_description:str):
	"""
	Modify EXIF description asynchronously using ExifTool.
	"""

	try:

		if state.exiftool_process is None:
			state.exiftool_process = exiftool.ExifToolHelper(executable=str(state.exiftool_path))

		# Ensure the file actually exists before calling subprocess
		if not os.path.isfile(state.exiftool_path) or not os.path.isfile(image_path):
			raise FileNotFoundError(f"A required file was not found at either {state.exiftool_path} or {image_path}.")

		metadata_json = {
			"EXIF:ImageDescription": new_description[0:254]
		}

		state.exiftool_process.set_tags(
			image_path, 
			tags_dict=metadata_json,
			extra_args=["-charset", "utf8", "-overwrite_original"])
		return True

	except Exception as e:
		state.error_dialog.show(
			"ExifTool Execution Failed",
			"An error occured when attemping to set the EXIF ImageDescription through ExifTool.",
			str(e)
		)
		return ""
	except FileNotFoundError as e:
		state.error_dialog.show(
			"Missing required file.",
			"An error occured when attemping to set the EXIF ImageDescription through ExifTool. Either ExifTool or the image file is missing.",
			str(e)
		)
