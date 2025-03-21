# utils/state.py
import os
import asyncio
from ui.dialogs import ErrorDialog
from collections import OrderedDict
import shlex
from nicegui import ui, Client
from utils.cache import ImageCache
from concurrent.futures import ThreadPoolExecutor
from utils.exiftool_wrapper import PatchedExifTool

def get_exiftool_path():
	path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "tools", "exiftool", "exiftool.exe"))
	if os.name == "nt":
		return path
	else:
		return shlex.quote(path)  # Only needed for Unix

def notify(message: str, type: str = "info") -> None:
    """
	Send a notification to all active clients safely.
	"""
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
		
		# UI Elements
		self.image_display = None # Image display ui element.
		self.undo_button = None # Undo button for metadata changes.
		self.prev_button = None # Previous image button.
		self.next_button = None # Next image button.	
		self.nav_txt = "0 / 0"
		self.app_status = None # Shows text underneath the editor.
		
		# Metadata
		self.metadata_input = None # Field for edit/set metadata.
		self.metadata_exif = None # Textarea with EXIF metadata (readonly)
		self.metadata_xmp = None # TextArea with XMP metadata (readonly)
		self.metadata_xmp_langs = None # Not used yet. For multi lang support.
		self.input_buffer = None # Buffer for holding the input value
		self.xmp_buffer = None # Buffer for holding xmp value
		self.exif_buffer = None # Buffer forholding exif value
				
		# Image Data
		self.current_image = None # Current image path.
		self.original_metadata = None # Original metadata for current image, used by "undo".
		self.unsaved_changes = False # Flag for unsaved metadata changes.
				
		# Queues (asyncio)
		self.save_queue = asyncio.Queue() # Queue for saving metadata.
		self.cache_queue = asyncio.Queue() # Queue for caching.
		self.nav_lock = asyncio.Lock() # Prevents overlapping the next/prev navigation.
		self.cache_executor = ThreadPoolExecutor(max_workers=4) # Thread pool executor for heavy cache operations
		
		# Image Cache
		self.cached_center_index = None # Last cached index center
		self.image_cache = ImageCache(50) # Cache for images.
		self.bg_cache_task = None # The background task for the caching.
		self.latest_image_task = None # The latest process image task.
		self.latest_cache_tasks = [] # The latest cache img tasks
		
		# Navigation
		self.nav_folder = None # The current folder the program is operating in.
		self.nav_img_index = 0 # The index of the current image in the list of images.
		self.nav_img_list = None # A Path list of images in the folder.
		self.nav_img_total = 0 # Len of images in folder
		self.nav_counter = None # The element itself.

		# Tools
		self.exiftool_path = get_exiftool_path() # Path to ExifTool executable.
		self.exiftool_process = PatchedExifTool(executable=str(self.exiftool_path)) # Keep an exiftool process running
		self.exiftool_process.start()

		# Dialogs
		self.error_dialog = ErrorDialog() # Error dialog for displaying errors.		

# Create a single instance of AppState to be shared across the app
state = AppState()