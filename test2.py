import ctypes
dll_test = ctypes.WinDLL(r'D:\GitHub\Repos\Image-Cataloger\tools\libjpeg-turbo\bin\turbojpeg.dll')
print(dll_test, "loaded successfully!")