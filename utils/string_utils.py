# utils/string_utils.py 🔠
def convert_to_ascii(text:str):
    """Converts special characters to ASCII for EXIF"""
    text = str(text)
    replacements = {"å": "aa", "æ": "ae", "ø": "oe", "é": "e", "ü": "u"}
    for special_char, ascii in replacements.items():
        text = text.replace(special_char, ascii)
    return str(text)

def convert_from_ascii(text:str):
    """Converts EXIF ASCII to special characters"""
    text = str(text)
    replacements = {"å": "aa", "æ": "ae", "ø": "oe", "é": "e", "ü": "u"}
    for special_char, ascii in replacements.items():
        text = text.replace(ascii, special_char)
    return str(text)
