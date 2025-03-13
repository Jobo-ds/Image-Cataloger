# utils/string_utils.py 🔠
def convert_to_ascii(text):
    """Converts special characters to ASCII for EXIF fallback."""
    replacements = {"å": "aa", "æ": "ae", "ø": "oe", "é": "e", "ü": "u"}
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)
    return text
