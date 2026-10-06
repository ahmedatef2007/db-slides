from lib import *


def result_box(lines, title="Result"):
    inner = (f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{ACCENT}">{esc(title)}</p>'
             + "".join(schema_line(n, c) for n, c in lines))
    return (f'<div style="display:flex;flex-direction:column;gap:8px;background:{CARD};border:1px solid {LINE};'
            f'border-radius:16px;padding:28px 36px">{inner}</div>')


def build():
    d = Deck(3, "Mapping ERD to Tables", "Lesson 3 · Mapping ERD to Tables")

    d.cover("cover", "From ERD to Tables",
            "A 7-step algorithm that turns any ER diagram into a relational schema.",
            ["Relational model", "Integrity constraints", "7 mapping steps", "COMPANY schema", "Ternary relationships", "Case studies"])

    d.slide("objectives", "Lesson 3", "By the end of this lesson you can",
            grid([card(None, body=t, tag=f"{i + 1:02d}", size=30) for i, t in enumerate([
                "Use the vocabulary of the **relational model**",
                "Name the five **integrity constraints**",
                "Apply the **7 mapping steps** to any ERD",
                "Place **foreign keys** on the correct side",
                "Map **ternary** relationships correctly",
                "Produce the full **COMPANY** schema"])], cols=3))

    # ---------- Part 1 ----------
    d.divider("d1", "01", "The relational model", "The target of the mapping: relations, keys and integrity constraints.")

    d.slide("terms", "Relational model", "Relational vocabulary",
            row(col(table(["Formal term", "Everyday term", "Example"],
                          [["Relation", "Table", "EMPLOYEE"],
                           ["Tuple", "Row / record", "(123456789, 'John', 30000)"],
                           ["Attribute", "Column / field", "Salary"],
                           ["Domain", "Data type + allowed values", "Salary: decimal ≥ 0"],
                           ["Degree", "Number of columns", "EMPLOYEE has degree 8"],
                           ["Cardinality", "Number of rows", "Changes as data changes"]],
                          widths=[26, 34, 40], size=26), flex="3"),
                col(callout("A relation is a **set** of tuples: no duplicate rows, and row order does not matter.", tone="blue", size=26),
                    callout("Every value is **atomic**: one value per cell. That is why multi-valued attributes need their own table (step 6).", size=26), flex="2"), gap=32),
            notes="Original notes: integrity constraints (PK, UK, NN, FK, Check) and data types. The picture on the original slide showed a table annotated with relation, tuple, attribute and domain.")

    d.slide("constraints", "Relational model", "Integrity constraints",
            grid([card("PRIMARY KEY", body="Unique + not null. Identifies each row. **Entity integrity**: no part of a PK may be NULL.", icon="Key", size=26),
                  card("UNIQUE", body="No two rows share the value (an alternate key). NULL usually allowed.", icon="Star", size=26),
                  card("NOT NULL", body="A value is mandatory: total participation often becomes NOT NULL.", icon="Check", size=26),
                  card("FOREIGN KEY", body="Value must exist in the referenced PK, or be NULL. **Referential integrity**.", icon="Link", size=26),
                  card("CHECK", body="A condition every row must satisfy: `Salary > 0`, `Gender IN ('M','F')`.", icon="Verified", size=26),
                  card("Domain / data type", body="The column type restricts values: DATE, INT, VARCHAR(50)…", icon="Settings", size=26)], cols=3))

    d.slide("keys", "Relational model", "Keys in a relation",
            table(["Key", "Definition", "EMPLOYEE example"],
                  [["Superkey", "Any set of columns that is unique", "{Ssn, Fname}, {Ssn}"],
                   ["Candidate key", "A minimal superkey (remove any column → not unique)", "{Ssn}, {Email}"],
                   ["Primary key", "The candidate key we choose", "Ssn"],
                   ["Alternate key", "A candidate key not chosen (→ UNIQUE)", "Email"],
                   ["Foreign key", "Column(s) referencing a PK in another (or the same) table", "Dno → DEPARTMENT(Dnumber)"]],
                  widths=[20, 46, 34], size=28),
            notes="New slide: completes the vocabulary used in the mapping steps. In the ERD we only marked key attributes; mapping is where the primary key is chosen.")

    # ---------- Part 2 ----------
    d.divider("d2", "02", "The 7 mapping steps", "Apply them in order; each step adds tables or columns to the schema.")

    d.slide("overview", "Mapping", "ER-to-relational mapping at a glance",
            grid([card(t, body=b, tag=f"Step {i + 1}", size=26, title_size=32) for i, (t, b) in enumerate([
                ("Regular entities", "One table each; pick the PK"),
                ("Weak entities", "Table + owner's key as FK; PK = FK + partial key"),
                ("Binary 1:1", "FK on the total side (or merge)"),
                ("Binary 1:N", "FK on the N side"),
                ("Binary M:N", "New table with both FKs"),
                ("Multi-valued attrs", "New table: FK + value"),
                ("N-ary (n > 2)", "New table with n FKs"),
                ("Then: constraints", "NOT NULL, UNIQUE, CHECK, ON DELETE rules")])], cols=4),
            notes="The eighth card is not a mapping step: it reminds students that the schema is complete only when participation and business rules become constraints.")

    def step(sid, n, title, rules, erd, results, notes="", extra=None):
        left = card(None, items=rules, size=28)
        spacer = '<div style="width:860px;flex:none"></div>'
        body = row(left, spacer, gap=32) + result_box(results) + (extra or "") + erd.html()
        d.slide(sid, f"Step {n}", title, body, notes=notes, gap=32)

    e = ERD()
    e.entity(1360, 500, "EMPLOYEE", w=260)
    e.attr(1060, 370, "Ssn", kind="key", w=150)
    e.attr(1290, 340, "Name (Fname, Lname)", w=290)
    e.attr(1590, 360, "Salary", w=160)
    e.attr(1650, 500, "Age", kind="derived", w=130)
    e.line(1100, 398, 1260, 456); e.line(1310, 372, 1340, 456); e.line(1560, 392, 1440, 456); e.line(1585, 500, 1490, 500)
    step("step1", 1, "Mapping regular (strong) entity types",
         ["Create **one table** per regular entity", "Simple attributes → columns", "Composite → only its **parts** (Fname, Lname)",
          "Derived → usually **not stored** (compute it or use a view)", "Choose one key as **PK**; others → UNIQUE"],
         e, [("EMPLOYEE", ["_Ssn_", "Fname", "Lname", "Salary", "Bdate"])],
         notes="Multi-valued attributes are NOT handled here; they wait for step 6. Age is derived from Bdate, so we store Bdate.")

    e = ERD()
    e.entity(1060, 470, "EMPLOYEE", w=220)
    e.rel(1350, 470, "DEPENDENTS_OF", w=260, h=120, ident=True, size=22)
    e.entity(1640, 470, "DEPENDENT", w=230, weak=True)
    e.line(1170, 470, 1220, 470); e.line(1480, 470, 1525, 470, double=True)
    e.attr(1060, 340, "Ssn", kind="key", w=140)
    e.attr(1640, 330, "Name (partial)", w=220)
    e.line(1060, 372, 1060, 426); e.line(1640, 360, 1640, 420)
    step("step2", 2, "Mapping weak entity types",
         ["Create **one table** per weak entity", "Add the **owner's PK as a FK**", "PK = **FK + partial key**",
          "Usually `ON DELETE CASCADE`: no employee, no dependents"],
         e, [("DEPENDENT", ["_Essn*_", "_Dependent_name_", "Sex", "Bdate", "Relationship"])],
         notes="Notation used on the result line: underlined = part of the primary key; blue italic = foreign key. Essn is both (underlined and FK): it references EMPLOYEE(Ssn).")

    e = ERD()
    e.entity(1060, 450, "EMPLOYEE", w=220)
    e.rel(1350, 450, "MANAGES", w=220, h=110)
    e.entity(1640, 450, "DEPARTMENT", w=240)
    e.line(1170, 450, 1240, 450); e.line(1460, 450, 1520, 450, double=True)
    e.text(1200, 420, "1", w=30); e.text(1495, 420, "1", w=30)
    e.attr(1350, 570, "StartDate", w=180)
    e.line(1350, 505, 1350, 538)
    step("step3", 3, "Mapping binary 1:1 relationships",
         ["**One side total** → put the FK in the table on the **total** side (DEPARTMENT: every department has a manager, so no NULLs)",
          "**Both total** → you may **merge** the two tables",
          "**Both partial** → FK on either side (allows NULLs) or a **separate relationship table**",
          "Add `UNIQUE` on the FK to keep it 1:1; relationship attributes travel with the FK"],
         e, [("DEPARTMENT", ["Dname", "_Dnumber_", "Mgr_ssn*", "Mgr_start_date"])],
         notes="Fixed: the original wording 'Add FK into table with the total participation relationship to represent optional side' was confusing. Rule: the FK goes into the table whose entity has TOTAL participation, referencing the other (optional) side. Putting Mgr_ssn in EMPLOYEE instead would leave it NULL for almost every employee.")

    e = ERD()
    e.entity(1060, 450, "DEPARTMENT", w=240)
    e.rel(1350, 450, "WORKS_FOR", w=220, h=110)
    e.entity(1640, 450, "EMPLOYEE", w=230)
    e.line(1180, 450, 1240, 450, double=True); e.line(1460, 450, 1525, 450, double=True)
    e.text(1210, 420, "1", w=30); e.text(1495, 420, "N", w=30)
    step("step4", 4, "Mapping binary 1:N relationships",
         ["Add the **FK to the N-side** table, referencing the 1-side", "Relationship attributes → columns of the N-side table",
          "Total participation of the N side → FK `NOT NULL`", "Recursive 1:N works the same: **Super_ssn** → EMPLOYEE"],
         e, [("EMPLOYEE", ["_Ssn_", "Fname", "Lname", "Salary", "Super_ssn*", "Dno*"])],
         notes="Why the N side? Each employee has exactly one department, so one column holds it. The 1 side (DEPARTMENT) would need a list of employees, which is not atomic.")

    e = ERD()
    e.entity(1060, 450, "EMPLOYEE", w=220)
    e.rel(1350, 450, "WORKS_ON", w=220, h=110)
    e.entity(1640, 450, "PROJECT", w=220)
    e.line(1170, 450, 1240, 450, double=True); e.line(1460, 450, 1530, 450, double=True)
    e.text(1200, 420, "M", w=30); e.text(1500, 420, "N", w=30)
    e.attr(1350, 570, "Hours", w=150)
    e.line(1350, 505, 1350, 538)
    step("step5", 5, "Mapping binary M:N relationships",
         ["Create a **new table** for the relationship", "Add **FKs to both** participating tables",
          "PK = the **combination** of both FKs", "Relationship attributes (Hours) become columns of the new table"],
         e, [("WORKS_ON", ["_Essn*_", "_Pno*_", "Hours"])],
         notes="M:N can never be represented by a single FK column: either side would need many values per row.")

    e = ERD()
    e.entity(1200, 480, "DEPARTMENT", w=260)
    e.attr(980, 350, "Dnumber", kind="key", w=170)
    e.attr(1560, 380, "Locations", kind="multi", w=200, h=70)
    e.line(1020, 380, 1140, 436); e.line(1460, 400, 1330, 460)
    step("step6", 6, "Mapping multi-valued attributes",
         ["Create a **new table** per multi-valued attribute", "Columns: the **owner's PK as FK** + the **value**",
          "PK = **both columns** together (one row per value)", "A multi-valued **composite** attribute adds all its parts"],
         e, [("DEPT_LOCATIONS", ["_Dnumber*_", "_Dlocation_"])],
         notes="Clarified: the original said 'Table will include two columns: one for the multi-valued attribute + FK column' without saying the primary key is the combination of both.")

    e = ERD()
    e.rel(1360, 440, "SUPPLY", w=210, h=110)
    e.entity(1040, 340, "SUPPLIER", w=220)
    e.entity(1680, 340, "PROJECT", w=220)
    e.entity(1360, 600, "PART", w=200)
    e.attr(1650, 560, "Quantity", w=170)
    e.line(1150, 360, 1265, 425); e.line(1570, 360, 1455, 425); e.line(1360, 495, 1360, 560); e.line(1565, 545, 1450, 470)
    step("step7", 7, "Mapping N-ary relationships (n > 2)",
         ["Create a **new table** for the relationship", "Add **FKs to all n** participating tables",
          "PK = usually the **combination of all FKs**", "If one entity participates with cardinality 1, its FK can be left out of the PK"],
         e, [("SUPPLY", ["_Sname*_", "_Part_no*_", "_Proj_name*_", "Quantity"])],
         notes="A ternary relationship is mapped exactly like M:N, generalized to n foreign keys.")

    d.slide("summary", "Mapping", "ER construct → relational construct",
            table(["ER model", "Relational model"],
                  [["Entity type", "Entity table"],
                   ["Weak entity type", "Table with PK = owner FK + partial key"],
                   ["1:1 or 1:N relationship", "Foreign key (or a relationship table)"],
                   ["M:N relationship", "Relationship table with two FKs"],
                   ["n-ary relationship", "Relationship table with n FKs"],
                   ["Simple / composite attribute", "Column / one column per component"],
                   ["Multi-valued attribute", "Table with FK + value"],
                   ["Key attribute", "Primary key or UNIQUE"],
                   ["Value set", "Domain (data type + CHECK)"]],
                  widths=[40, 60], size=28),
            notes="Correspondence table adapted from Elmasri & Navathe (table 9.1).")

    # ---------- Part 3 ----------
    d.divider("d3", "03", "The COMPANY schema", "All seven steps applied to the ERD from Lesson 2.")

    d.slide("companyschema", "COMPANY schema", "The COMPANY ERD, mapped",
            f'<div style="display:flex;flex-direction:column;gap:12px;background:{CARD};border:1px solid {LINE};border-radius:16px;padding:32px 40px">'
            + schema_line("EMPLOYEE", ["Fname", "Minit", "Lname", "_Ssn_", "Bdate", "Address", "Sex", "Salary", "Super_ssn*", "Dno*"], size=28)
            + schema_line("DEPARTMENT", ["Dname", "_Dnumber_", "Mgr_ssn*", "Mgr_start_date"], size=28)
            + schema_line("DEPT_LOCATIONS", ["_Dnumber*_", "_Dlocation_"], size=28)
            + schema_line("PROJECT", ["Pname", "_Pnumber_", "Plocation", "Dnum*"], size=28)
            + schema_line("WORKS_ON", ["_Essn*_", "_Pno*_", "Hours"], size=28)
            + schema_line("DEPENDENT", ["_Essn*_", "_Dependent_name_", "Sex", "Bdate", "Relationship"], size=28)
            + "</div>"
            + p(f'<u><b>underlined</b></u> = primary key · <span style="color:{BLUE}"><i>blue italic</i></span> = foreign key', size=24, color=MUTED, raw=True),
            notes="Redrawn from the original 'Mapping Result' figure. Ask which step produced each table or column: EMPLOYEE/DEPARTMENT/PROJECT step 1, DEPENDENT step 2, Mgr_ssn step 3, Dno/Super_ssn/Dnum step 4, WORKS_ON step 5, DEPT_LOCATIONS step 6.")

    d.slide("companyfks", "COMPANY schema", "Where every foreign key points",
            table(["Foreign key", "References", "Created by"],
                  [["EMPLOYEE.Super_ssn", "EMPLOYEE.Ssn", "Step 4 (recursive SUPERVISION)"],
                   ["EMPLOYEE.Dno", "DEPARTMENT.Dnumber", "Step 4 (WORKS_FOR)"],
                   ["DEPARTMENT.Mgr_ssn", "EMPLOYEE.Ssn", "Step 3 (MANAGES, FK on total side)"],
                   ["DEPT_LOCATIONS.Dnumber", "DEPARTMENT.Dnumber", "Step 6 (Locations)"],
                   ["PROJECT.Dnum", "DEPARTMENT.Dnumber", "Step 4 (CONTROLS)"],
                   ["WORKS_ON.Essn / Pno", "EMPLOYEE.Ssn / PROJECT.Pnumber", "Step 5 (WORKS_ON)"],
                   ["DEPENDENT.Essn", "EMPLOYEE.Ssn", "Step 2 (weak entity)"]],
                  widths=[32, 36, 32], size=26),
            notes="This replaces the arrows of the original figure with a table students can check against their own mapping.")

    d.slide("companysql", "COMPANY schema", "Preview: the mapping as SQL",
            row(code_block("""CREATE TABLE works_on (
  essn   CHAR(9)      NOT NULL,
  pno    INT          NOT NULL,
  hours  DECIMAL(4,1) CHECK (hours >= 0),
  CONSTRAINT pk_works_on PRIMARY KEY (essn, pno),
  CONSTRAINT fk_wo_emp  FOREIGN KEY (essn)
      REFERENCES employee (ssn),
  CONSTRAINT fk_wo_proj FOREIGN KEY (pno)
      REFERENCES project (pnumber)
);""", size=26, flex="3"),
                col(callout("Composite **PRIMARY KEY** = step 5's rule.", tone="blue", size=26),
                    callout("Each FK becomes a **FOREIGN KEY … REFERENCES** constraint.", tone="blue", size=26),
                    callout("Total participation and business rules become **NOT NULL** and **CHECK**.", size=26), flex="2", gap=16), gap=32),
            notes="New bridge slide to Lesson 4: the logical schema we just built is what CREATE TABLE implements.")

    # ---------- Part 4 ----------
    d.divider("d4", "04", "Ternary relationships & cases", "When three entities must be related at once, and practice on three narratives.")

    d.slide("ternary", "Ternary relationships", "Ternary vs three binary relationships",
            row(card("One ternary: SUPPLY", tone="blue", size=28, items=[
                "Records **which supplier** supplies **which part** to **which project**",
                "Table SUPPLY(Sname, Part_no, Proj_name, Quantity)",
                "Answers: *does S1 supply bolts to Project X?*"]),
                card("Three binaries: CAN_SUPPLY, USES, SUPPLIES", tone="accent", size=28, items=[
                    "S1 can supply bolts; Project X uses bolts; S1 supplies Project X…",
                    "…but S1 may supply Project X **only nuts**",
                    "The combined fact is **lost**: you cannot rebuild the ternary from the three pairs"]))
            + callout("Use a ternary relationship when the fact only makes sense for **all three entities together**, e.g. Quantity depends on supplier, part and project.", label="Rule:"),
            notes="Completes the original note 'Discuss ternary relationship'. Counter-example in the car case: 'parts made in the same factory as the model' does not need a ternary, because each model has exactly one factory (model -> factory). A ternary there would repeat the factory for every part, a 2NF violation.")

    d.slide("car", "Case study 1", "Car manufacturer: map it",
            row(card("Narrative recap", size=26, items=["MODEL: unique name, suffix, engine size", "PART: id code, description, year, **many images**",
                                                        "MODEL M:N PART", "Each model produced at **one** FACTORY (one per city)",
                                                        "FACTORY: machines, capacity, computer system (OS, DBMS, Internet)",
                                                        "Parts and model produced in the **same** factory"]),
                card("Your task", tone="blue", size=26, items=["Draw the ERD (Lesson 2 method)", "Apply steps 1–7", "Underline PKs, mark FKs",
                                                               "Ternary or two binaries? Check model → factory"])),
            notes="Model answer: FACTORY(_City_, Machines_no, Capacity, OS, DBMS, Internet); MODEL(_Name_, Suffix, Engine_size, Factory_city*); PART(_Id_code_, Description, Prod_year); PART_IMAGES(_Id_code*_, _Image_); MODEL_PART(_Model_name*_, _Id_code*_). No ternary: each model has one factory, so 'same factory' holds automatically; the factories that make a part come from joining MODEL_PART with MODEL.")

    d.slide("bus", "Case study 2", "Country bus company: map it",
            row(card("Narrative recap", size=26, items=["BUS: number, chairs, options (AC, Automatic, PS), brand", "Each bus → one ROUTE; a route has many buses",
                                                        "ROUTE: KM, start, end, duration", "ROUTE M:N TOWN; town has stations (multi-valued)",
                                                        "DRIVER: name, mobile, hire date, salary, grade", "Keep **history** of driver allocations and each driver's last route"]),
                card("Your task", tone="blue", size=26, items=["Propose keys where none are given", "Map history as an M:N with dates",
                                                               "Map 'last route' as a separate 1:N FK", "Options: multi-valued or three BOOLEAN columns?"])),
            notes="Sketch: ROUTE(_Route_no_, KM, Start_pt, End_pt, Duration); BUS(_Bus_no_, Chairs, Brand, Route_no*); BUS_OPTIONS(_Bus_no*_, _Option_); TOWN(_Town_name_); TOWN_STATIONS(_Town_name*_, _Station_); ROUTE_TOWN(_Route_no*_, _Town_name*_); DRIVER(_Driver_id_, Name, Mobile, Hire_date, Salary, Grade, Last_route*); ALLOCATION(_Driver_id*_, _Route_no*_, _From_date_, To_date).")

    d.slide("bank", "Lab", "Banking system: map it",
            row(card("Narrative recap", size=26, items=["BRANCH: unique name, unique address, phone", "CUSTOMER: unique ID, name, address, **phones**",
                                                        "Each customer has **one** ACCOUNT: number, amount, last transaction date (D/M/Y)",
                                                        "TRANSACTION: number, type, date, amount, time, branch", "Any customer, any type, any branch"]),
                card("Your task", tone="blue", size=26, items=["Two candidate keys in BRANCH: which is the PK?", "Where does the 1:1 customer–account FK go?",
                                                               "Map TRANSACTION and its two FKs", "Is last transaction date derived?"])),
            notes="Sketch: BRANCH(_Br_name_, Address UNIQUE, Phone); CUSTOMER(_Cust_id_, Name, Address); CUST_PHONES(_Cust_id*_, _Phone_); ACCOUNT(_Acc_no_, Amount, Last_tr_date, Cust_id* UNIQUE NOT NULL); TRANSACTION(_Tr_no_, Type, Tr_date, Tr_time, Amount, Acc_no*, Br_name*).")

    d.takeaways("recap", [
        "Mapping turns the **conceptual** ERD into a **logical** relational schema.",
        "Regular entities → tables; **weak** entities → PK = owner FK + partial key.",
        "1:1 → FK on the **total** side; 1:N → FK on the **N** side.",
        "M:N, multi-valued and n-ary → a **new table** whose PK combines FKs.",
        "Participation and business rules become **NOT NULL**, **UNIQUE** and **CHECK**.",
        "A ternary relationship is **not** the same as three binaries."])

    d.exercises("practice", "Practice: Lesson 3", [
        ("Core", "Map your **library** ERD from Lesson 2 to tables. Mark every PK and FK and the step that created it."),
        ("Core", "A PERSON may own one PASSPORT; every passport belongs to one person. Where does the FK go, and why?"),
        ("Core", "Map: STUDENT M:N COURSE with attribute Grade; STUDENT has multi-valued Phones."),
        ("Stretch", "Map the **car manufacturer** case completely and write the CREATE TABLE for the M:N table."),
        ("Stretch", "Give a scenario where a ternary relationship cannot be replaced by three binaries."),
        ("Challenge", "Map the **bus company** including allocation history, then write a query idea to find each driver's current route.")])

    d.resources("study", "Go deeper: Lesson 3", [
        ("Book", "Elmasri & Navathe (7th ed.)", "chapter 9: relational database design by ER-to-relational mapping", ""),
        ("Book", "Elmasri & Navathe (7th ed.)", "chapter 5: the relational data model and constraints", ""),
        ("Tool", "dbdiagram.io", "write the schema as text and see tables + FK arrows", "https://dbdiagram.io/"),
        ("Practice", "DB Fiddle", "run your CREATE TABLE statements online", "https://www.db-fiddle.com/"),
        ("Course", "CMU 15-445", "relational model lecture", "https://15445.courses.cs.cmu.edu/")])

    d.thanks()
    return d
