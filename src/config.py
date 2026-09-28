"""Global, UI-independent parameters (shared by the filter engine and the tkinter UI)."""

WORD_LENGTH = 5
MAX_GUESSES = 6

# Tile states. "empty" = no letter typed yet; the other three are the clue colors.
EMPTY = "empty"
ABSENT = "absent"      # grey   - letter is not in the word (or no further copies of it)
PRESENT = "present"    # yellow - letter is in the word, but at another position
CORRECT = "correct"    # green  - letter sits exactly here
CYCLE = (ABSENT, PRESENT, CORRECT)

# Suggestions: exact information-gain (entropy) ranking is used up to this many
# remaining words, above it a cheap letter-frequency score is used instead.
ENTROPY_LIMIT = 150
SUGGESTION_COUNT = 3
