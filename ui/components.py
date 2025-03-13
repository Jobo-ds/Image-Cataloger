# ui/components.py 🖥️
from nicegui import ui
from metadata.exif_handler import get_exif_description, set_exif_description
from metadata.xmp_handler import get_xmp_description, set_xmp_description
from utils.string_utils import convert_to_ascii
from utils.file_utils import navigate_image

def create_metadata_section():
    """Create metadata input, EXIF fallback display, and reset functionality."""

    ui.label("Image Description (XMP)").style("font-weight: bold; margin-top: 10px;")

    metadata_input = ui.textarea(placeholder="Enter image description...").style("width: 100%; height: 100px;")

    reset_button = ui.button("⟲ Reset", on_click=lambda: reset_metadata(metadata_input))

    ui.label("EXIF Fallback (Read-Only)").style("color: gray; margin-top: 10px;")
    exif_fallback = ui.textarea().props("readonly").style("width: 100%; height: 100px; color: gray;")

    def reset_metadata(field):
        """Reset the metadata field to the original value."""
        field.set_value(ui.store.get("original_metadata", ""))

    def save_metadata():
        """Save metadata when the user clicks away."""
        image_path = ui.store.get("current_image")
        if not image_path:
            return  # No image loaded yet

        new_description = metadata_input.get_value()
        ascii_description = convert_to_ascii(new_description)

        set_xmp_description(image_path, new_description)  # Save to XMP
        set_exif_description(image_path, ascii_description)  # Save ASCII to EXIF

        exif_fallback.set_value(ascii_description)  # Update fallback view

    metadata_input.on('blur', save_metadata)  # ✅ Corrected blur event

    return metadata_input, exif_fallback, reset_button

def create_navigation_controls():
    """Create navigation buttons for previous/next image."""
    prev_button = ui.button("← Previous", on_click=lambda: navigate_image(-1))
    next_button = ui.button("Next →", on_click=lambda: navigate_image(1))

    return prev_button, next_button
