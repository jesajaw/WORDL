"""
Wordle constraint engine.

Every completed row on the board is one guess plus the colors Wordle gave back.
A word is still possible if and only if playing the recorded guess against it
would have produced exactly the recorded colors. This "replay the feedback" check
is exact -- including repeated letters -- and needs no special cases for
grey/yellow/green interplay.
"""

from __future__ import annotations

from collections import Counter
from math import log2

from .config import ABSENT, CORRECT, PRESENT, WORD_LENGTH
from .wordlist import load_words


def feedback(guess: str, answer: str) -> tuple[str, ...]:
    """Colors Wordle would show for `guess` if `answer` were the solution."""
    result = [ABSENT] * len(guess)
    unmatched = Counter()                       # answer letters not used up by greens
    for g, a in zip(guess, answer):
        if g != a:
            unmatched[a] += 1
    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            result[i] = CORRECT
    for i, g in enumerate(guess):               # yellows, left to right, limited by letter count
        if result[i] != CORRECT and unmatched[g] > 0:
            result[i] = PRESENT
            unmatched[g] -= 1
    return tuple(result)


class Filter:
    """Filters a word list based on Wordle-style clues."""

    def __init__(self, words: list[str] | None = None, word_length: int = WORD_LENGTH):
        self.word_length = word_length
        source = load_words(word_length=word_length) if words is None else words
        self.wordlist = [w.strip().lower() for w in source
                         if len(w.strip()) == word_length and w.strip().isalpha()]
        self.reset()

    def reset(self) -> None:
        self.guesses: list[tuple[str, tuple[str, ...]]] = []

    def add_guess(self, guess: str, pattern) -> None:
        guess, pattern = guess.lower(), tuple(pattern)
        if len(guess) != self.word_length or len(pattern) != self.word_length:
            raise ValueError(f"A guess needs exactly {self.word_length} letters and colors.")
        self.guesses.append((guess, pattern))

    def filter(self) -> list[str]:
        return [w for w in self.wordlist
                if all(feedback(g, w) == p for g, p in self.guesses)]
