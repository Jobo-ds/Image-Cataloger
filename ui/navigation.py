from nicegui import ui
from utils.state import state
from utils.file_navigation import navigate_image

@ui.refreshable
def index_counter():
	"""Creates a label that updates dynamically when refreshed."""
	return ui.label(state.index_counter_text).classes("mx-4 text-gray-700 text-lg")

# Store the function reference in state (not the label itself)
state.index_counter = index_counter  

def create_navigation_controls():
	"""Create navigation buttons for previous/next image."""
	prev_button = ui.button("Previous", icon="sym_o_arrow_back", on_click=lambda: navigate_image(-1))
	counter = state.index_counter()  # Call function to get the label
	next_button = ui.button("Next", icon="sym_o_arrow_forward", on_click=lambda: navigate_image(1))

	return prev_button, counter, next_button
