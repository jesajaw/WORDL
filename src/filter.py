from __future__ import annotations
from collections import Counter

from .config import ABSENT, CORRECT, PRESENT, WORD_LENGTH
from .wordlist import load_words


def feedback(guess: str, answer: str) -> tuple[str, ...]:
    # colors for `guess` if `answer` were the solution
    result = [ABSENT] * len(guess)
    unmatched = Counter() # answer letters not used up by greens
    for g, a in zip(guess, answer):
        if g != a:
            unmatched[a] += 1
    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            result[i] = CORRECT
    for i, g in enumerate(guess): # yellows, left to right, limited by letter count
        if result[i] != CORRECT and unmatched[g] > 0:
            result[i] = PRESENT
            unmatched[g] -= 1
    return tuple(result)


class Filter:
    # filter potential solution words based on guess feedback patterns
    def __init__(self, words: list[str] | None = None, word_length: int = WORD_LENGTH):
        # loads default words if none are provided, cleans up input words, and initializes the guess history
        self.word_length = word_length

        # if no list is passed -> load default dictionary
        source = load_words(word_length=word_length) if words is None else words

        # clean word list: remove whitespace, convert to lowercase, ensure words only contain alphabetic characters
        self.wordlist = [
            w.strip().lower()
            for w in source
                if len(w.strip()) == word_length
                    and w.strip().isalpha()
            ]
        self.reset() # reset state to clear previous guesses

    def reset(self) -> None: # clears all stored guesses and feedback patterns
        self.guesses: list[tuple[str, tuple[str, ...]]] = []

    def add_guess(self, guess: str, pattern) -> None:
        # new guess with its resulting feedback pattern
        # Args: guess: word attempted and pattern: color sequence/feedback
        # Raises: ValueError if guess or pattern length does not match word_length.

        guess, pattern = guess.lower(), tuple(pattern) # standardize input formats

        # Validation: check input dimensions against configured word length
        if len(guess) != self.word_length or len(pattern) != self.word_length: raise ValueError(f"A guess needs exactly {self.word_length} letters and colors.")

        self.guesses.append((guess, pattern)) # store pattern tuple in history

    def filter(self) -> list[str]:
        # filters initial wordlist -> returns a list of remaining words
        # A word w is valid if it produces the exact same feedback pattern 'p' when evaluated against every past guess 'g' in self.guesses
        return [
            w for w in self.wordlist
            if all(
                feedback(g, w) == p
                for g, p in self.guesses
            )
        ]
