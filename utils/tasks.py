from utils.state import state, notify
from utils.string_utils import convert_to_ascii
from metadata.exif_handler import set_exif_description
from metadata.xmp_handler import set_xmp_description
from ui.editor import update_metadata_display
from nicegui import ui


async def save_metadata_queue():
	"""
	Background task to process metadata save requests.
	"""
	while True:
		try:
			undo = await state.save_queue.get()

			if not state.current_image:
				state.save_queue.task_done()
				continue

			state.metadata_input.props(add="disable readonly")
			state.editor_spinner.show()
			
			try:
				new_description = str(state.metadata_input.value)
				ascii_description = convert_to_ascii(new_description)

				if undo and new_description == state.original_metadata:
					notify("Nothing to undo.")

				elif undo:
					state.metadata_input.value = state.original_metadata
					xmp_save_check = await set_xmp_description(state.current_image, state.original_metadata)
					exif_save_check = await set_exif_description(state.current_image, convert_to_ascii(state.original_metadata))

					warnings = []
					if not xmp_save_check:
						warnings.append("XMP metadata")
					if not exif_save_check:
						warnings.append("EXIF metadata")

					if warnings:
						notify(f"{', '.join(warnings)} could not be saved.", "warning")
					else:
						notify("Metadata saved successfully!", "positive")
					await update_metadata_display()

				else:
					xmp_save_check = False
					xmp_save_check = await set_xmp_description(state.current_image, new_description)
					exif_save_check = False
					exif_save_check = await set_exif_description(state.current_image, ascii_description)
					
					warnings = []
					if not xmp_save_check:
						warnings.append("XMP metadata")
					if not exif_save_check:
						warnings.append("EXIF metadata")
					
					if warnings:
						notify(f"{', '.join(warnings)} could not be saved.", "warning")
					else:
						notify("Metadata saved succesfully!", "positive")
					await update_metadata_display()

			except Exception as e:
				print(f"ERROR: Exception in save_metadata_queue: {e}")
				state.error_dialog.show(
					"Metadata could not be saved.", 
					"An error occurred while saving the metadata, try again or reload the image.", 
					f"{e}")

			finally:
				print("SQ: Re-enabling metadata input field...")
				state.metadata_input.props(remove="disable readonly")
				print("SQ: Hiding spinner...")
				state.editor_spinner.hide()
				print("SQ: Marking save queue task as done...")
				state.save_queue.task_done()

		except Exception as e:
			print(f"CRITICAL ERROR: process_metadata_queue crashed! {e}")
			break  # Prevent infinite errors if something goes wrong