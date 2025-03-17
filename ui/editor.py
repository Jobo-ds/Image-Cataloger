import asyncio
from nicegui import ui
from utils.state import state
from utils.string_utils import convert_to_ascii, convert_from_ascii
from metadata.xmp_handler import set_xmp_description, get_xmp_description
from metadata.exif_handler import set_exif_description, get_exif_description
from ui.spinners import PremadeSpinner

metadata_save_queue = asyncio.Queue()

async def process_metadata_queue():
	"""
	Background task to process metadata save requests.
	"""
	while True:
		undo = await metadata_save_queue.get()
		
		if not state.current_image:
			metadata_save_queue.task_done()
			continue
		
		state.metadata_input.add_props("disable readonly")
		state.editor_spinner.show()
		await ui.update(state.metadata_input)
		await ui.update(state.editor_spinner)

		try:
			new_description = state.metadata_input.value
			ascii_description = convert_to_ascii(new_description)

			if undo and new_description == state.original_metadata:
				ui.notify("Nothing to undo.", type="warning", close_button="X", position="top-right")
			
			elif undo:
				state.metadata_input.value = state.original_metadata
				await ui.update(state.metadata_input)
				xmp_saved = set_xmp_description(state.current_image, state.original_metadata)
				exif_saved = set_exif_description(state.current_image, convert_to_ascii(state.original_metadata))
				warnings = []
				if not xmp_saved:
					warnings.append("XMP metadata")
				if not exif_saved:
					warnings.append("EXIF metadata")

				if warnings:
					ui.notify(f"{', '.join(warnings)} could not be saved.", type="warning", close_button="X", position="top-right")
				else:
					ui.notify("Metadata saved successfully!", type="positive", close_button="X", position="top-right")

				await(update_metadata_display())
			
			else:
				xmp_saved = set_xmp_description(state.current_image, new_description)
				exif_saved = set_exif_description(state.current_image, ascii_description)
				warnings = []
				if not xmp_saved:
					warnings.append("XMP metadata")
				if not exif_saved:
					warnings.append("EXIF metadata")

				if warnings:
					ui.notify(f"{', '.join(warnings)} could not be saved.", type="warning", close_button="X", position="top-right")
				else:
					ui.notify("Metadata saved successfully!", type="positive", close_button="X", position="top-right")
				await(update_metadata_display())
		
		except Exception as e:
			state.error_dialog.show("Metadata could not be saved.", "An error occurred while saving the metadata, try again or reload the image.", f"{e}")
			await ui.update(state.error_dialog)
		
		finally:
			state.metadata_input.remove_props("disable readonly")
			state.editor_spinner.hide()
			await ui.update(state.metadata_input)
			await ui.update(state.editor_spinner)

			metadata_save_queue.task_done()

async def save_metadata(undo=False):
	"""
	Add a metadata save request to the queue.
	"""
	await metadata_save_queue.put_nowait(undo)

async def update_metadata_display():
	"""
	Update the metadata display with the current image's metadata.
	"""
	if not state.current_image:
		return  # No image loaded yet

	xmp = get_xmp_description(state.current_image)
	exif = get_exif_description(state.current_image)
	state.metadata_input.value = xmp if xmp else convert_from_ascii(exif)
	state.metadata_xmp.value = xmp
	state.metadata_exif.value = exif
	

	await ui.update(state.metadata_input)
	await ui.update(state.metadata_exif)
	await ui.update(state.metadata_xmp)

def create_metadata_section():
	"""
	Create metadata input, EXIF display, and reset functionality.
	"""
	with ui.tabs().classes('w-full max-w-2xl').props('transition-prev="fade" transition-next="fade"') as tabs:
		tab_editor = ui.tab('Edit Description')
		tab_xmp = ui.tab('View XMP')
		tab_exif = ui.tab('View EXIF')
		undo_button = ui.button("Undo",icon="sym_o_undo", on_click=lambda: save_metadata(undo=True)).classes(
				"p-2 absolute right-0")
	
	with ui.tab_panels(tabs, value=tab_editor).classes('w-full bg-transparent h-[130px]').props('transition-prev="fade" transition-next="fade"'):
		with ui.tab_panel(tab_editor):
			dev_placeholder = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure awd a."
			prod_placeholder = "No image description."
			with ui.row().classes("w-full justify-center min-height-screen"):
				validations =  {'Exif limit: 255 characters.': lambda value: len(value) < 255}
				metadata_input = ui.textarea(placeholder=prod_placeholder, validation=validations).classes("w-full max-w-2xl").props("filled square autogrow v-model='text'")

		with ui.tab_panel(tab_xmp):
			with ui.row().classes("w-full justify-center"):
				metadata_xmp = ui.textarea(
				).classes("w-full max-w-2xl no-scrollbar").props("filled readonly disable square autogrow rows=1")

		with ui.tab_panel(tab_exif):
			with ui.row().classes("w-full justify-center"):
				metadata_exif = ui.textarea(
				).classes("w-full max-w-2xl no-scrollbar").props("filled readonly disable square autogrow rows=1")

	state.editor_spinner = PremadeSpinner(containers=[metadata_input, metadata_xmp, metadata_exif], size="xl", classes="relative")

	metadata_input.on('blur', save_metadata)  # Autosave on blur

	return {
		"input": metadata_input, 
		"exif": metadata_exif, 
		"xmp": metadata_xmp,
		"undo": undo_button
	}