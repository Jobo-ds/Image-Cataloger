from nicegui import ui
from ui.components import create_metadata_section, create_navigation_controls
from utils.file_utils import open_image
from utils.state import state

def setup_ui():
    """Setup the main UI layout based on the Figma design."""
    ui.query('.nicegui-content').classes('p-0 gap-0')

    # Full-page flex container
    with ui.column().classes('h-screen w-full flex flex-col'):

        # Controls (fixed height)
        with ui.row().classes('w-full h-16 p-4 justify-start shrink-0 border border-red-500'):
            ui.button("📂 Open Image", on_click=open_image)

        # Image container (fills remaining space dynamically)
        with ui.column().classes('flex-1 w-full min-h-0 items-center justify-center border border-blue-500'):
            with ui.row().classes('h-full w-full items-center justify-center'):
                state.image_display = ui.image().classes("w-full max-h-full").props('fit=scale-down')

        # Editor (fixed height)
        with ui.row().classes('w-full p-4 justify-center shrink-0 border border-red-500'):
            state.metadata_input, state.exif_fallback, state.reset_button = create_metadata_section()

        # Navigation (fixed height, sticks to bottom)
        with ui.row().classes('w-full p-4 justify-center shrink-0 border border-yellow-500'):
            state.prev_button, state.next_button = create_navigation_controls()
            ui.label("8 / 24").classes("mx-4 text-gray-700 text-lg")  # Image counter
