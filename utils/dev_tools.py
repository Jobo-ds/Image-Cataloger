# utils/dev_tools.py
import psutil
from utils.state import state
import config
import time

def display_memory_usage():
    """Displays current memory usage (for debugging)."""
    process = psutil.Process()
    mem_usage = process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB
    #print(f"Memory Usage: {mem_usage:.2f} MB | Buffer Size: {len(state.image_buffer)}/{config.IMAGE_BUFFER_SIZE}")

def measure_execution_time(func, *args, **kwargs):
    """Measures execution time of a function."""
    start_time = time.perf_counter()  # Start the timer
    result = func(*args, **kwargs)    # Run the function
    end_time = time.perf_counter()    # Stop the timer
    elapsed_time = end_time - start_time
    print(f"{func.__name__} executed in {elapsed_time:.6f} seconds")
    return result, elapsed_time

async def async_measure_execution_time(func, *args, **kwargs):
    """Measures execution time of an async function."""
    start_time = time.perf_counter()
    result = await func(*args, **kwargs)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"{func.__name__} executed in {elapsed_time:.6f} seconds")
    return result, elapsed_time