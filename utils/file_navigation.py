# utils/file_navigation.py

from utils.state import state
from utils.file_utils import load_image

def get_image_list():
    """Get all supported images in the current folder."""
    if not state.current_image:
        return []

    folder = state.current_image.parent
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

    # Show spinners explicitly before switching
    if state.image_spinner:
        state.image_spinner.show()
    if state.editor_spinner:
        state.editor_spinner.show()

    # Autosave before switching
    if state.metadata_input and state.metadata_input.value != state.original_metadata:
        state.metadata_input.run_method("on", "blur")  # Trigger autosave

    # Load the new image
    await load_image(images[new_index])
