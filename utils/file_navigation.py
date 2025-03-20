# utils/file_navigation.py

from utils.state import state
from utils.file_utils import load_image, update_cache_window
from pathlib import Path
import glob
import asyncio
from nicegui import ui

async def navigate_next():
	async with state.nav_lock:
		state.nav_img_index = (state.nav_img_index + 1) % state.nav_img_total
		next_image_path = state.nav_img_list[state.nav_img_index]
		state.nav_counter.refresh()
		await load_image(next_image_path)
		await update_cache_window(state.nav_img_index)

async def navigate_prev():
	async with state.nav_lock:
		state.nav_img_index = (state.nav_img_index - 1) % state.nav_img_total
		prev_image_path = state.nav_img_list[state.nav_img_index]
		state.nav_counter.refresh()
		await load_image(prev_image_path)
		await update_cache_window(state.nav_img_index)