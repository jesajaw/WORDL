import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.wordlist import load_words  # noqa: E402

START, END = "/*WORDS_START*/", "/*WORDS_END*/"


def main() -> None:
    page = ROOT / "index.html"
    html = page.read_text(encoding="utf-8")
    words = load_words()
    block = f'{START}const WORDS = "{" ".join(words)}".split(" ");{END}'
    new_html, count = re.subn(re.escape(START) + r".*?" + re.escape(END), lambda _m: block, html, flags=re.S)
    if count != 1:
        raise SystemExit(f"Expected exactly one {START} ... {END} block in index.html, found {count}.")
    page.write_text(new_html, encoding="utf-8")
    print(f"Embedded {len(words)} words into {page.name}.")


if __name__ == "__main__":
    main()
