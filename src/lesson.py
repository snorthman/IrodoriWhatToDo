import re
from enum import Enum
from dataclasses import dataclass, InitVar


class Book(Enum):
    def __new__(cls, ja: str, order: int, label: str, color: str, slug: str):
        obj = object.__new__(cls)
        obj._value_ = ja
        obj.order = order
        obj.label = label
        obj.color = color
        obj.slug = slug
        return obj

    Starter      = ('入門', 0,      'Starter',          '#F3B0C1', 'starter')
    Elementary1  = ('初級1', 1,     'Elementary 1',     '#EC8B2F', 'elementary01')
    Elementary2  = ('初級2', 2,     'Elementary 2',      '#F9C726', 'elementary02')
    Intermediate = ('初中級', 3,    'Pre-Intermediate',  '#C3D600', 'pre-intermediate')

class SkillType(Enum):
    Speaking =  '話'
    Writing =   '書'
    Reading =   '読'
    Listening = '聞'


class SkillActivity(Enum):
    def __new__(cls, ja: str, category: str, modality: str, label: str):
        obj = object.__new__(cls)
        obj._value_ = ja
        obj.category = category
        obj.modality = modality
        obj.label = label
        return obj

    Reading            = ('受容（読む）',   'reception',   'written', 'Reading')
    Listening          = ('受容（聞く）',   'reception',   'spoken',  'Listening')
    Writing            = ('産出（書く）',   'production',  'written', 'Writing')
    Speaking           = ('産出（話す）',   'production',  'spoken',  'Speaking')
    WrittenInteraction = ('やりとり（文書）', 'interaction', 'written', 'Written interaction')
    SpokenInteraction  = ('やりとり（口頭）', 'interaction', 'spoken',  'Spoken interaction')

    @property
    def cefr(self) -> str:
        return f'{self.category}, {self.modality}'


class SkillSituation(Enum):
    def __new__(cls, ja: str, label: str):
        obj = object.__new__(cls)
        obj._value_ = ja
        obj.label = label
        return obj

    DailyLife = ('暮らす',   'Daily life')
    Work      = ('働く',     'Work')
    GoingOut  = ('出かける', 'Going out')


@dataclass
class Skill:
    title: str
    type: SkillType
    description: str
    cefr: str
    activity: SkillActivity
    situation: SkillSituation
    question: str
    example: str
    example_translated: str

    def __post_init__(self):
        self.description = re.match(r'<\d+> (.+)', self.description).group(1)
        self.cefr = self.cefr.strip()
        self.type = SkillType(str(self.type)[1])
        self.activity = SkillActivity(self.activity)
        self.situation = SkillSituation(self.situation)


@dataclass
class Sentence:
    pattern: str
    pattern_translated: str
    example: str
    example_translated: str
    highlights: InitVar[list[list[int]]]

    def __post_init__(self, highlights):
        example_highlighted = ''
        i, end = 0, 0
        for start, end in highlights:
            example_highlighted += f'{self.example[i:start]}<i>{self.example[start:end]}</i>'
            i = end
        self.example = example_highlighted + self.example[end:]


class Lesson:
    def __init__(self, data: dict):
        self.index = data['index']
        self.book = Book(data['book'])
        self.topic = data['topic']
        self.lesson = data['lesson']
        self.number = int(re.findall(r'\d+', self.lesson)[0])

        self.skill = Skill(**{k[6:]: v for k, v in data.items() if k.startswith('skill_')}) if 'skill_title' in data else None
        self.sentence = Sentence(**{k[9:]: v for k, v in data.items() if k.startswith('sentence_')}) if 'sentence_pattern' in data else None

    @property
    def key(self):
        return f'{self.book.value}+{self.number}'

    def __str__(self):
        return f'{self.book.value}: {self.number}'

    def merge(self, other: Lesson) -> Lesson:
        if self.skill is None:
            self.skill = other.skill
        if self.sentence is None:
            self.sentence = other.sentence
        return self
