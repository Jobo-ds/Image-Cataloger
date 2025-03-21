import asyncio
from nicegui import ui
from utils.state import state
from ui.spinners import PremadeSpinner
from ui.status_icon import StatusIcon


async def save_metadata(undo=False):
	try:
		if state.save_queue is None:
			state.error_dialog.show(
				"Save queue not ready.",
				"An error occured when creating the save queue task.",
				str(e)
			)			
			return  # Prevents queue operations if it's not initialized
		await state.save_queue.put(undo)  # Ensures we are putting a valid item
	except Exception as e:
		state.error_dialog.show(
			"Save metadata error",
			"An error occured when creating the save queue task.",
			str(e)
		)

def update_status_icons():

	def has_non_latin1(text: str) -> bool:
		try:
			text.encode('latin-1')
			return False
		except UnicodeEncodeError:
			return True

	text = state.input_buffer or ""

	if len(text) > 255:
		state.status_warn_len.show()
	else:
		state.status_warn_len.hide()

	if has_non_latin1(text):
		"Yikes"
		state.status_warn_chars.show()
	else:
		"ok"
		state.status_warn_chars.hide()

def create_metadata_section():
	"""
	Create metadata input, EXIF display, and reset functionality.
	"""
	with ui.tabs().classes('w-full max-w-2xl').props('transition-prev="fade" transition-next="fade"') as tabs:
		with ui.row().classes("absolute left-0"):
			state.status_warn_len = StatusIcon("Description will be truncated in EXIF (Max 255 chars)", icon="sym_o_warning", color="yellow-500")
			state.status_warn_chars = StatusIcon("This description contains characters not supported by EXIF.", icon="sym_o_warning", color="yellow-500")
			state.editor_spinner = PremadeSpinner(size="sm")
		tab_editor = ui.tab('Edit Description')
		tab_xmp = ui.tab('View XMP')
		tab_exif = ui.tab('View EXIF')
		state.undo_button = ui.button("Undo",icon="sym_o_undo", on_click=lambda: save_metadata(undo=True)).classes(
				"p-2 absolute right-0").classes('std-btn')
	
	with ui.tab_panels(tabs, value=tab_editor).classes('w-full bg-transparent min-h-[130px] max-h-[600px]').props('transition-prev="fade" transition-next="fade"'):
		with ui.tab_panel(tab_editor):
			with ui.scroll_area():
				with ui.row().classes("w-full justify-center min-height-screen"):				
					state.metadata_input = ui.textarea(placeholder="No image description.", on_change=lambda: update_status_icons()) \
						.bind_value(state, "input_buffer") \
						.classes("w-full max-w-2xl no-scrollbar") \
						.props("filled square autogrow readonly disable")

		with ui.tab_panel(tab_xmp):
			with ui.scroll_area():
				with ui.row().classes("w-full justify-center"):
					state.metadata_xmp = ui.textarea(
					).classes("w-full max-w-2xl no-scrollbar").props("filled readonly disable square autogrow rows=1")

		with ui.tab_panel(tab_exif):
			with ui.scroll_area():
				with ui.row().classes("w-full justify-center"):
					state.metadata_exif = ui.textarea(
					).classes("w-full max-w-2xl no-scrollbar").props("filled readonly disable square autogrow rows=1")

	state.metadata_input.on('blur', lambda _: asyncio.create_task(asyncio.sleep(0.1)).add_done_callback(
		lambda _: asyncio.create_task(save_metadata())
	))