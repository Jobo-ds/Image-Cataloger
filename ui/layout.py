import asyncio
from nicegui import ui, app
from ui.editor import create_metadata_section
from ui.spinners import PremadeSpinner
from utils.file_utils import open_image
from utils.state import state
from utils.file_navigation import navigate_next, navigate_prev
import time
from PIL import Image

@ui.refreshable
def index_counter():
	"""Creates a label that updates dynamically when refreshed."""
	return ui.label(state.nav_txt).classes("mx-4 text-gray-700 text-lg")

state.nav_counter = index_counter

def setup_ui():
	ui.query('.nicegui-content').classes('p-0 gap-0 bg-neutral-800')  # Remove system gaps from NiceGUI
	# Load custom styles
	app.add_static_files('/static', 'static')
	ui.add_head_html('<link rel="stylesheet" href="static/styles.css">')

	# Full-page flex container
	with ui.column().classes('h-screen w-full flex flex-col gap-0'):

		# Image container (fills remaining space dynamically)
		with ui.column().classes('flex-1 w-full min-h-0 items-center justify-center relative gap-0') as image_container:
			# Floating buttons above the image
			with ui.row().classes('absolute top-6 left-5 right-5 justify-between z-10'):
				with ui.row().classes("flex justify-start"):
					ui.button("Open Image", icon="sym_o_folder_open", on_click=lambda: asyncio.create_task(open_image())).classes('std-btn')
					ui.button("Reload Folder", icon="sym_o_refresh").classes('std-btn')
				with ui.row().classes("flex justify-end"):
					ui.button("Settings", icon="sym_o_settings").classes('std-btn')
			
			with ui.row().classes('h-full w-full items-center justify-center pt-5 pb-5'):
				state.image_spinner = PremadeSpinner(size="xl", classes="absolute top-1/4 left-1/2")
				state.image_display = ui.image('static/image.png').classes("w-1/6 max-h-full opacity-100").props(
					'fit=scale-down loading="eager" fetchpriority="high" no-spinner no-native-menu no-transition'
				)

		# Metadata Editor (separate row below image)
		with ui.row().classes('w-full justify-center items-center shrink-0 bg-neutral-900 pt-4 border-t border-neutral-700'):
			create_metadata_section()

		# Navigation bar (fixed height, sticks to bottom)
		with ui.row().classes('relative w-full pb-5 justify-center items-center bg-neutral-900'):
			with ui.row().classes('w-full justify-center items-center'):
				ui.button("Previous", icon="sym_o_arrow_back", on_click=lambda: asyncio.create_task(navigate_prev())).classes('std-btn')
				index_counter()
				ui.button("Next", icon="sym_o_arrow_forward", on_click=lambda: asyncio.create_task(navigate_next())).classes('std-btn')
