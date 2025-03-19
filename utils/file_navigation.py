# utils/file_navigation.py

from utils.state import state
from utils.file_utils import load_image
from pathlib import Path
import glob
import asyncio
from nicegui import ui

async def navigate_image(direction):
	"""
	Move to the next or previous image.
	"""
	async with state.nav_lock:		
		state.nav_img_index = (state.nav_img_index + direction) % state.nav_img_total  # Loop around
		state.nav_txt = f"{state.nav_img_index + 1} / {state.nav_img_total}"

		# Autosave before switching
		if state.metadata_input and state.metadata_input.value != state.original_metadata:
			state.metadata_input.run_method("on", "blur")  # Trigger autosave

		# Cancel any ongoing image loading task
		if state.latest_image_task:
			state.latest_image_task.cancel()
			try:
				await state.latest_image_task  # Ensure cancellation completes
			except asyncio.CancelledError:
				pass
			except Exception as e:
				state.error_dialog.show(
					"Error cancelling previous image",
					"Something went wrong while stopping the previous image load. Please try again.",
					f"{e}"
				)

		# Start loading the new image and track it
		state.latest_image_task = asyncio.create_task(load_image(state.nav_img_list[state.nav_img_index]))