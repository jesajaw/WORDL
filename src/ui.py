import tkinter as tk
from tkinter import ttk

import ctypes
import sys

from . import parameters
from . import Filter


class ThemedDialog(tk.Toplevel):
    def __init__(self, parent, title, message, buttons):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=parameters.COLOR_BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        force_dark_titlebar(parent)

        self.result = None

        ttk.Label(self, text=message, wraplength=280, justify="left").pack(padx=20, pady=(20, 10))

        btn_row = ttk.Frame(self)
        btn_row.pack(padx=20, pady=(0, 20))
        for label in buttons:
            ttk.Button(btn_row, text=label, command=lambda l=label: self._on_button(l)).pack(side="left", padx=5)

        self.bind("<Escape>", lambda e: self._on_button(None))
        self.protocol("WM_DELETE_WINDOW", lambda: self._on_button(None))

        self.update_idletasks()
        self._center_on(parent)
        self.wait_window(self)

    def _center_on(self, parent):
        x = parent.winfo_rootx() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _on_button(self, label):
        self.result = label
        self.grab_release()
        self.destroy()


class LetterTile(tk.Frame):
    def __init__(self, parent, on_change=None, on_state_change=None):
        super().__init__(parent, width=56, height=56, takefocus=1, highlightthickness=2, highlightbackground=parameters.TILE_BORDER, highlightcolor=parameters.TILE_BORDER)
        self.pack_propagate(False)
        self.on_change = on_change
        self.on_state_change = on_state_change
        self.letter = ""
        self.state = "empty"

        self.label = tk.Label(self, text="", font=("Helvetica", 22, "bold"), fg=parameters.TILE_TEXT)
        self.label.pack(expand=True, fill="both")

        self.bind("<Button-1>", self._cycle_state)
        self.label.bind("<Button-1>", self._cycle_state)
        self.bind("<Key>", self._on_key)

        self._redraw()

    # interactive editing -----------------------------------------
    def _on_key(self, event):
        if event.keysym == "Tab":
            return
        if event.keysym in ("BackSpace", "Delete"):
            had_letter = bool(self.letter)
            self.set_letter("")
            if self.on_change:
                self.on_change(self, backspace=not had_letter)
            return "break"
        if event.keysym == "space":
            self._cycle_state()
            return "break"
        ch = event.char
        if len(ch) == 1 and ch.isalpha():
            self.set_letter(ch.upper())
            if self.on_change:
                self.on_change(self, advance=True)
        return "break"

    def _cycle_state(self, event=None):
        if not self.letter:
            return "break"
        current = parameters.CYCLE.index(self.state) if self.state in parameters.CYCLE else -1
        self.state = parameters.CYCLE[(current + 1) % len(parameters.CYCLE)]
        self._redraw()
        if self.on_state_change:
            self.on_state_change()
        return "break"

    # programmatic control ------------------------------------------
    def set_letter(self, letter):
        self.letter = letter
        if letter and self.state == "empty":
            self.state = "absent"
        elif not letter:
            self.state = "empty"
        self._redraw()
        if self.on_state_change:
            self.on_state_change()

    def clear(self):
        self.letter = ""
        self.state = "empty"
        self._redraw()
        if self.on_state_change:
            self.on_state_change()

    def _redraw(self):
        bg = {
            "empty": parameters.COLOR_BG,
            "absent": parameters.TILE_ABSENT,
            "present": parameters.TILE_PRESENT,
            "correct": parameters.TILE_CORRECT,
        }[self.state]
        self.configure(bg=bg)
        self.label.configure(bg=bg, text=self.letter)


class Board(ttk.Frame):
    def __init__(self, parent, on_change=None):
        super().__init__(parent)
        self.on_change = on_change
        self.rows = []
        for r in range(parameters.MAX_GUESSES):
            row_frame = ttk.Frame(self)
            row_frame.pack(pady=3)
            row_tiles = []
            for c in range(parameters.WORD_LENGTH):
                tile = LetterTile(row_frame, on_change=self._make_on_change(r, c), on_state_change=self.on_change)
                tile.grid(row=0, column=c, padx=3)
                row_tiles.append(tile)
            self.rows.append(row_tiles)

    def _make_on_change(self, r, c):
        def handler(tile, advance=False, backspace=False):
            if advance:
                if c + 1 < parameters.WORD_LENGTH:
                    self.rows[r][c + 1].focus_set()
                elif r + 1 < parameters.MAX_GUESSES:
                    self.rows[r + 1][0].focus_set()
            elif backspace:
                if c - 1 >= 0:
                    self.rows[r][c - 1].clear()
                    self.rows[r][c - 1].focus_set()
                elif r - 1 >= 0:
                    self.rows[r - 1][parameters.WORD_LENGTH - 1].focus_set()
        return handler

    def focus_first_tile(self):
        self.rows[0][0].focus_set()

    def clear(self):
        for row in self.rows:
            for tile in row:
                tile.clear()
        self.focus_first_tile()


class FilterUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WORDL Filter")
        self.root.resizable(False, False)
        self.root.configure(bg=parameters.COLOR_BG)

        apply_dark_titlebar(root)

        self.wf = Filter()
        self._filter_job = None

        self._setup_style()
        self._build_board()
        self._build_actions()
        self._build_result_area()

        self.board.focus_first_tile()
        self._run_filter_now()

    # Styling
    def _setup_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(".", background=parameters.COLOR_BG, foreground=parameters.COLOR_FG, font=("Segoe UI", 9))
        style.configure("TFrame", background=parameters.COLOR_BG)
        style.configure("TLabel", background=parameters.COLOR_BG, foreground=parameters.COLOR_FG)

        style.configure("TButton", background=parameters.COLOR_BG_LIGHT, foreground=parameters.COLOR_FG,
                         bordercolor=parameters.COLOR_DARK, focusthickness=1, padding=6)
        style.map("TButton",
                  background=[("active", parameters.COLOR_DARK), ("pressed", parameters.COLOR)],
                  foreground=[("active", parameters.COLOR_FG)])

        style.configure("Count.TLabel", background=parameters.COLOR_BG, foreground=parameters.COLOR_STATUS_TEXT,
                         font=("Segoe UI", 9, "bold"))
        style.configure(
            "Vertical.TScrollbar",
            gripcount=0,
            background=parameters.COLOR_BG_LIGHT,
            darkcolor=parameters.COLOR_BG,
            lightcolor=parameters.COLOR_BG,
            troughcolor=parameters.COLOR_BG,
            bordercolor=parameters.COLOR_BG,
            arrowcolor=parameters.COLOR_FG,
        )

        style.map("TButton", background=[("active", parameters.COLOR_DARK), ("pressed", parameters.COLOR),], foreground=[("active", parameters.COLOR_FG)])

        style.configure("Count.TLabel", background=parameters.COLOR_BG, foreground=parameters.COLOR_STATUS_TEXT, font=("Segoe UI", 9, "bold"))

        # arrows out 
        style.layout("Vertical.TScrollbar", [("Vertical.Scrollbar.trough", {"sticky": "ns", "children": [("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "ns"})],},)],)
        style.configure("Vertical.TScrollbar", width=20, background=parameters.COLOR, darkcolor=parameters.COLOR, lightcolor=parameters.COLOR, bordercolor=parameters.COLOR_BG, troughcolor=parameters.COLOR_BG)
        style.map("Vertical.TScrollbar", background=[("active", parameters.COLOR), ("pressed", parameters.COLOR)], darkcolor=[("active", parameters.COLOR), ("pressed", parameters.COLOR)], lightcolor=[("active", parameters.COLOR), ("pressed", parameters.COLOR)])

    # UI
    def _build_board(self):
        board_frame = ttk.Frame(self.root, padding=10)
        board_frame.pack()
        self.board = Board(board_frame, on_change=self._schedule_filter)
        self.board.pack()

    def _build_actions(self):
        bar = ttk.Frame(self.root, padding=(10, 0, 10, 5))
        bar.pack()
        ttk.Button(bar, text="Clear", command=self.clear_board).pack(side="left", padx=5)

    def _build_result_area(self):
        result = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        result.pack(fill="both", expand=True)

        self.count_label = ttk.Label(result, text="0 possible words", style="Count.TLabel")
        self.count_label.pack(anchor="w", pady=(0, 5))

        text_container = ttk.Frame(result).pack(fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(text_container, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")
        self.text_result = tk.Text(
            text_container,
            width=60,
            height=14,
            relief="flat",
            font=parameters.RESULT_FONT,
            bg=parameters.COLOR_BG_LIGHT,
            fg=parameters.COLOR_FG,
            insertbackground=parameters.COLOR_FG,
            selectbackground=parameters.COLOR_DARK,
            yscrollcommand=self.scrollbar.set,
            state="disabled"
        )
        self.text_result.pack(side="left", fill="both", expand=True)

        self.scrollbar.config(command=self.text_result.yview)

    
    # Live filtering
    def _schedule_filter(self):
        # Debounced auto-filter: cancel any pending run and schedule a fresh one shortly after the most recent tile change. A burst of quick edits collapses into a single recompute instead of one per keystroke.
        if self._filter_job is not None:
            self.root.after_cancel(self._filter_job)
        self._filter_job = self.root.after(parameters.FILTER_DEBOUNCE_MS, self._run_filter_now)

    def _run_filter_now(self):
        self._filter_job = None
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
        self.count_label.config(text=f"{len(results)} possible word(s)")
        self.text_result.config(state="normal")
        self.text_result.delete("1.0", tk.END)
        self.text_result.insert(tk.END, self._format_results(results))
        self.text_result.config(state="disabled")

    @staticmethod
    def _format_results(words):
        # Lays the word list out in aligned, uppercase columns
        if not words:
            return "No matches."
        upper = [w.upper() for w in words]
        col_width = max(len(w) for w in upper) + 3
        lines = []
        for i in range(0, len(upper), parameters.RESULT_COLUMNS):
            row = upper[i:i + parameters.RESULT_COLUMNS]
            lines.append("".join(w.ljust(col_width) for w in row))
        return "\n".join(lines)

    def clear_board(self):
        self.board.clear()
        self.wf.reset()
        self._run_filter_now()

# Windows-only visual fixes tkinter doesn't handle by itself: DPI awareness (fixes
# blurry/blocky text on HiDPI displays) and a dark title bar to match the theme.
# Both are no-ops on non-Windows.
def _is_win() -> bool:
    return sys.platform == "win32"

def enable_dpi_awareness() -> None:
    if not _is_win():
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_SYSTEM_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # fallback for older Windows
        except Exception:
            pass

def apply_dark_titlebar(window) -> None:
    if not _is_win():
        return
    window.update_idletasks()
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    for attribute in (20, 19):  # DWMWA_USE_IMMERSIVE_DARK_MODE: 20 (Win10 2004+), 19 (older)
        value = ctypes.c_int(1)
        result = ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attribute, ctypes.byref(value), ctypes.sizeof(value))
        if result == 0:
            break

def force_dark_titlebar(window) -> None:
        if not _is_win():
            return
        try:
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            rendering_policy = ctypes.c_int(2)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(rendering_policy), ctypes.sizeof(rendering_policy))
        except Exception:
            pass