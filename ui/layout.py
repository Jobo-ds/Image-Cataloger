# ui/layout.py 🎨
from nicegui import ui
from ui.components import create_metadata_section, create_navigation_controls
from utils.file_utils import open_image
from utils.state import state  # Import global state

def setup_ui():
    """Setup the main UI layout."""

    with ui.row():
        ui.button("Open Image", on_click=open_image)

    # Image Display
    state.image_display = ui.image().style("max-width: 80%; max-height: 500px; margin: auto;")

    # Metadata Section
    state.metadata_input, state.exif_fallback, state.reset_button = create_metadata_section()

    # Navigation Controls
    state.prev_button, state.next_button = create_navigation_controls()
