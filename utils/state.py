# utils/state.py 🌍
class AppState:
    """Global state management for the app."""
    
    def __init__(self):
        self.spinner = None
        self.image_display = None
        self.metadata_input = None
        self.exif_fallback = None
        self.reset_button = None
        self.prev_button = None
        self.next_button = None
        self.current_image = None
        self.original_metadata = None
        self.image_counter = None

# Create a single instance of AppState to be shared across the app
state = AppState()
