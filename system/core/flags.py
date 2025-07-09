from enum import IntFlag, auto

class SystemFlags(IntFlag):
    NONE = 0
    SKIP_SPLASH_SCREEN = auto()
    SKIP_SHUTDOWN_SCREEN = auto()
    WINDOW_FULLSCREEN = auto()