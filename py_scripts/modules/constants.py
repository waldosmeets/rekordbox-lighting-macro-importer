# constants.py
import os

# SCREEN SIZES
SMALL_SCREEN = "600x250"
BIG_SCREEN = "600x600"

CONFIG_FILE = os.path.expanduser("~/.rekordbox_tool_config")
CACHE_DIR = os.path.expanduser("~/.rekordbox_tool_cache")
MACRO_DB_FILENAME = "macro.db3"
USER_DB_FILENAME = "user.db3"

# Default beats for macros
DEFAULT_BEATS = 64
DEFAULT_THUMBNAIL = "USER_SCENE.png"

# Energy level mapping
ENERGY_LEVEL_MAP = {
    "LOW": 3,
    "MID": 2,
    "HIGH": 1,
}
INVERTED_ENERGY_LEVEL_MAP = {value: key for key, value in ENERGY_LEVEL_MAP.items()}

# Bank mapping
BANK_MAP = {
    "COOL": 1,
    "NATURAL": 2,
    "HOT": 3,
    "SUBTLE": 4,
    "WARM": 5,
    "VIVID": 6,
    "CLUB1": 7,
    "CLUB2": 8,
    "AMBIENT": 99,
}
INVERTED_BANK_MAP = {value: key for key, value in BANK_MAP.items()}
