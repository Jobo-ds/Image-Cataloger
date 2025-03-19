# utils/file_navigation.py

from utils.state import state
from utils.file_utils import load_image
from pathlib import Path
import glob
import asyncio

def get_image_list():
	"""Get all supported images in the current folder."""
	if not state.current_image:
		return []

	folder = Path(state.current_image).parent
	images = sorted(folder.glob("*.jpg")) + sorted(folder.glob("*.jpeg")) + sorted(folder.glob("*.png")) + sorted(folder.glob("*.tiff")) + sorted(folder.glob("*.tif"))
	state.total_images_folder = len(images)
	return images

async def navigate_image(direction):
	"""Move to the next or previous image."""
	images = get_image_list()
	if not images:
		return  # No images found

	if state.current_image not in images:
		return  # Image not in the folder

	
	index = images.index(state.current_image)
	new_index = (index + direction) % len(images)  # Loop around

	# Autosave before switching
	if state.metadata_input and state.metadata_input.value != state.original_metadata:
		state.metadata_input.run_method("on", "blur")  # Trigger autosave

	# Cancel any ongoing image loading task
	if state.latest_image_task:
		state.latest_image_task.cancel()
		try:
			await state.latest_image_task  # Ensure cancellation completes
		except asyncio.CancelledError:
			print(f"Cancelled previous image loading task for {state.current_image}")
		except Exception as e:
			state.error_dialog.show(
				"Error cancelling previous image",
				"Something went wrong while stopping the previous image load. Please try again.",
				f"{e}"
			)

	# Start loading the new image and track it
	state.latest_image_task = asyncio.create_task(load_image(images[new_index]))