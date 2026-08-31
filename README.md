# About

Wordle is a fantastic daily puzzle game, and while there are many versions available today, the **New York Times** edition remains a classic favorite [[NWT WORDL](https://www.nytimes.com/games/wordle/index.html)].

If you have ever watched 3Blue1Brown's brilliant video, [Solving Wordle using information theory](https://www.youtube.com/watch?v=v68zYyaEmEA), you know how fascinating the strategy behind optimal guessing can be. However, sometimes you just need a little extra assistance cracking the daily puzzle.

That is why I put together this simple script - to help guide you toward the solution and make solving the puzzle a breeze!

# Features

- Filters a 5-letter word list down to the words still possible (based on clues)
- 3 switchable color themes (Dark / Purple, Dark / Blue, Black / White)

## Files

- `wordle_filter_gui.py` — the app (filtering logic + Tkinter UI)
- `wordlist.py` — the 5-letter word list, kept separate so it's easy
  to swap out or extend

## Run
Once you have cloned the repository to your local machine, simply navigate to the correct folder in your terminal and run the script using:
```
python wordle_filter.py
```

## Clue format

- **Absent letters (grey):** plain letters, e.g. `xyz`
- **Correct position (green):**
- **Wrong position (yellow):**

## Theme

Pick a theme from the dropdown at the top: **Dark / Purple**,
**Dark / Blue**, or **Black / White** — same palette approach as the
DMX Derby Controller project. Error/validation popups follow the
active theme instead of using the OS-default dialog style.
