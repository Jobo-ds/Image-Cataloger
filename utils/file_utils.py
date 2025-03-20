# utils/file_utils.py
import asyncio
import base64
import concurrent.futures
from nicegui import ui
from pathlib import Path
from PIL import Image
from metadata.exif_handler import get_exif_description
from metadata.xmp_handler import get_xmp_description
from utils.dev_tools import display_memory_usage, async_measure_execution_time
from utils.string_utils import convert_to_ascii
from utils.state import state
from io import BytesIO
import config
import tkinter as tk
from tkinter import filedialog

async def open_image():
	"""
	Asynchronously opens a file dialog and loads the selected image.
	"""
	async with state.nav_lock:
		loop = asyncio.get_event_loop()

		# Run the file dialog in a separate thread (since Tkinter is blocking)
		def select_file():
			root = tk.Tk()
			root.withdraw()
			root.attributes('-topmost', True)
			file_path = filedialog.askopenfilename(
				title="Select an Image",
				filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.tiff;*.tif")]
			)
			root.destroy()
			return file_path

		file_path = await loop.run_in_executor(None, select_file)

		if not file_path:
			print("No file selected.")
			return


		# Cancel previous image loading task if it's still running
		if state.latest_image_task:
			state.latest_image_task.cancel()
			try:
				await state.latest_image_task  # Wait for it to cancel properly
			except asyncio.CancelledError:
				pass
			except Exception as e:
				state.error_dialog.show(
					"Error cancelling previous image",
					"Something went wrong when stopping the previous image load. Please try again.",
					f"{e}"
				)

		# Prepare indexing of images
		folder = Path(file_path).parent		
		state.nav_folder = folder
		state.nav_img_list = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg")) + sorted(folder.glob("*.png")) + sorted(folder.glob("*.tiff")) + sorted(folder.glob("*.tif"))
		print(state.nav_img_list)
		state.nav_img_index = state.nav_img_list.index(Path(file_path))
		state.nav_img_total = len(state.nav_img_list)
		state.nav_txt = f"{state.nav_img_index + 1} / {state.nav_img_total}"
		state.nav_counter.refresh()
		# Start loading new image
		state.latest_image_task = asyncio.create_task(load_image(Path(file_path)))


async def load_image(image_path):
	"""
	Loads an image, using the buffer if available, and extracts metadata.
	"""
	try:
		# Image buffering
		state.current_image = image_path

		# Activate Spinners
		state.image_spinner.show()
		state.editor_spinner.show()

		# Check if image actually exists.
		image_path = Path(image_path)
		if not await asyncio.to_thread(image_path.exists):
			state.error_dialog.show(
				"File does not exist.", 
				"Confirm the image file exists, and try again.")
			state.image_spinner.hide()
			state.editor_spinner.hide()
			return

		# Start getting Metadata
		metadata_task = asyncio.create_task(extract_metadata(image_path))

		# Process image or use buffer
		cache_task = None # For the asyncio.gather.
		if image_path not in state.image_cache:
			cache_task = asyncio.create_task(cache_image(image_path))

		tasks = [metadata_task]
		if cache_task:
			tasks.append(cache_task)

		await asyncio.gather(*tasks)
		await asyncio.gather(display_image(state.image_cache[image_path]), display_metadata())
	except Exception as e:
		state.error_dialog.show(
			f"Could not load image.", 
			"Please try again, and confirm the image works in a different program.", 
			f"{e}")
	finally:
		state.nav_counter.refresh()
		state.image_spinner.hide()
		state.editor_spinner.hide()

async def cache_image(image_path):
	"""
	Quickly converts the image to a compressed in-memory JPG Base64 string for NiceGUI.
	"""
	try:
		with Image.open(image_path) as img:
			if img.mode != "RGB":
				img = img.convert("RGB")
			img_io = BytesIO()
			img.save(img_io, format="JPEG", quality=50)  # Compress for low memory
			img_io.seek(0)

			# Convert to Base64 for nicegui
			base64_str = base64.b64encode(img_io.getvalue()).decode("utf-8")
			base64_image = f"data:image/jpeg;base64,{base64_str}"

			# Store in the buffer (Remove oldest if full)
			if len(state.image_cache) >= config.IMAGE_CACHE_SIZE:
				state.image_cache.popitem(last=False)  # Remove the oldest entry

			# Cache the image in buffer
			state.image_cache[image_path] = base64_image

	except Exception as e:
		state.error_dialog.show(
			f"Could not process {image_path.name} for app.", 
			"Please try again, and confirm the image works in a different program.", 
			f"{e}")

async def display_image(cached_image):
	"""
	Updates the UI with the processed image and hides the spinner.
	"""

	if not cached_image:
		state.error_dialog.show(
			"Could not display image",
			"No image data was found."
		)
		return
	try:
		if state.image_display:
			state.image_display.set_source(cached_image)
		else:
			print("Warning: Image display UI not initialized yet.")
	except Exception as e:
		state.error_dialog.show(
			f"Could not display image.", 
			"Please try again, and confirm the image works in a different program.", 
			f"{e}")

async def extract_metadata(image_path):
	"""
	Extracts EXIF/XMP metadata and updates the UI in the background.
	"""
	try:
		# Reset buffers
		state.xmp_buffer = None
		state.exif_buffer = None
		state.input_buffer = None
		state.original_metadata = None
		
		# Get file extension in lowercase
		extension = image_path.suffix.lower()

		# Define supported formats
		supported_exif = {".jpg", ".jpeg", ".tiff", ".tif"}  # EXIF supported formats
		supported_xmp = {".jpg", ".jpeg", ".tiff", ".tif", ".png"}  # XMP supported formats

		if extension in supported_xmp:
			state.xmp_buffer = await get_xmp_description(image_path)
		if extension in supported_exif:
			state.exif_buffer = await get_exif_description(image_path)

		# Set input buffer
		if state.xmp_buffer:
			state.input_buffer = state.xmp_buffer
		elif state.exif_buffer:
			state.input_buffer = convert_to_ascii(state.exif_buffer)
		else:
			state.input_buffer = ""

	except Exception as e:
		state.error_dialog.show(
			f"Unable to extract metadata", 
			"The app was not able to extract the EXIF or XMP data from this image.", 
			f"{e}")
		
async def display_metadata():
	# XMP Field
	if state.xmp_buffer:
		state.metadata_xmp.value = state.xmp_buffer
		state.metadata_xmp.classes(remove="text-italic")
	else:
		state.metadata_xmp.value = "No XMP metadata found."
		state.metadata_xmp.classes(add="text-italic")
	
	# EXIF Field
	if state.exif_buffer:
		state.metadata_exif.value = state.exif_buffer
		state.metadata_exif.classes(remove="text-italic")
	else:
		state.metadata_exif.value = "No EXIF metadata found."
		state.metadata_exif.classes(add="text-italic")

	# Input Field
	state.metadata_input.value = state.input_buffer
	state.original_metadata = state.metadata_input.value

	# Update UI
	ui.update(state.metadata_input)
	ui.update(state.metadata_exif)
	ui.update(state.metadata_xmp)
