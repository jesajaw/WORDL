"""
Wordle Word Filter
===================

Tkinter GUI that filters a 5-letter word list down to the words that
are still possible, based on the clues Wordle gives you:

    - grey / absent    : letter is not in the word at all
    - yellow / present : letter is in the word, but not at that position
    - green / fixed    : letter is confirmed at that exact position

Clue handling
-------------
A "grey" letter only excludes a word if that letter isn't *also*
marked yellow or green somewhere else. This covers repeated-letter
cases correctly (e.g. the answer has one "e", you guessed two: one
came back green, the other grey).

Theming
-------
Same color-token approach as the DMX Derby Controller project
(COLOR_BG / COLOR_BG_LIGHT / COLOR_FG / COLOR / COLOR_DARK /
COLOR_STATUS_TEXT), bundled into named themes and switchable at
runtime from the dropdown instead of being commented in/out.
"""

import re
import tkinter as tk
from tkinter import ttk, scrolledtext

from wordlist import WORDS

WORD_LENGTH = 5

THEMES = {
    "Dark / Purple": dict(
        BG="#1e1e24", BG_LIGHT="#2a2a33", FG="#e0dff0",
        ACCENT="#9b59d9", ACCENT_DARK="#6c3fa0", STATUS_TEXT="#c9a6f5",
    ),
    "Dark / Blue": dict(
        BG="#1e1e24", BG_LIGHT="#2a2a33", FG="#e0dff0",
        ACCENT="#4a90d9", ACCENT_DARK="#2f5f9e", STATUS_TEXT="#a6c9f5",
    ),
    "Black / White": dict(
        BG="#000000", BG_LIGHT="#1a1a1a", FG="#ffffff",
        ACCENT="#ffffff", ACCENT_DARK="#808080", STATUS_TEXT="#d9d9d9",
    ),
}
DEFAULT_THEME = "Dark / Purple"


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
# Themed popup, same approach as the DMX Derby Controller project
# (nicer than the default tkinter.messagebox, and follows the
# current theme instead of using the OS dialog style)
# ------------------------------------------------------------
class ThemedDialog(tk.Toplevel):
    """Modal popup styled to match the app's current color theme."""

    def __init__(self, parent, title, message, buttons):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=parent.winfo_toplevel()["bg"])
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


class WordleFilterApp:
    """Tkinter UI for the Wordle Word Filter."""

    def __init__(self, root):
        self.root = root
        self.root.title("Wordle Word Filter")
        self.root.resizable(False, False)

        self.wf = WordleFilter(WORDS)
        self.theme_name = tk.StringVar(value=DEFAULT_THEME)

        self._build_theme_bar()
        self._build_input_form()
        self._build_result_area()

        self._apply_theme(DEFAULT_THEME)

    # ------------------------------------------------------------
    # Theming
    # ------------------------------------------------------------
    def _apply_theme(self, theme_name):
        c = THEMES[theme_name]
        self.root.configure(bg=c["BG"])

        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(".", background=c["BG"], foreground=c["FG"], font=("Segoe UI", 9))
        style.configure("TFrame", background=c["BG"])
        style.configure("TLabelframe", background=c["BG"], foreground=c["FG"], bordercolor=c["ACCENT_DARK"])
        style.configure("TLabelframe.Label", background=c["BG"], foreground=c["ACCENT"])
        style.configure("TLabel", background=c["BG"], foreground=c["FG"])

        style.configure("TButton", background=c["BG_LIGHT"], foreground=c["FG"],
                         bordercolor=c["ACCENT_DARK"], focusthickness=1, padding=6)
        style.map("TButton",
                  background=[("active", c["ACCENT_DARK"]), ("pressed", c["ACCENT"])],
                  foreground=[("active", c["FG"])])

        style.configure("TCombobox", fieldbackground=c["BG_LIGHT"], background=c["BG_LIGHT"],
                         foreground=c["FG"], arrowcolor=c["ACCENT"])
        style.map("TCombobox", fieldbackground=[("readonly", c["BG_LIGHT"])])

        style.configure("TEntry", fieldbackground=c["BG_LIGHT"], foreground=c["FG"],
                         insertcolor=c["FG"])

        style.configure("Filter.TButton", background=c["ACCENT_DARK"], foreground=c["FG"])
        style.map("Filter.TButton", background=[("active", c["ACCENT"])])

        style.configure("Count.TLabel", background=c["BG"], foreground=c["STATUS_TEXT"],
                         font=("Segoe UI", 9, "bold"))

        # scrolledtext.ScrolledText is plain tk, not ttk -- style it by hand
        self.text_result.configure(
            bg=c["BG_LIGHT"], fg=c["FG"], insertbackground=c["FG"],
            selectbackground=c["ACCENT_DARK"],
        )

    def _on_theme_change(self, event=None):
        self._apply_theme(self.theme_name.get())

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------
    def _build_theme_bar(self):
        bar = ttk.Frame(self.root, padding=10)
        bar.pack(fill="x")

        ttk.Label(bar, text="Theme:").pack(side="left", padx=(0, 5))
        theme_cb = ttk.Combobox(
            bar, textvariable=self.theme_name, values=list(THEMES),
            state="readonly", width=15,
        )
        theme_cb.pack(side="left")
        theme_cb.bind("<<ComboboxSelected>>", self._on_theme_change)

    def _build_input_form(self):
        form = ttk.LabelFrame(self.root, text="Clues", padding=10)
        form.pack(fill="x", padx=10, pady=5)

        ttk.Label(form, text="Absent letters (grey), e.g. xyz").grid(
            row=0, column=0, sticky="w", padx=5, pady=4)
        self.entry_absent = ttk.Entry(form, width=40)
        self.entry_absent.grid(row=0, column=1, padx=5, pady=4)

        ttk.Label(form, text="Correct position (green), e.g. 1:c,3:r").grid(
            row=1, column=0, sticky="w", padx=5, pady=4)
        self.entry_fixed = ttk.Entry(form, width=40)
        self.entry_fixed.grid(row=1, column=1, padx=5, pady=4)

        ttk.Label(form, text="Wrong position (yellow), e.g. 2:a,4:a").grid(
            row=2, column=0, sticky="w", padx=5, pady=4)
        self.entry_present = ttk.Entry(form, width=40)
        self.entry_present.grid(row=2, column=1, padx=5, pady=4)

        btn_row = ttk.Frame(form)
        btn_row.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btn_row, text="Filter", command=self.run_filter,
                   style="Filter.TButton").pack(side="left", padx=5)
        ttk.Button(btn_row, text="Reset", command=self.reset_form).pack(side="left", padx=5)

    def _build_result_area(self):
        result = ttk.Frame(self.root, padding=(10, 0, 10, 10))
        result.pack(fill="both", expand=True)

        self.count_label = ttk.Label(result, text="0 possible words", style="Count.TLabel")
        self.count_label.pack(anchor="w", pady=(0, 5))

        self.text_result = scrolledtext.ScrolledText(result, width=60, height=20, relief="flat")
        self.text_result.pack(fill="both", expand=True)

    # ------------------------------------------------------------
    # Parsing / validation (fixes silently-ignored bad input)
    # ------------------------------------------------------------
    @staticmethod
    def _parse_letters(raw):
        """Returns the lowercase a-z letters in raw, or raises ValueError."""
        raw = raw.strip().lower()
        if raw and not re.fullmatch(r"[a-z]*", raw):
            raise ValueError(f"'{raw}' should only contain letters a-z.")
        return raw

    def _parse_position_pairs(self, raw, field_name):
        """Parses 'pos:letter,pos:letter,...' into a list of
        (0-indexed position, letter) tuples. `pos` is 1-indexed by the
        user, matching the 1..WORD_LENGTH they see on screen."""
        raw = raw.strip()
        pairs = []
        if not raw:
            return pairs
        for item in raw.split(","):
            item = item.strip()
            if not item:
                continue
            if ":" not in item:
                raise ValueError(f"{field_name}: '{item}' is missing a ':' (expected e.g. '1:c').")
            pos_str, letter = item.split(":", 1)
            letter = letter.strip().lower()
            if not re.fullmatch(r"[a-z]", letter):
                raise ValueError(f"{field_name}: '{item}' -- letter must be a single a-z character.")
            try:
                pos = int(pos_str.strip())
            except ValueError:
                raise ValueError(f"{field_name}: '{item}' -- position must be a number.")
            if not (1 <= pos <= self.wf.word_length):
                raise ValueError(
                    f"{field_name}: position {pos} is out of range "
                    f"(1-{self.wf.word_length})."
                )
            pairs.append((pos - 1, letter))  # convert to 0-indexed
        return pairs

    # ------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------
    def run_filter(self):
        try:
            absent = self._parse_letters(self.entry_absent.get())
            fixed_pairs = self._parse_position_pairs(self.entry_fixed.get(), "Correct position")
            present_pairs = self._parse_position_pairs(self.entry_present.get(), "Wrong position")
        except ValueError as e:
            show_error(self.root, "Invalid input", str(e))
            return

        self.wf.reset()
        self.wf.add_absent(absent)
        for pos, letter in fixed_pairs:
            self.wf.add_fixed(pos, letter)
        for pos, letter in present_pairs:
            self.wf.add_present(letter, pos)

        results = self.wf.filter()
        self.count_label.config(text=f"{len(results)} possible word(s)")
        self.text_result.delete("1.0", tk.END)
        self.text_result.insert(tk.END, "\n".join(results))

    def reset_form(self):
        self.entry_absent.delete(0, tk.END)
        self.entry_fixed.delete(0, tk.END)
        self.entry_present.delete(0, tk.END)
        self.wf.reset()
        self.count_label.config(text="0 possible words")
        self.text_result.delete("1.0", tk.END)


def main():
    root = tk.Tk()
    WordleFilterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()