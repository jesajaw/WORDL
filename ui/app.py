"""
WORDL Filter -- tkinter UI.

Type your guesses, click tiles to set the colors Wordle showed you, and the list of
remaining words updates live. Look and feel are shared with mtools (see style.py,
widgets.py, dialogs.py); the constraint logic lives in src/filter.py.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from src.config import WORD_LENGTH, WINDOW_TITLE, LIST_COLUMNS, LIST_ROWS
from src.filter import Filter
from . import dialogs, style
from .widgets import Board, Cell

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title(WINDOW_TITLE)
        style.apply_style(root)

        try:
            self.filter = Filter()
        except OSError as e:
            dialogs.show_error(root, "Word list missing", f"Could not read words.txt:\n{e}")
            root.destroy()
            raise SystemExit(1)

        self._last_key = None
        self._build()
        root.bind("<Key>", self._on_key)
        self._update()
        self._size_to_content()

    # UI
    def _build(self) -> None:
        pad = dict(padx=10)

        self.board = Board(self.root, on_change=self._update)
        self.board.pack(pady=(0, 6))

        buttons = ttk.Frame(self.root)
        buttons.pack(fill="x", pady=(0, 8), **pad)
        Cell(buttons, "Clear", on_click=self.board.clear, height=40, width=80).pack(side="left", fill="x", expand=True, padx=(0, 4))
        Cell(buttons, "Undo", on_click=self.board.remove_last_row, height=40, width=80).pack(side="left", fill="x", expand=True, padx=(4, 0))

        info = ttk.Frame(self.root)
        info.pack(fill="x", pady=(0, 8), **pad)
        self.count_cell = Cell(info, "Possible words", status_text="", height=style.CELL_HEIGHT, width=120)
        self.count_cell.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        box = ttk.LabelFrame(self.root, text="Remaining words", padding=6)
        box.pack(fill="both", expand=True, pady=(0, 10), **pad)

        self.text = tk.Text(
            box, width=LIST_COLUMNS * (WORD_LENGTH + 2) - 2,
            height=LIST_ROWS, wrap="none", cursor="arrow",
            bg=style.COLOR_BG_LIGHT, fg=style.COLOR_STATUS_TEXT, font=style.FONT_MONO_LIST, relief="flat", borderwidth=0, highlightthickness=0, padx=8, pady=6, takefocus=0, selectbackground=style.COLOR_DARK, selectforeground=style.COLOR_FG, spacing1=2, spacing3=2,
        )

        
        scroll = ttk.Scrollbar(box, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        self.text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.text.tag_configure("word", foreground=style.COLOR_STATUS_TEXT)
        self.text.tag_configure("hint", foreground=style.COLOR_FG)
        self.text.tag_bind("word", "<Enter>", lambda _e: self.text.configure(cursor="hand2"))
        self.text.tag_bind("word", "<Leave>", lambda _e: self.text.configure(cursor="arrow"))
        self.text.bind("<Button-1>", self._on_word_click)
        self.text.configure(state="disabled")

    def _size_to_content(self) -> None:
        self.root.update_idletasks()
        width, height = self.root.winfo_reqwidth(), self.root.winfo_reqheight()
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(width, height)

    # keyboard / mouse
    def _on_key(self, event) -> None:
        key = event.keysym
        if key in ("BackSpace", "Delete"):
            self.board.backspace()
        elif key == "space":
            self.board.cycle()
        elif key == "Left":
            self.board.move(-1)
        elif key == "Right":
            self.board.move(1)
        elif key == "Up":
            self.board.move(-WORD_LENGTH)
        elif key == "Down":
            self.board.move(WORD_LENGTH)
        elif len(event.char) == 1 and event.char.isascii() and event.char.isalpha():
            self.board.put_letter(event.char)

    def _on_word_click(self, event):
        index = self.text.index(f"@{event.x},{event.y}")
        word = self.text.get(f"{index} wordstart", f"{index} wordend").strip()
        if len(word) == WORD_LENGTH and word.isalpha():
            self.board.fill_next_row(word)
        return "break"          # no text selection / caret in the read-only list

    # filtering
    def _update(self) -> None:
        rows = self.board.complete_rows()
        if rows == self._last_key:
            return
        self._last_key = rows

        self.filter.reset()
        for guess, pattern in rows:
            self.filter.add_guess(guess, pattern)
        words = self.filter.filter()

        self.count_cell.set_status(f"{len(words)} of {len(self.filter.wordlist)}")
        self._show_words(words)

    def _show_words(self, words: list[str]) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        if not words:
            self.text.insert("end", "No matches -- check the tile colors (new rows start all grey).", "hint")
        else:
            for i, word in enumerate(words):
                self.text.insert("end", word.upper(), "word")
                last_in_line = (i + 1) % LIST_COLUMNS == 0 or i == len(words) - 1
                self.text.insert("end", "\n" if last_in_line else "  ")
        self.text.configure(state="disabled")
        self.text.yview_moveto(0)


def run() -> None:
    style.enable_dpi_awareness()
    root = tk.Tk()
    App(root)
    root.mainloop()
