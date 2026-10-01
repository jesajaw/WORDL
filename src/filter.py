"""
Wordle constraint engine.
Every completed row on the board is one guess plus the colors Wordle gave back. A word is still possible if and only if playing the recorded guess against it would have produced exactly the recorded colors. This "replay the feedback" check is exact -- including repeated letters -- and needs no special cases for grey/yellow/green interplay.
"""

from __future__ import annotations

from collections import Counter

from .config import ABSENT, CORRECT, PRESENT, WORD_LENGTH
from .wordlist import load_words


def feedback(guess: str, answer: str) -> tuple[str, ...]:
    # Colors Wordle would show for `guess` if `answer` were the solution
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
    # filter potential Wordle solution words based on guess feedback patterns
    def __init__(self, words: list[str] | None = None, word_length: int = WORD_LENGTH):
        # Loads default words if none are provided, cleans up input words, and initializes the guess history
        self.word_length = word_length

        # if no list is passed, load the default dictionary for the given word length
        source = load_words(word_length=word_length) if words is None else words

        # clean word list: remove whitespace, convert to lowercase, and ensure words only contain alphabetic characters of the correct length
        self.wordlist = [
            w.strip().lower()
            for w in source if len(w.strip()) == word_length
            and w.strip().isalpha()
            ]

        # reset state to clear previous guesses
        self.reset()

    def reset(self) -> None:
        # clears all stored guesses and feedback patterns.
        self.guesses: list[tuple[str, tuple[str, ...]]] = []

    def add_guess(self, guess: str, pattern) -> None:
        """
        Records a new guess along with its resulting feedback pattern.
        
        Args:
            guess: The word attempted by the player
            pattern: Sequence representing colors/feedback
            
        Raises: ValueError if guess or pattern length does not match word_length.
        """

        # standardize input formats
        guess, pattern = guess.lower(), tuple(pattern)

        # Validation: check input dimensions against configured word length
        if len(guess) != self.word_length or len(pattern) != self.word_length:
            raise ValueError(f"A guess needs exactly {self.word_length} letters and colors.")

        # store guess and feedback pattern tuple in history
        self.guesses.append((guess, pattern))

    def filter(self) -> list[str]:
        """
        Filters the initial wordlist to find candidate words matching all past guesses.
        returns a list of remaining possible secret words.
        """

        # A word w is valid if it produces the exact same feedback pattern 'p' 
        # when evaluated against every past guess 'g' in self.guesses
        return [
            w for w in self.wordlist
            if all(
                feedback(g, w) == p
                for g, p in self.guesses
            )
        ]
