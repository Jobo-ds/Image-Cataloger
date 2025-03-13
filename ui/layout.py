# ui/layout.py 🎨
from nicegui import ui
from ui.components import create_metadata_section, create_navigation_controls
from utils.file_utils import open_image
from utils.state import state

def setup_ui():
    """Setup the main UI layout."""

    with ui.row():
        ui.button("Open Image", on_click=open_image)  # Normal Windows File Dialog

    # Image Display + Spinner
    with ui.column().style("position: relative; max-width: 80%; max-height: 500px; margin: auto;"):
        state.image_display = ui.image().style("width: 100%; height: auto;")
        state.spinner = ui.spinner(size='lg').style(
            "position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); display: none;"
        )

    # Metadata Section
    state.metadata_input, state.exif_fallback, state.reset_button = create_metadata_section()

    # Navigation Controls
    state.prev_button, state.next_button = create_navigation_controls()
