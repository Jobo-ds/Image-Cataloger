# ui/components.py 🎥
from nicegui import ui
from metadata.exif_handler import set_exif_description
from metadata.xmp_handler import set_xmp_description
from utils.string_utils import convert_to_ascii
from utils.state import state
from utils.file_utils import navigate_image

def create_metadata_section():
	"""Create metadata input, EXIF fallback display, and reset functionality."""

	with ui.tabs().classes('w-full') as tabs:
		editor = ui.tab('Edit')
		xmp_view = ui.tab('View XMP')
		exif_view = ui.tab('View EXIF')
	
	with ui.tab_panels(tabs, value=editor).classes('w-full bg-transparent'):
		with ui.tab_panel(editor):
			dev_placeholder = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit."
			prod_placeholder = "No image description."
			with ui.row().classes("w-full justify-center min-height-screen"):
				validations =  {'Exif limit: 255 characters.': lambda value: len(value) < 255}
				metadata_input = ui.textarea(placeholder=prod_placeholder, validation=validations, value=dev_placeholder).classes("w-full max-w-2xl").props("filled square autogrow v-model='text'")
				reset_button = ui.button("⟲ Reset", on_click=lambda: reset_metadata(metadata_input)).classes(
				"bg-red-500 text-white rounded-md px-4 py-2"
			)
		with ui.tab_panel(xmp_view):
			with ui.row().classes("w-full justify-center min-height-screen"):
				xmp_view = ui.textarea(placeholder=prod_placeholder, validation=validations, value=dev_placeholder).classes("w-full max-w-2xl").props("filled readonly disable square autogrow v-model='text'")  
		with ui.tab_panel(exif_view):
			with ui.row().classes("w-full justify-center min-height-screen"):
				exif_view = ui.textarea(placeholder=prod_placeholder, validation=validations, value=dev_placeholder).classes("w-full max-w-2xl").props("filled readonly disable square autogrow v-model='text'")  
	
	def reset_metadata(field):
		"""Reset the metadata field to the original value and save it."""
		field.value = state.original_metadata  # Reset field to original metadata
		print("✅ Metadata reset to original value.")
		save_metadata(reset=True)  # ✅ Ensure reset is also saved

	def save_metadata(reset=False):
		"""Save metadata when the user clicks away or resets."""
		if not state.current_image:
			return  # No image loaded yet

		new_description = metadata_input.value
		ascii_description = convert_to_ascii(new_description)

		set_xmp_description(state.current_image, new_description)  # Save to XMP
		set_exif_description(state.current_image, ascii_description)  # Save ASCII to EXIF

		exif_view.value = ascii_description  # Update fallback view

		if reset:
			print("✅ Reset metadata saved successfully!")
		else:
			print("✅ Metadata saved successfully!")

	metadata_input.on('blur', save_metadata)  # Autosave on blur

	return metadata_input, exif_view, reset_button

def create_navigation_controls():
	"""Create navigation buttons for previous/next image."""
	prev_button = ui.button("← Previous", on_click=lambda: navigate_image(-1))
	image_counter = ui.label("8 / 24").classes("mx-4 text-gray-700 text-lg")  # Image counter
	next_button = ui.button("Next →", on_click=lambda: navigate_image(1))

	return prev_button, image_counter, next_button