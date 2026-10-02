from lib import *


def legend(left, top, width, items):
    return pin_block(left, top, width, card(None, items=items, size=24))


def note_box(left, top, width, text, size=26):
    return pin_text(left, top, width, text, size, BODY)


def build():
    d = Deck(2, "Entity Relationship Diagrams", "Lesson 2 · Entity Relationship Diagrams")

    d.cover("cover", "Entity Relationship Diagrams",
            "Turning a business narrative into a picture of entities, attributes and relationships.",
            ["Entities", "Attributes & keys", "Relationships", "Chen & crow's foot", "COMPANY case", "Case studies"])

    d.slide("objectives", "Lesson 2", "By the end of this lesson you can",
            grid([card(None, body=t, tag=f"{i + 1:02d}", size=30) for i, t in enumerate([
                "Explain where the ERD sits in the **design process**",
                "Identify **entities**, strong and weak",
                "Classify **attributes** and choose **keys**",
                "Describe relationships by **degree, cardinality, participation**",
                "Read and draw **Chen** notation, and read **crow's foot**",
                "Build an ERD from a **narrative**, step by step"])], cols=3))

    # ------------- Part 1 -------------
    d.divider("d1", "01", "Modeling basics", "What an ERD is for, and its building blocks: entities (strong and weak), instances and attributes.")

    steps = [("Requirements", "Interview users; write the narrative"), ("Conceptual design", "ERD (this lesson)"),
             ("Logical design", "Tables, keys (Lesson 3)"), ("Physical design", "SQL, indexes (Lesson 4)")]
    boxes = []
    for i, (t, s) in enumerate(steps):
        tone = "accent" if i == 1 else "card"
        boxes.append(card(t, body=s, tone=tone, size=28))
        if i < 3:
            boxes.append(arrow_right())
    d.slide("whyerd", "Modeling basics", "Where the ERD fits",
            p("An **Entity Relationship Diagram** identifies the information a business needs by showing the relevant **entities** and the **relationships** between them.", size=32)
            + row(*boxes, gap=16)
            + callout("The ERD is a **conceptual** model: no tables, data types or SQL yet. It is a shared language between designers and the business.", tone="blue"),
            notes="New framing slide: the original jumped straight to definitions. Showing the four design phases explains why we draw an ERD before writing CREATE TABLE.")

    d.slide("questions", "Modeling basics", "Four questions every data model answers",
            grid([card("Which entities?", body="What things does the business need to describe?", tag="1", size=30),
                  card("Which attributes?", body="What facts must be recorded about each entity?", tag="2", size=30),
                  card("Which key?", body="Which attribute(s) uniquely identify one occurrence?", tag="3", size=30),
                  card("Which relationships?", body="How are the entities associated with each other?", tag="4", size=30)], cols=2))

    d.slide("entity", "Modeling basics", "Entities, instances, attributes",
            row(card("Entity", size=28, body="A thing in the real world with an independent existence.",
                     items=["Physical: a person, a car", "Conceptual: a job, a course"]),
                card("Entity instance", size=28, body="One particular occurrence of an entity.",
                     items=["*Mai*, *Ali* are instances of STUDENT"]),
                card("Attribute", size=28, body="A property that describes the entity.",
                     items=["EMPLOYEE: name, age, address, salary"]))
            + table(["SSN", "Name", "Address", "Salary"],
                    [["123456789", "John Smith", "731 Fondren, Houston", "30000"],
                     ["333445555", "Franklin Wong", "638 Voss, Houston", "40000"]], widths=[22, 26, 34, 18], size=26)
            + p("Entity type **EMPLOYEE** (the set) · each row = one **instance** · each column = one **attribute**", size=24, color=MUTED),
            gap=32)

    e = ERD()
    e.entity(430, 520, "EMPLOYEE")
    e.rel(960, 520, "DEPENDENTS_OF", w=300, h=140, ident=True, size=24)
    e.entity(1490, 520, "DEPENDENT", weak=True, w=280)
    e.line(560, 520, 810, 520)
    e.line(1110, 520, 1350, 520, double=True)
    e.text(600, 490, "1", w=40)
    e.text(1310, 490, "N", w=40)
    e.attr(430, 350, "Ssn", kind="key")
    e.line(430, 382, 430, 476)
    e.attr(1380, 720, "Name (partial key)", w=280)
    e.attr(1680, 720, "BirthDate", w=200)
    e.line(1420, 564, 1390, 688)
    e.line(1560, 564, 1660, 688)
    side = note_box(128, 640, 820,
                    "A **weak entity** has no key of its own. It is identified by its **owner** (EMPLOYEE) + its **partial key** (Name), through an **identifying relationship** (double diamond). Its participation is always **total** (double line).")
    d.diagram("weak", "Modeling basics", "Strong vs weak entity types", e, side=side,
              notes="Example: a DEPENDENT is identified by the dependent's first name (and birth date) together with the EMPLOYEE they belong to. Two employees can each have a son called Ahmed; only Ssn + Name is unique. In Chen notation the partial key is drawn with a dashed underline.")

    # ------------- Part 2 -------------
    d.divider("d2", "02", "Attributes & keys", "Five kinds of attributes, and how keys identify each instance.")

    e = ERD()
    e.entity(860, 580, "EMPLOYEE", w=280)
    e.attr(520, 420, "Ssn", kind="key")
    e.attr(860, 420, "Name", kind="composite")
    e.attr(700, 310, "Fname", w=160)
    e.attr(1020, 310, "Lname", w=160)
    e.attr(1220, 440, "Phones", kind="multi")
    e.attr(520, 760, "Salary")
    e.attr(860, 790, "BirthDate", w=200)
    e.attr(1220, 760, "Age", kind="derived")
    for x1, y1, x2, y2 in ((520, 452, 760, 536), (860, 452, 860, 536), (720, 342, 820, 394), (1000, 342, 900, 394),
                           (1220, 472, 980, 536), (520, 728, 760, 624), (860, 758, 860, 624), (1220, 728, 960, 624)):
        e.line(x1, y1, x2, y2)
    side = legend(1420, 300, 372, ["**Ssn**: key (underlined)", "**Name**: composite → Fname, Lname", "**Phones**: multi-valued (double)",
                                   "**Age**: derived from BirthDate (dashed)", "**Salary**: simple, single-valued"])
    d.diagram("attrdiagram", "Attributes", "Attribute types on one entity", e, side=side)

    d.slide("attrtypes", "Attributes", "Attribute types",
            table(["Type", "Meaning", "Example", "Chen symbol"],
                  [["Simple (atomic)", "Cannot be divided; one value per instance", "Salary", "Ellipse"],
                   ["Composite", "Made of smaller parts", "Name = Fname + Lname; Address = Street + City", "Ellipse with sub-ellipses"],
                   ["Multi-valued", "A set of values for one instance", "Phones, Locations, Images", "Double ellipse"],
                   ["Derived", "Calculated from other attributes or entities", "Age from BirthDate; NumberOfEmployees", "Dashed ellipse"],
                   ["Key", "Unique for each instance", "Ssn, Student_ID", "Underlined name"]],
                  widths=[18, 32, 32, 18], size=26)
            + callout("Store **BirthDate**, not Age: a derived attribute is computed when needed, so it never goes stale.", tone="blue", label="Tip:"),
            notes="Simple is also called single or atomic. Composite and multi-valued attributes can nest: e.g. a multi-valued composite attribute {AddressPhone(Phone, Address)}.")

    e = ERD()
    e.entity(400, 560, "EMPLOYEE", w=240, h=80, size=26)
    e.attr(400, 400, "Ssn", kind="key", w=160)
    e.line(400, 432, 400, 520)
    e.entity(960, 560, "MODEL", w=240, h=80, size=26)
    e.attr(960, 400, "(Name, Suffix)", kind="key", w=250)
    e.attr(830, 300, "Name", w=150, h=56)
    e.attr(1090, 300, "Suffix", w=150, h=56)
    e.line(960, 432, 960, 520); e.line(870, 326, 920, 370); e.line(1050, 326, 1000, 370)
    e.entity(1520, 560, "EMPLOYEE", w=240, h=80, size=26)
    e.attr(1410, 400, "Ssn", kind="key", w=150)
    e.attr(1640, 400, "Email", kind="key", w=170)
    e.line(1430, 432, 1480, 520); e.line(1620, 432, 1560, 520)
    labels = ""
    for x, t, sub in ((400, "Simple key", "One attribute is unique"), (960, "Composite key", "The combination is unique; no part alone is"),
                      (1520, "Candidate keys", "More than one key; each underlined separately")):
        labels += pin_text(x - 270, 630, 540, t, 28, ACCENT, bold=True, align="center")
        labels += pin_text(x - 270, 674, 540, sub, 24, BODY, align="center")
    labels += pin_block(128, 760, 1664, callout("There is **no primary key in an ERD**. We pick one candidate key as the primary key later, during mapping (Lesson 3). An entity type with **no key** of its own is a **weak entity** type.", label="Note:", size=26))
    d.diagram("keys", "Keys", "Key attributes", e, side=labels,
              notes="If two attributes are underlined separately, then each is a key on its own (candidate keys). If they are joined into one composite attribute that is underlined, the combination is the key. Other composite-key example from the original: (ID, Application_no).")

    # ------------- Part 3 -------------
    d.divider("d3", "03", "Relationships", "How entities connect: degree, cardinality ratio and participation, drawn in Chen and crow's foot notation.")

    d.slide("relconcepts", "Relationships", "Describing a relationship",
            p("A **relationship** is an association between entity instances: *Ali* **works for** *Research*.", size=32)
            + row(card("Degree", body="How many entity types take part: unary, binary, ternary…", tag="How many?", size=28),
                  card("Cardinality ratio", body="The **maximum** number of instances an entity can be related to: 1:1, 1:N, M:N.", tag="At most?", size=28),
                  card("Participation", body="The **minimum**: must every instance take part (total) or not (partial)?", tag="At least?", size=28)),
            notes="Relationship: establishes a connection between a pair of entities in an ERD, or a pair of tables in a database. Cardinality ratio and participation together are called the structural constraints of a relationship.")

    e = ERD()
    # unary
    e.entity(400, 380, "EMPLOYEE", w=240)
    e.rel(400, 640, "SUPERVISES", w=230, h=120)
    e.line(330, 424, 285, 640)
    e.line(470, 424, 515, 640)
    e.text(240, 520, "supervisor", size=24, color=MUTED, w=150, bold=False)
    e.text(565, 520, "supervisee", size=24, color=MUTED, w=150, bold=False)
    # binary
    e.entity(960, 380, "EMPLOYEE", w=240)
    e.rel(960, 560, "WORKS_FOR", w=230, h=120)
    e.entity(960, 740, "DEPARTMENT", w=260)
    e.line(960, 424, 960, 500)
    e.line(960, 620, 960, 696)
    # ternary
    e.entity(1520, 380, "SUPPLIER", w=240)
    e.rel(1520, 560, "SUPPLY", w=200, h=110)
    e.entity(1380, 760, "PART", w=200)
    e.entity(1660, 760, "PROJECT", w=220)
    e.line(1520, 424, 1520, 505)
    e.line(1470, 588, 1400, 716)
    e.line(1570, 588, 1640, 716)
    lab = ""
    for x, t in ((400, "Unary (recursive): 1 entity type"), (960, "Binary: 2 entity types"), (1520, "Ternary: 3 entity types")):
        lab += pin_text(x - 260, 836, 520, t, 26, ACCENT, bold=True, align="center")
    d.diagram("degree", "Relationships", "Degree of a relationship", e, side=lab,
              notes="In a recursive relationship the same entity type plays two different roles, so we label the lines with role names (supervisor, supervisee). Binary relationships are by far the most common.")

    e = ERD()
    rows_ = [(370, "EMPLOYEE", "MANAGES", "DEPARTMENT", "1", "1", "An employee manages at most one department; a department has at most one manager."),
             (580, "DEPARTMENT", "HAS", "EMPLOYEE", "1", "N", "A department has many employees; an employee belongs to at most one department."),
             (790, "EMPLOYEE", "WORKS_ON", "PROJECT", "M", "N", "An employee works on many projects; a project has many employees.")]
    side = ""
    for y, a, r, b, ca, cb, txt in rows_:
        e.entity(300, y, a, w=250, h=80, size=26)
        e.rel(640, y, r, w=210, h=110)
        e.entity(980, y, b, w=250, h=80, size=26)
        e.line(425, y, 535, y)
        e.line(745, y, 855, y)
        e.text(455, y - 28, ca, w=40)
        e.text(825, y - 28, cb, w=40)
        side += note_box(1160, y - 40, 632, txt)
    d.diagram("cardinality", "Relationships", "Cardinality ratio: 1:1, 1:N, M:N", e, side=side,
              notes="Read each side: 'one employee manages ONE department' (the number next to DEPARTMENT), 'one department is managed by ONE employee' (the number next to EMPLOYEE).")

    e = ERD()
    for y, a, r, b, txt in ((400, "EMPLOYEE", "MANAGES", "DEPARTMENT", "Not every employee manages a department → **partial** (single line). Every department must have a manager → **total** (double line)."),
                            (720, "EMPLOYEE", "HAS", "CAR", "An employee **may** have a car → partial. A car **must** be assigned to an employee → total.")):
        e.entity(300, y, a, w=250, h=80, size=26)
        e.rel(640, y, r, w=210, h=110)
        e.entity(980, y, b, w=250, h=80, size=26)
        e.line(425, y, 535, y)
        e.line(745, y, 855, y, double=True)
        e.text(455, y - 28, "1", w=40)
        e.text(825, y - 28, "1", w=40)
    side = (note_box(1160, 340, 632, "Not every employee manages a department → **partial** (single line). Every department must have a manager → **total** (double line).")
            + note_box(1160, 660, 632, "An employee **may** have a car → **partial**. A car **must** be assigned to an employee → **total**."))
    d.diagram("participation", "Relationships", "Participation: total vs partial", e, side=side,
              notes="Synonyms: total = full = mandatory (existence dependency); partial = optional. The double line is always drawn on the side of the entity that MUST participate.")

    e = ERD()
    e.entity(400, 400, "DEPARTMENT", w=260)
    e.rel(960, 400, "HIRES", w=220, h=120)
    e.entity(1520, 400, "EMPLOYEE", w=260)
    e.line(530, 400, 850, 400)
    e.line(1070, 400, 1390, 400, double=True)
    e.text(640, 368, "(0,N)", w=120)
    e.text(1280, 368, "(1,1)", w=120)
    side = pin_block(128, 540, 1664, table(["Pair", "Read it as", "So participation is"],
                    [["(0,N) next to DEPARTMENT", "A department may hire **zero or more** employees", "Partial (min = 0)"],
                     ["(1,1) next to EMPLOYEE", "An employee is hired by **exactly one** department", "Total (min ≥ 1)"]],
                    widths=[30, 46, 24], size=26))
    d.diagram("minmax", "Relationships", "Structural constraints in (min, max) notation", e, side=side,
              notes="Formal constraint: (min,max) means each entity participates in at least min and at most max relationship instances. min = 0 means partial participation, min >= 1 means total. Careful: (min,max) is written next to the entity it describes, which is the opposite side from the 1:N labels on the previous slides.")

    e = ERD()
    e.entity(400, 420, "EMPLOYEE", w=260)
    e.rel(960, 420, "WORKS_ON", w=240, h=120)
    e.entity(1520, 420, "PROJECT", w=260)
    e.line(530, 420, 840, 420, double=True)
    e.line(1080, 420, 1390, 420, double=True)
    e.text(570, 388, "M", w=40)
    e.text(1350, 388, "N", w=40)
    e.attr(960, 600, "Hours")
    e.line(960, 480, 960, 568)
    side = note_box(128, 680, 1664,
                    "**Hours** belongs to the *pair* (employee, project), not to either entity alone. Relationships can have attributes too: e.g. **StartDate** on MANAGES. When we map to tables, an M:N attribute goes into the new relationship table; a 1:N attribute can move to the N-side entity.")
    d.diagram("relattr", "Relationships", "Attributes on relationships", e, side=side,
              notes="Completes an idea that the original showed only inside the COMPANY ERD (Hours, StartDate).")

    # ------------- notation -------------
    e = ERD()
    cells = []
    cw, ch, top0 = 416, 205, 280
    def cell(i):
        c, r = i % 4, i // 4
        return 128 + c * cw + cw // 2, top0 + r * ch
    labels = ["Entity type", "Weak entity type", "Relationship type", "Identifying relationship",
              "Attribute", "Key attribute", "Multi-valued attribute", "Derived attribute",
              "Composite attribute", "Total participation of E in R", "Cardinality 1:N for E1:E2", "(min, max) of E in R"]
    cx, cy = cell(0); e.entity(cx, cy + 70, "E", w=200, h=80)
    cx, cy = cell(1); e.entity(cx, cy + 70, "E", w=200, h=80, weak=True)
    cx, cy = cell(2); e.rel(cx, cy + 70, "R", w=170, h=100)
    cx, cy = cell(3); e.rel(cx, cy + 70, "R", w=170, h=100, ident=True)
    cx, cy = cell(4); e.attr(cx, cy + 70, "A", w=170, h=70)
    cx, cy = cell(5); e.attr(cx, cy + 70, "A", w=170, h=70, kind="key")
    cx, cy = cell(6); e.attr(cx, cy + 70, "A", w=170, h=70, kind="multi")
    cx, cy = cell(7); e.attr(cx, cy + 70, "A", w=170, h=70, kind="derived")
    cx, cy = cell(8); e.attr(cx, cy + 40, "A", w=130, h=54); e.attr(cx - 100, cy + 118, "A1", w=120, h=50); e.attr(cx + 100, cy + 118, "A2", w=120, h=50)
    e.line(cx - 30, cy + 67, cx - 80, cy + 93); e.line(cx + 30, cy + 67, cx + 80, cy + 93)
    cx, cy = cell(9); e.entity(cx - 110, cy + 70, "E", w=110, h=64); e.rel(cx + 100, cy + 70, "R", w=120, h=80); e.line(cx - 55, cy + 70, cx + 40, cy + 70, double=True)
    cx, cy = cell(10); e.entity(cx - 150, cy + 70, "E1", w=90, h=60, size=24); e.rel(cx, cy + 70, "R", w=110, h=76); e.entity(cx + 150, cy + 70, "E2", w=90, h=60, size=24)
    e.line(cx - 105, cy + 70, cx - 55, cy + 70); e.line(cx + 55, cy + 70, cx + 105, cy + 70); e.text(cx - 80, cy + 44, "1", w=30, size=24); e.text(cx + 80, cy + 44, "N", w=30, size=24)
    cx, cy = cell(11); e.entity(cx - 120, cy + 70, "E", w=100, h=64); e.rel(cx + 110, cy + 70, "R", w=110, h=76); e.line(cx - 70, cy + 70, cx + 55, cy + 70); e.text(cx - 5, cy + 40, "(min,max)", w=140, size=24)
    lab = ""
    for i, t in enumerate(labels):
        cx, cy = cell(i)
        lab += pin_text(cx - 200, cy + 150, 400, t, 24, MUTED, align="center")
    d.diagram("notation", "Notation", "Summary of Chen notation", e, side=lab,
              notes="Guidelines: a relationship between two entities is a line through a diamond. Verbs name relationships (e.g. 'addresses LOCATE businesses'). Attribute lists grow as you go. Select (or assign) one unique identifier per entity.")

    d.slide("crowsfoot", "Notation", "The same ideas in crow's foot notation",
            p("Most modern tools (dbdiagram.io, draw.io, MySQL Workbench, Lucidchart) draw **crow's foot** ERDs: attributes go inside the entity box and the line ends show cardinality.", size=30)
            + table(["Line end", "Meaning", "Chen equivalent"],
                    [["—||—  (two bars)", "Exactly one (mandatory one)", "1 + total participation"],
                     ["—o|—  (circle, bar)", "Zero or one", "1 + partial participation"],
                     ["—|<   (bar, crow's foot)", "One or many", "N + total participation"],
                     ["—o<   (circle, crow's foot)", "Zero or many", "N + partial participation"]],
                    widths=[34, 36, 30], size=28)
            + callout("Example: DEPARTMENT —||————o< EMPLOYEE reads \"each employee belongs to exactly one department; a department has zero or many employees\".", tone="blue"),
            notes="New slide: students will meet crow's foot in industry and in most online tools. The circle = minimum 0, the bar = minimum/maximum 1, the crow's foot = many.")

    def cf_entity(x, w, name, cols):
        out = pin_box(x, 340, w, 64, fill=INK, text=name, text_size=26, text_color=ON_INK, font=DISPLAY)
        out += pin_box(x, 404, w, 52 * len(cols) + 24, fill=CARD, border=INK)
        for k, c in enumerate(cols):
            out += pin_text(x + 20, 418 + 52 * k, w - 40, c, 24, BODY, font=MONO)
        return out

    def bars(x, y):
        return pin_conn(x, y - 18, x, y + 18, width=3)

    def foot(x_tip, y, toward):  # crow's foot that opens toward the entity edge at x_tip
        d = 34 * toward
        return (pin_conn(x_tip - d, y, x_tip, y - 20, width=3) + pin_conn(x_tip - d, y, x_tip, y, width=3)
                + pin_conn(x_tip - d, y, x_tip, y + 20, width=3))

    y = 470
    art = (cf_entity(150, 380, "DEPARTMENT", ["dnumber  PK", "dname", "mgr_ssn  FK"])
           + cf_entity(770, 380, "EMPLOYEE", ["ssn  PK", "fname", "dno  FK"])
           + cf_entity(1390, 380, "PROJECT", ["pnumber  PK", "pname", "dnum  FK"])
           + pin_conn(530, y, 770, y, width=3) + bars(552, y) + bars(566, y)
           + pin_ellipse(706, y - 12, 24, 24, fill=CARD, border=INK) + foot(770, y, 1)
           + pin_conn(1150, y, 1390, y, width=3) + bars(1172, y) + foot(1150, y, -1)
           + bars(1368, y) + foot(1390, y, 1)
           + pin_text(560, y - 64, 180, "works for", 24, MUTED, italic=True, align="center")
           + pin_text(1180, y - 64, 180, "works on", 24, MUTED, italic=True, align="center")
           + pin_block(128, 700, 1664, row(
               callout("**DEPARTMENT ||——o< EMPLOYEE**: an employee works for exactly one department; a department has zero or many employees.", tone="blue", size=26),
               callout("**EMPLOYEE >|——|< PROJECT**: M:N, both total; it becomes the WORKS_ON junction table. Tools draw logical models, so PK/FK columns appear; a Chen ERD has no FKs.", size=26))))
    d.slide("crowsdraw", "Notation", "Crow's foot, drawn", art,
            notes="New diagram: the same COMPANY relationships drawn the way dbdiagram.io, draw.io or MySQL Workbench draw them. The symbol next to an entity tells how many of THAT entity relate to one instance on the other side: o< next to EMPLOYEE = a department has zero or many employees; || next to DEPARTMENT = an employee has exactly one department.")

    # ------------- Part 4 -------------
    d.divider("d4", "04", "Building an ERD", "A repeatable method, applied to the COMPANY database, and the mistakes to avoid.")

    d.slide("method", "Method", "From narrative to ERD, step by step",
            grid([card(t, body=b, tag=f"{i + 1}", size=26, title_size=32) for i, (t, b) in enumerate([
                ("Find entities", "Nouns that have their own facts: *department, project*"),
                ("Find attributes", "Facts about a noun: *name, number, location*"),
                ("Pick keys", "Words like *unique*, *identified by*"),
                ("Find relationships", "Verbs linking nouns: *controls, works on*"),
                ("Cardinality", "*one*, *several*, *many*, *a number of*"),
                ("Participation", "*must* → total; *may* → partial"),
                ("Weak entities & extras", "No own key? Relationship attributes like *hours*?"),
                ("Review with users", "Read every relationship aloud as a sentence")])], cols=4),
            notes="New method slide (the eighth card, review, is the habit that catches most errors). Students apply it to every case study that follows.")

    d.slide("company1", "COMPANY case", "The COMPANY database: requirements (1/2)",
            card(None, size=32, body="A company is organized into **departments**. Each department has a *unique name*, a *unique number*, and a particular employee who **manages** the department. We keep track of the *start date* when that employee began managing. A department may have **several locations**.")
            + card(None, size=32, body="A department **controls** a number of **projects**, each of which has a *unique name*, a *unique number*, and a single *location*. A project must be controlled by a department."),
            notes="Ask students to underline nouns (entities), circle verbs (relationships), and highlight 'unique' (keys) before moving on.")

    d.slide("company2", "COMPANY case", "The COMPANY database: requirements (2/2)",
            card(None, size=30, body="We store each **employee**'s *name, social security number, address, salary, gender and birth date*. An employee must be assigned to **one department** and must **work on** one or more projects, which are not necessarily controlled by the same department. We keep track of the *number of hours per week* that an employee works on each project. We also keep track of the **direct supervisor** of each employee.")
            + card(None, size=30, body="We keep track of the **dependents** of each employee for insurance purposes: each dependent's *first name, gender, birth date* and *relationship* to the employee."))

    e = ERD()
    e.entity(560, 440, "EMPLOYEE")
    e.entity(1460, 440, "DEPARTMENT")
    e.entity(1460, 800, "PROJECT")
    e.entity(560, 850, "DEPENDENT", weak=True, w=280)
    e.rel(1010, 340, "WORKS_FOR", w=220, h=100)
    e.rel(1010, 500, "MANAGES", w=220, h=100)
    e.rel(1010, 710, "WORKS_ON", w=220, h=100)
    e.rel(1460, 620, "CONTROLS", w=220, h=100)
    e.rel(560, 655, "DEPENDENTS_OF", w=280, h=110, ident=True)
    e.rel(250, 650, "SUPERVISION", w=230, h=100)
    # lines
    e.line(690, 420, 900, 340, double=True); e.line(1120, 340, 1330, 420, double=True)
    e.line(690, 460, 900, 500); e.line(1120, 500, 1330, 460, double=True)
    e.line(640, 484, 900, 710, double=True); e.line(1120, 710, 1330, 800, double=True)
    e.line(1460, 484, 1460, 570); e.line(1460, 670, 1460, 756, double=True)
    e.line(560, 484, 560, 600); e.line(560, 710, 560, 806, double=True)
    e.line(430, 430, 250, 600); e.line(470, 484, 365, 650)
    # cardinalities
    for x, y, t in ((740, 372, "N"), (1290, 372, "1"), (740, 480, "1"), (1290, 452, "1"), (760, 560, "M"), (1290, 740, "N"),
                    (1490, 520, "1"), (1490, 720, "N"), (590, 520, "1"), (590, 770, "N"), (300, 520, "1"), (420, 600, "N")):
        e.text(x, y, t, w=40, size=26)
    e.text(250, 470, "supervisor", w=160, size=24, color=MUTED, bold=False)
    e.text(330, 720, "supervisee", w=160, size=24, color=MUTED, bold=False)
    # attributes
    e.attr(250, 330, "Ssn", kind="key", w=140, h=56)
    e.attr(430, 300, "Name", w=150, h=56)
    e.attr(660, 300, "Salary", w=150, h=56)
    e.line(290, 352, 440, 410); e.line(450, 326, 520, 396); e.line(640, 326, 590, 396)
    e.attr(1330, 300, "Number", kind="key", w=160, h=56)
    e.attr(1580, 300, "Name", kind="key", w=140, h=56)
    e.attr(1710, 470, "Locations", kind="multi", w=180, h=60)
    e.line(1360, 328, 1420, 396); e.line(1560, 328, 1500, 396); e.line(1620, 460, 1590, 450)
    e.attr(1010, 590, "StartDate", w=170, h=50)
    e.line(1010, 550, 1010, 565)
    e.attr(860, 800, "Hours", w=130, h=50)
    e.line(940, 740, 890, 776)
    e.attr(1720, 720, "Number", kind="key", w=160, h=56)
    e.attr(1720, 880, "Location", w=170, h=56)
    e.line(1640, 740, 1590, 780); e.line(1640, 865, 1590, 830)
    e.attr(250, 870, "Name (partial)", w=210, h=56)
    e.line(355, 870, 420, 860)
    d.diagram("companyerd", "COMPANY case", "The COMPANY ERD", e,
              notes="Redrawn from the original figure (Elmasri & Navathe). Some attributes are omitted to keep the diagram readable: EMPLOYEE also has Bdate, Address, Sex and a composite Name (Fname, Minit, Lname); DEPARTMENT has the derived attribute NumberOfEmployees; PROJECT has Name; DEPENDENT has Sex, BirthDate, Relationship. Walk the relationships aloud: WORKS_FOR N:1 (both total), MANAGES 1:1 (department total), CONTROLS 1:N (project total), WORKS_ON M:N with Hours (both total), SUPERVISION 1:N recursive (partial), DEPENDENTS_OF identifying 1:N.")

    d.slide("companymap", "COMPANY case", "From sentence to symbol",
            table(["Sentence in the requirements", "ERD decision"],
                  [["\"Each department has a unique name, a unique number\"", "DEPARTMENT with two candidate keys: Name, Number"],
                   ["\"A department may have several locations\"", "Locations is multi-valued"],
                   ["\"A particular employee who manages the department\"", "MANAGES 1:1; DEPARTMENT total, EMPLOYEE partial"],
                   ["\"A project must be controlled by a department\"", "CONTROLS 1:N; PROJECT total"],
                   ["\"Must work on one or more projects… hours per week\"", "WORKS_ON M:N, EMPLOYEE total, attribute Hours"],
                   ["\"The direct supervisor of each employee\"", "SUPERVISION, recursive 1:N with roles"],
                   ["\"Dependents of each employee… first name\"", "Weak entity DEPENDENT, partial key Name"]],
                  widths=[52, 48], size=26),
            notes="New slide: makes the reasoning behind every symbol explicit, which is what students struggle with in the case studies.")

    d.slide("mistakes", "Method", "Common ERD mistakes",
            grid([card("Attributes as entities", body="*City* with only a name is usually an attribute, not an entity.", icon="Warning", size=26),
                  card("Foreign keys in the ERD", body="Don't add *DeptNo* to EMPLOYEE: the relationship already says it. FKs appear in Lesson 3.", icon="Warning", size=26),
                  card("Wrong side for cardinality", body="Read both directions aloud as sentences before writing 1 or N.", icon="Warning", size=26),
                  card("Relationship facts on an entity", body="*Hours* on EMPLOYEE is wrong: it depends on the project too.", icon="Warning", size=26),
                  card("Storing derived values", body="Prefer *BirthDate* over *Age*; mark derived attributes dashed.", icon="Warning", size=26),
                  card("Ignoring history", body="\"Keep track of changes\" means a relationship with dates, not one overwritten value.", icon="Warning", size=26)], cols=3),
            notes="New slide collecting the mistakes most often seen when grading ERD labs.")

    # ------------- Part 5 -------------
    d.divider("d5", "05", "Case studies", "Practice the method on three narratives: a car manufacturer, a bus company and a bank.")

    d.slide("car1", "Case study 1", "Car manufacturer (1/2)",
            card(None, size=32, body="An organization makes many **models** of cars, where a model is characterized by a *unique name* and a *suffix* (such as GL or XL) and an *engine size*.")
            + card(None, size=32, body="Each model is made up from many **parts**, and each part has a *description*, an *id code*, *production year*, and *many images*. Each part may be used in the manufacturing of more than one model."))

    d.slide("car2", "Case study 1", "Car manufacturer (2/2)",
            card(None, size=32, body="Each model must be produced at just one of the firm's **factories**, which are located in London, Birmingham, Bristol, Wolverhampton and Manchester (one in each city). Each factory has a *number of machines*, *capacity*, and *computer system* used (OS, DBMS, Internet).")
            + card(None, size=32, body="A factory produces many models of cars and many types of parts.")
            + callout("Is the key of MODEL just Name, or (Name, Suffix)? Is *images* single- or multi-valued? Is *computer system* composite?", label="Think:", tone="blue"),
            notes="Hints: the narrative says the model name is unique, so Name is the key (Lesson 3 uses name as the PK). If only the combination were unique (Corolla GL, Corolla XL), the key would be the composite (Name, Suffix), as on the keys slide. PART: Id code key, Images multi-valued. MODEL-PART is M:N (uses). FACTORY key = City; Computer system is composite (OS, DBMS, Internet). PRODUCED_AT: N models : 1 factory, model total. 'Parts made in the same factory as the model' needs no ternary: each model has one factory, so the factory of a part follows from its models (Lesson 3 shows the tables).")

    d.slide("bus1", "Case study 2", "Country bus company (1/2)",
            card(None, size=32, body="A country bus company owns a number of **buses**. A bus is characterized by *number*, *number of chairs*, *options* (AC, Automatic, PS) and *brand name*.")
            + card(None, size=32, body="Each bus is allocated to a particular **route**, although some routes may have several buses. Each route is described by *KM*, *start point*, *end point* and *duration*."),
            notes="Unique keys are not specified in the narrative: students must propose surrogate keys (e.g. Route_No) and say so as an assumption.")

    d.slide("bus2", "Case study 2", "Country bus company (2/2)",
            card(None, size=30, body="Each route passes through a number of **towns**. A town may be situated along several routes. We keep track of a *unique name* and the *station names* in each town.")
            + card(None, size=30, body="One or more **drivers** are allocated to one route during a period of time. The system keeps the driver's *name*, *mobile number*, *hire date*, *basic salary* and *job grade*.")
            + card(None, size=30, body="The system keeps information about **any changes** in the allocation of drivers to routes."),
            notes="Hints: BUS N:1 ROUTE. ROUTE M:N TOWN; Stations multi-valued in TOWN. Allocation history: DRIVER M:N ROUTE with attributes FromDate, ToDate (the 'changes' sentence turns a 1:N into M:N over time).")

    d.slide("bank1", "Lab", "Banking system (1/2)",
            card(None, size=32, body="A database for a banking system controls withdrawal, deposit and loan **transactions** with **customers**.")
            + card(None, size=32, body="Banks using this system have many **branches**; each branch has a *unique name*, *unique address* and *phone*.")
            + card(None, size=32, body="The system stores information about customers: *unique customer ID*, *name*, *address* and *phones*."))

    d.slide("bank2", "Lab", "Banking system (2/2)",
            card(None, size=30, body="Each customer has one **account** identified by a *unique account number*, *amount*, and *last transaction date* (day, month and year).")
            + card(None, size=30, body="The system records *transaction number*, *transaction type*, *transaction date*, *amount* and *time*, and the **branch** where the transaction occurred.")
            + card(None, size=30, body="A customer can make any type of transaction (withdrawal or deposit) from any branch of the bank."),
            notes="Hints: Phones multi-valued; last transaction date composite (Day, Month, Year) and arguably derived from transactions. TRANSACTION relates CUSTOMER (or ACCOUNT), BRANCH: discuss whether it is an entity with two 1:N relationships or a ternary relationship.")

    d.takeaways("recap", [
        "An ERD is the **conceptual** model: entities, attributes, relationships; no tables yet.",
        "A **weak entity** is identified through its owner plus a partial key.",
        "Attributes can be simple, composite, multi-valued, derived or key.",
        "Relationships have a **degree**, a **cardinality ratio** (max) and **participation** (min).",
        "Chen and crow's foot express the **same constraints** with different symbols.",
        "Build ERDs **methodically**: nouns → verbs → keys → constraints → review."])

    d.exercises("practice", "Practice: Lesson 2", [
        ("Core", "For a **library**: members borrow copies of books; each book has many authors. Draw the ERD with keys and constraints."),
        ("Core", "Give one real example each of a 1:1, a 1:N and an M:N relationship, with participation for both sides."),
        ("Core", "Redraw the COMPANY ERD in **crow's foot** notation."),
        ("Stretch", "A **hospital**: patients, doctors, rooms, admissions with dates. Which entity is weak? Which relationship has attributes?"),
        ("Stretch", "Rewrite every relationship in the bus case as two sentences (one per direction) and check your cardinalities."),
        ("Challenge", "Model an online **course platform** (students, instructors, courses, lessons, enrollments, ratings) and justify each M:N.")])

    d.resources("study", "Go deeper: Lesson 2", [
        ("Book", "Elmasri & Navathe, Fundamentals of Database Systems (7th ed.)", "chapter 3: ER modeling, the COMPANY example", ""),
        ("Tool", "dbdiagram.io", "draw crow's foot ERDs from text, free", "https://dbdiagram.io/"),
        ("Tool", "diagrams.net (draw.io)", "free diagram editor with Chen and crow's foot shapes", "https://app.diagrams.net/"),
        ("Read", "Lucidchart: What is an ERD?", "notations compared with pictures", "https://www.lucidchart.com/pages/er-diagrams"),
        ("Video", "CMU 15-445 / Stanford DB courses", "search \"ER model\" lectures for worked examples", "https://15445.courses.cs.cmu.edu/")])

    return d
