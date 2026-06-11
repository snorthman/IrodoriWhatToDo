# Irodori Exam Generation Spec

This document specifies how to turn a list of Irodori can-do items into exam
entries. For each input item the generator produces, when a skill is present, a
reader-facing question plus one example and its translation; and when a
sentence is present, a structural gloss of the grammar pattern plus a
translation of the example sentence. Input and output are paired by `index`,
not by repeating the lesson fields.

## Input

The input is a JSON list of objects. A full object (both groups present) looks
like:

```json
{
  "book": "初級2",
  "topic": "地域のイベント",
  "lesson": "第8課  屋台はどこかわかりますか？",
  "skill_title": "イベントの感想",
  "skill_type": "【書】",
  "skill_description": "<37> SNSに、自分が参加したイベントについて、簡単に書き込むことができる。",
  "skill_cefr": "A2",
  "skill_activity": "やりとり（文書）",
  "skill_situation": "暮らす",
  "sentence_pattern": "【疑問詞】＋S（普通形）か、～",
  "sentence_example": "明日のフリーマーケットは、何時からか、わかりますか？",
  "sentence_highlights": [[13, 18]],
  "index": 43
}
```

### Field meanings

- `index`: integer unique key. This is the join key between input and output.
  Copy it to the output verbatim. It is the only field carried across.
- `book`, `topic`, `lesson`: lesson context. Not echoed to the output, but use
  `topic` and `skill_situation` to keep generated examples on-theme.
- `skill_title`: a short label or representative phrase for the skill (e.g.
  `イベントの感想`, `防災パンフレット`). Treat it only as a hint to intent. It
  is not the example and need not appear in the output.
- `skill_type`: modality tag, `【話】` speaking, `【書】` writing, `【読】`
  reading, `【聞】` listening. Drives how the question and example are framed.
- `skill_description`: the can-do statement, the authoritative description of
  what the reader should be able to do. May carry an item-number prefix in
  angle brackets such as `<37>`. Strip that prefix and surrounding whitespace
  before using it.
- `skill_cefr`: CEFR level (`A1`, `A2`, ...). Metadata; does not change the
  question.
- `skill_activity`: CEFR communicative activity plus channel, e.g.
  `やりとり（文書）`, `受容（読む）`, `やりとり（口頭）`. Metadata. If its
  channel ever disagrees with `skill_type` / `skill_description`, trust
  `skill_type` and `skill_description` for modality.
- `skill_situation`: life situation, e.g. `暮らす` (daily life), `働く`
  (working). Metadata; useful for grounding examples.
- `sentence_pattern`: the grammar pattern, written in Irodori's pattern
  notation (slot placeholders like `V`, `N`, `S`; form annotations in round
  brackets like `（普通形）`; a grammar-category tag in angle brackets like
  `＜使役受身＞`; and glue such as `＋`, `～`, `か`). It is glossed into
  `sentence_pattern_translated`; it is not turned into a question or a new
  example.
- `sentence_example`: the example sentence for the pattern. The output
  translates this; it is not regenerated.
- `sentence_highlights`: a list of half-open `[start, end)` character ranges
  into `sentence_example` marking where the pattern appears. Provided already,
  consumed by the display layer. Not transformed and not echoed to the output.
- A skill group is present when `skill_description` is populated; a sentence
  group is present when `sentence_example` is populated.

### Invariant

Every object has a skill group or a sentence group or both, never neither.

## Output

A JSON list of objects, paired to the input by `index`. The output never
repeats `book`, `topic`, `lesson`, the patterns, or the highlights; the
consumer rejoins on `index`.

```json
{
  "index": 43,
  "skill_question": "Can you write a short post on social media about an event you took part in?",
  "skill_example": "昨日の夏祭りに行きました。屋台がたくさんあって、楽しかったです！",
  "skill_example_translated": "I went to the summer festival yesterday. There were lots of food stalls and it was fun!",
  "sentence_pattern_translated": "question word + clause (plain form) + か, …",
  "sentence_pattern_description": "Embedding a question inside a larger sentence (an indirect question)",
  "sentence_example_translated": "Do you know what time tomorrow's flea market starts?"
}
```

### Fields

- `index`: copied from the input.
- `skill_question`: English, addressed to the reader. Present only when the
  skill group is present.
- `skill_example`: one Japanese example demonstrating the skill. Generated.
  Present only when the skill group is present.
- `skill_example_translated`: natural English translation of `skill_example`.
  Present only when the skill group is present.
- `sentence_pattern_translated`: a structural gloss of `sentence_pattern` that
  explains it in English while keeping its Japanese morphology intact (see
  [sentence_pattern_translated](#sentence_pattern_translated)). Present only
  when the sentence group is present.
- `sentence_pattern_description`: a short English phrase describing what the
  pattern is *for* — its communicative intent or function — rather than its
  structure (see
  [sentence_pattern_description](#sentence_pattern_description)). Present only
  when the sentence group is present.
- `sentence_example_translated`: natural English translation of the input
  `sentence_example`. Present only when the sentence group is present.

### Absent groups

When a group is absent, omit its fields entirely rather than emitting empty
strings. So a sentence-only item has `index`, `sentence_pattern_translated`,
`sentence_pattern_description`, and `sentence_example_translated`; a skill-only
item has `index`,
`skill_question`, `skill_example`, and `skill_example_translated`. (If you
prefer stable keys across all rows, substitute `""` for the missing fields
instead, but pick one convention and keep it.)

## Building each field

### skill_question

English, framed as a yes/no question asking the reader about their own ability:
"Can you ...?" (or "Can you ... each other ...?" for mutual can-dos such as
たずね合う). Base it on `skill_description` with the `<nn>` prefix stripped, not
on `skill_title` or `skill_activity`. Frame the verb by modality:

- Productive (`【話】` speak, `【書】` write): "Can you say / ask / write ...?"
- Receptive (`【読】` read, `【聞】` listen): "Can you understand ... when you
  read it / hear it?"

### skill_example and skill_example_translated

`skill_example` is a single Japanese example that demonstrates
`skill_description`, generated fresh; `skill_title` is at most a hint. Ground it
in `topic` and `skill_situation` so it reads as a plausible instance of the
can-do.

- Productive skills: an utterance or short text the reader would produce.
- Receptive skills: a short sample of the text or announcement the reader is
  meant to understand (a pamphlet line, a store announcement, a notice), not
  something the reader produces.

`skill_example_translated` is a natural English translation of `skill_example`.

**Line breaks (`　`, U+3000).** A full-width / ideographic space `　` inside
`skill_example` is not whitespace — it is a deliberate line break (e.g. the two
lines of a message sticker or a short notice). Treat it as a hard newline:

- In `skill_example`, keep the break as a real newline character `\n` (the JSON
  escape `\n`), not as a literal `　`.
- In `skill_example_translated`, translate each line on its own and join them
  with the same `\n`, so the Japanese and the English line up line-for-line.

So `おはよう！　今日もがんばろう！` becomes `"おはよう！\n今日もがんばろう！"` and
its translation `"Good morning!\nLet's do our best again today!"`.

### sentence_pattern_translated

A structural gloss of `sentence_pattern`, **not** a free translation and **not**
a translation of the example sentence. The goal: a reader who cannot decode
Irodori's pattern notation can still see exactly which Japanese morphemes make
up the pattern and what grammatical category it belongs to. Two rules:

1. **Keep the Japanese morphology verbatim.** The kana that *is* the grammar
   point — conjugation fragments, particles, and fixed endings such as
   `さ（せら）れる`, `かどうか`, `か`, `は`, `ありますか` — is copied through
   unchanged. Do not romanize it, translate it away, or "fix" its okurigana.
2. **Translate the notation around it into English.** Render the meta-symbols
   that frame the morphology:
   - Slot placeholders → the English word: `V` → "verb", `N` → "noun",
     `A`/`Adj` → "adjective", `S` → "sentence/clause", `【疑問詞】` →
     "question word".
   - Round-bracket form annotations → English in parentheses: `（普通形）` →
     "(plain form)", `（は）` → "(は)" (an optional particle stays as the
     particle).
   - Angle-bracket category tags `＜…＞` → the English grammar term in
     parentheses: `＜使役受身＞` → "(causative-passive)", `＜使役＞` →
     "(causative)", `＜受身＞` → "(passive)", `＜尊敬＞` → "(honorific)".
   - Glue: `＋` → "+", `～` → "…", `、` → ",".

So `V-さ（せら）れる＜使役受身＞` becomes:

```
verb + さ（せら）れる (causative-passive)
```

The English carries the placeholder ("verb"), the literal Japanese ending is
preserved (`さ（せら）れる`), and the `＜使役受身＞` tag is rendered as the
grammar term `(causative-passive)`. Note `使役受身` is specifically
*causative-passive* ("be made to do"), distinct from a plain causative
`使役`; translate the tag exactly, not loosely.

This is a best-effort gloss, not a guaranteed round-trippable grammar. When a
pattern resists a clean structural reading, keep the morphology intact and gloss
the meta-notation as well as you can rather than rewriting the pattern.

**Numbered annotations (`①②③④⑤` etc.).** Some patterns carry a circled or
otherwise non-ASCII number, e.g. `V-（ら）れる＜受身⑤：迷惑の受身＞` or
`V-ています ①`. These are Irodori's *curriculum index* — which sub-type of a
grammar point is being taught (here, the 5th kind of passive, the "adversative /
annoyance" passive) — not part of the grammar a learner produces. The bare
number means nothing to an English reader, so **drop it from
`sentence_pattern_translated`** and express the *sense* it stands for instead
(e.g. "adversative passive"); `sentence_pattern_description` then carries the
intent.

### sentence_pattern_description

A short English phrase naming the **communicative intent** of the pattern — what
a learner uses it *to do*, and the nuance it carries — as opposed to
`sentence_pattern_translated`, which describes its *structure*. It does not
mention the example sentence; it characterizes the pattern itself.

For `V-（ら）れる＜受身⑤：迷惑の受身＞` / `遅い時間に音を出されると困る人もいますからね。`:

```
"Passive voice to express annoyance"
```

Keep it just a little fuller than a bare label — one short clause naming what
the speaker is doing plus the nuance, e.g. "Passive voice used to express that
something is annoying or troublesome". Not a sentence or two; just a bit more
than the terse "Passive voice to express annoyance". When the pattern carried a
numbered sub-type (see the note above), this field is where that meaning lands.

### sentence_example_translated

A natural English translation of the input `sentence_example`. Do not
regenerate the sentence or alter the pattern; just translate what is there. The
translation should convey the grammar the highlights point at, but the
highlight ranges themselves are not reproduced in the output.

## Worked examples

### Both groups, productive writing

The `index 43` input above produces the Output example above.

### Both groups, receptive reading

Input:

```json
{
  "book": "初級2",
  "topic": "自然と環境",
  "lesson": "第16課  地震が来ても、あわてて動かないでください",
  "skill_title": "防災パンフレット",
  "skill_type": "【読】",
  "skill_description": "<72> 外国人向けのやさしい日本語で書かれた防災パンフレットを読んで、内容を理解することができる。",
  "skill_cefr": "A2",
  "skill_activity": "受容（読む）",
  "skill_situation": "暮らす",
  "sentence_pattern": "V（普通形）かどうか、～",
  "sentence_example": "店が開いているかどうか、わからないけど…。",
  "sentence_highlights": [[2, 11], [12, 17]],
  "index": 51
}
```

Output:

```json
{
  "index": 51,
  "skill_question": "Can you read a disaster-prevention pamphlet written in easy Japanese for foreigners and understand its content?",
  "skill_example": "地震のときは、まず火を消してください。そして、机の下に入って、頭を守ってください。",
  "skill_example_translated": "When there is an earthquake, first turn off any flames. Then get under a desk and protect your head.",
  "sentence_pattern_translated": "verb (plain form) + かどうか, …",
  "sentence_pattern_description": "Saying whether or not something is the case (expressing uncertainty)",
  "sentence_example_translated": "I'm not sure whether the shop is open or not..."
}
```

Note: the skill is receptive, so `skill_example` is a sample pamphlet text the
reader should understand, not an utterance they produce.

### Sentence only, no skill

Input:

```json
{
  "book": "入門",
  "topic": "好きな食べ物",
  "lesson": "第6課  チ-ズバ-ガ-ください",
  "sentence_pattern": "N（は）ありますか？",
  "sentence_example": "マヨネ-ズ、ありますか？",
  "sentence_highlights": [[6, 12]],
  "index": 54
}
```

Output:

```json
{
  "index": 54,
  "sentence_pattern_translated": "noun (は) + ありますか？",
  "sentence_pattern_description": "Asking whether a shop or place has an item",
  "sentence_example_translated": "Do you have mayonnaise?"
}
```

Note: no skill group, so the three `skill_*` fields are omitted.

### Skill only, no sentence

Input:

```json
{
  "book": "入門",
  "topic": "はじめての日本語",
  "lesson": "第2課  すみません、よくわかりません",
  "skill_title": "これは日本語で何と言いますか？",
  "skill_type": "【話】",
  "skill_description": "<7> 日本語の言い方がわからないとき、どう言えばいいか質問して、その答えを理解することができる。",
  "skill_cefr": "A1",
  "skill_activity": "やりとり（口頭）",
  "skill_situation": "暮らす",
  "index": 1
}
```

Output:

```json
{
  "index": 1,
  "skill_question": "When you don't know how to say something in Japanese, can you ask how to say it and understand the answer?",
  "skill_example": "すみません、これは日本語で何と言いますか？",
  "skill_example_translated": "Excuse me, how do you say this in Japanese?"
}
```

Note: no sentence group, so `sentence_example_translated` is omitted.

### Skill with a line break (`　`)

Input:

```json
{
  "book": "入門",
  "topic": "あいさつ",
  "lesson": "第1課  はじめまして",
  "skill_title": "メッセージスタンプ",
  "skill_type": "【読】",
  "skill_description": "<3> 「おはよう」「ありがとう」などのメッセージスタンプを見て、意味を理解することができる。",
  "skill_cefr": "A1",
  "skill_activity": "受容（読む）",
  "skill_situation": "暮らす",
  "index": 8
}
```

Output:

```json
{
  "index": 8,
  "skill_question": "When you see message stickers like \"good morning\" or \"thank you\", can you understand what they mean?",
  "skill_example": "おはよう！\n今日もがんばろう！",
  "skill_example_translated": "Good morning!\nLet's do our best again today!"
}
```

Note: the source example used a full-width space `　` between the two lines; it
becomes a `\n` in both `skill_example` and `skill_example_translated`, kept
aligned line-for-line.

## Edge cases

- Item-number prefixes like `<37>`, `<72>` in `skill_description`: strip before
  phrasing the question.
- Modality conflict between `skill_type` / `skill_description` and
  `skill_activity`: trust `skill_type` and `skill_description`.
- Full-width space `　` (U+3000) in `skill_example`: it is a line break, not
  whitespace. Convert it to `\n` and mirror the break in
  `skill_example_translated`. (Ordinary half-width spaces are not affected.)
- `sentence_pattern_translated` keeps the Japanese morphology verbatim; only the
  notation around it (placeholders, `（…）` annotations, `＜…＞` tags, glue) is
  rendered in English. Do not romanize the kana or rewrite the pattern.
- Emit valid JSON; escape any embedded double quotes as `\"`. Real newlines from
  `　` are written as the `\n` escape.
- An object with neither group violates the invariant; skip it and report it
  rather than emitting a row with only `index`.
