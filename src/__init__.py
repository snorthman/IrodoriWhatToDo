import json

from src.lesson import Lesson
from src.preprocess import input_data
from src.resources import output_claude
from src.site import build_site

def main() -> None:
    data = input_data()
    for item in json.loads(output_claude.path.read_text(encoding='utf-8')):
        data[item['index']] |= item

    lessons = {}
    for item in data.values():
        lesson = Lesson(item)
        lessons[lesson.key] = lesson.merge(lessons[lesson.key]) if lesson.key in lessons else lesson

    lessons = sorted(lessons.values(), key=lambda a: (a.book.order, a.number))
    index = build_site(lessons)
    print(f'Wrote {index}')


if __name__ == '__main__':
    main()
