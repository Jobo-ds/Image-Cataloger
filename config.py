from pathlib import Path

# config.py 📂
DEVELOPMENT_MODE = True  # Set to False in production to hide debug info
AUTOLOAD_DEV_IMAGE = Path("test_files\jpg_large_file.jpg")

# Image Buffer Settings
IMAGE_CACHE_SIZE = 15  # Maximum number of images to store in memory
