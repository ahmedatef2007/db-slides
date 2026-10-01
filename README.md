# Database Fundamentals — revised slides

Revised edition of the ITI *Database Fundamentals* course slides (original by Shahinaz S. Azab, edited by Mona Saleh & Rana Salah).
The original decks are in `drive-download-20261001T105258Z-1-001.zip`.

| Lesson | Topic | Slides |
| --- | --- | --- |
| 1 | Introduction to databases | 28 |
| 2 | Entity Relationship Diagrams | 37 |
| 3 | Mapping ERD to tables | 28 |
| 4 | SQL | 65 |
| 5 | Normalization | 36 |

Every lesson ends with key takeaways, optional exercises (Core / Stretch / Challenge) and a "Study more" list.
Speaker notes start with `Fixed:` where a slide corrects the original material.

## Layout

- `design-system/` — the "Database Course" design system (colors, type scale, spacing, cover).
- `builder/` — Python generator: `lib.py` (templates, ERD drawing, SQL highlighting) and `lessonN.py` (content).
- `decks/lessonN/project/` — generated slide files (`deck.json` + one HTML file per slide).

Rebuild after editing content:

```sh
cd builder && python3 build.py 1 2 3 4 5
```
