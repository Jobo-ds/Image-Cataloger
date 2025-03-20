import asyncio
from nicegui import ui, app
from ui.editor import create_metadata_section
from ui.spinners import PremadeSpinner
from utils.file_utils import open_image
from utils.state import state
from utils.file_navigation import navigate_next, navigate_prev

@ui.refreshable
def index_counter():
	"""Creates a label that updates dynamically when refreshed."""
	return ui.label(state.nav_txt).classes("mx-4 text-gray-700 text-lg")

state.nav_counter = index_counter

def setup_ui():
    ui.query('.nicegui-content').classes('p-0 gap-0 bg-neutral-800') # Remove ssystme gaps from nicegui
    # Load custom styles
    app.add_static_files('/static', 'static')
    ui.add_head_html('<link rel="stylesheet" href="static/styles.css">')

    # Full-page flex container
    with ui.column().classes('h-screen w-full flex flex-col'):

        # Image container (fills remaining space dynamically)
        with ui.column().classes('flex-1 w-full min-h-0 items-center justify-center border border-blue-500') as image_container:
            with ui.row().classes('h-full w-full items-center justify-center'):
                state.image_spinner = PremadeSpinner(image_container, "xl", "absolute top-1/4 left-1/2")
                state.image_display = ui.image().classes("w-full max-h-full opacity-100").props('fit=scale-down loading="eager" fetchpriority="high" no-spinner no-native-menu no-transition')

        # Editor (fixed height)
        with ui.row().classes('w-full justify-center shrink-0 border border-red-500'):
            elements = create_metadata_section()
            state.metadata_input = elements["input"]
            state.metadata_exif = elements["exif"]
            state.metadata_xmp = elements["xmp"]
            state.undo_button = elements["undo"]

        # Navigation bar (fixed height, sticks to bottom)
        with ui.row().classes('relative w-full p-4 justify-between items-center border border-yellow-500'):
            
            # Left Section: Open Image button (stays left-aligned)
            with ui.column().classes("flex justify-start"):
                with ui.row():
                    ui.button("Open Image", icon="sym_o_folder_open", on_click=lambda: asyncio.create_task(open_image()))
                    ui.button("Reload folder", icon="sym_o_refresh")

            # Center Section: Navigation controls (properly centered)
            with ui.column().classes('absolute left-1/2 transform -translate-x-1/2'):
                with ui.row().classes('w-full justify-center items-center'):
                    ui.button("Previous", icon="sym_o_arrow_back", on_click=lambda: asyncio.create_task(navigate_prev()))
                    index_counter()
                    ui.button("Next", icon="sym_o_arrow_forward", on_click=lambda: asyncio.create_task(navigate_next()))                    

            # Right Section: Settings button (stays right-aligned)
            with ui.column().classes('flex justify-end'):
                ui.button("Settings", icon="sym_o_settings")
