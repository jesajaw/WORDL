# About

Wordle is a fantastic daily puzzle game, and while there are many versions available today, the **New York Times** edition remains a classic favorite [NYT WORDL](https://www.nytimes.com/games/wordle/index.html).

If you have ever watched 3Blue1Brown's brilliant video, [Solving Wordle using information theory](https://www.youtube.com/watch?v=v68zYyaEmEA), you know how fascinating the strategy behind optimal guessing can be. However, sometimes you just need a little extra assistance cracking the daily puzzle.

That is why I put together this simple script -- to help guide you toward the solution and make solving the puzzle a breeze!

---

## 🚀 Features

* **Interactive Wordle Board**: 6-row by 5-letter visual grid with custom letter tiles.
* **Tile State Feedback**:
  * ⬛ **Absent**: Letter is not in the word.
  * 🟨 **Present**: Letter exists in the target word, but in a different position.
  * 🟩 **Correct**: Letter is fixed in the exact position.
* **Live filtering**: recomputes the list of remaining possible words after every change.
* **Color theme**: dark theme defined in `src/config.py`, with two additional presets (`dark_blue`, `black_white`) ready to switch to by changing `_active` in that file.

---

## 📁 Project Structure

```text
WORDL/
├── src/
│   ├── __init__.py
│   ├── app.py          # Dear PyGui UI (current front end) + entry point (run())
│   ├── config.py       # theme colors, dimensions, and settings
│   ├── filter.py       # Wordle constraint evaluation & filter engine
│   ├── wordlist.py     # word list
├── .gitignore
├── LICENSE
├── main.py           # Application entry point
├── README.md         # ... readme
└── requirements.txt  # dependencies
```

---

## 💻 Usage

Install the **dependency**:

```
pip install -r requirements.txt
```
then run the app from the project root:
```
python main.py
```

Clue entry is a tile board that looks like NYT Wordle:
* type letters on the keyboard; focus starts on the first tile and auto-advances tile by tile, row by row, as you type
* click a tile (or press Space) to cycle its color/clue

You can fill in as many guess rows as you've actually played; the filter re-runs automatically after every change.

---
**Clue handling:** A "grey" letter only excludes a word if that letter isn't *also* marked yellow or green somewhere else (any row, any column). This covers repeated-letter cases correctly (e.g. the answer has one "e", you guessed two: one came back green, the other grey).

---
**Live filtering:** Every tile edit runs the filter immediately. The word list (~2,300 words) is small enough that this is instant, so no debouncing is needed.
