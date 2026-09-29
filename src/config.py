# Global, UI-independent parameters (shared by the filter engine and the tkinter UI)

WORD_LENGTH = 5
MAX_GUESSES = 6

# Tile states. "empty" = no letter typed yet; the other three are the clue colors.
EMPTY = "empty"
ABSENT = "absent"      # grey   - letter is not in the word (or no further copies of it)
PRESENT = "present"    # yellow - letter is in the word, but at another position
CORRECT = "correct"    # green  - letter sits exactly here
CYCLE = (ABSENT, PRESENT, CORRECT)

WINDOW_TITLE = "WORDL Filter"
LIST_COLUMNS = 6            # words per line in the result list
LIST_ROWS = 9               # visible lines of the result list
