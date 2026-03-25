# 🏀 Anime Basketball

A fun desktop basketball game built with Python and Pygame. Score baskets to unlock anime girl photos!

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python) ![Pygame](https://img.shields.io/badge/Pygame--CE-latest-green)

---

## Requirements

- **Python** 3.9 or higher (3.12 recommended — Python 3.14 may cause issues with some packages)
- **pygame-ce** (Community Edition) — supports Python 3.12+
- **Internet connection** — needed to download anime images on score

---

## Installation

### 1. Check your Python version
```bash
python --version
```
> If you have Python 3.14, consider installing 3.12 from [python.org](https://www.python.org/downloads/) for best compatibility.

### 2. Install pygame-ce
```bash
pip install pygame-ce
```
> ⚠️ Use `pygame-ce` instead of `pygame`. The standard `pygame` package does **not** support Python 3.13+.

### 3. Run the game
```bash
python basketball_anime.py
```

---

## How to Play

| Action | Input |
|---|---|
| Aim | Hold left click + move mouse |
| Shoot | Release left click |
| Restart | Press `R` after game over |

- You have **10 shots** per game.
- Score a basket to unlock an anime image 🌸
- Try bouncing off the backboard for trick shots!

---

## Customizing Images

Open `basketball_anime.py` and edit the `WAIFU_API_URLS` list at the top of the file. You can use direct image URLs or local file paths:

```python
WAIFU_API_URLS = [
    "https://example.com/my-anime-image.jpg",   # remote URL
    "waifu1.jpg",                                # local file (same folder as .py)
    r"C:/Users/yourname/Pictures/waifu2.png",    # full local path
]
```

> **Tip:** Right-click any image in your browser → **"Copy image address"** to get a direct URL.

---

## Troubleshooting

**`pip install pygame` fails with build errors**
→ Use `pip install pygame-ce` instead.

**Images show a placeholder instead of the anime photo**
→ The URL may be blocking direct downloads. Try a different image host (Imgur, Wikimedia, etc.).  
→ Check the PowerShell window for `[imagen] FALLO` messages to see which URL is failing.

**`python` is not recognized**
→ Reinstall Python from [python.org](https://www.python.org/downloads/) and make sure to check ✅ **"Add Python to PATH"** during installation.

**Game runs but window doesn't open**
→ Try running with `py -3.12 basketball_anime.py` if you have multiple Python versions installed.
