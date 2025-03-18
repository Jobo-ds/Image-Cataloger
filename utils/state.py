# utils/state.py
import os
from ui.dialogs import ErrorDialog
from collections import OrderedDict
import shlex

def get_exiftool_path():
	path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "exiftool", "exiftool.exe"))
	if os.name == "nt":
		return path
	else:
		return shlex.quote(path)  # Only needed for Unix


class AppState:
	"""Global state management for the app."""
	
	def __init__(self):
		# Spinners
		self.app_spinner = None
		self.image_spinner = None
		self.editor_spinner = None
		self.image_display = None
		# Metadata
		self.metadata_input = None
		self.metadata_exif = None
		self.metadata_xmp = None
		self.metadata_xmp_langs = None
		# Buttons
		self.undo_button = None
		self.prev_button = None
		self.next_button = None
		# App data
		self.image_buffer = OrderedDict()
		self.current_image = None
		self.original_metadata = None
		self.image_counter = None
		self.current_image_count_folder = None
		self.total_images_folder = None
		self.unsaved_changes = False
		# Dialogs
		self.error_dialog = ErrorDialog()
		# Tools
		self.exiftool_path = get_exiftool_path()

# Create a single instance of AppState to be shared across the app
state = AppState()