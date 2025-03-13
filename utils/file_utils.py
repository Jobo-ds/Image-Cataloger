# utils/file_utils.py 📂
from nicegui import ui
from pathlib import Path
from metadata.exif_handler import get_exif_description
from metadata.xmp_handler import get_xmp_description
from utils.string_utils import convert_to_ascii
from utils.state import state  # Import global state

def open_image():
    """Opens an image and loads its metadata."""
    file = ui.open_file_dialog(filters=[".jpg", ".tiff", ".png"])
    if file:
        load_image(file)

def load_image(image_path):
    """Loads the image and extracts metadata."""
    image_path = Path(image_path)
    state.current_image = image_path

    # Update UI with the selected image
    state.image_display.set_source(str(image_path))

    # Extract metadata
    xmp_description = get_xmp_description(image_path)
    exif_description = get_exif_description(image_path)

    # Convert XMP to ASCII for EXIF display
    ascii_exif_description = convert_to_ascii(xmp_description)

    # Update UI fields
    state.metadata_input.set_value(xmp_description)
    state.exif_fallback.set_value(ascii_exif_description)
    state.original_metadata = xmp_description  # Store for reset functionality

def get_image_list():
    """Get all supported images in the current folder."""
    if not state.current_image:
        return []

    folder = state.current_image.parent
    images = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.tiff")) + sorted(folder.glob("*.png"))
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
