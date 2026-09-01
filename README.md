# About

Wordle is a fantastic daily puzzle game, and while there are many versions available today, the **New York Times** edition remains a classic favorite [[NWT WORDL](https://www.nytimes.com/games/wordle/index.html)].

If you have ever watched 3Blue1Brown's brilliant video, [Solving Wordle using information theory](https://www.youtube.com/watch?v=v68zYyaEmEA), you know how fascinating the strategy behind optimal guessing can be. However, sometimes you just need a little extra assistance cracking the daily puzzle.

That is why I put together this simple script - to help guide you toward the solution and make solving the puzzle a breeze!

# Features

- Filters a 5-letter word list down to the words still possible (based on clues)
- 3 switchable color themes (Dark / Purple, Dark / Blue, Black / White)

## Files

- `wordle.py` — filtering logic + Tkinter UI
- `wordlist.py` — the 5-letter word list, kept separate so it's easy to swap out or extend

## Run
Once you have cloned the repository to your local machine, simply navigate to the correct folder in your terminal and run the script using:
```
python wordle.py
```

Clue handling
-------------
A "grey" letter only excludes a word if that letter isn't *also* marked yellow or green somewhere else (any row, any column). This covers repeated-letter cases correctly (e.g. the answer has one "e", you guessed two: one came back green, the other grey).

Live filtering
---------------
Every tile edit schedules a filter run via `root.after(...)`; a new edit cancels the previous *scheduled* run before it fires, so a burst of fast edits (typing a whole row, clicking several colors) collapses into a single recompute instead of one per keystroke.
