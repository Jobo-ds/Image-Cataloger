from nicegui import ui
from utils.state import state
from utils.file_navigation import navigate_image

def create_navigation_controls():
	"""Create navigation buttons for previous/next image."""
	prev_button = ui.button("Previous", icon="sym_o_arrow_back", on_click=lambda: navigate_image(-1))
	image_counter = ui.label(f"? / {state.total_images_folder}").classes("mx-4 text-gray-700 text-lg")  # Image counter
	next_button = ui.button("Next", icon="sym_o_arrow_forward" , on_click=lambda: navigate_image(1))

	return prev_button, image_counter, next_button
