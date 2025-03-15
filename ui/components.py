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
			with ui.row().classes("w-full justify-center"):
				metadata_input = ui.textarea(placeholder=dev_placeholder).classes("w-full max-w-2xl").props("filled square autogrow v-model='text'").style("background:#343434;")
		with ui.tab_panel(xmp_view):
			ui.label('Second tab')    
		with ui.tab_panel(exif_view):
			ui.label('Second tab')                 
	
	# Outer container to ensure proper alignment
	with ui.column().classes("w-full max-w-3xl mx-auto p-4 bg-gray-800 rounded-md shadow-md"):
		
		# Row 1: Label for Image Description
		with ui.row().classes("w-full justify-start"):
			ui.label("Image Description").classes("text-white font-bold text-lg")

		# Row 2: Metadata Input (User editable)


		# Row 3: Reset Button (Aligned Right)
		with ui.row().classes("w-full justify-end"):
			reset_button = ui.button("⟲ Reset", on_click=lambda: reset_metadata(metadata_input)).classes(
				"bg-red-500 text-white rounded-md px-4 py-2"
			)

		# Row 4: Label for EXIF Fallback
		with ui.row().classes("w-full justify-start mt-2"):
			ui.label("EXIF Fallback (Read-Only)").classes("text-gray-400")

		# Row 5: EXIF Fallback (Read-Only)
		with ui.row().classes("w-full"):
			exif_fallback = ui.textarea().props("readonly").classes(
				"w-full max-w-2xl h-24 bg-gray-700 text-gray-400 rounded-md p-2"
			)

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