# utils/file_utils.py
import asyncio
import base64
import concurrent.futures
import cv2
import tkinter as tk
from tkinter import filedialog

from nicegui import ui
from pathlib import Path
from PIL import Image
from io import BytesIO
import numpy as np

from metadata.exif_handler import get_exif_description
from metadata.xmp_handler import get_xmp_description
from utils.dev_tools import display_memory_usage, async_measure_execution_time
from utils.state import state
from utils.ui_helpers import resize_all_textareas
import config

def open_file_dialog():
	"""
	Create a file dialog in tkinter to select an image path.
	"""
	root = tk.Tk()
	root.withdraw()
	root.attributes('-topmost', True)
	file_path = filedialog.askopenfilename(
		title="Select an Image",
		filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.tiff;*.tif")]
	)
	root.destroy()
	return file_path

async def open_image():
	"""
	Open a file dialog and start loading an image
	"""
	file_path = await asyncio.get_event_loop().run_in_executor(None, open_file_dialog)
	if file_path:
		await load_initial_image(file_path)

async def load_initial_image(path: Path):
	"""
	Load the initial image, and then start caching.
	"""
	async with state.nav_lock:
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
		folder = Path(path).parent		
		state.nav_folder = folder
		state.nav_img_list = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg")) + sorted(folder.glob("*.png")) + sorted(folder.glob("*.tiff")) + sorted(folder.glob("*.tif"))
		state.nav_img_index = state.nav_img_list.index(Path(path))
		state.nav_img_total = len(state.nav_img_list)
		state.nav_txt = f"{state.nav_img_index + 1} / {state.nav_img_total}"
		state.nav_counter.refresh()

		# Immediately load and show the first image first!
		state.latest_image_task = asyncio.create_task(load_image(Path(path)))
		await state.latest_image_task
		state.image_display.classes(remove="w-1/6", add="w-full")
		state.meta_textarea_input.props(remove="readonly disable")

		# Queue background caching
		await update_cache_window(state.nav_img_index)		

async def load_image(image_path):
	"""
	Loads an image, using the buffer if available, and extracts metadata.
	"""
	try:
		state.current_image = image_path
		# Prepare indexing of images
		state.nav_img_index = state.nav_img_list.index(Path(image_path))
		state.nav_txt = f"{state.nav_img_index + 1} / {state.nav_img_total}"
		state.nav_counter.refresh()	

		# Activate Spinners
		state.image_spinner.show()
		state.editor_spinner.show()

		# Check if image actually exists.
		image_path = Path(image_path)
		if not await asyncio.to_thread(image_path.exists):
			state.error_dialog.show(
				"File does not exist.", 
				"Confirm the image file exists, and try again.")
			return

		# Start getting Metadata
		metadata_task = asyncio.create_task(extract_metadata(image_path))

		# Get cached image
		cached_image = state.image_cache.get(image_path)
		if cached_image is None:
			cache_task = asyncio.create_task(asyncio.to_thread(cache_image, image_path))
		else:
			cache_task = None

		tasks = [metadata_task]
		if cache_task:
			tasks.append(cache_task)

		await asyncio.gather(*tasks)
		cached_image = state.image_cache.get(image_path)
		await asyncio.gather(display_image(cached_image), display_metadata())
		state.nav_counter.refresh()
		state.image_spinner.hide()
		state.editor_spinner.hide()
		ui.update()

	except Exception as e:
		state.error_dialog.show(
			f"Could not load image.", 
			"Please try again, and confirm the image works in a different program.", 
			f"{e}")
	finally:
		state.image_spinner.hide()
		state.editor_spinner.hide()

def cache_image(image_path):
	"""
	Quickly converts the image to a compressed in-memory JPG Base64 string for NiceGUI.
	"""
	def safe_imread(path):
		try:
			data = np.fromfile(str(path), dtype=np.uint8)
			img = cv2.imdecode(data, cv2.IMREAD_COLOR)
			return img
		except Exception as e:
			state.error_dialog.show(
				f"safe_imread failed on {image_path.name}", 
				"Please try again, and confirm the image works in a different program.", 
				f"{e}")
			return None

	try:
		if image_path is None:
			raise ValueError("Attempted to read None Image.")
		
		img = safe_imread(image_path)
		if img is None:
			raise ValueError("Image could not be loaded by OpenCV.")
		
		height, width = img.shape[:2]

		scale = min(1.0, 1920 / max(height, width))
		if scale < 1.0:
			img = cv2.resize(img, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)

		success, jpeg_buf = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 60])
		if not success:
			raise ValueError("Failed to encode image.")
		
		base64_image = f"data:image/jpeg;base64,{base64.b64encode(jpeg_buf).decode('utf-8')}"
		state.image_cache.add(image_path, base64_image)

	except Exception as e:
		state.error_dialog.show(
			f"Could not process {image_path.name} for app.", 
			"Please try again, and confirm the image works in a different program.", 
			f"{e}")

def calculate_cache_indices(current_index: int, total_images: int, window_size: int = 25) -> set:
	"""
	Calculate indices for caching, handling wrap-around logic clearly.

	Args:
		current_index (int): The current index in the navigation.
		total_images (int): The total number of images in the current folder.
		window_size (int): Number of images to cache before and after current.

	Returns:
		set: A set of calculated indices for caching.
	"""
	indices = set()
	for offset in range(-window_size, window_size + 1):
		wrapped_index = (current_index + offset) % total_images
		indices.add(wrapped_index)
	return indices

async def update_cache_window(current_index: int, threshold: int = 10, window_size: int = 25):
	"""
	Updates image cache proactively around the current image index.

	Args:
		current_index (int): Current navigation index.
		threshold (int): Distance from last cached center to trigger re-caching.
		window_size (int): Images to cache on each side of the current index.
	"""
	total_images = state.nav_img_total
	image_list = state.nav_img_list

	# Check if caching is necessary
	if state.cached_center_index:
		distance_moved = abs(current_index - state.cached_center_index)
		if distance_moved < threshold:
			return
	
	state.cached_center_index = current_index

	# Calculate new indices
	new_indices = calculate_cache_indices(current_index, total_images, window_size)
	new_window_set = {image_list[i] for i in new_indices}

	# Evict images no longer within the new window
	images_to_evict = set(state.image_cache.cache.keys()) - new_window_set
	state.image_cache.evict(images_to_evict)

	# Cancel previous cache tasks if rapidly navigating
	if state.latest_cache_tasks is not None:
		for task in state.latest_cache_tasks:
			if not task.done():
				task.cancel()
	else:
		state.latest_cache_tasks = []

	# Add new images to cache asynchronously
	for img_path in new_window_set:
		if not state.image_cache.has(img_path):
			await state.cache_queue.put(img_path)

async def display_image(cached_image):
	"""
	Updates the UI with the processed image and hides the spinner.
	"""
	if cached_image:
		if state.image_display:
			state.image_display.set_source(cached_image)
			ui.update(state.image_display)
		else:
			state.error_dialog.show(
				"Image display not initialized yet.",
				"Please try again."
			)
	else:
		state.error_dialog.show(
			"Image not cached.",
			"The requested image is not cached yet. Please try again."
		)

async def extract_metadata(image_path):
	"""
	Extracts EXIF/XMP metadata and updates the UI in the background.
	"""
	try:
		# Reset buffers
		state.meta_value_xmp = None
		state.meta_value_exif = None
		state.meta_value_input = None
		state.original_metadata = None
		
		# Get file extension in lowercase
		extension = image_path.suffix.lower()

		# Define supported formats
		supported_exif = {".jpg", ".jpeg", ".tiff", ".tif"}  # EXIF supported formats
		supported_xmp = {".jpg", ".jpeg", ".tiff", ".tif", ".png"}  # XMP supported formats

		if extension in supported_xmp:
			state.meta_value_xmp = await get_xmp_description(image_path)
		if extension in supported_exif:
			state.meta_value_exif = await get_exif_description(image_path)

		# Set input buffer
		if state.meta_value_xmp:
			state.meta_value_input = state.meta_value_xmp
		elif state.meta_value_exif:
			state.meta_value_input = state.meta_value_exif
		else:
			state.meta_value_input = ""

	except Exception as e:
		state.error_dialog.show(
			f"Unable to extract metadata", 
			"The app was not able to extract the EXIF or XMP data from this image.", 
			f"{e}")
		
async def display_metadata():
	# XMP Field
	if state.meta_value_xmp:
		state.meta_textarea_xmp.value = state.meta_value_xmp
		state.meta_textarea_xmp.classes(remove="text-italic")
	else:
		state.meta_textarea_xmp.value = "No XMP metadata found."
		state.meta_textarea_xmp.classes(add="text-italic")
	
	# EXIF Field
	if state.meta_value_exif:
		state.meta_textarea_exif.value = state.meta_value_exif
		state.meta_textarea_exif.classes(remove="text-italic")
	else:
		state.meta_textarea_exif.value = "No EXIF metadata found."
		state.meta_textarea_exif.classes(add="text-italic")

	# Input Field
	state.meta_textarea_input.value = state.meta_value_input
	state.original_metadata = state.meta_textarea_input.value