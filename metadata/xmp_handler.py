# metadata/xmp_handler.py 
import asyncio
import os
import sys
from utils.state import state
import exiftool
import unicodedata

async def get_xmp_description(image_path):
	"""
	Extract XMP description asynchronously using ExifTool.
	"""
	try:
		# Ensure the file actually exists before calling subprocess
		if not os.path.isfile(state.exiftool_path) or not os.path.isfile(image_path):
			raise FileNotFoundError(f"A required file was not found at either {state.exiftool_path} or {image_path}.")
		
		metadata = state.exiftool_process.get_tags(
			image_path, 
			["XMP-dc:Description"])
		# TODO: Consider getting all languages and implement language selection
		return metadata[0].get("Description", False)

	except Exception as e:
		state.error_dialog.show(
			"ExifTool Execution Failed",
			"An error occured when attemping to get the XMP Description through ExifTool.",
			str(e)
		)
		return ""
	except FileNotFoundError as e:
		state.error_dialog.show(
			"Missing required file.",
			"An error occured when attemping to get the XMP Description through ExifTool. Either ExifTool or the image file is missing.",
			str(e)
		)


async def set_xmp_description(image_path, new_description:str):
	"""
	Modify XMP description asynchronously using ExifTool.
	"""

	try:
		# Ensure the file actually exists before calling subprocess
		if not os.path.isfile(state.exiftool_path) or not os.path.isfile(image_path):
			raise FileNotFoundError(f"A required file was not found at either {state.exiftool_path} or {image_path}.")

		metadata_json = {
			"XMP-dc:Description": new_description
		}


		state.exiftool_process.set_tags(
			image_path, 
			tags_dict=metadata_json,
			extra_args=["-charset UTF8", "-overwrite_original"])
		return True

	except Exception as e:
		state.error_dialog.show(
			"ExifTool Execution Failed",
			"An error occured when attemping to set the XMP Description through ExifTool.",
			str(e)
		)
		return False
	except FileNotFoundError as e:
		state.error_dialog.show(
			"Missing required file.",
			"An error occured when attemping to set the XMP Description through ExifTool. Either ExifTool or the image file is missing.",
			str(e)
		)
		return False
