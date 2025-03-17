# metadata/exif_handler.py 
import asyncio
import os
import sys
from utils.state import state

async def get_exif_description(image_path):
	"""
	Extract EXIF description asynchronously using ExifTool.
	"""
	try:
		exiftool_path = os.path.abspath(state.exiftool_path)  # Ensure absolute path
		print(exiftool_path)

		# Ensure the file actually exists before calling subprocess
		if not os.path.isfile(exiftool_path):
			raise FileNotFoundError(f"ExifTool not found at {exiftool_path}")
		print(image_path)

		process = await asyncio.create_subprocess_exec(
			exiftool_path, "-EXIF:ImageDescription", "-b", image_path,
			stdin=asyncio.subprocess.DEVNULL,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE
		)
		stdout, stderr = await process.communicate()
		print("STDOUT:", stdout.decode().strip())
		print("STDERR:", stderr.decode().strip())

		if process.returncode != 0:
			print(f"ExifTool failed with code {process.returncode}")
			return "No data in ImageDescription tag."

		return stdout.decode().strip() or "No data in ImageDescription tag."

	except Exception as e:
		print(f"Error: {e}")  # Print error for debugging
		state.error_dialog.show(
			"ExifTool Execution Failed (Exif)",
			"Could not execute ExifTool and get ImageDescription from Exif. Ensure the bundled ExifTool is present and accessible.",
			str(e)
		)
		return ""


async def set_exif_description(image_path, new_description):
	"""
	Modify EXIF description asynchronously using ExifTool.
	"""

	try:
		process = await asyncio.create_subprocess_exec(
			state.exiftool_path, f"-EXIF:ImageDescription={new_description}", "-overwrite_original", str(image_path),
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE
		)
		stdout, stderr = await process.communicate()

		if process.returncode != 0:
			error_message = stderr.decode().strip()
			state.error_dialog.show(
				"Could not write EXIF data.",
				"An error occurred while modifying the EXIF metadata. Please check if the file is valid and not locked.",
				error_message
			)
			return False

		return True

	except Exception as e:
		state.error_dialog.show(
			"ExifTool Execution Failed",
			"Could not execute ExifTool and write ImageDescription to Exif. Ensure the bundled ExifTool is present and accessible.",
			str(e)
		)
		return False
