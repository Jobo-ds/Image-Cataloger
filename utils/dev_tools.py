# utils/dev_tools.py
import psutil
from utils.state import state
import config

def display_memory_usage():
    """Displays current memory usage (for debugging)."""
    process = psutil.Process()
    mem_usage = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB
    print(f"Memory Usage: {mem_usage:.2f} MB | Buffer Size: {len(state.image_buffer)}/{config.IMAGE_BUFFER_SIZE}")