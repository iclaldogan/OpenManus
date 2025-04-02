import os
import urllib.request

# Replace with the actual image URL
image_url = "https://www.example.com/space_wallpaper.jpg"

# Save the image to a temporary file
image_path = "temp_wallpaper.jpg"
urllib.request.urlretrieve(image_url, image_path)

# Change the desktop background (platform-specific)
# For Windows:
# import ctypes
# SPI_SETDESKWALLPAPER = 0x0014
# ctypes.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)

# For Linux (using gnome): 
# os.system("gsettings set org.gnome.desktop.background picture-uri file://" + image_path)

# For macOS:
# os.system("osascript -e 'tell application "Finder" to set desktop picture to POSIX file "" + image_path + ""'")