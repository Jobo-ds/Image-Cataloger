from nicegui import ui
from utils.state import state
from utils.string_utils import convert_to_ascii
from metadata.xmp_handler import set_xmp_description
from metadata.exif_handler import set_exif_description


def create_metadata_section():
	"""Create metadata input, EXIF fallback display, and reset functionality."""

	with ui.tabs().classes('w-full max-w-2xl').props('transition-prev="fade" transition-next="fade"') as tabs:
		editor = ui.tab('Edit Description')
		metadata_xmp = ui.tab('View XMP')
		metadata_exif = ui.tab('View EXIF')
		reset_button = ui.button("Undo",icon="sym_o_undo", on_click=lambda: reset_metadata(metadata_input)).classes(
				"p-2 absolute right-0")
	
	with ui.tab_panels(tabs, value=editor).classes('w-full bg-transparent h-[130px]').props('transition-prev="fade" transition-next="fade"'):
		with ui.tab_panel(editor):
			state.editor_spinner.get()
			dev_placeholder = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure awd a."
			prod_placeholder = "No image description."
			with ui.row().classes("w-full justify-center min-height-screen"):
				validations =  {'Exif limit: 255 characters.': lambda value: len(value) < 255}
				metadata_input = ui.textarea(placeholder=prod_placeholder, validation=validations).classes("w-full max-w-2xl").props("filled square autogrow v-model='text'")

		with ui.tab_panel(metadata_xmp):
			with ui.row().classes("w-full justify-center"):
				state.editor_spinner.get()
				metadata_xmp = ui.textarea(
					placeholder=prod_placeholder,
					value=dev_placeholder
				).classes("w-full max-w-2xl no-scrollbar").props("filled readonly disable square autogrow rows=1")

		with ui.tab_panel(metadata_exif):
			with ui.row().classes("w-full justify-center"):
				state.editor_spinner.get()
				metadata_exif = ui.textarea(
					placeholder=prod_placeholder,
					value=dev_placeholder
				).classes("w-full max-w-2xl no-scrollbar").props("filled readonly disable square autogrow rows=1")

	
	def set_metadata_field(field, value):
		"""Set the metadata field to the given value."""
		field.value = value

	def reset_metadata(field):
		"""Reset the metadata field to the original value and save it."""
		field.value = state.original_metadata
		save_metadata(reset=True)

	def save_metadata(reset=False):
		"""Save metadata when the user clicks away or resets."""
		if not state.current_image:
			return  # No image loaded yet

		new_description = metadata_input.value
		ascii_description = convert_to_ascii(new_description)

		set_xmp_description(state.current_image, new_description)  # Save to XMP
		set_exif_description(state.current_image, ascii_description)  # Save ASCII to EXIF

		metadata_exif.value = ascii_description  # Update fallback view

		if reset:
			print("Reset metadata saved successfully!")
		else:
			print("Metadata saved successfully!")

	metadata_input.on('blur', save_metadata)  # Autosave on blur

	return metadata_input, metadata_exif, metadata_xmp, reset_button