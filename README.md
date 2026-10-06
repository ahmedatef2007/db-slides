# Database Fundamentals — revised slides

Revised edition of the ITI *Database Fundamentals* course slides (original by Shahinaz S. Azab, edited by Mona Saleh & Rana Salah).
The original decks are in `drive-download-20261001T105258Z-1-001.zip`.

| Lesson | Topic | Slides | Live deck |
| --- | --- | --- | --- |
| 1 | Introduction to databases | 33 | [open](https://claude.ai/artifact/5teStuvyM1f1oLaU8L3GcW) |
| 2 | Entity Relationship Diagrams | 39 | [open](https://claude.ai/artifact/TE7NwTVj8XWn9FJqDt9sdM) |
| 3 | Mapping ERD to tables | 29 | [open](https://claude.ai/artifact/JqZE53MiihvTU84s272k1s) |
| 4 | SQL | 69 | [open](https://claude.ai/artifact/2JY6phqo8DmAq7UBtjYwp4) |
| 5 | Normalization | 44 | [open](https://claude.ai/artifact/S4aGyaTj33KiZvx9nW4ioj) |

Design system: [Database Course](https://claude.ai/artifact/WdbVXkRa43NmX6n2AKuXTF). The decks are private until shared from each deck's Share menu.

Every lesson ends with key takeaways, optional exercises (Core / Stretch / Challenge) and a "Study more" list.
Speaker notes start with `Fixed:` where a slide corrects the original material.

## PowerPoint decks (ITI template)

`pptx/` holds the five lessons as PowerPoint files in the style of the *Lesson 3 Enhanced* deck
(white slides, ITI crimson, teal for foreign keys, Arial / Calibri / Courier New, 20" × 11.25"):

| Lesson | File | Slides |
| --- | --- | --- |
| 1 | `ITI_Database_Course_Lesson_1_Introduction.pptx` | 35 |
| 2 | `ITI_Database_Course_Lesson_2_ERD.pptx` | 41 |
| 3 | `ITI_Database_Course_Lesson_3_Enhanced.pptx` (the template deck itself) | 27 |
| 4 | `ITI_Database_Course_Lesson_4_SQL.pptx` | 71 |
| 5 | `ITI_Database_Course_Lesson_5_Normalization.pptx` | 46 |

They are generated from the same lesson content as the web decks: `builder/pptlib.py` is a
PowerPoint backend for the builder and `builder/iti_template.pptx` supplies the theme. Rebuild with:

```sh
cd builder && python3 build_pptx.py 1 2 4 5   # needs python-pptx
```

## Layout

- `design-system/` — the "Database Course" design system (colors, type scale, spacing, cover).
- `builder/` — Python generator: `lib.py` (templates, ERD drawing, SQL highlighting) and `lessonN.py` (content).
- `decks/lessonN/project/` — generated slide files (`deck.json` + one HTML file per slide).

Rebuild after editing content:

```sh
cd builder && python3 build.py 1 2 3 4 5
```
