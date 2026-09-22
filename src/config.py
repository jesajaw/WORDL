# jsut all global parameters / ui-stuff
class parameters:
    WORD_LENGTH = 5
    MAX_GUESSES = 6

    CYCLE = ["absent", "present", "correct"]

    FILTER_DEBOUNCE_MS = 150
    RESULT_COLUMNS = 6
    RESULT_FONT = ("Consolas", 11)

    _SCHEMES = {
        "dark_purple": dict(
            BG="#1e1e24", BG_LIGHT="#2a2a33", FG="#e0dff0",
            ACCENT="#9b59d9", ACCENT_DARK="#6c3fa0", STATUS_TEXT="#c9a6f5",
        ),
        "dark_blue": dict(
            BG="#1e1e24", BG_LIGHT="#2a2a33", FG="#e0dff0",
            ACCENT="#4a90d9", ACCENT_DARK="#2f5f9e", STATUS_TEXT="#a6c9f5",
        ),
        "black_white": dict(
            BG="#000000", BG_LIGHT="#1a1a1a", FG="#ffffff",
            ACCENT="#ffffff", ACCENT_DARK="#808080", STATUS_TEXT="#d9d9d9",
        ),
    }
    # Color schemes
    _active = _SCHEMES["dark_purple"]

    COLOR_BG = _active["BG"]
    COLOR_BG_LIGHT = _active["BG_LIGHT"]
    COLOR_FG = _active["FG"]
    COLOR = _active["ACCENT"]
    COLOR_DARK = _active["ACCENT_DARK"]
    COLOR_STATUS_TEXT = _active["STATUS_TEXT"]


    # Tile colors
    TILE_ABSENT = "#3a3a3c"
    TILE_PRESENT = "#b59f3b"
    TILE_CORRECT = "#538d4e"
    TILE_BORDER = "#565758"
    TILE_TEXT = "#ffffff"