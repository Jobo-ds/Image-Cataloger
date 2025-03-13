# main.py 🚀
from nicegui import ui
from ui.layout import setup_ui

# Initialize the UI
setup_ui()

# Run the NiceGUI app in native mode (opens as a window)
ui.run(
    title="EXIF/XMP Metadata Editor",
    native=True,  # Enables standalone window mode
    window_size=(1200, 800),  # Set initial window size
    fullscreen=False,  # Prevent full-screen on startup
    dark=True
)
