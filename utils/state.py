# utils/state.py
import os
import asyncio
from ui.dialogs import ErrorDialog
from collections import OrderedDict
import shlex
from nicegui import ui, Client

def get_exiftool_path():
	path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "exiftool", "exiftool.exe"))
	if os.name == "nt":
		return path
	else:
		return shlex.quote(path)  # Only needed for Unix


def notify(message: str, type: str = "info") -> None:
    """Send a notification to all active clients safely."""
    for client in Client.instances.values():
        if not client.has_socket_connection:
            continue
        with client:
            ui.notify(message, type=type, close_button="X", position="top-right")

class AppState:
	"""Global state management for the app."""
	
	def __init__(self):
		# Spinners
		self.app_spinner = None # Spinner for the entire app screen.
		self.image_spinner = None # Spinner for the current image loaded.
		self.editor_spinner = None # Spinner for the metadata fields.
		self.image_display = None # Global image display widget.
		# Metadata
		self.metadata_input = None # Field for edit/set metadata.
		self.metadata_exif = None # Textarea with EXIF metadata (readonly)
		self.metadata_xmp = None # TextArea with XMP metadata (readonly)
		self.metadata_xmp_langs = None # Not used yet. For multi lang support.
		# Buttons
		self.undo_button = None # Undo button for metadata changes.
		self.prev_button = None # Previous image button.
		self.next_button = None # Next image button.
		# Image Data
		self.current_image = None # Current image path.
		self.original_metadata = None # Original metadata for current image, used by "undo".
		self.current_image_index = None # The index of the current image in the folder.
		self.total_images_folder = None # Total images in current folder.
		self.unsaved_changes = False # Flag for unsaved metadata changes.
		# Dialogs
		self.error_dialog = ErrorDialog() # Error dialog for displaying errors.
		# Tools
		self.exiftool_path = get_exiftool_path() # Path to ExifTool executable.
		# Queues
		self.save_queue = asyncio.Queue() # Queue for saving metadata.
		# Image buffer
		self.image_buffer = OrderedDict() # Cache for images.
		self.latest_image_request = None # Tracking the latest requested image.
		self.latest_image_task = None # The latest process image task.

# Create a single instance of AppState to be shared across the app
state = AppState()