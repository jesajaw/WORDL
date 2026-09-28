# About

Wordle is a fantastic daily puzzle game, and while there are many versions available today, the **New York Times** edition remains a classic favorite: [NYT Wordle](https://www.nytimes.com/games/wordle/index.html).

If you have ever watched 3Blue1Brown's brilliant video, [Solving Wordle using information theory](https://www.youtube.com/watch?v=v68zYyaEmEA), you know how fascinating the strategy behind optimal guessing can be. However, sometimes you just need a little extra assistance cracking the daily puzzle.

That is why I put together this simple tool -- to help guide you toward the solution and make solving the puzzle a breeze! It comes in two flavors that share the same logic and look:

* **Web version** (`index.html`) -- runs directly in the browser, hosted for free on GitHub Pages: <https://jesajaw.github.io/WORDL/>
* **Desktop version** (`main.py`) -- a tkinter app.

---

## Features

* **Interactive Wordle board**: 6-row by 5-letter grid with custom letter tiles.
* **Tile state feedback**:
  * Grey: the letter is not in the word.
  * Yellow: the letter is in the word, but at a different position.
  * Green: the letter is fixed at exactly this position.
* **Live filtering**: the list of remaining words is recomputed after every change.
* **Best next guesses**: the three most informative words among the remaining ones (exact information gain / entropy for up to 150 words left, a letter-frequency score above that).
* **Click a word** in the list to use it as your next guess.
* **Repeated letters handled exactly**: each finished row is replayed against every candidate word, so cases like "one E in the answer, two E in the guess" just work.
* **Same look as mtools**: dark theme with switchable palettes (`dark_purple`, `dark_blue`, `black_white`) in `ui/style.py`.

---

## Project Structure

```text
WORDL/
├── index.html          # web version (single self-contained file, served by GitHub Pages)
├── main.py             # desktop entry point
├── words.txt           # word list (one word per line)
├── src/
│   ├── config.py       # shared parameters (word length, tile states, ...)
│   ├── wordlist.py     # loads words.txt
│   └── filter.py       # feedback replay, filtering, suggestions
├── ui/
│   ├── app.py          # tkinter main window
│   ├── widgets.py      # Cell, Tile, Board
│   ├── dialogs.py      # themed popups
│   └── style.py        # theme colors, fonts, ttk styles
├── tools/
│   └── build_html.py   # embeds words.txt into index.html
├── LICENSE
└── requirements.txt
```

---

## Usage

### Web (GitHub Pages)

1. Push the repository to GitHub.
2. Go to **Settings > Pages**, choose **Deploy from a branch**, select the `main` branch and the `/ (root)` folder, and save.
3. After a minute the app is live at `https://<your-user>.github.io/WORDL/`.

If you change `words.txt`, run `python tools/build_html.py` to embed the new list into `index.html`, then commit both files.

### Desktop

No installation needed beyond Python 3.9+ (tkinter is part of the standard library):

```
python main.py
```

### Controls

* Type letters: focus starts on the first tile and advances tile by tile, row by row.
* Click a tile (or press Space) to cycle its color: grey > yellow > green.
* Backspace deletes, arrow keys move the focus.
* Click a word in the result list to fill the next free row with it.
* **Clear** empties the board, **Undo row** removes the last row.
* The web version also has an on-screen keyboard for phones and tablets.

A row only counts as a guess once all five letters are typed; unfinished rows are ignored. New rows start all grey, so set the colors you got back from Wordle.

---

## Acknowledgments

* [3Blue1Brown](https://www.youtube.com/@3blue1brown), for the brilliant [video](https://www.youtube.com/watch?v=v68zYyaEmEA) on Wordle and information theory that brought this project up.
* The New York Times for creating and maintaining the daily puzzle phenomenon: [NYT Wordle](https://www.nytimes.com/games/wordle/index.html).

## License

Distributed under the MIT License. See `LICENSE` for more information.
