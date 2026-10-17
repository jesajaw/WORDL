from .config import WORD_LENGTH, WORDS_FILE

def load_words(path=WORDS_FILE, word_length: int = WORD_LENGTH) -> list[str]:
    words, seen = [], set() # 'words' preserves insertion order; 'seen' optimizes lookup speed
    with open(path, encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower() # 'words' preserves insertion order; 'seen' optimizes lookup speed
            # criteria: length, alphabetic, non-duplicate
            if len(word) == word_length and word.isalpha() and word.isascii() and word not in seen:
                seen.add(word) # track to prevent duplicates
                words.append(word) # add to ordered output list
    return words
