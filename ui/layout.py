from nicegui import ui, app
from ui.editor import create_metadata_section
from ui.navigation import create_navigation_controls
from ui.spinners import PremadeSpinner
from utils.file_utils import open_image
from utils.state import state

def setup_ui():
    ui.query('.nicegui-content').classes('p-0 gap-0 bg-slate-700') # Remove ssystme gaps from nicegui
    # Load custom styles
    app.add_static_files('/static', 'static')
    ui.add_head_html('<link rel="stylesheet" href="static/styles.css">')

    # Full-page flex container
    with ui.column().classes('h-screen w-full flex flex-col'):

        # Image container (fills remaining space dynamically)
        with ui.column().classes('flex-1 w-full min-h-0 items-center justify-center border border-blue-500') as image_container:
            with ui.row().classes('h-full w-full items-center justify-center'):
                state.image_spinner = PremadeSpinner(image_container, "xl", "absolute top-1/4 left-1/2")
                state.image_display = ui.image().classes("w-full max-h-full opacity-100").props('fit=scale-down')

        # Editor (fixed height)
        with ui.row().classes('w-full justify-center shrink-0 border border-red-500'):
            state.metadata_input, state.metadata_exif, state.metadata_xmp, state.reset_button = create_metadata_section()

        # Navigation bar (fixed height, sticks to bottom)
        with ui.row().classes('w-full p-4 justify-between items-center border border-yellow-500'):
            
            # Left Section: Open Image button (stays left-aligned)
            with ui.column():
                ui.button("Open Image", icon="sym_o_folder_open", on_click=open_image)

            # Center Section: Navigation controls (properly centered)
            with ui.column().classes('flex-1 flex justify-center'):
                with ui.row().classes('w-full justify-center items-center'):
                    state.prev_button, state.total_images_folder, state.next_button = create_navigation_controls()

                    state.metadata_input.value = "No image opened."
                    state.metadata_exif.value = "No image opened."
                    state.metadata_xmp.value = "No image opened."
                    state.original_metadata = ""

                    ui.update(state.metadata_input)
                    ui.update(state.metadata_exif)
                    ui.update(state.metadata_xmp)

            # Right Section: Settings button (stays right-aligned)
            with ui.column().classes('flex justify-end'):
                ui.button("Settings", icon="sym_o_settings")
