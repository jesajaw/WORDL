"""Loads the word list from words.txt (one word per line) in the project root."""

from pathlib import Path

from .config import WORD_LENGTH

WORDS_FILE = Path(__file__).resolve().parent.parent / "words.txt"


def load_words(path=WORDS_FILE, word_length: int = WORD_LENGTH) -> list[str]:
    """Return the cleaned, de-duplicated word list (lowercase, letters only, fixed length)."""
    words, seen = [], set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            if len(word) == word_length and word.isalpha() and word.isascii() and word not in seen:
                seen.add(word)
                words.append(word)
    return words
