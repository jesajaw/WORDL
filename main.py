"""
Wordl Filter
-------------
UI that filters a 5-letter word list down to the words that are still possible (2025), based on the clues Wordle gives you.

Clue entry is a tile board that looks like NYT Wordle:
 - type letters on the keyboard; focus starts on the first tile and auto-advances tile by tile, row by row, as you type
 - click a tile's letter to cycle its color/clue: grey:absent, default || yellow: present, not this position || green: correct
You can fill in as many guess rows as you've actually played; filter re-runs automatically after every change.


Clue handling
-------------
A "grey" letter only excludes a word if that letter isn't *also* marked yellow or green somewhere else (any row, any column). This covers repeated-letter cases correctly (e.g. the answer has one "e", you guessed two: one came back green, the other grey).
"""

import tkinter as tk
from src import ui

def main():
    ui.enable_dpi_awareness()
    root = tk.Tk()
    ui.FilterUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()