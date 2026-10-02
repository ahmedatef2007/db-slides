# Database Fundamentals — revised slides

Revised edition of the ITI *Database Fundamentals* course slides (original by Shahinaz S. Azab, edited by Mona Saleh & Rana Salah).
The original decks are in `drive-download-20261001T105258Z-1-001.zip`.

| Lesson | Topic | Slides | Live deck |
| --- | --- | --- | --- |
| 1 | Introduction to databases | 28 | [open](https://claude.ai/artifact/5teStuvyM1f1oLaU8L3GcW) |
| 2 | Entity Relationship Diagrams | 37 | [open](https://claude.ai/artifact/TE7NwTVj8XWn9FJqDt9sdM) |
| 3 | Mapping ERD to tables | 28 | [open](https://claude.ai/artifact/JqZE53MiihvTU84s272k1s) |
| 4 | SQL | 65 | [open](https://claude.ai/artifact/2JY6phqo8DmAq7UBtjYwp4) |
| 5 | Normalization | 36 | [open](https://claude.ai/artifact/S4aGyaTj33KiZvx9nW4ioj) |

Design system: [Database Course](https://claude.ai/artifact/WdbVXkRa43NmX6n2AKuXTF). The decks are private until shared from each deck's Share menu.

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
