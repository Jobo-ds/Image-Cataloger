# main.py 🚀
import os
import atexit
from nicegui import ui, app
from ui.layout import setup_ui

# Initialize the UI
setup_ui()

# Flag to prevent multiple shutdown calls
shutdown_called = False

def on_close():
    """Ensure NiceGUI shuts down only once when the window is closed."""
    global shutdown_called
    if shutdown_called:
        return  # Prevent multiple calls
    shutdown_called = True

    print("Window closed. Exiting program...")
    try:
        app.shutdown()  # Gracefully shut down NiceGUI
    except Exception as e:
        print(f"Error shutting down NiceGUI: {e}")
    os._exit(0)  # Hard exit to prevent any hanging

# Register cleanup function to run when the window is closed
atexit.register(on_close)

# Run the NiceGUI app in native mode
ui.run(
    title="EXIF/XMP Metadata Editor",
    native=False,  # Opens in a standalone window
    #window_size=(1200, 800),  # Set initial window size
    fullscreen=False,  # Prevent fullscreen on startup
    dark=True
)
