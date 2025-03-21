import asyncio
from nicegui import ui
from utils.state import state
from ui.spinners import PremadeSpinner


async def save_metadata(undo=False):
	print(f"DEBUG: save_metadata called. save_queue = {state.save_queue}")  # Debugging line
	try:
		if state.save_queue is None:
			print("ERROR: save_queue is None!")
			return  # Prevents queue operations if it's not initialized
		await state.save_queue.put(undo)  # Ensures we are putting a valid item
	except Exception as e:
		print(f"ERROR: Exception in save_metadata: {e}")

def create_metadata_section():
	"""
	Create metadata input, EXIF display, and reset functionality.
	"""
	with ui.tabs().classes('w-full max-w-2xl').props('transition-prev="fade" transition-next="fade"') as tabs:
		tab_editor = ui.tab('Edit Description')
		tab_xmp = ui.tab('View XMP')
		tab_exif = ui.tab('View EXIF')
		undo_button = ui.button("Undo",icon="sym_o_undo", on_click=lambda: save_metadata(undo=True)).classes(
				"p-2 absolute right-0").classes('std-btn')
	
	with ui.tab_panels(tabs, value=tab_editor).classes('w-full bg-transparent h-[130px]').props('transition-prev="fade" transition-next="fade"'):
		with ui.tab_panel(tab_editor):
			dev_placeholder = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure awd a."
			prod_placeholder = "No image description."
			with ui.row().classes("w-full justify-center min-height-screen"):
				validations =  {'Exif limit: 255 characters.': lambda value: len(value) < 255}
				metadata_input = ui.textarea(placeholder=prod_placeholder, validation=validations).classes("w-full max-w-2xl").props("filled square autogrow readonly disable v-model='text'")

		with ui.tab_panel(tab_xmp):
			with ui.row().classes("w-full justify-center"):
				metadata_xmp = ui.textarea(
				).classes("w-full max-w-2xl no-scrollbar").props("filled readonly disable square autogrow rows=1")

		with ui.tab_panel(tab_exif):
			with ui.row().classes("w-full justify-center"):
				metadata_exif = ui.textarea(
				).classes("w-full max-w-2xl no-scrollbar").props("filled readonly disable square autogrow rows=1")

	state.editor_spinner = PremadeSpinner(containers=[metadata_input, metadata_xmp, metadata_exif], size="xl", classes="relative")

	metadata_input.on('blur', lambda _: asyncio.create_task(asyncio.sleep(0.1)).add_done_callback(
		lambda _: asyncio.create_task(save_metadata())
	))

	return {
		"input": metadata_input, 
		"exif": metadata_exif, 
		"xmp": metadata_xmp,
		"undo": undo_button
	}