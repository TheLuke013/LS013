import os

SYSTEM_NAME = "LS013"

#path dir
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SYSTEM_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WALLPAPERS_PATH = os.path.abspath(os.path.join(SYSTEM_PATH, "resources/wallpapers/"))
ICONS_PATH = os.path.abspath(os.path.join(SYSTEM_PATH, "resources/icons/"))
LOGS_PATH = os.path.abspath(os.path.join(SYSTEM_PATH, "logs/"))
USERS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "users/"))

#file dir
USERS_DATA_FILENAME = os.path.abspath(os.path.join(USERS_PATH, "users.json"))
DEFAULT_WALLPAPER_FILENAME = os.path.abspath(os.path.join(WALLPAPERS_PATH, "login.jpg"))
DEFAULT_DESKTOP_WALLPAPER_FILENAME = os.path.abspath(os.path.join(WALLPAPERS_PATH, "desktop_2.png"))

LOADING_SPINNER_ICON = os.path.abspath(os.path.join(ICONS_PATH, "loading_spinner.gif"))
CONFIG_ICON = os.path.abspath(os.path.join(ICONS_PATH, "config.png"))
POWER_ICON = os.path.abspath(os.path.join(ICONS_PATH, "power.png"))
APPS_ICON = os.path.abspath(os.path.join(ICONS_PATH, "apps.png"))
DOCUMENT_ICON = os.path.abspath(os.path.join(ICONS_PATH, "document.png"))