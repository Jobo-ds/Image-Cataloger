import threading
from ui.dialogs import ErrorDialog
from collections import OrderedDict

# utils/state.py
class AppState:
    """Global state management for the app."""
    
    def __init__(self):
        # Spinners
        self.app_spinner = None
        self.image_spinner = None
        self.editor_spinner = None
        self.save_spinner = None
        self.image_display = None
        # Metadata
        self.metadata_input = None
        self.metadata_exif = None
        self.metadata_xmp = None
        # Buttons
        self.reset_button = None
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

# Create a single instance of AppState to be shared across the app
state = AppState()
