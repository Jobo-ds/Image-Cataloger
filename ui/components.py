# ui/components.py 🖥️
from nicegui import ui
from metadata.exif_handler import set_exif_description
from metadata.xmp_handler import set_xmp_description
from utils.string_utils import convert_to_ascii
from utils.state import state
from utils.file_utils import navigate_image

def create_metadata_section():
	"""Create metadata input, EXIF fallback display, and reset functionality."""

	ui.label("Image Description (XMP)").style("font-weight: bold; margin-top: 10px;")

	metadata_input = ui.textarea(placeholder="Enter image description...").style("width: 100%; height: 100px;")

	reset_button = ui.button("⟲ Reset", on_click=lambda: reset_metadata(metadata_input))

	ui.label("EXIF Fallback (Read-Only)").style("color: gray; margin-top: 10px;")
	exif_fallback = ui.textarea().props("readonly").style("width: 100%; height: 100px; color: gray;")

	def reset_metadata(field):
		"""Reset the metadata field to the original value and save it."""
		field.value = state.original_metadata  # Reset field to original metadata
		print("✅ Metadata reset to original value.")
		save_metadata(reset=True)  # ✅ Ensure reset is also saved

	def save_metadata(reset=False):
		"""Save metadata when the user clicks away or resets."""
		if not state.current_image:
			return  # No image loaded yet

		new_description = metadata_input.value  # ✅ Corrected from .get_value() to .value
		ascii_description = convert_to_ascii(new_description)

		set_xmp_description(state.current_image, new_description)  # Save to XMP
		set_exif_description(state.current_image, ascii_description)  # Save ASCII to EXIF

		exif_fallback.value = ascii_description  # Update fallback view

		if reset:
			print("✅ Reset metadata saved successfully!")
		else:
			print("✅ Metadata saved successfully!")

	metadata_input.on('blur', save_metadata)  # Autosave on blur

	return metadata_input, exif_fallback, reset_button

def create_navigation_controls():
	"""Create navigation buttons for previous/next image."""
	prev_button = ui.button("← Previous", on_click=lambda: navigate_image(-1))
	next_button = ui.button("Next →", on_click=lambda: navigate_image(1))

	return prev_button, next_button
