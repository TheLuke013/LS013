import os

SYSTEM_NAME = "LS013"

#path dir
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WALLPAPERS_PATH = os.path.abspath(os.path.join(ROOT_PATH, "assets/wallpapers/"))
ICONS_PATH = os.path.abspath(os.path.join(ROOT_PATH, "assets/icons/"))
LOGS_PATH = os.path.abspath(os.path.join(ROOT_PATH, "logs/"))
USERS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "users/"))

#file dir
USERS_DATA_FILENAME = os.path.abspath(os.path.join(USERS_PATH, "users.json"))
DEFAULT_WALLPAPER_FILENAME = os.path.abspath(os.path.join(WALLPAPERS_PATH, "login.jpg"))
DEFAULT_DESKTOP_WALLPAPER_FILENAME = os.path.abspath(os.path.join(WALLPAPERS_PATH, "desktop_2.png"))
LOADING_SPINNER_ICON = os.path.abspath(os.path.join(ICONS_PATH, "loading_spinner.gif"))