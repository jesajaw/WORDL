"""
Wordle Word Filter
===================

Tkinter GUI that filters a 5-letter word list down to the words that
are still possible, based on the clues Wordle gives you.

Clue entry is a tile board that looks like NYT Wordle:
    - click a tile, type a letter -> focus auto-advances to the next tile
    - right-click (or Space while focused) cycles that tile's color:
      grey (absent) -> yellow (present) -> green (correct) -> grey ...
You can fill in as many guess rows as you've actually played; every
row with letters/colors contributes to the filter.

Clue handling
-------------
A "grey" letter only excludes a word if that letter isn't *also*
marked yellow or green somewhere else (any row, any column). This
covers repeated-letter cases correctly (e.g. the answer has one "e",
you guessed two: one came back green, the other grey).

Theming
-------
Same approach as the DMX Derby Controller project: pick ONE color
block below and comment out the others, then restart the app.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext

from wordlist import WORDS

WORD_LENGTH = 5
MAX_GUESSES = 6  # same as the real game


# Theme — uncomment ONE block, comment out the others
# dark grey / purple
COLOR_BG = "#1e1e24"; COLOR_BG_LIGHT = "#2a2a33"; COLOR_FG = "#e0dff0"; COLOR = "#9b59d9"; COLOR_DARK = "#6c3fa0"; COLOR_STATUS_TEXT = "#c9a6f5"

# dark grey / blue
# COLOR_BG = "#1e1e24"; COLOR_BG_LIGHT = "#2a2a33"; COLOR_FG = "#e0dff0"; COLOR = "#4a90d9"; COLOR_DARK = "#2f5f9e"; COLOR_STATUS_TEXT = "#a6c9f5"

# black / white
# COLOR_BG = "#000000"; COLOR_BG_LIGHT = "#1a1a1a"; COLOR_FG = "#ffffff"; COLOR = "#ffffff"; COLOR_DARK = "#808080"; COLOR_STATUS_TEXT = "#d9d9d9"


# Tile colors are fixed to the real NYT Wordle palette (dark mode) on
# purpose, regardless of which theme block above is active, so the
# board stays instantly recognizable.
TILE_ABSENT = "#3a3a3c"
TILE_PRESENT = "#b59f3b"
TILE_CORRECT = "#538d4e"
TILE_BORDER = "#565758"
TILE_TEXT = "#ffffff"


class WordleFilter:
    """Filters a word list based on Wordle-style clues."""

    def __init__(self, wordlist, word_length=WORD_LENGTH):
        self.word_length = word_length
        self.wordlist = [
            w.strip().lower() for w in wordlist
            if len(w.strip()) == word_length
        ]
        self.reset()

    def reset(self):
        """Clears all clues (the loaded word list itself is kept)."""
        self.absent_letters = set()   # grey: not in the word at all
        self.present_letters = {}     # yellow: letter -> {excluded positions}
        self.fixed_positions = {}     # green: position -> letter

    def add_absent(self, letters):
        self.absent_letters.update(letters)

    def add_present(self, letter, position):
        """`position` is 0-indexed. The letter is known to be in the
        word, just not at this position."""
        self.present_letters.setdefault(letter, set()).add(position)

    def add_fixed(self, position, letter):
        self.fixed_positions[position] = letter

    def _matches(self, word):
        # green: letter must sit exactly here
        for pos, letter in self.fixed_positions.items():
            if pos >= len(word) or word[pos] != letter:
                return False

        # yellow: letter must be in the word, just not at these positions
        for letter, excluded_positions in self.present_letters.items():
            if letter not in word:
                return False
            for pos in excluded_positions:
                if pos < len(word) and word[pos] == letter:
                    return False

        # grey: letter must not appear at all, UNLESS it's also
        # confirmed present elsewhere (duplicate-letter case)
        known_present = set(self.fixed_positions.values()) | set(self.present_letters)
        for letter in self.absent_letters:
            if letter in known_present:
                continue
            if letter in word:
                return False

        return True

    def filter(self):
        return [w for w in self.wordlist if self._matches(w)]


# ------------------------------------------------------------
# Themed popups, same approach as the DMX Derby Controller project
# (nicer than the default tkinter.messagebox, and follows the
# active theme instead of using the OS dialog style)
# ------------------------------------------------------------
class ThemedDialog(tk.Toplevel):
    """Modal popup styled to match the app's color theme."""

    def __init__(self, parent, title, message, buttons):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=COLOR_BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result = None

        ttk.Label(self, text=message, wraplength=280, justify="left").pack(
            padx=20, pady=(20, 10)
        )

        btn_row = ttk.Frame(self)
        btn_row.pack(padx=20, pady=(0, 20))
        for label in buttons:
            ttk.Button(
                btn_row, text=label,
                command=lambda l=label: self._on_button(l),
            ).pack(side="left", padx=5)

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


def show_error(parent, title, message):
    ThemedDialog(parent, title, message, buttons=["OK"])


def ask_yes_no(parent, title, message):
    dlg = ThemedDialog(parent, title, message, buttons=["Yes", "No"])
    return dlg.result == "Yes"


# ------------------------------------------------------------
# NYT-style letter tile
# ------------------------------------------------------------
class LetterTile(tk.Frame):
    """A single Wordle tile: click + type a letter, right-click (or
    Space while focused) cycles absent -> present -> correct."""

    SIZE = 56
    CYCLE = ["absent", "present", "correct"]

    def __init__(self, parent, on_change=None, interactive=True):
        super().__init__(
            parent, width=self.SIZE, height=self.SIZE,
            highlightthickness=2, highlightbackground=TILE_BORDER,
            highlightcolor=TILE_BORDER,
        )
        self.pack_propagate(False)
        self.on_change = on_change
        self.letter = ""
        self.state = "empty"  # empty -> absent -> present -> correct

        self.label = tk.Label(self, text="", font=("Helvetica", 22, "bold"), fg=TILE_TEXT)
        self.label.pack(expand=True, fill="both")

        if interactive:
            self.configure(takefocus=1)
            self.bind("<Button-1>", lambda e: self.focus_set())
            self.label.bind("<Button-1>", lambda e: self.focus_set())
            self.bind("<Button-3>", self._cycle_state)
            self.label.bind("<Button-3>", self._cycle_state)
            self.bind("<Key>", self._on_key)

        self._redraw()

    # -- interactive editing -----------------------------------------
    def _on_key(self, event):
        if event.keysym == "Tab":
            return  # let normal focus traversal happen
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
        current = self.CYCLE.index(self.state) if self.state in self.CYCLE else -1
        self.state = self.CYCLE[(current + 1) % len(self.CYCLE)]
        self._redraw()
        return "break"

    # -- programmatic control ------------------------------------------
    def set_letter(self, letter):
        self.letter = letter
        if letter and self.state == "empty":
            self.state = "absent"
        elif not letter:
            self.state = "empty"
        self._redraw()

    def preset(self, letter, state):
        """Set letter + state directly, for non-interactive legend tiles."""
        self.letter = letter
        self.state = state
        self._redraw()

    def clear(self):
        self.letter = ""
        self.state = "empty"
        self._redraw()

    def _redraw(self):
        bg = {
            "empty": COLOR_BG,
            "absent": TILE_ABSENT,
            "present": TILE_PRESENT,
            "correct": TILE_CORRECT,
        }[self.state]
        self.configure(bg=bg)
        self.label.configure(bg=bg, text=self.letter)


class WordleBoard(ttk.Frame):
    """A grid of guess rows, each MAX_GUESSES x WORD_LENGTH tiles."""

    def __init__(self, parent):
        super().__init__(parent)
        self.rows = []
        for r in range(MAX_GUESSES):
            row_frame = ttk.Frame(self)
            row_frame.pack(pady=3)
            row_tiles = []
            for c in range(WORD_LENGTH):
                tile = LetterTile(row_frame, on_change=self._make_on_change(r, c))
                tile.grid(row=0, column=c, padx=3)
                row_tiles.append(tile)
            self.rows.append(row_tiles)

    def _make_on_change(self, r, c):
        def handler(tile, advance=False, backspace=False):
            if advance and c + 1 < WORD_LENGTH:
                self.rows[r][c + 1].focus_set()
            elif backspace and c - 1 >= 0:
                self.rows[r][c - 1].clear()
                self.rows[r][c - 1].focus_set()
        return handler

    def clear(self):
        for row in self.rows:
            for tile in row:
                tile.clear()


class WordleFilterApp:
    """Tkinter UI for the Wordle Word Filter."""

    def __init__(self, root):
        self.root = root
        self.root.title("Wordle Word Filter")
        self.root.resizable(False, False)
        self.root.configure(bg=COLOR_BG)

        self.wf = WordleFilter(WORDS)

        self._setup_style()
        self._build_legend()
        self._build_board()
        self._build_actions()
        self._build_result_area()

    # ------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------
    def _setup_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(".", background=COLOR_BG, foreground=COLOR_FG, font=("Segoe UI", 9))
        style.configure("TFrame", background=COLOR_BG)
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_FG)

        style.configure("TButton", background=COLOR_BG_LIGHT, foreground=COLOR_FG,
                         bordercolor=COLOR_DARK, focusthickness=1, padding=6)
        style.map("TButton",
                  background=[("active", COLOR_DARK), ("pressed", COLOR)],
                  foreground=[("active", COLOR_FG)])

        style.configure("Filter.TButton", background=COLOR_DARK, foreground=COLOR_FG)
        style.map("Filter.TButton", background=[("active", COLOR)])

        style.configure("Count.TLabel", background=COLOR_BG, foreground=COLOR_STATUS_TEXT,
                         font=("Segoe UI", 9, "bold"))
        style.configure("Legend.TLabel", background=COLOR_BG, foreground=COLOR_FG,
                         font=("Segoe UI", 8))

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------
    def _build_legend(self):
        legend = ttk.Frame(self.root, padding=(10, 10, 10, 0))
        legend.pack(fill="x")

        examples = [
            ("W", "correct", "is in the word and in the correct spot."),
            ("I", "present", "is in the word but in the wrong spot."),
            ("U", "absent", "is not in the word in any spot."),
        ]
        for letter, state, caption in examples:
            item = ttk.Frame(legend)
            item.pack(side="left", padx=(0, 20))
            tile = LetterTile(item, interactive=False)
            tile.preset(letter, state)
            tile.pack()
            ttk.Label(item, text=f"{letter} {caption}", style="Legend.TLabel",
                      wraplength=140, justify="left").pack(pady=(4, 0))

    def _build_board(self):
        board_frame = ttk.Frame(self.root, padding=10)
        board_frame.pack()
        self.board = WordleBoard(board_frame)
        self.board.pack()

    def _build_actions(self):
        bar = ttk.Frame(self.root, padding=(10, 0, 10, 5))
        bar.pack()
        ttk.Button(bar, text="Filter", command=self.run_filter,
                   style="Filter.TButton").pack(side="left", padx=5)
        ttk.Button(bar, text="Clear board", command=self.clear_board).pack(side="left", padx=5)

    def _build_result_area(self):
        result = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        result.pack(fill="both", expand=True)

        self.count_label = ttk.Label(result, text="0 possible words", style="Count.TLabel")
        self.count_label.pack(anchor="w", pady=(0, 5))

        self.text_result = scrolledtext.ScrolledText(
            result, width=60, height=14, relief="flat",
            bg=COLOR_BG_LIGHT, fg=COLOR_FG, insertbackground=COLOR_FG,
            selectbackground=COLOR_DARK,
        )
        self.text_result.pack(fill="both", expand=True)

    # ------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------
    def run_filter(self):
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
        self.text_result.delete("1.0", tk.END)
        self.text_result.insert(tk.END, "\n".join(results))

    def clear_board(self):
        if not ask_yes_no(self.root, "Clear board", "Clear all tiles and start over?"):
            return
        self.board.clear()
        self.wf.reset()
        self.count_label.config(text="0 possible words")
        self.text_result.delete("1.0", tk.END)


def main():
    root = tk.Tk()
    WordleFilterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()