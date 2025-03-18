# utils/file_utils.py
import asyncio
import base64
import concurrent.futures
from nicegui import ui
from pathlib import Path
from PIL import Image
from metadata.exif_handler import get_exif_description
from metadata.xmp_handler import get_xmp_description
from utils.dev_tools import display_memory_usage
from utils.string_utils import convert_to_ascii
from utils.state import state
from io import BytesIO
import config
import tkinter as tk
from tkinter import filedialog

def check_tasks_done(future_image, future_metadata):
    """Checks if both tasks are done, then hides spinners."""
    if future_image.done() and future_metadata.done():
        ui.timer(0.5, lambda: (state.image_spinner.hide(), state.editor_spinner.hide()), once=True)
    else:
        ui.timer(0.1, lambda: check_tasks_done(future_image, future_metadata), once=True)



async def open_image():
	"""
	Asynchronously opens a file dialog and loads the selected image.
	"""
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

	await load_image(Path(file_path))


async def load_image(image_path):
    """
    Loads an image, using the buffer if available, and extracts metadata.
    """

    state.image_spinner.show()
    state.editor_spinner.show()

    image_path = Path(image_path)
    if not await asyncio.to_thread(image_path.exists):
        state.error_dialog.show("File does not exist.", "Confirm the image file exists, and try again.")
        state.image_spinner.hide()
        state.editor_spinner.hide()
        return

    state.current_image = image_path

    # Process image or use buffer
    if image_path in state.image_buffer:
        display_image(state.image_buffer[image_path])
        ui.timer(0.5, lambda: (state.image_spinner.hide(), state.editor_spinner.hide()), once=True)
    else:
        # Run tasks in parallel but ensure they complete
        image_task = asyncio.create_task(process_image_for_display(image_path))
        metadata_task = asyncio.create_task(extract_metadata(image_path))
        
        await asyncio.gather(image_task, metadata_task)

        # Ensure both tasks completed before hiding spinners
        if image_task.done() and metadata_task.done():
            state.image_spinner.hide()
            state.editor_spinner.hide()
        else:
            # Retry hiding after a short delay if not done yet
            ui.timer(0.5, lambda: (state.image_spinner.hide(), state.editor_spinner.hide()), once=True)

    if config.DEVELOPMENT_MODE:
        display_memory_usage()

async def process_image_for_display(image_path):
    """
    Converts the image to an in-memory JPG Base64 string for NiceGUI display.
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
            if len(state.image_buffer) >= config.IMAGE_BUFFER_SIZE:
                state.image_buffer.popitem(last=False)  # Remove the oldest entry

            state.image_buffer[image_path] = base64_image

            display_image(base64_image)

    except Exception as e:
        state.error_dialog.show(
            f"Could not process {image_path.name} for app.", 
            "Please try again, and confirm the image works in a different program.", 
            f"{e}")

def display_image(image_data):
    """
    Updates the UI with the processed image and hides the spinner.
    """
    try:
        if state.image_display:
            state.image_display.set_source(image_data)
        else:
            print("Warning: Image display UI not initialized yet.")
    except Exception as e:
        state.error_dialog.show(f"Could not display image.", "Please try again, and confirm the image works in a different program.", f"{e}")

async def extract_metadata(image_path):
    """
    Extracts EXIF/XMP metadata and updates the UI in the background.
    """
    try:

        # Get file extension in lowercase
        extension = image_path.suffix.lower()

        # Define supported formats
        supported_exif = {".jpg", ".jpeg", ".tiff", ".tif"}  # EXIF supported formats
        supported_xmp = {".jpg", ".jpeg", ".tiff", ".tif", ".png"}  # XMP supported formats

        xmp_description = False
        exif_description = False

        if extension in supported_xmp:
            xmp_description = await get_xmp_description(image_path)
        if extension in supported_exif:
            exif_description = await get_exif_description(image_path)

        # Input Field
        if xmp_description:
            state.metadata_input.value = xmp_description
        elif exif_description:
            state.metadata_input.value = convert_to_ascii(exif_description)
        else:
            state.metadata_input.value = ""

        # XMP Field
        if xmp_description:
            state.metadata_xmp.value = xmp_description
            state.metadata_xmp.classes(remove="text-italic")
        else:
            state.metadata_xmp.value = "No XMP metadata found."
            state.metadata_xmp.classes(add="text-italic")
        
        # EXIF Field
        if exif_description:
            state.metadata_exif.value = exif_description
            state.metadata_exif.classes(remove="text-italic")
        else:
            state.metadata_exif.value = "No EXIF metadata found."
            state.metadata_exif.classes(add="text-italic")

        state.original_metadata = state.metadata_input.value

        # Update UI
        ui.update(state.metadata_input)
        ui.update(state.metadata_exif)
        ui.update(state.metadata_xmp)

    except Exception as e:
        state.error_dialog.show(
            f"Unable to extract metadata", 
            "The app was not able to extract the EXIF or XMP data from this image.", 
            f"{e}")