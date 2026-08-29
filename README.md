# Wordle Word Filter

# About

There is the pretty neat game WORDL - which has nowadays multiple provider - but personally I like the one from the **New York Times** the most (wasnt it also the first introducing it?).

[NWT WORDL](https://www.nytimes.com/games/wordle/index.html)

Well anyways, I saw the video from 3Blue1Brown: [Solving Wordle using information theory](https://www.youtube.com/watch?v=v68zYyaEmEA) and thought, well thats a nice help but wouldnt it be nice for a dumbass like me to find it at all. So and this is why I implemented this little script which basically provides the solution for it.

# Features

- Filters a 5-letter word list down to the words still possible, based on grey/yellow/green Wordle clues
- Correctly handles repeated letters (grey doesn't wrongly exclude a letter that's also confirmed present elsewhere)
- Input validation with themed error popups
- Reset button and live result counter
- 3 switchable color themes (Dark / Purple, Dark / Blue, Black / White)

## Files

- `wordle_filter_gui.py` — the app (filtering logic + Tkinter UI)
- `wordlist.py` — the 5-letter word list, kept separate so it's easy
  to swap out or extend

## Run

```
python wordle_filter.py
```

## Clue format

- **Absent letters (grey):** plain letters, e.g. `xyz`
- **Correct position (green):** `position:letter`, comma-separated,
  e.g. `1:c,3:r`
- **Wrong position (yellow):** `position:letter`, comma-separated,
  e.g. `2:a,4:a`

Positions are 1-indexed (1 to 5). A letter marked both green/yellow
somewhere and grey elsewhere (repeated letters) is handled correctly —
the grey mark only excludes the letter if it isn't also confirmed
present.

## Theme

Pick a theme from the dropdown at the top: **Dark / Purple**,
**Dark / Blue**, or **Black / White** — same palette approach as the
DMX Derby Controller project. Error/validation popups follow the
active theme instead of using the OS-default dialog style.