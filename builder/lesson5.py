from lib import *


def rel_cells(names, x0, top, w, keys=(), h=70, label=None):
    out = ""
    if label:
        out += f'<p style="position:absolute;left:{x0}px;top:{top - 48}px;width:600px;font-family:{DISPLAY};font-size:28px;font-weight:600;color:{INK}">{esc(label)}</p>'
    for i, n in enumerate(names):
        t = f"<u>{esc(n)}</u>" if n in keys else esc(n)
        out += (f'<div style="position:absolute;left:{x0 + i * w}px;top:{top}px;width:{w}px;height:{h}px;background:{CARD};'
                f'border:2px solid {INK};display:flex;align-items:center;justify-content:center">'
                f'<p style="font-family:{MONO};font-size:24px;color:{INK};text-align:center">{t}</p></div>')
    return out


def conn(x1, y1, x2, y2, head="none", color=INK):
    return (f'<x-connector x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" head="{head}" '
            f'style="color:{color};border-width:3px"></x-connector>')


def stage_box(label, lines, tone=None, size=24):
    bg, bd = (BLUE_TINT, "#C3D3EE") if tone == "blue" else (CARD, LINE)
    inner = (f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{ACCENT}">{esc(label)}</p>'
             + "".join(schema_line(n, c, size=size) for n, c in lines))
    return (f'<div style="flex:1;display:flex;flex-direction:column;gap:8px;background:{bg};border:1px solid {bd};'
            f'border-radius:16px;padding:24px 32px">{inner}</div>')


KEY_LEGEND = f'<u><b>underlined</b></u> = primary key · <span style="color:{BLUE}"><i>blue italic</i></span> = foreign key'


def build():
    d = Deck(5, "Normalization", "Lesson 5 · Normalization")

    d.cover("cover", "Normalization",
            "Test a table design against normal forms to remove redundancy and update anomalies.",
            ["Anomalies", "Functional dependencies", "1NF · 2NF · 3NF", "BCNF", "Decomposition", "Worked examples"])

    d.slide("objectives", "Lesson 5", "By the end of this lesson you can",
            grid([card(None, body=t, tag=f"{i + 1:02d}", size=30) for i, t in enumerate([
                "Spot **insert, update and delete anomalies**",
                "Identify **functional dependencies** and their types",
                "Normalize a table step by step to **3NF**",
                "Recognize when a table is not in **BCNF**",
                "Check a decomposition is **lossless**",
                "Decide when **denormalizing** is justified"])], cols=3))

    # ---------- 01 ----------
    d.divider("d1", "01", "Why normalize?", "Redundancy causes anomalies; normal forms are tests that catch them.")

    d.slide("what", "Why normalize", "What is normalization?",
            callout("Normalization takes a table through a series of tests (**normal forms**) to certify the goodness of a design and **minimize redundancy and anomalies**.", label="Definition:", size=30)
            + row(card("Top-down design", size=26, body="Conceptual model first (ERD), then map to tables (Lessons 2–3).",
                       items=["Normalization **checks** the result", "Most common in practice"]),
                  card("Bottom-up design", size=26, body="Start from attributes and their relationships (e.g. existing forms, files, spreadsheets).",
                       items=["Normalization **builds** the tables", "Typical for legacy data"])),
            notes="Normalization plays a limited role when the top-down (ERD) approach is used, and a major role in the bottom-up approach, where it is essential to build appropriate relations.")

    d.slide("anomalies", "Why normalize", "Redundancy causes anomalies",
            table(["Ename", "Ssn", "Dnumber", "Dname", "Dmgr_ssn"],
                  [["Smith", "123456789", "5", "**Research**", "**333445555**"], ["Wong", "333445555", "5", "**Research**", "**333445555**"],
                   ["English", "453453453", "5", "**Research**", "**333445555**"], ["Zelaya", "999887777", "4", "Administration", "987654321"]],
                  widths=[18, 22, 16, 24, 20], size=24)
            + grid([card("Insert anomaly", body="Can't add a new department until it has an employee (Ssn is the key).", tone="accent", size=26),
                    card("Update anomaly", body="Research's manager changes → update **every** Research row, or the data becomes inconsistent.", tone="accent", size=26),
                    card("Delete anomaly", body="Delete Zelaya, the last employee of dept 4 → Administration is **lost**.", tone="accent", size=26)], cols=3),
            gap=28,
            notes="EMP_DEPT combines employee and department facts in one table. Department data (Dname, Dmgr_ssn) is repeated for every employee: that redundancy is what causes all three anomalies.")

    d.slide("guidelines", "Why normalize", "Four informal design guidelines",
            grid([card("Clear semantics", body="Don't combine attributes from different entities or relationships in one table.", tag="1", size=26),
                  card("No anomalies", body="Design tables so insert, update and delete anomalies cannot occur.", tag="2", size=26),
                  card("Few NULLs", body="Attributes that are often NULL belong in a separate table (with the PK).", tag="3", size=26),
                  card("No spurious tuples", body="Join only on (FK, PK) pairs; joining on other matching columns invents rows.", tag="4", size=26)], cols=2),
            notes="These are the four informal measures of quality from Elmasri & Navathe: semantics, redundant information, NULL values, spurious tuples.")

    d.slide("avoids", "Why normalize", "Normalization avoids",
            grid([card("Duplicated data", body="The same fact stored in many rows.", icon="Warning", size=26),
                  card("Insert anomaly", body="Can't record one fact without another.", icon="Warning", size=26),
                  card("Update anomaly", body="One change must be made in many places.", icon="Warning", size=26),
                  card("Delete anomaly", body="Deleting one fact loses another.", icon="Warning", size=26),
                  card("Frequent NULLs", body="Wasted space, unclear meaning.", icon="Warning", size=26)], cols=5)
            + row(card("When to use it", tone="blue", size=28, items=["To certify the quality of a relational design",
                                                                       "When taking over designs from legacy systems, files or spreadsheets"]),
                  card("How far to go", size=28, items=["Usually **3NF** or **BCNF** in practice", "Higher forms (4NF, 5NF) for special cases"])))

    # ---------- 02 ----------
    d.divider("d2", "02", "Functional dependencies", "The formal tool behind every normal form.")

    d.slide("fd", "Functional dependencies", "Functional dependency (FD)",
            callout("**A → B** (A *determines* B) if every value of A is associated with **exactly one** value of B.", size=32)
            + table(["FD", "Read as"],
                    [["Ssn → Ename", "A social security number determines one employee name"],
                     ["Pnumber → {Pname, Plocation}", "A project number determines the project's name and location"],
                     ["{Ssn, Pnumber} → Hours", "An employee and a project together determine the weekly hours"]],
                    widths=[38, 62], size=28)
            + p("FDs come from the **meaning** of the data (business rules), not from looking at a few rows.", size=28),
            notes="FDs are constraints derived from the meaning and interrelationships of the attributes. FDs and keys are used to define normal forms. A set of attributes A functionally determines B if the value of A determines a unique value for B.")

    cells = rel_cells(["Ssn", "Pnumber", "Hours", "Ename", "Pname", "Plocation"], 260, 340, 220, keys=("Ssn", "Pnumber"), label="EMP_PROJ")
    lines = (conn(370, 410, 370, 560) + conn(590, 410, 590, 640) + conn(370, 480, 810, 480) + conn(810, 480, 810, 414, head="end")
             + conn(370, 560, 1030, 560) + conn(1030, 560, 1030, 414, head="end")
             + conn(590, 640, 1470, 640) + conn(1250, 640, 1250, 414, head="end") + conn(1470, 640, 1470, 414, head="end"))
    labs = ""
    for y, t in ((480, "FD1"), (560, "FD2"), (640, "FD3")):
        labs += f'<p style="position:absolute;left:150px;top:{y - 18}px;width:90px;font-family:{MONO};font-size:26px;font-weight:700;color:{ACCENT}">{t}</p>'
    expl = (f'<div style="position:absolute;left:128px;top:700px;width:1664px">'
            + table(["FD", "Dependency", "Type"],
                    [["FD1", "{Ssn, Pnumber} → Hours", "**Full**: needs the whole key"],
                     ["FD2", "Ssn → Ename", "**Partial**: depends on part of the key"],
                     ["FD3", "Pnumber → {Pname, Plocation}", "**Partial**: depends on part of the key"]],
                    widths=[12, 46, 42], size=24) + "</div>")
    d.slide("fdpartial", "Functional dependencies", "Full and partial dependencies", lines + cells + labs + expl,
            notes="Redrawn from the original figure (Elmasri & Navathe). The key of EMP_PROJ is {Ssn, Pnumber}. FD2 and FD3 are partial: they violate 2NF.")

    cells = rel_cells(["Ename", "Ssn", "Bdate", "Address", "Dnumber", "Dname", "Dmgr_ssn"], 260, 340, 200, keys=("Ssn",), label="EMP_DEPT")
    lines = (conn(560, 410, 560, 480) + conn(360, 480, 1140, 480)
             + "".join(conn(x, 480, x, 414, head="end") for x in (360, 760, 960, 1140))
             + conn(1190, 410, 1190, 560) + conn(1190, 560, 1560, 560)
             + conn(1360, 560, 1360, 414, head="end") + conn(1560, 560, 1560, 414, head="end"))
    labs = (f'<p style="position:absolute;left:150px;top:462px;width:90px;font-family:{MONO};font-size:26px;font-weight:700;color:{ACCENT}">FD1</p>'
            f'<p style="position:absolute;left:150px;top:542px;width:90px;font-family:{MONO};font-size:26px;font-weight:700;color:{ACCENT}">FD2</p>')
    expl = (f'<div style="position:absolute;left:128px;top:640px;width:1664px;display:flex;flex-direction:column;gap:16px">'
            + callout("Ssn → Dnumber and Dnumber → {Dname, Dmgr_ssn}, so Ssn → Dname **through** Dnumber: a **transitive** dependency. Dnumber is not a key of EMP_DEPT.", size=28)
            + "</div>")
    d.slide("fdtransitive", "Functional dependencies", "Transitive dependencies", lines + cells + labs + expl,
            notes="Transitive dependencies violate 3NF. This is the EMP_DEPT table from the anomalies slide.")

    d.slide("fdtypes", "Functional dependencies", "Three types of functional dependency",
            grid([card("Full", tone="blue", size=26, body="X → Y is **full** if removing **any** attribute from X breaks the dependency.",
                       items=["{Ssn, Pnumber} → Hours"]),
                  card("Partial", size=26, body="X → Y is **partial** if some attribute can be removed from X and the dependency **still holds**.",
                       items=["{Ssn, Pnumber} → Ename (Ssn alone is enough)"]),
                  card("Transitive", tone="accent", size=26, body="X → Y is **transitive** if X → Z and Z → Y, where Z is **not** a key (nor part of one).",
                       items=["Ssn → Dnumber → Dname"])], cols=3))

    # ---------- 03 ----------
    d.divider("d3", "03", "Normal forms", "1NF, 2NF and 3NF step by step, then BCNF and beyond.")

    steps = [("1NF", "Atomic values"), ("2NF", "No partial deps"), ("3NF", "No transitive deps"), ("BCNF", "Every determinant is a key"),
             ("4NF", "No multi-valued deps"), ("5NF", "No join deps")]
    blocks = []
    for i, (n, t) in enumerate(steps):
        tone_bg = BLUE if i < 3 else (INK if i == 3 else "#4A5874")
        blocks.append(f'<div style="flex:1;display:flex;flex-direction:column;justify-content:end;gap:8px;background:{tone_bg};'
                      f'border-radius:16px;padding:28px;height:{220 + i * 70}px">'
                      f'<p style="font-family:{DISPLAY};font-size:48px;font-weight:700;color:{ON_INK}">{n}</p>'
                      f'<p style="font-size:24px;line-height:1.3;color:{ON_INK}">{esc(t)}</p></div>')
    d.slide("ladder", "Normal forms", "Each normal form includes the previous one",
            f'<div style="display:flex;flex-direction:row;gap:16px;align-items:flex-end">' + "".join(blocks) + "</div>"
            + p("Practical designs usually stop at **3NF** or **BCNF**. *Denormalization* deliberately goes back down for performance.", size=28),
            notes="A table in 3NF is also in 2NF and 1NF. Database designers need not normalize to the highest possible normal form.")

    d.slide("1nf", "Normal forms", "First normal form (1NF)",
            callout("A table is in **1NF** if every cell holds a single, **atomic** value: no multi-valued attributes, repeating groups or composite attributes.", size=30)
            + row(card("To reach 1NF", size=28, items=["Move each **repeating group** to a new table, carrying the PK as a FK",
                                                       "Move each **multi-valued attribute** to a new table, carrying the PK as a FK",
                                                       "Split **composite** attributes into one column per part"]),
                  card("Repeating group?", tone="blue", size=28, body="A set of multi-valued columns that belong together, e.g. Subject + Description + Grade for one student.")),
            notes="1NF disallows composite attributes, multivalued attributes and nested relations: attribute domains must contain only atomic (simple, indivisible) values.")

    d.slide("school0", "School example", "School example: unnormalized",
            table(["Stud_ID", "Name", "Location", "Tel", "Level", "Level_Mgr", "Subject", "Subj_Desc", "Grade"],
                  [["11", "Ali", "Cairo", "010", "Primary", "Noha M.", "DB, CN", "Database, Networks", "A, B"],
                   ["22", "Mai", "Giza", "011, 010", "Primary", "Noha M.", "CN, DB", "Networks, Database", "B, C"],
                   ["33", "Marwa", "Giza", "010", "Secondary", "Moh. A.", "SW, DB", "Software, Database", "A, A"]],
                  widths=[9, 9, 10, 10, 11, 11, 10, 19, 11], size=24)
            + row(callout("**Tel** is multi-valued.", tone="blue", size=26),
                  callout("**Subject, Subj_Desc, Grade** form a repeating group.", tone="blue", size=26),
                  callout("**Level → Level_Mgr** and **Subject → Subj_Desc** hide more FDs.", size=26)),
            notes="Solution path (original notes): 1NF (Stud_ID, Name, Loc, Level, Level_Mgr), (Stud_ID, Tel), (Stud_ID, Subject, Subj_desc, Grade); 2NF moves Subj_desc to (Subject, Subj_desc); 3NF moves Level_Mgr to (Level, Level_Mgr).")

    d.slide("school1", "School example", "School example: 1NF",
            stage_box("1NF", [("STUDENT", ["_Stud_ID_", "Name", "Location", "Level", "Level_Mgr"]),
                              ("STUDENT_TEL", ["_Stud_ID*_", "_Tel_"]),
                              ("STUDENT_SUBJECT", ["_Stud_ID*_", "_Subject_", "Subject_Desc", "Grade"])], size=28)
            + p(KEY_LEGEND, size=24, color=MUTED, raw=True)
            + callout("Every cell is now atomic. But STUDENT_SUBJECT still repeats Subject_Desc for every student taking that subject.", size=28))

    d.slide("2nf", "Normal forms", "Second normal form (2NF)",
            callout("A table is in **2NF** if it is in 1NF and **no non-key attribute is partially dependent** on the primary key.", size=30)
            + row(card("To reach 2NF", size=28, items=["Move attributes that depend on **part** of the key to a new table",
                                                       "Take that **part of the key** with them as the new table's PK"]),
                  card("Already in 2NF if any is true", tone="blue", size=28, items=["The PK is a **single** column",
                                                                                    "All columns are part of the PK",
                                                                                    "Every non-key column depends on the **whole** PK"])))

    d.slide("school2", "School example", "School example: 2NF",
            stage_box("2NF", [("STUDENT", ["_Stud_ID_", "Name", "Location", "Level", "Level_Mgr"]),
                              ("STUDENT_TEL", ["_Stud_ID*_", "_Tel_"]),
                              ("STUD_SUBJECT", ["_Stud_ID*_", "_Subject*_", "Grade"]),
                              ("SUBJECT", ["_Subject_", "Subject_Desc"])], size=28)
            + p(KEY_LEGEND, size=24, color=MUTED, raw=True)
            + callout("Subject → Subject_Desc was partial (only part of {Stud_ID, Subject}). STUDENT is still not in 3NF: Level → Level_Mgr.", size=28))

    d.slide("3nf", "Normal forms", "Third normal form (3NF)",
            callout("A table is in **3NF** if it is in 2NF and **no non-key attribute depends transitively** on the primary key (no non-key → non-key dependency).", size=30)
            + row(card("To reach 3NF", size=28, items=["Move the dependent non-key attributes to a new table",
                                                       "Its PK is the non-key attribute they depend on",
                                                       "**Leave** that attribute in the original table as a FK"]),
                  callout("*Every non-key attribute must depend on the key, the whole key, and nothing but the key.*", tone="blue", size=30)),
            notes="The quote summarizes 1NF (the key), 2NF (the whole key) and 3NF (nothing but the key). It is attributed to Bill Kent.")

    d.slide("school3", "School example", "School example: 3NF",
            stage_box("3NF", [("STUDENT", ["_Stud_ID_", "Name", "Location", "Level*"]),
                              ("LEVEL", ["_Level_", "Level_Mgr"]),
                              ("STUDENT_TEL", ["_Stud_ID*_", "_Tel_"]),
                              ("STUD_SUBJECT", ["_Stud_ID*_", "_Subject*_", "Grade"]),
                              ("SUBJECT", ["_Subject_", "Subject_Desc"])], size=28)
            + p(KEY_LEGEND, size=24, color=MUTED, raw=True)
            + callout("Five tables, each about **one thing**. Changing a level manager now updates exactly one row.", tone="blue", size=28))

    d.slide("bcnf", "Normal forms", "Boyce–Codd normal form (BCNF)",
            row(col(callout("A table is in **BCNF** if for every non-trivial FD **X → Y**, X is a **superkey**.", size=28),
                    table(["Student", "Course", "Instructor"], [["Narayan", "Database", "Mark"], ["Smith", "Database", "Navathe"],
                                                                ["Smith", "Operating Systems", "Ammar"], ["Wong", "Database", "Omiecinski"]], size=24),
                    p("TEACH · key {Student, Course} · FD: **Instructor → Course**", size=24, color=MUTED), gap=20, flex="1"),
                col(card("Why it is 3NF but not BCNF", size=26, items=["Course is part of the key, so 3NF allows Instructor → Course",
                                                                       "But Instructor is **not a superkey** → BCNF is violated"]),
                    stage_box("BCNF decomposition", [("INSTRUCTOR_COURSE", ["_Instructor_", "Course"]),
                                                     ("STUDENT_INSTRUCTOR", ["_Student_", "_Instructor*_"])], size=24),
                    gap=20, flex="1"), gap=32),
            notes="New slide: BCNF is the practical target in many textbooks. Trade-off: this decomposition is lossless but does not preserve the FD {Student, Course} → Instructor, which can no longer be checked inside one table. Example from Elmasri & Navathe.")

    d.slide("4nf5nf", "Normal forms", "Beyond BCNF: 4NF and 5NF",
            row(card("4NF: multi-valued dependencies", size=26, body="Two **independent** multi-valued facts about the same key in one table.",
                     items=["EMP(Ename, Pname, Dname): projects and dependents are unrelated", "Every project × every dependent → huge redundancy",
                            "Fix: EMP_PROJECTS(Ename, Pname) + EMP_DEPENDENTS(Ename, Dname)"]),
                card("5NF: join dependencies", size=26, body="A table that can only be rebuilt by joining **three or more** of its projections.",
                     items=["Rare in practice", "Related to the ternary vs three binaries question (Lesson 3)"]))
            + callout("A well-designed ERD mapped with the 7 steps rarely produces 4NF/5NF problems: multi-valued attributes already get their own tables.", tone="blue", size=26),
            notes="New overview slide: the original stopped at 3NF but its notes mentioned BCNF and 4NF as typical targets.")

    d.slide("decomp", "Normal forms", "Good decompositions",
            row(card("Lossless join (required)", tone="blue", size=26, body="Joining the new tables gives back **exactly** the original rows: no spurious rows.",
                     items=["Split R into R1, R2 so the common columns are a **key** of R1 or R2", "That is why we keep the FK (Level) in STUDENT"]),
                card("Dependency preservation (desired)", size=26, body="Every FD can still be checked **inside one table**.",
                     items=["3NF can always keep both properties", "BCNF sometimes must give this up (TEACH example)"])),
            notes="New slide: explains why normalization splits tables in a specific way (Guideline 4: no spurious tuples).")

    d.slide("denorm", "Normal forms", "Denormalization",
            row(card("What", size=28, body="Deliberately storing the **join** of normalized tables, or a derived value, as a base table (a lower normal form)."),
                card("When", tone="blue", size=28, items=["Read-heavy reports and dashboards", "Data warehouses (star schemas)", "Measured performance problems, not guesses"]),
                card("Cost", tone="accent", size=28, items=["Redundancy comes back", "Application or triggers must keep copies in sync", "More storage"]))
            + callout("Normalize first; denormalize only with a **measured** reason, and document it.", size=28))

    # ---------- 04 ----------
    d.divider("d4", "04", "Worked examples", "An ITI student sheet, real school data, and a suppliers table.")

    d.slide("iti0", "ITI example", "ITI student sheet",
            row(card(None, size=26, items=["Student number: **ITI205-40**", "Name: Hassan Ali Ahmed", "Address (Street, City): 12 Haram St, Giza",
                                           "Tel / mobile: 33868420 · 01111111253", "F-code: ENG · Faculty: Engineering · Major: Computer"]), gap=24)
            + table(["Department name", "Department description", "Admission grade", "Comments"],
                    [["ERP-SAP", "ERP-SAP Functional Consultant", "59", "Average personality"], ["Java-MAD", "Java mobile applications developer", "70", "Very good"],
                     ["CS", "Cyber Security", "60", "Above average technical"]], widths=[20, 38, 18, 24], size=24),
            gap=28)

    d.slide("iti1", "ITI example", "ITI sheet: 1NF → 2NF → 3NF",
            row(stage_box("1NF", [("STUDENT", ["_Stud_No_", "Stud_Name", "F_code", "Faculty", "Major", "Street", "City"]),
                                  ("STUDENT_TEL", ["_Stud_No*_", "_Tel_No_"]),
                                  ("DEPT_STUDENT", ["_Dept_Name_", "_Stud_No*_", "Dept_Desc", "Ad_Grade", "Comments"])]),
                stage_box("2NF", [("DEPT_STUDENT", ["_Dept_Name*_", "_Stud_No*_", "Ad_Grade", "Comments"]),
                                  ("DEPARTMENT", ["_Dept_Name_", "Dept_Desc"])]),
                stage_box("3NF", [("STUDENT", ["_Stud_No_", "Stud_Name", "F_code*", "Major", "Street", "City"]),
                                  ("FACULTY", ["_F_code_", "Faculty"])], tone="blue"), gap=20)
            + p(KEY_LEGEND + " · each stage lists only the tables that changed", size=24, color=MUTED, raw=True),
            notes="1NF: phone numbers and the department rows were repeating; Address split into Street, City. 2NF: Dept_Desc depends only on Dept_Name. 3NF: Faculty depends on F_code, a non-key attribute.")

    d.slide("real0", "Real-world data", "Real-world school data",
            table(["First", "Parent 1", "Parent 2", "App No", "City", "Postal code", "Birth date"],
                  [["Renee", "Ann Jones", "Theodore Smith", "123", "Annandale", "22003", "6/25/1983"],
                   ["Lucy", "Barbara Mills", "Steve Mills", "558", "Annandale", "22003", "8/14/1983"],
                   ["Brendan", "Jennifer Jones", "Stephen Jones", "145", "Fairfax", "22032", "6/13/1984"]], size=24)
            + table(["Prev. teacher", "Curr. teacher", "Student phone", "Course", "Course desc", "Enrolled", "Attended days"],
                    [["Hamil", "Burke", "(703) 323-0893, (703) 324-0708", "X, Y, Z", "X, Y, Z", "96/97, 96/97, 97/98", "0, 0, 0"],
                     ["Hamil", "Burke", "(703) 764-5829", "Y", "Y", "96/97", "0"], ["Hamil", "Burke", "(703) 978-1083", "Z", "Z", "96/97", "0"]],
                    widths=[12, 12, 22, 11, 12, 18, 13], size=24),
            gap=24,
            notes="0NF: STUDENT(App_No, Stud_Fname, Parent1, Parent2, City, Postal_Code, Birthdate, Prev_Teacher, Curr_Teacher, Student_Phone, Course, Course_Desc, Enrolled, Att_Days)")

    d.slide("real1", "Real-world data", "School data: 1NF → 3NF",
            stage_box("1NF", [("STUDENT", ["_App_No_", "Stud_Fname", "Parent1", "Parent2", "City", "Postal_Code", "Birthdate", "Prev_Teacher", "Curr_Teacher"]),
                              ("STUDENT_COURSE", ["_App_No*_", "_Course_", "Course_Desc", "Enrolled", "Att_Days"]),
                              ("STUDENT_PHONE", ["_App_No*_", "_Phone_"])])
            + row(stage_box("2NF (changed)", [("STUDENT_COURSE", ["_App_No*_", "_Course*_", "Enrolled", "Att_Days"]),
                                              ("COURSE", ["_Course_", "Course_Desc"])]),
                  stage_box("3NF (changed)", [("STUDENT", ["_App_No_", "…", "Postal_Code*", "…"]),
                                              ("POSTAL_CODE", ["_Postal_Code_", "City"])], tone="blue"), gap=20)
            + p(KEY_LEGEND, size=24, color=MUTED, raw=True),
            gap=20,
            notes="Clarified: the original 3NF table was written City (City, Postal_Code). The dependency is Postal_Code → City, so the new table's key is Postal_Code and STUDENT keeps Postal_Code as a FK.")

    d.slide("supp0", "Suppliers", "Suppliers data",
            row(card(None, size=28, items=["Relation (**S#**, Country, Currency, **P#**, Qty)", "S#: supplier number", "Country: where the supplier is located",
                                           "Currency: the currency of that country", "P#: part number supplied", "Qty: quantity supplied to date"]),
                card("Key", tone="blue", size=28, body="Qty depends on supplier **and** part, so the PK is the composite **{S#, P#}**.",
                     items=["S# → Country", "Country → Currency", "{S#, P#} → Qty"])))

    d.slide("supp1", "Suppliers", "Suppliers: 1NF → 2NF → 3NF",
            row(stage_box("1NF", [("SUPPLY", ["_S#_", "Country", "Currency", "_P#_", "Qty"])]),
                stage_box("2NF", [("SUPPLIER", ["_S#_", "Country", "Currency"]), ("SUPPLIER_PART", ["_S#*_", "_P#_", "Qty"])]),
                stage_box("3NF", [("SUPPLIER", ["_S#_", "Country*"]), ("COUNTRY", ["_Country_", "Currency"]), ("SUPPLIER_PART", ["_S#*_", "_P#_", "Qty"])], tone="blue"), gap=20)
            + callout("Every value is already atomic, so the original relation **is already in 1NF**. The split into SUPPLIER and SUPPLIER_PART removes the **partial** dependency S# → Country, Currency: that is the **2NF** step.", size=26)
            + p(KEY_LEGEND, size=24, color=MUTED, raw=True),
            notes="Fixed: the original showed the SUPPLIER / SUPPLIER_PARTS split as the 1NF step and said 2NF was 'same as first'. Since the relation has no multi-valued or repeating attributes it is already in 1NF; removing the partial dependency is by definition the 2NF step.")

    d.takeaways("recap", [
        "Redundancy causes **insert, update and delete anomalies**.",
        "A **functional dependency** A → B: A determines exactly one B.",
        "**1NF** atomic values · **2NF** no partial deps · **3NF** no transitive deps.",
        "**BCNF**: every determinant is a superkey.",
        "Decompositions must be **lossless**; keep dependencies when you can.",
        "**Denormalize** only for measured performance needs."])

    d.slide("salesorder", "Practice", "Normalize this sales order",
            row(col(card(None, size=26, items=["Customer number: 1001 · Name: ABC Company", "Customer address: 100 Points, Manhattan, KS 66502",
                                               "Sales order number: 405 · Date: 2/1/2000", "Clerk number: 210 · Clerk name: Martin Lawrence"]),
                    table(["Item", "Description", "Qty", "Unit price", "Total"],
                          [["800", "widget small", "40", "60.00", "2,400.00"], ["801", "tingimajigger", "20", "20.00", "400.00"],
                           ["805", "thingibob", "10", "100.00", "1,000.00"], ["", "**Order total**", "", "", "**3,800.00**"]],
                          widths=[12, 34, 12, 20, 22], size=24), gap=16, flex="3"),
                col(card("Your task", tone="blue", size=26, items=["List the FDs", "Write the 0NF relation", "Normalize to 1NF, 2NF, 3NF",
                                                                   "Which values are **derived**?"]), flex="2"), gap=32),
            bg=PAPER2,
            notes="Recreated from the original slide's image. Expected 3NF: CUSTOMER(Cust_no, Name, Address...), CLERK(Clerk_no, Clerk_name), ORDER(Order_no, Order_date, Cust_no*, Clerk_no*), ITEM(Item_no, Description, Unit_price), ORDER_LINE(Order_no*, Item_no*, Qty). Line total and order total are derived and should not be stored. Discuss: should the unit price at order time be copied into ORDER_LINE? (Yes, if prices change: that is a historical fact, not redundancy.)")

    d.exercises("practice", "Practice: Lesson 5", [
        ("Core", "For COURSE_REG(StudentID, StudentName, CourseID, CourseTitle, Grade): list the FDs and normalize to 3NF."),
        ("Core", "Show one insert, one update and one delete anomaly in EMP_PROJ (Ssn, Pnumber, Hours, Ename, Pname, Plocation)."),
        ("Core", "Classify each FD as full, partial or transitive in the school example."),
        ("Stretch", "Normalize the **sales order** on the previous slide and say which values should not be stored."),
        ("Stretch", "Is BOOK(ISBN, Title, AuthorID, AuthorName, PublisherID, PublisherCity) in 3NF? Fix it."),
        ("Challenge", "Find a table in BCNF violation in your own project, decompose it, and check the join is lossless.")])

    d.resources("study", "Go deeper: Lesson 5", [
        ("Book", "Elmasri & Navathe (7th ed.)", "chapters 14–15: FDs, normal forms, decomposition properties", ""),
        ("Read", "Wikipedia: Database normalization", "worked example from 1NF to 6NF", "https://en.wikipedia.org/wiki/Database_normalization"),
        ("Read", "William Kent: A Simple Guide to Five Normal Forms", "the classic short paper (1983), free online", "https://www.bkent.net/Doc/simple5.htm"),
        ("Course", "CMU 15-445", "database design and normal forms lectures", "https://15445.courses.cs.cmu.edu/"),
        ("Practice", "DB Fiddle", "create your normalized tables and test joins", "https://www.db-fiddle.com/")])

    return d
