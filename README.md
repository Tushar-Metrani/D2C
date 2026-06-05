# DesignToCode (D2C)

A desktop visual HTML/CSS builder built with PySide6 that lets you build web pages visually and export clean HTML/CSS — no coding required.

> **⚠️ Early Prototype** — This project is in early development and is far from a polished product. Many features are incomplete, buggy, or missing entirely.

![DesignToCode Screenshot](https://raw.githubusercontent.com/Tushar-Metrani/tushar-metrani/refs/heads/main/Screenshot-D2C.png)

---

## Features

- **Visual canvas** — place HTML elements onto a live-rendered page powered by `QWebEngineView`
- **Property inspector** — edit CSS (layout, sizing, spacing, typography, borders, and more)
- **Asset manager** — upload and reuse images across your project
- **Code export** — exports a `.zip` with `index.html`, `style.css`, and an `assets/` folder
- **Browser preview** — open your page in the default browser instantly

### Canvas interactions
- Click to select an element
- `Delete` — remove selected element
- `↑` / `↓` — reorder element within its parent

---

## Built with

- **PySide6** — desktop UI framework
- **QWebEngineView** — live HTML canvas rendering
- **QWebChannel** — Python ↔ JavaScript bridge
- **HTML / CSS / JS** — canvas-side logic

---

## Getting started

**Requirements:** Python 3.10+

```bash
pip install PySide6
python main.py
```

---

## Known limitations

- UI layout and design needs significant improvement
- Canvas interactions feel rough — element placement, selection, and movement lack polish
- No visual logic / JavaScript editor (planned but not implemented)
- No multi-page support
- No undo / redo
- No responsive / breakpoint preview
- Limited set of placeable components

