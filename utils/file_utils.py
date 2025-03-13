# utils/file_utils.py 📂
import threading
import psutil
import base64
from collections import OrderedDict
from nicegui import ui
from pathlib import Path
from PIL import Image
from metadata.exif_handler import get_exif_description
from metadata.xmp_handler import get_xmp_description
from utils.string_utils import convert_to_ascii
from utils.state import state
from io import BytesIO
import config

# ✅ Image Buffer (FIFO Cache)
image_buffer = OrderedDict()

def open_image():
    """Opens a file dialog and loads the selected image."""
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.tiff;*.tif")]
    )

    root.destroy()
    if not file_path:
        print("No file selected.")
        return

    load_image(Path(file_path))

def load_image(image_path):
    """Loads an image, using the buffer if available, and extracts metadata."""
    image_path = Path(image_path)
    if not image_path.exists():
        print("Error: File does not exist.")
        return

    state.current_image = image_path

    # ✅ Show the spinner while processing the image
    if state.spinner:
        print("Showing spinner")
        state.spinner.style('display: block;')

    # ✅ Check if the image is already in the buffer
    if image_path in image_buffer:
        print(f"Using cached version of {image_path.name}")
        display_image(image_buffer[image_path])  # ✅ Show from buffer
    else:
        # ✅ Process the image in a separate thread
        print("Processing new image...")
        threading.Thread(target=process_image_for_display, args=(image_path,), daemon=True).start()

    # ✅ Extract metadata in a background thread (non-blocking)
    threading.Thread(target=extract_metadata, args=(image_path,), daemon=True).start()

    # ✅ Show memory usage in development mode
    if config.DEVELOPMENT_MODE:
        display_memory_usage()

def process_image_for_display(image_path):
    """Converts the image to an in-memory JPG Base64 string for NiceGUI display."""
    try:
        with Image.open(image_path) as img:
            # ✅ Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")

            # ✅ Always convert to JPG to optimize memory
            img_io = BytesIO()
            img.save(img_io, format="JPEG", quality=75)  # ✅ Compress for low memory
            img_io.seek(0)

            # ✅ Convert to Base64
            base64_str = base64.b64encode(img_io.getvalue()).decode("utf-8")
            base64_image = f"data:image/jpeg;base64,{base64_str}"
            print("Base64 image length:", len(base64_image))
            print("Image processed into base64")

            # ✅ Store in the buffer (FIFO: Remove oldest if full)
            if len(image_buffer) >= config.IMAGE_BUFFER_SIZE:
                image_buffer.popitem(last=False)  # Remove the oldest entry

            image_buffer[image_path] = base64_image

            # ✅ Update UI with the processed image
            display_image(base64_image)

    except Exception as e:
        print(f"Image processing error: {e}")
        if state.spinner:
            state.spinner.style('display: none;')  # Hide spinner on error

def display_image(image_data):
    """Updates the UI with the processed image and hides the spinner."""
    try:
        print("Setting image source")
        state.image_display.set_source(image_data)
        print("Image should be visible now")
    except Exception as e:
        print(f"Error displaying image: {e}")
    finally:
        if state.spinner:
            state.spinner.style('display: none;')

def extract_metadata(image_path):
    """Extracts EXIF/XMP metadata and updates the UI in the background."""
    try:
        with Image.open(image_path) as img:
            xmp_description = get_xmp_description(image_path)
            exif_description = get_exif_description(image_path)
            ascii_exif_description = convert_to_ascii(exif_description)

            state.metadata_input.value = xmp_description if xmp_description else ascii_exif_description
            state.exif_fallback.value = ascii_exif_description
            state.original_metadata = state.metadata_input.value

            ui.update(state.metadata_input)
            ui.update(state.exif_fallback)

            print("✅ Metadata loaded successfully!")
    except Exception as e:
        print(f"Metadata extraction error: {e}")

def get_image_list():
    """Get all supported images in the current folder."""
    if not state.current_image:
        return []

    folder = state.current_image.parent
    images = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg")) + sorted(folder.glob("*.png")) + sorted(folder.glob("*.tiff")) + sorted(folder.glob("*.tif"))
    return images

def navigate_image(direction):
    """Move to the next or previous image."""
    images = get_image_list()
    if not images:
        return  # No images found

    if state.current_image not in images:
        return  # Image not in the folder

    index = images.index(state.current_image)
    new_index = (index + direction) % len(images)  # Loop around

    # Autosave before switching
    if state.metadata_input:
        state.metadata_input.run_method("on", "blur")  # Trigger autosave

    # Load the new image
    load_image(images[new_index])

def display_memory_usage():
    """Displays current memory usage (for debugging)."""
    process = psutil.Process()
    mem_usage = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB
    print(f"🧠 Memory Usage: {mem_usage:.2f} MB | Buffer Size: {len(image_buffer)}/{config.IMAGE_BUFFER_SIZE}")
