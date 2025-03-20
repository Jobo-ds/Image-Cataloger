# main.py
import os
import atexit
import asyncio
from nicegui import ui, app


from ui.dialogs import ErrorDialog
from utils.tasks import save_metadata_queue, cache_worker
from ui.layout import setup_ui
from utils.state import state

# Initialize the UI
setup_ui()

@app.on_startup
async def start_background_tasks():
	print("DEBUG: Starting save_metadata_queue...")
	asyncio.create_task(save_metadata_queue())
	if state.bg_cache_task is None or state.bg_cache_task.done():
		state.bg_cache_task = asyncio.create_task(cache_worker())		 

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
	native=True,  # Opens in a standalone window
	#window_size=(1200, 800),  # Set initial window size
	fullscreen=False,  # Prevent fullscreen on startup
	dark=True
)
