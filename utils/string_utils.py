# utils/string_utils.py 🔠
def convert_to_ascii(text):
    """Converts special characters to ASCII for EXIF"""
    replacements = {"å": "aa", "æ": "ae", "ø": "oe", "é": "e", "ü": "u"}
    for special_char, ascii in replacements.items():
        text = text.replace(special_char, ascii)
    return text

def convert_from_ascii(text):
    """Converts EXIF ASCII to special characters"""
    replacements = {"å": "aa", "æ": "ae", "ø": "oe", "é": "e", "ü": "u"}
    for special_char, ascii in replacements.items():
        text = text.replace(ascii, special_char)
    return text
