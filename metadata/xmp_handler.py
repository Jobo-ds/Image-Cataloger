# metadata/xmp_handler.py 📝
import asyncio
import os
import sys
from utils.state import state  # Import your error dialog system

async def get_xmp_description(image_path):
	"""Extract XMP description asynchronously using the bundled ExifTool."""

	try:
		process = await asyncio.create_subprocess_exec(
			state.exiftool_path, "-XMP-dc:Description", "-b", image_path,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE
		)
		
		stdout, stderr = await process.communicate()
		
		if process.returncode != 0:
			error_message = stderr.decode().strip()
			state.error_dialog.show(
				"Could not read XMP data.",
				"An error occurred while reading the XMP metadata. Please check if the file is valid.",
				error_message
			)
			return None

		return stdout.decode().strip()

	except Exception as e:
		state.error_dialog.show(
			"ExifTool Execution Failed (XMP)",
			"Could not execute ExifTool to read XMP description. Ensure the bundled ExifTool is present and accessible.",
			str(e)
		)
		return None

async def set_xmp_description(image_path, new_description):
	"""Modify XMP description asynchronously using the bundled ExifTool."""

	try:
		process = await asyncio.create_subprocess_exec(
			state.exiftool_path, f"-XMP-dc:Description={new_description}", "-overwrite_original", image_path,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE
		)
		
		stdout, stderr = await process.communicate()

		if process.returncode != 0:
			error_message = stderr.decode().strip()
			state.error_dialog.show(
				"Could not write XMP data.",
				"An error occurred while modifying the XMP metadata. Please check if the file is valid and not locked.",
				error_message
			)
			return False

		return True

	except Exception as e:
		state.error_dialog.show(
			"ExifTool Execution Failed (XMP)",
			"Could not execute ExifTool to set XMP description. Ensure the bundled ExifTool is present and accessible.",
			str(e)
		)
		return False
