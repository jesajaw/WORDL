"""
Reusable building blocks for WORDL's window:
- Cell: a clickable tile (title, optional status line, hover highlight) -- the same building block mtools is made of
- Tile: one Wordle letter tile (letter + clue color + focus border)
- Board: the 6x5 grid of tiles plus its data model (letters, clue states, focus, typing/editing helpers)
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from src.config import ABSENT, CYCLE, EMPTY, MAX_GUESSES, WORD_LENGTH
from . import style


class Cell(ttk.Frame):
    """
    A clickable tile: title, optional description/status line, hover highlight
    optional:
    - status_text is the description line: Leave it out (None, the default) for a cell that never shows one
    - on_click: leave it out for a plain, inert status tile (no hover, no click cursor, nothing bound)
    - extra_button: render an extra button (text, command) in the cell's corner
    """
    def __init__(self, parent, title: str, on_click=None, status_text: str | None = None, width: int = style.CELL_WIDTH, height: int = style.CELL_HEIGHT, extra_button=None):
        super().__init__(parent, padding=8, relief="groove", style="Cell.TFrame")
        wraplength = width - 20
        self.on_click = on_click
        self.pack_propagate(False)
        self.configure(width=width, height=height)

        self.title_label = ttk.Label(self, text=title, style="CellTitle.TLabel")
        self.title_label.pack(anchor="w")

        self.status_label = None
        clickable = [self, self.title_label]
        if status_text is not None:
            self.status_label = ttk.Label(self, text=status_text, style="Status.TLabel", wraplength=wraplength, justify="left")
            self.status_label.pack(anchor="w", pady=(4, 8), fill="x")
            clickable.append(self.status_label)

        if on_click is not None:
            for w in clickable:
                w.configure(cursor="hand2")
                w.bind("<Button-1>", self._on_click)
                w.bind("<Enter>", self._on_enter)
                w.bind("<Leave>", self._on_leave)

        if extra_button:
            text, command = extra_button
            ttk.Button(self, text=text, command=command).pack(anchor="e")

        self.bind("<Configure>", self._on_resize)

    def set_title(self, text: str) -> None:
        self.title_label.configure(text=text)

    def set_status(self, text: str) -> None:
        if self.status_label is not None:
            self.status_label.configure(text=text)

    def _on_click(self, _event=None) -> None:
        if self.on_click:
            self.on_click()

    def _on_enter(self, _event=None) -> None:
        self.configure(style="CellHover.TFrame")
        self.title_label.configure(style="CellTitleHover.TLabel")
        if self.status_label is not None:
            self.status_label.configure(style="StatusHover.TLabel")

    def _on_leave(self, _event=None) -> None:
        self.configure(style="Cell.TFrame")
        self.title_label.configure(style="CellTitle.TLabel")
        if self.status_label is not None:
            self.status_label.configure(style="Status.TLabel")

    def _on_resize(self, event) -> None:
        # Keep text reflowing with the cell's actual rendered width, not just its initial size.
        wrap = max(event.width - 20, 20)
        self.title_label.configure(wraplength=wrap)
        if self.status_label is not None:
            self.status_label.configure(wraplength=wrap)


class Tile(tk.Frame):
    # One letter tile: a colored label inside a frame whose color is the border (accent color while focused)

    def __init__(self, parent, on_click):
        super().__init__(parent, width=style.TILE_SIZE, height=style.TILE_SIZE, bg=style.TILE_BORDER)
        self.pack_propagate(False)
        self.label = tk.Label(self, text="", font=style.FONT_TILE, fg=style.TILE_TEXT, bg=style.TILE_COLORS[EMPTY], cursor="hand2")
        self.label.pack(fill="both", expand=True, padx=2, pady=2)
        for w in (self, self.label):
            w.bind("<Button-1>", lambda _e: on_click())

    def render(self, letter: str, state: str, focused: bool) -> None:
        self.configure(bg=style.COLOR if focused else style.TILE_BORDER)
        self.label.configure(text=letter, bg=style.TILE_COLORS[state])


class Board(ttk.Frame):
    """
    GUI component representing the Wordle tile grid (6 rows x 5 columns).
    
    Serves as the main container for tile widgets and maintains the underlying data model, consisting of 2D matrix representations for entered letters and their associated color feedback states.
    """

    def __init__(self, parent, on_change=None):
        super().__init__(parent)
        self.on_change = on_change

        # Data model matrices (6x5 matrix initialized with empty default values)
        self.letters = [[""] * WORD_LENGTH for _ in range(MAX_GUESSES)]
        self.states = [[EMPTY] * WORD_LENGTH for _ in range(MAX_GUESSES)]
        
        # Current active cursor position represented as (row, column) tuple
        self.focus = (0, 0)

        # 2D list storing the UI widget references (Tile components)
        self.tiles: list[list[Tile]] = []
        gap = style.TILE_GAP // 2

        # Instantiate and position Tile widgets using Tkinter grid layout manager
        for r in range(MAX_GUESSES):
            row = []
            for c in range(WORD_LENGTH):
                # Bind default arguments in lambda to capture current loop iteration (r, c)
                tile = Tile(self, on_click=lambda r=r, c=c: self._click(r, c))
                tile.grid(row=r, column=c, padx=gap, pady=gap)
                row.append(tile)
            self.tiles.append(row)

        # Initial render pass to synchronize UI with blank data model
        self.render_all()

    # -- rendering ---------------------------------------------------

    def render_tile(self, r: int, c: int) -> None:
        # Updates the visual presentation of a single tile based on current model data.
        self.tiles[r][c].render(
            self.letters[r][c], 
            self.states[r][c], 
            self.focus == (r, c)
        )

    def render_all(self) -> None:
        # Iterates through the entire grid matrix and updates every tile's render state.
        for r in range(MAX_GUESSES):
            for c in range(WORD_LENGTH):
                self.render_tile(r, c)

    def _changed(self) -> None:
        # Helper method to trigger the registered change listener callback if defined.
        if self.on_change:
            self.on_change()

    def set_focus(self, r: int, c: int) -> None:
        # Updates active cursor coordinates and re-renders affected tiles to accurately reflect focus highlight changes.
        old = self.focus
        self.focus = (r, c)
        self.render_tile(*old)  # Remove focus highlight from previously focused tile
        self.render_tile(r, c)  # Apply focus highlight to newly targeted tile

    # -- editing -----------------------------------------------------

    def _click(self, r: int, c: int) -> None:
        # Event handler for direct tile click events: updates focus and toggles clue state.
        self.set_focus(r, c)
        self.cycle(r, c)

    def cycle(self, r: int | None = None, c: int | None = None) -> None:
        # Cycles the feedback state color of a targeted tile using modulo arithmetic (Sequence transition: ABSENT -> PRESENT -> CORRECT -> ABSENT).

        r, c = (r, c) if r is not None else self.focus

        # State cannot be modified on empty tile cells
        if not self.letters[r][c]:
            return

        # Advance state to the next index in CYCLE tuple using modulo wrapping
        self.states[r][c] = CYCLE[(CYCLE.index(self.states[r][c]) + 1) % len(CYCLE)]
        self.render_tile(r, c)
        self._changed()

    def put_letter(self, letter: str) -> None:
        # Inserts a single character at the currently focused position, updates state and advances the cursor forward.

        r, c = self.focus
        self.letters[r][c] = letter.upper()

        # Default newly typed letters to ABSENT feedback color if previously empty
        if self.states[r][c] == EMPTY:
            self.states[r][c] = ABSENT

        self._advance()
        self.render_tile(r, c)
        self._changed()

    def _advance(self) -> None:
        # Advances the input focus cursor to the next sequential cell (row-major order).

        r, c = self.focus
        if c + 1 < WORD_LENGTH:
            self.set_focus(r, c + 1)
        elif r + 1 < MAX_GUESSES:
            self.set_focus(r + 1, 0)

    def backspace(self) -> None:
        # Handles backspace input: removes character at active focus or steps backward to clear the preceding non-empty cell.

        r, c = self.focus

        # If current cell is empty, navigate one step backward prior to clearing
        if not self.letters[r][c]:
            if c > 0:
                r, c = r, c - 1
            elif r > 0:
                r, c = r - 1, WORD_LENGTH - 1
            self.set_focus(r, c)

        self._clear_tile(r, c)
        self._changed()

    def move(self, step: int) -> None:
        # Moves the focus relative to current position by converting 2D coordinates  to a 1D flat index, applying step offset, and mapping back via divmod.
        r, c = self.focus
        # Flatten coordinate to 1D index and clamp within board boundaries
        index = min(max(r * WORD_LENGTH + c + step, 0), MAX_GUESSES * WORD_LENGTH - 1)
        # Convert back to (row, column) coordinates using divmod
        self.set_focus(*divmod(index, WORD_LENGTH))

    def _clear_tile(self, r: int, c: int) -> None:
        # Resets letter and feedback state of a target cell to empty default values.
        
        self.letters[r][c] = ""
        self.states[r][c] = EMPTY
        self.render_tile(r, c)

    def clear(self) -> None:
        # Resets the entire board state to default empty matrix and moves focus to (0,0).
        for r in range(MAX_GUESSES):
            for c in range(WORD_LENGTH):
                self._clear_tile(r, c)
        self.set_focus(0, 0)
        self._changed()

    def remove_last_row(self) -> None:
        # Locates the latest row containing entered letters and clears all its contents.
        for r in reversed(range(MAX_GUESSES)):
            if any(self.letters[r]):
                for c in range(WORD_LENGTH):
                    self._clear_tile(r, c)
                self.set_focus(r, 0)
                self._changed()
                return

    def fill_next_row(self, word: str) -> bool:
        # Programmatically populates the first available incomplete row with a target word.

        # returns: bool: True if a row was successfully populated, False if board is completely full.

        for r in range(MAX_GUESSES):
            if not self.is_complete(r):
                for c, ch in enumerate(word.upper()):
                    self.letters[r][c] = ch
                    self.states[r][c] = ABSENT
                    self.render_tile(r, c)
                
                # Advance focus cursor to the start of the following row
                self.set_focus(min(r + 1, MAX_GUESSES - 1), 0)
                self._changed()
                return True
        return False

    # -- reading -----------------------------------------------------

    def is_complete(self, r: int) -> bool:
        # Checks if a row is fully filled with non-empty characters across all columns.
        return all(self.letters[r])

    def complete_rows(self) -> list[tuple[str, tuple[str, ...]]]:
        # Extracts all completed guess rows along with their corresponding feedback states.

        # returns: list[tuple[str, tuple[str, ...]]]: Formatted list of tuples containing (guessed_word, tuple_of_colors).
        return [
            ("".join(self.letters[r]).lower(), tuple(self.states[r]))
            for r in range(MAX_GUESSES) 
            if self.is_complete(r)
        ]