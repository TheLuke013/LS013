import os

SYSTEM_NAME = "LS013"

#path dir
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WALLPAPERS_PATH = os.path.abspath(os.path.join(ROOT_PATH, "assets/wallpapers/"))
ICONS_PATH = os.path.abspath(os.path.join(ROOT_PATH, "assets/icons/"))
LOGS_PATH = os.path.abspath(os.path.join(ROOT_PATH, "logs/"))

#file dir
DEFAULT_WALLPAPER_FILENAME = os.path.abspath(os.path.join(WALLPAPERS_PATH, "macos-monterey-wwdc-21-stock-dark-mode-5k-3840x2160-5585.jpg"))
LOADING_SPINNER_ICON = os.path.abspath(os.path.join(ICONS_PATH, "loading_spinner.gif"))