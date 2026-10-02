# Bringing the Google Slides copies up to date

The Google Slides decks in the Drive folder
(https://drive.google.com/drive/folders/1A9KdZtTAAscFbfyCkaus1eiJxGaDCe_N) were converted from the
PowerPoint files at commit `1de440f`. This lists every change made since then, as exact
"old text → new text" pairs, so they can be applied in place with Slides `replaceAllText`
(match case on). Re-read each deck's `revisionId` before writing.

| Lesson | Google Slides ID | Status |
| --- | --- | --- |
| 1 | `1oxFbmVdb1cVu9SL2_K6M1sWrFxjf4w1Y9hgSYTWgPRM` | Done |
| 2 | `1X4jHPyu0O0T5gmhCg4pUujpdqHX02DJyFnhWk5Q9ihI` | Done |
| 3 | `1_Jc6W1PN4MZgqWMecsNq296upP43r_rzks4TeyGw0ZE` | Done |
| 4 | `11NsjNpAkyWpkMDKh69TpNc2TRA5R0G__aoKArdGxsA8` | Done |
| 5 | `1PN0t1OTRE26NMXrN3LQeItFmcXpvlWQg6fegUtaZS-c` | Done |

The Lesson 1 Google Slides deck has an extra slide after the agenda added by the owner; leave it alone.

## Lesson 2

- `What an ERD is for, and its building blocks: entities, instances and attributes.` → `What an ERD is for, and its building blocks: entities (strong and weak), instances and attributes.` (2×)
- `A repeatable method, applied to the COMPANY database.` → `A repeatable method, applied to the COMPANY database, and the mistakes to avoid.` (2×)
- `How entities connect: degree, cardinality ratio and participation.` → `How entities connect: degree, cardinality ratio and participation, drawn in Chen and crow's foot notation.` (2×)
- `M:N, both total. In a real schema this becomes the WORKS_ON junction table (Lesson 3).` → `M:N, both total; it becomes the WORKS_ON junction table. Tools draw logical models, so PK/FK columns appear; a Chen ERD has no FKs.`
- Notes, car case (2/2): replace the whole "Hints: MODEL key = composite (Name, Suffix)…" note with the note in `builder/lesson2.py` (`notes="Hints: the narrative says the model name is unique…"`).

## Lesson 4

- `The four families of SQL statements, transactions, schemas, data types and constraints.` → `The four families of SQL statements, transactions, schemas and data types.` (2×)
- `CREATE, ALTER, DROP and TRUNCATE.` → `CREATE, ALTER, DROP and TRUNCATE, with constraints and foreign keys.` (2×, agenda + divider only)
- `SELECT, filtering, NULLs, sorting and computed columns.` → `SELECT, DISTINCT, filtering, NULLs, sorting, computed columns and CASE.` (2×)
- ALTER TABLE slide code: after the line `ALTER TABLE students MODIFY city VARCHAR2(80);            -- Oracle` add the line `ALTER TABLE students ALTER COLUMN city VARCHAR(80);       -- SQL Server`
- `ALTER TABLE students ADD city VARCHAR(30);` → `ALTER TABLE persons ADD city VARCHAR(30);`
- `Dates in ISO format 'YYYY-MM-DD' are understood by every DBMS.` → `Write dates as 'YYYY-MM-DD' (SQL Server, PostgreSQL, MySQL). Oracle needs the ANSI literal DATE '2003-05-14' or TO_DATE.`
- `INSERT INTO students (last_name, city)` → `INSERT INTO persons (last_name, city)`
- Update safely slide: `UPDATE students` (the one followed by `SET    address = '241 El-Haram'`) → `UPDATE persons`
- `-- employees working in Giza` → `-- employees in departments located in Houston`; `WHERE  dlocation = 'Giza');` → `WHERE  dlocation = 'Houston');`
- `-- departments in Giza or managed by 333445555` → `-- departments in Stafford or managed by 333445555`; `WHERE  dlocation = 'Giza';` → `WHERE  dlocation = 'Stafford';`
- `They ignore NULLs: COUNT(*) counts rows` → `All except COUNT(*) ignore NULLs: COUNT(*) counts rows`
- Notes, INSERT with missing columns: append `: that is why this example uses a simple persons table, not students (whose id and first_name are required).` in place of the final `.` of "…the INSERT fails."

## Lesson 3

Text:
- `Case study · pitfalls · recap` → `Summary · pitfalls · 3 case studies · recap`
- `weekday (PK) , start_time, room` → `weekday (PK), start_time (PK), room`
- `Binary 1:N —Put the FK` → `Binary 1:N — put the FK`
- `CASE STUDY · 1 OF 3 · NARRATIVE` (bank slide only, not CAR/BUS) → `BANK CASE STUDY · 1 OF 3 · NARRATIVE`; same for `2 OF 3 · ERD` and `3 OF 3 · TABLES`
- `Why is the fact ternary, not three binaries?` → `Ternary, or two binaries? Check the FDs.`
- Car narrative callout → `Key constraint: a model's parts are made in the same factory as the model. Each model has exactly one factory, so the model already tells us the factory: two binary relationships are enough.`
- `One ternary “produces” — model, part, factory` → `Two binaries: model uses parts, model produced at one factory`
- Car ERD callout → `Why not a ternary? model → factory: a ternary produces(model, part, factory) would repeat the model's factory for every part — a 2NF violation (Lesson 5). The factory that makes a part is found through its models.`
- Car tables: model badge `step 1` → `step 1+4`; model columns add `factory_city (FK, NN)` (teal); table `produces` / `step 7` → `model_part` / `step 5`; its columns → `model_name (PK, FK) part_id (PK, FK)`
- Car design note → `Design note — no ternary: factory_city lives in model (N:1, step 4) and model_part is a plain M:N junction (step 5). Every table is in 3NF; the factories that make a part come from joining model_part with model.`
- `km, start, end duration` → `km, start_point, end_point, duration`
- `20 · RECAP` → `25 · RECAP`; `21 · CHECK YOURSELF` → `26 · CHECK YOURSELF`
- Notes on slides 8, 19, 20, 21, 24, 27: copy from `pptx/ITI_Database_Course_Lesson_3_Enhanced.pptx`.

Images (`replaceImage`, public URLs):
- Slide 8 ERD → https://raw.githubusercontent.com/ahmedatef2007/db-slides/claude/database-course-slides-eb98f7/pptx/images/lesson3_weak_entity_erd.png
- Slide 20 ERD → https://raw.githubusercontent.com/ahmedatef2007/db-slides/claude/database-course-slides-eb98f7/pptx/images/lesson3_car_erd.png
