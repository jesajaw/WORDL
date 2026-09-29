# About

Wordle is a fantastic daily puzzle game, and while there are many versions available today, the **New York Times** edition remains a classic favorite: [NYT Wordle](https://www.nytimes.com/games/wordle/index.html).

If you have ever watched 3Blue1Brown's brilliant video, [Solving Wordle using information theory](https://www.youtube.com/watch?v=v68zYyaEmEA), you know how fascinating the strategy behind optimal guessing can be. However, sometimes you just need a little extra assistance cracking the daily puzzle.

That is why I put together this simple tool -- to help guide you toward the solution and make solving the puzzle a breeze!

---

## 🚀 Features

* **Interactive Wordle Board**: 6-row by 5-letter visual grid with custom letter tiles.
* **Tile State Feedback**:
  * ⬛ **Absent**: Letter is not in the word.
  * 🟨 **Present**: Letter exists in the target word, but in a different position.
  * 🟩 **Correct**: Letter is fixed in the exact position.
* **Live filtering**: recomputes the list of remaining possible words after every change.
* **Color theme**: dark theme defined in `src/theme.py`, with two additional presets (`dark_purple`, `black_white`) ready to switch to by changing `_active` in that file.

---

## 📁 Project Structure

```text
WORDL/
├── index.html          # web version (single self-contained file, served by GitHub Pages)
├── main.py             # desktop entry point
├── words.txt           # word list (one word per line)
├── src/
│   ├── config.py       # shared parameters (word length, tile states, ...)
│   ├── wordlist.py     # loads words
│   └── filter.py       # feedback replay, filtering, suggestions
├── ui/
│   ├── app.py          # tkinter main window
│   ├── widgets.py      # Cell, Tile, Board
│   ├── dialogs.py      # themed popups
│   └── style.py        # theme colors, fonts, ttk styles
├── tools/
│   └── build_html.py   # embeds words.txt into index.html
└── LICENSE
```

---

## 💻 Usage

### Web (GitHub Pages)

Just click on the link under “About” in the sidebar or [here](jesajaw.github.io/WORDL/)

If you change `words.txt`, run:
```bash
python tools/build_html.py
```
to embed the new list into `index.html`, commit both files.

### Desktop

No installation needed beyond Python 3.9+:

```bash
python main.py
```

---

## 🙏 Acknowledgments

* [3Blue1Brown](https://www.youtube.com/@3blue1brown), for the brilliant [video](https://www.youtube.com/watch?v=v68zYyaEmEA) on Wordle and information theory that brought this project up.
* The New York Times for creating and maintaining the daily puzzle phenomenon [NYT WORDL](https://www.nytimes.com/games/wordle/index.html).
* And thanks to [Claude](claude.ai/) for building this `.html` shit I would never do on my own.

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.
