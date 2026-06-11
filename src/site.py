import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.lesson import Lesson

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
TEMPLATES = Path(__file__).resolve().parent / "resources"
TEMPLATE = "questionnaire.html.j2"
SCRIPT_TEMPLATE = "script.js.j2"
STATIC_ASSETS = ("style.css", "favicon.ico")


def _meta(lesson: Lesson) -> dict:
    """The minimal per-lesson data the result table needs, client-side."""
    return {
        "index": lesson.index,
        "book": lesson.book.label,
        "color": lesson.book.color,
        "slug": lesson.book.slug,
        "lesson": lesson.number,
        "skill": lesson.skill is not None,
        "sentence": lesson.sentence is not None,
    }


def build_site(lessons: list[Lesson], out_dir: Path = DOCS) -> Path:
    """Render the questionnaire into ``out_dir/index.html`` for GitHub Pages."""
    lessons = [lesson for lesson in lessons if lesson.skill or lesson.sentence]

    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=True)
    html = env.get_template(TEMPLATE).render(lessons=lessons)
    script = env.get_template(SCRIPT_TEMPLATE).render(
        meta=[_meta(lesson) for lesson in lessons],
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    index = out_dir / "index.html"
    index.write_text(html, encoding="utf-8")
    (out_dir / "script.js").write_text(script, encoding="utf-8")

    for asset in STATIC_ASSETS:
        src = TEMPLATES / asset
        if src.exists():
            shutil.copyfile(src, out_dir / asset)

    return index
