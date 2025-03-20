from utils.state import state, notify
from utils.string_utils import convert_to_ascii
from utils.file_utils import cache_image, extract_metadata, display_metadata
from metadata.exif_handler import set_exif_description
from metadata.xmp_handler import set_xmp_description
from nicegui import ui
import asyncio


async def save_metadata_queue():
	"""
	Background task to process metadata save requests.
	"""
	while True:
		try:
			undo = await state.save_queue.get()

			# No image loaded.
			if not state.current_image:
				state.save_queue.task_done()
				continue

			# Disable input field during saving.
			state.metadata_input.props(add="disable readonly")
			state.editor_spinner.show()
			# Get file extension in lowercase
			extension = state.current_image.suffix.lower()

			# Define supported formats, so we don't try to add meta data to unsupported files.
			supported_exif = {".jpg", ".jpeg", ".tiff", ".tif"}  # EXIF supported formats
			supported_xmp = {".jpg", ".jpeg", ".tiff", ".tif", ".png"}  # XMP supported formats

			save_xmp = False
			save_exif = False
			xmp_save_check = False
			exif_save_check = False			

			if extension in supported_xmp:
				save_xmp = True
			if extension in supported_exif:
				save_exif = True

			new_description = str(state.metadata_input.value)

			if undo and new_description == state.original_metadata:
				notify("Nothing to undo.")

			elif undo:
				state.metadata_input.value = state.original_metadata
			
			try:
				if save_xmp:
					xmp_save_check = await set_xmp_description(state.current_image, state.original_metadata)
				
				if save_exif:
					exif_save_check = await set_exif_description(state.current_image, convert_to_ascii(state.original_metadata))

				warnings = []
				if not xmp_save_check and save_xmp:
					warnings.append("XMP metadata")
				if not exif_save_check and save_exif:
					warnings.append("EXIF metadata")

				if warnings:
					notify(f"{', '.join(warnings)} could not be saved.", "warning")
				else:
					notify("Metadata saved successfully!", "positive")				

			except Exception as e:
				state.error_dialog.show(
					"Metadata could not be saved.", 
					"An error occurred while saving the metadata, try again or reload the image.", 
					f"{e}")

			finally:
					await extract_metadata
					await display_metadata
					state.metadata_input.props(remove="disable readonly")
					state.editor_spinner.hide()
					state.save_queue.task_done()
					

		except Exception as e:
			state.error_dialog(
				"App has crashed (Critical)",
				"The background task for saving metadata has crashed. Please restart the app.",
				{e}
			)
			break  # Prevent infinite errors if something goes wrong

async def start_cache_worker():
	"""Ensure the cache worker is running."""
	if state.bg_cache_task is None or state.bg_cache_task.done():
		state.bg_cache_task = asyncio.create_task(cache_worker())
		
async def cache_worker():
	"""
	Background task that processes cache requests sequentially.
	"""
	while True:
		img_path = await state.cache_queue.get()
		if img_path is None:
			break  # Exit gracefully if we enqueue None as a stop signal
		try:
			await asyncio.get_running_loop().run_in_executor(state.cache_executor, cache_image, img_path)
		except Exception as e:
			print(f"Error caching image {img_path}: {e}")
		state.cache_queue.task_done()