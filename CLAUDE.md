# Irodori — What To Do

## What this is

A small Python tool that builds a **static self-assessment questionnaire** for the
[Irodori](https://www.irodori.jpf.go.jp/) Japanese textbooks (the Japan
Foundation's *Irodori: Japanese for Life in Japan* course).

**The intent:** someone who already has *some* Japanese shouldn't start Irodori
from page one. This tool lets such a learner quickly gauge, lesson by lesson,
what they can already do — and turns that into a concrete plan of which lessons
in which book to **skip**, **review**, or **study**. So it's a triage tool for
entering the Irodori series at the right place rather than grinding through
material you've already mastered.

Each Irodori lesson is assessed on up to two axes:
- a **skill** ("can-do") — a real-world task, e.g. *"Can you read a disaster-
  prevention pamphlet and understand it?"*
- a **sentence pattern** — the grammar point taught in that lesson.

For each, the learner answers **Can do / Needs revision / New to me**, which map
to **Skip / Review / Study**. The result is a per-lesson table.

## How it works (the pipeline)

```
Irodori .xlsx (official)  ──►  preprocess  ──►  output/claude_input.json
                                                      │
                                       (LLM, guided by SPEC.md)
                                                      ▼
                              src/resources/claude_output.json  ──┐
                                                                  ├──►  Lesson objects  ──►  docs/ (static site)
                              output/claude_input.json  ──────────┘
```

1. **Fetch source data** — `src/resources/` (the `Resource` class) downloads the
   two official Irodori spreadsheets (sentence-pattern list + can-do list) into a
   persistent per-user cache, or loads bundled files shipped in the package. A
   URL is downloaded once and reused; a plain filename is read from the package.

2. **Preprocess** — `src/preprocess.py` reads the `.xlsx` with `openpyxl`,
   flattens merged cells, pulls the relevant columns, and merges the two sheets
   by book/topic/lesson into one record per row keyed by `index`
   (`input_data()`). `src/__init__.py` also writes this to
   `output/claude_input.json`.

3. **Enrich with an LLM** — a Claude run transforms `claude_input.json` into
   `src/resources/claude_output.json` following **`SPEC.md`** (the authoritative
   spec for that transform). It produces English can-do questions, fresh
   Japanese examples + translations, a structural gloss of each sentence pattern
   (`sentence_pattern_translated`), and a short intent description
   (`sentence_pattern_description`). This step is **not** automated in code — it
   is run separately against `SPEC.md`; the checked-in `claude_output.json` is
   the result.

4. **Model** — `src/lesson.py` defines the domain types: `Book`, `SkillType`,
   `SkillActivity`, `SkillSituation` enums (each Japanese value mapped to an
   English label / metadata, e.g. `Book.color`, `Book.order`), and the `Skill`,
   `Sentence`, and `Lesson` dataclasses. `src/__init__.py` merges the preprocess
   data with `claude_output.json`, builds `Lesson` objects, merges duplicates by
   `lesson.key`, and sorts by `(book.order, number)`.

5. **Render** — `src/site.py` (`build_site`) renders the lessons into
   `docs/index.html` via the Jinja template
   `src/resources/questionnaire.html.j2`, and copies the static assets
   (`style.css`, `favicon.ico`) alongside it.

## The static site (`docs/`)

A single self-contained page, designed for **GitHub Pages** (Settings → Pages →
deploy from branch, `/docs` folder). Everything is baked in — no server, no
fetch at runtime.

- **Questionnaire view**: one card per skill / sentence question, colored by its
  book (`Book.color`). Answers are radio chips (Can do / Needs revision / New to
  me).
- **Results view**: a Book · Lesson · Skill · Sentence table mapping each answer
  to Skip / Review / Study. `—` means the lesson has no skill/sentence of that
  kind; `Unknown` means it was left unanswered.
- Answers and the current view persist in `localStorage`, and "Back to Can-do's"
  returns you to where you were scrolled.

## Build & run

The package uses **uv**. Build the site (downloads source data on first run,
then caches it):

```bash
uv run python -m src.__init__
```

This writes `docs/index.html` (+ assets) and `output/claude_input.json`.
(Running `python src/__init__.py` directly fails — the module uses absolute
`src.*` imports, so it must run with the repo root on the path, i.e. as a
module.)

## Layout

| Path | Role |
|---|---|
| `src/resources/__init__.py` | `Resource` class — cached download / bundled-file access |
| `src/preprocess.py` | xlsx → merged records (`input_data()`) |
| `src/lesson.py` | domain enums + `Skill` / `Sentence` / `Lesson` dataclasses |
| `src/site.py` | `build_site()` — Jinja render into `docs/` |
| `src/resources/questionnaire.html.j2` | the page template |
| `src/resources/style.css` | styles (native CSS nesting, no build step) |
| `src/resources/claude_output.json` | LLM-generated enrichment (bundled) |
| `SPEC.md` | authoritative spec for the `claude_input.json` → `claude_output.json` transform |
| `output/claude_input.json` | preprocess output, regenerated each build |
| `docs/` | generated static site for GitHub Pages |

## Conventions & gotchas

- **Dependencies:** `openpyxl` (read xlsx) and `jinja2` (render) are runtime
  deps; `pytest` is dev. Stick to `uv add` / `uv run`.
- **The LLM step is spec-driven.** If the output shape changes, update `SPEC.md`
  first — it is the contract. `claude_output.json` is regenerated from it, not
  hand-edited.
- **CSS is plain CSS** using native nesting No CSS build step; `style.css` is copied verbatim.
- **Encoding:** all Japanese text is UTF-8; JSON is written with
  `ensure_ascii=False`. A full-width space `　` (U+3000) in a skill example means
  a line break (see `SPEC.md`).
- **Windows:** this repo is developed on Windows; the `Resource` cache lives
  under `%LOCALAPPDATA%\irodori_whattodo`.
