# This file contains a list of valid 5-letter words — it may not be up to date with the current WORDL list
from .config import parameters
from .wordlist import WORDS


class Filter:
    # Filters a word list based on Wordle-style clues
    def __init__(self, word_length=parameters.WORD_LENGTH):
        self.word_length = word_length
        self.wordlist = [
            w.strip().lower() for w in WORDS
            if len(w.strip()) == word_length
        ]
        self.reset()

    def reset(self):
        # Clears all clues
        self.absent_letters = set()   # grey: not in the word at all
        self.present_letters = {}     # yellow: letter -> {excluded positions}
        self.fixed_positions = {}     # green: position -> letter

    def add_absent(self, letters):
        self.absent_letters.update(letters)

    def add_present(self, letter, position):
        # `position` is 0-indexed. The letter is known to be in the word, just not at this position.
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

        # grey: letter must not appear at all, UNLESS it's also confirmed present elsewhere (duplicate-letter case)
        known_present = set(self.fixed_positions.values()) | set(self.present_letters)
        for letter in self.absent_letters:
            if letter in known_present:
                continue
            if letter in word:
                return False
        return True

    def filter(self):
        return [w for w in self.wordlist if self._matches(w)]