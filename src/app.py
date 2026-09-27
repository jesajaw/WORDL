import ctypes
import os
import string
import sys

import dearpygui.dearpygui as dpg

from . import parameters
from . import Filter


# ---------------------------------------------------------------------------
# Windows-only DPI / native-window helpers. No-ops on non-Windows platforms.
# ---------------------------------------------------------------------------
def _is_win() -> bool:
    return sys.platform == "win32"


def enable_dpi_awareness() -> None:
    """Must run BEFORE dpg.create_context()/the viewport is created."""
    if not _is_win():
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # fallback for older Windows
        except Exception:
            pass


def get_dpi_scale() -> float:
    """Best-effort scale factor of the primary monitor (1.0, 1.25, 1.5, ...)."""
    if not _is_win():
        return 1.0
    try:
        MONITOR_DEFAULTTOPRIMARY = 1
        hmonitor = ctypes.windll.user32.MonitorFromWindow(
            ctypes.windll.user32.GetDesktopWindow(), MONITOR_DEFAULTTOPRIMARY
        )
        dpi_x = ctypes.c_uint()
        dpi_y = ctypes.c_uint()
        ctypes.windll.shcore.GetDpiForMonitor(hmonitor, 0, ctypes.byref(dpi_x), ctypes.byref(dpi_y))
        return dpi_x.value / 96.0
    except Exception:
        return 1.0


def center_viewport(width: int, height: int) -> None:
    if not _is_win():
        return
    try:
        screen_w = ctypes.windll.user32.GetSystemMetrics(0)
        screen_h = ctypes.windll.user32.GetSystemMetrics(1)
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        dpg.set_viewport_pos([x, y])
    except Exception:
        pass


def apply_dark_titlebar_by_title(title: str) -> None:
    """Finds the OS window by its title and forces a dark titlebar (DWM)."""
    if not _is_win():
        return
    try:
        hwnd = ctypes.windll.user32.FindWindowW(None, title)
        if not hwnd:
            return
        for attribute in (20, 19):  # DWMWA_USE_IMMERSIVE_DARK_MODE: 20 (Win10 2004+), 19 (older)
            value = ctypes.c_int(1)
            result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, attribute, ctypes.byref(value), ctypes.sizeof(value)
            )
            if result == 0:
                break
    except Exception:
        pass


def _setup_fonts(scale: float):
    """Loads real TTFs at a DPI-scaled pixel size for crisp text instead of
    stretching Dear PyGui's built-in bitmap font (which looks blurry).

    Returns (loaded_ui_font: bool, mono_font_id_or_None). The results word
    list is column-aligned with fixed-width padding, which only lines up
    correctly with a MONOSPACE font - Segoe UI/Arial are proportional and
    would misalign (and can wrap oddly) the word columns.
    """
    ui_size = max(13, round(16 * scale))
    mono_size = max(13, round(15 * scale))

    ui_candidates = [
        r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    mono_candidates = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\cour.ttf",
    ]

    loaded_ui = False
    mono_font = None

    with dpg.font_registry():
        for path in ui_candidates:
            if os.path.exists(path):
                font = dpg.add_font(path, ui_size)
                dpg.bind_font(font)
                loaded_ui = True
                break

        for path in mono_candidates:
            if os.path.exists(path):
                mono_font = dpg.add_font(path, mono_size)
                break

    return loaded_ui, mono_font


def _key_const(*names):
    for name in names:
        if hasattr(dpg, name):
            return getattr(dpg, name)
    return None


def _theme_color(name, value):
    """Adds a theme color only if this DPG version exposes that constant."""
    const = getattr(dpg, name, None)
    if const is not None:
        dpg.add_theme_color(const, value)


def _theme_style(name, *args):
    """Adds a theme style only if this DPG version exposes that constant."""
    const = getattr(dpg, name, None)
    if const is not None:
        dpg.add_theme_style(const, *args)


# Key constants differ between Dear PyGui versions (e.g. mvKey_Space vs.
# mvKey_Spacebar). Resolve once, with fallbacks, instead of hard failing.
KEY_BACKSPACE = _key_const("mvKey_Back", "mvKey_Backspace")
KEY_DELETE = _key_const("mvKey_Delete")
KEY_SPACE = _key_const("mvKey_Spacebar", "mvKey_Space")

WINDOW_TITLE = "WORDL Filter"
TILE_SIZE = 62
TILE_GAP = 6


class LetterTile:
    """A single 5x5 Wordle-style tile implemented with a Dear PyGui button."""

    def __init__(self, owner, row, col):
        self.owner = owner
        self.row = row
        self.col = col
        self.letter = ""
        self.state = "empty"
        self.tag = f"tile_{row}_{col}"

        dpg.add_button(
            label="",
            tag=self.tag,
            width=TILE_SIZE,
            height=TILE_SIZE,
            callback=self._cycle_state,
            user_data=(row, col),
        )
        self.redraw()

    def set_letter(self, letter):
        self.letter = letter.upper() if letter else ""
        if self.letter and self.state == "empty":
            self.state = "absent"
        elif not self.letter:
            self.state = "empty"
        self.redraw()
        self.owner.on_tile_changed()

    def clear(self, notify=True):
        self.letter = ""
        self.state = "empty"
        self.redraw()
        if notify:
            self.owner.on_tile_changed()

    def cycle_state(self):
        if not self.letter:
            return

        cycle = parameters.CYCLE
        try:
            current = cycle.index(self.state)
        except ValueError:
            current = -1

        self.state = cycle[(current + 1) % len(cycle)]
        self.redraw()
        self.owner.on_tile_changed()

    def _cycle_state(self, sender=None, app_data=None, user_data=None):
        self.cycle_state()

    def redraw(self):
        label = self.letter or " "
        dpg.configure_item(self.tag, label=label)

        focused = self.owner.is_focused(self.row, self.col)
        theme_set = self.owner.focus_themes if focused else self.owner.themes
        dpg.bind_item_theme(self.tag, theme_set[self.state])


class Board:
    def __init__(self, owner):
        self.owner = owner
        self.rows = []

        with dpg.group():
            for row in range(parameters.MAX_GUESSES):
                with dpg.group(horizontal=True):
                    tiles = []
                    for col in range(parameters.WORD_LENGTH):
                        tile = LetterTile(owner, row, col)
                        tiles.append(tile)
                        if col < parameters.WORD_LENGTH - 1:
                            dpg.add_spacer(width=TILE_GAP)
                if row < parameters.MAX_GUESSES - 1:
                    dpg.add_spacer(height=TILE_GAP)
                self.rows.append(tiles)

    def tile(self, row, col):
        return self.rows[row][col]

    def clear(self):
        for row in self.rows:
            for tile in row:
                tile.clear(notify=False)
        self.owner.set_focus(0, 0)

    def focus_first_tile(self):
        self.owner.set_focus(0, 0)

    def advance(self):
        row, col = self.owner.focus_row, self.owner.focus_col
        if col + 1 < parameters.WORD_LENGTH:
            self.owner.set_focus(row, col + 1)
        elif row + 1 < parameters.MAX_GUESSES:
            self.owner.set_focus(row + 1, 0)

    def backspace(self):
        row, col = self.owner.focus_row, self.owner.focus_col

        current = self.tile(row, col)
        if current.letter:
            current.clear()
            return

        if col > 0:
            self.owner.set_focus(row, col - 1)
            self.tile(row, col - 1).clear()
        elif row > 0:
            self.owner.set_focus(row - 1, parameters.WORD_LENGTH - 1)
            self.tile(row - 1, parameters.WORD_LENGTH - 1).clear()


class FilterUI:
    WINDOW_WIDTH = 760

    def __init__(self, mono_font=None):
        self.wf = Filter()
        self.focus_row = 0
        self.focus_col = 0
        self.themes = {}
        self.focus_themes = {}
        self.mono_font = mono_font

        self._create_themes()
        self._apply_global_theme()
        self._create_ui()
        self._run_filter_now()

    # ------------------------------------------------------------------
    # Dear PyGui setup
    # ------------------------------------------------------------------

    def _create_themes(self):
        def tile_theme(bg, fg=parameters.TILE_TEXT, border=parameters.TILE_BORDER, border_size=1):
            with dpg.theme() as theme:
                with dpg.theme_component(dpg.mvButton):
                    _theme_color("mvThemeCol_Button", self._rgb(bg))
                    _theme_color("mvThemeCol_ButtonHovered", self._rgb(bg))
                    _theme_color("mvThemeCol_ButtonActive", self._rgb(bg))
                    _theme_color("mvThemeCol_Text", self._rgb(fg))
                    _theme_style("mvStyleVar_FrameRounding", 3)
                    _theme_style("mvStyleVar_FrameBorderSize", border_size)
                    _theme_color("mvThemeCol_Border", self._rgb(border))
            return theme

        focus_border = getattr(parameters, "TILE_FOCUS_BORDER", parameters.COLOR)

        states = {
            "empty": parameters.COLOR_BG,
            "absent": parameters.TILE_ABSENT,
            "present": parameters.TILE_PRESENT,
            "correct": parameters.TILE_CORRECT,
        }
        for state, bg in states.items():
            self.themes[state] = tile_theme(bg)
            self.focus_themes[state] = tile_theme(bg, border=focus_border, border_size=2)

    def _apply_global_theme(self):
        with dpg.theme() as theme:
            with dpg.theme_component(dpg.mvAll):
                _theme_color("mvThemeCol_WindowBg", self._rgb(parameters.COLOR_BG))
                _theme_color("mvThemeCol_ChildBg", self._rgb(parameters.COLOR_BG))
                _theme_color("mvThemeCol_PopupBg", self._rgb(parameters.COLOR_BG))
                _theme_color("mvThemeCol_Text", self._rgb(parameters.COLOR_FG))
                _theme_color("mvThemeCol_Border", self._rgb(parameters.COLOR_DARK))
                _theme_color("mvThemeCol_FrameBg", self._rgb(parameters.COLOR_BG_LIGHT))
                _theme_color("mvThemeCol_FrameBgHovered", self._rgb(parameters.COLOR_DARK))
                _theme_color("mvThemeCol_FrameBgActive", self._rgb(parameters.COLOR_DARK))
                _theme_color("mvThemeCol_ScrollbarBg", self._rgb(parameters.COLOR_BG))
                _theme_color("mvThemeCol_ScrollbarGrab", self._rgb(parameters.COLOR))
                _theme_color("mvThemeCol_ScrollbarGrabHovered", self._rgb(parameters.COLOR))
                _theme_color("mvThemeCol_ScrollbarGrabActive", self._rgb(parameters.COLOR))
                _theme_style("mvStyleVar_ScrollbarSize", 14)

            with dpg.theme_component(dpg.mvButton):
                _theme_color("mvThemeCol_Button", self._rgb(parameters.COLOR_BG_LIGHT))
                _theme_color("mvThemeCol_ButtonHovered", self._rgb(parameters.COLOR_DARK))
                _theme_color("mvThemeCol_ButtonActive", self._rgb(parameters.COLOR))
                _theme_style("mvStyleVar_FrameRounding", 4)
                _theme_style("mvStyleVar_FramePadding", 8, 6)

        dpg.bind_theme(theme)

    @staticmethod
    def _rgb(hex_color):
        value = hex_color.lstrip("#")
        return [int(value[i:i + 2], 16) for i in (0, 2, 4)] + [255]

    def _create_ui(self):
        with dpg.handler_registry():
            dpg.add_key_press_handler(
                callback=self._on_key_press,
                tag="wordl_key_handler",
            )

        content_width = self.WINDOW_WIDTH - 40  # rough allowance for window padding
        board_width = parameters.WORD_LENGTH * TILE_SIZE + (parameters.WORD_LENGTH - 1) * TILE_GAP
        board_height = parameters.MAX_GUESSES * TILE_SIZE + (parameters.MAX_GUESSES - 1) * TILE_GAP + 10
        clear_width = 140

        window_height = (
            8 + 30 + 14            # header + spacer
            + board_height + 12     # board + spacer
            + 32 + 16                # clear button + spacer
            + 24 + 8                  # count label + spacer
            + 280                      # result list
            + 100                       # chrome / safety margin (title bar, window padding, ...)
        )
        self.window_height = window_height

        with dpg.window(
            tag="main_window",
            label=WINDOW_TITLE,
            width=self.WINDOW_WIDTH,
            height=window_height,
            no_collapse=True,
            no_resize=False,
            no_scrollbar=True,
            no_scroll_with_mouse=True,
        ):
            dpg.add_spacer(height=8)

            with dpg.group(horizontal=True):
                dpg.add_text("WORDL", color=self._rgb(parameters.COLOR_STATUS_TEXT))
                dpg.add_text("  Wordle Filter")

            dpg.add_spacer(height=14)

            # No child_window here on purpose: a child_window adds its own
            # internal padding, which was silently clipping the 5th tile.
            # The board sits directly in the (centered) group instead.
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=max(0, (content_width - board_width) // 2))
                self.board = Board(self)

            dpg.add_spacer(height=12)

            with dpg.group(horizontal=True):
                dpg.add_spacer(width=max(0, (content_width - clear_width) // 2))
                dpg.add_button(label="Clear", width=clear_width, height=32, callback=self.clear_board)

            dpg.add_spacer(height=16)

            self.count_label = dpg.add_text(
                "0 possible words",
                color=self._rgb(parameters.COLOR_STATUS_TEXT),
            )

            dpg.add_spacer(height=8)

            self.result_text = dpg.add_input_text(
                tag="result_text",
                multiline=True,
                readonly=True,
                width=-1,
                height=280,
                default_value="",
            )
            if self.mono_font:
                try:
                    dpg.bind_item_font(self.result_text, self.mono_font)
                except Exception:
                    pass

        self.board.focus_first_tile()

    # ------------------------------------------------------------------
    # Focus handling
    # ------------------------------------------------------------------

    def is_focused(self, row, col):
        return self.focus_row == row and self.focus_col == col

    def set_focus(self, row, col):
        old_row, old_col = self.focus_row, self.focus_col
        self.focus_row, self.focus_col = row, col
        if hasattr(self, "board"):
            self.board.tile(old_row, old_col).redraw()
            self.board.tile(row, col).redraw()

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def _on_key_press(self, sender, app_data):
        key = app_data

        if KEY_BACKSPACE is not None and key in (KEY_BACKSPACE, KEY_DELETE):
            self.board.backspace()
            return

        if KEY_SPACE is not None and key == KEY_SPACE:
            self.board.tile(self.focus_row, self.focus_col).cycle_state()
            return

        if isinstance(key, int) and 65 <= key <= 90:
            self._put_letter(chr(key))
            return

        if isinstance(key, str) and len(key) == 1 and key in string.ascii_letters:
            self._put_letter(key)

    def _put_letter(self, letter):
        tile = self.board.tile(self.focus_row, self.focus_col)
        tile.set_letter(letter)
        self.board.advance()

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def on_tile_changed(self):
        self._run_filter_now()

    def _run_filter_now(self):
        self.wf.reset()

        for row in self.board.rows:
            for col, tile in enumerate(row):
                letter = tile.letter.lower()
                if not letter:
                    continue

                if tile.state == "correct":
                    self.wf.add_fixed(col, letter)
                elif tile.state == "present":
                    self.wf.add_present(letter, col)
                elif tile.state == "absent":
                    self.wf.add_absent(letter)

        results = self.wf.filter()

        dpg.set_value(self.count_label, f"{len(results)} possible word(s)")
        dpg.set_value(self.result_text, self._format_results(results))

    @staticmethod
    def _format_results(words):
        if not words:
            return "No matches."

        upper = [word.upper() for word in words]
        col_width = max(len(word) for word in upper) + 3
        lines = []

        for i in range(0, len(upper), parameters.RESULT_COLUMNS):
            row = upper[i:i + parameters.RESULT_COLUMNS]
            lines.append("".join(word.ljust(col_width) for word in row))

        return "\n".join(lines)

    def clear_board(self, sender=None, app_data=None, user_data=None):
        self.board.clear()
        self.wf.reset()
        self._run_filter_now()


def run():
    enable_dpi_awareness()
    dpg.create_context()

    scale = get_dpi_scale()
    loaded_ui_font, mono_font = _setup_fonts(scale)

    ui = FilterUI(mono_font=mono_font)

    viewport_width = ui.WINDOW_WIDTH + 20
    viewport_height = ui.window_height + 20

    dpg.create_viewport(
        title=WINDOW_TITLE,
        width=viewport_width,
        height=viewport_height,
    )
    center_viewport(viewport_width, viewport_height)

    dpg.setup_dearpygui()

    if not loaded_ui_font and scale and scale != 1.0:
        dpg.set_global_font_scale(scale)

    dpg.show_viewport()
    apply_dark_titlebar_by_title(WINDOW_TITLE)
    dpg.set_primary_window("main_window", True)

    dpg.start_dearpygui()
    dpg.destroy_context()
