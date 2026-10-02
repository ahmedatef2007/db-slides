from lib import *


def build():
    d = Deck(1, "Introduction to Databases", "Lesson 1 · Introduction to Databases")

    d.cover("cover", "Introduction to Databases",
            "Why databases exist, what a DBMS does, and the landscape beyond relational systems.",
            ["File systems vs DBMS", "Three-schema architecture", "Data models", "NoSQL", "Big Data", "Environments"],
            notes="Welcome. This lesson sets the vocabulary we use for the whole course: database, DBMS, schema, data model, data independence.")

    d.slide("course", "The course", "Five lessons, from data to SQL",
            table(["Lesson", "Topic", "You will be able to"],
                  [["1", "Introduction to databases", "Explain what a DBMS does and why we use one"],
                   ["2", "Entity Relationship Diagrams", "Model a business narrative as an ERD"],
                   ["3", "Mapping ERD to tables", "Turn any ERD into a relational schema in 7 steps"],
                   ["4", "SQL", "Create tables, query, join, group, and secure data"],
                   ["5", "Normalization", "Detect anomalies and normalize a table to 3NF / BCNF"]],
                  widths=[12, 34, 54], size=28)
            + row(card("Time", body="15 hours of lectures · 12 hours of labs", icon="Clock", size=28),
                  card("Grading", body="Assignments and labs **40%** · Final exam **60%**", icon="Check", size=28),
                  card("Running examples", body="The **COMPANY** database plus ITI student and course data.", icon="Database", size=28)),
            notes="Running examples: the COMPANY database (from Elmasri & Navathe) appears in Lessons 2, 4 and 5; Lesson 3 maps ITI student, instructor and course examples. Students see the same kind of design travel from narrative -> ERD -> tables -> SQL -> normalization.")

    d.slide("objectives", "Lesson 1", "By the end of this lesson you can",
            grid([card(None, body=t, tag=f"{i + 1:02d}", size=30) for i, t in enumerate([
                "Define **database**, **DBMS** and **database system**",
                "Explain the limits of **file-based** systems",
                "List the **functions**, advantages and costs of a DBMS",
                "Describe the **three-schema architecture** and data independence",
                "Compare **conceptual, logical and physical** data models",
                "Place **NoSQL, data warehouses and Big Data** on the map"])], cols=3))

    # ---------------- Part 1 ----------------
    d.divider("d1", "01", "From files to databases", "Why organizations moved from separate program files to a shared, managed database.")

    d.slide("filebased", "Files to databases", "The file-based approach",
            p("Each program defines and manages **its own data files**. It worked when computers ran one job at a time.")
            + row(card("Sales program", items=["customers.dat", "orders.dat"], icon="Code"),
                  card("Billing program", items=["customers.csv (again)", "invoices.dat"], icon="Code"),
                  card("HR program", items=["employees.xls", "payroll.dat"], icon="Code"))
            + callout("The same customer lives in two files with two formats. Change an address in Sales and Billing still sends the invoice to the old one.", label="Problem:"),
            notes="Example: a company where every department wrote its own program and file. Ask the students: what happens when a customer moves?")

    d.slide("filelimits", "Files to databases", "Limitations of the file-based approach",
            grid([card("Separation & isolation", body="Data is split across files; combining it needs custom code for every question."),
                  card("Duplication", body="The same facts are stored many times: wasted space and **inconsistent** copies."),
                  card("Program–data dependence", body="The file layout is coded into each program. Add a field and every program must change."),
                  card("Incompatible formats", body="COBOL, C, Excel, CSV… files written by one program cannot be read by another."),
                  card("No integrity rules", body="Nothing stops a negative salary or an order for a customer who does not exist."),
                  card("No concurrency or recovery", body="Two users updating the same file at once, or a crash mid-write, can corrupt data.")], cols=3),
            notes="The last two cards are additions that complete the picture: the DBMS functions on the next slides answer each of these six problems one by one.")

    e = ERD()
    for cx, prog, f in ((250, "Sales app", "sales.dat"), (515, "Billing app", "billing.csv"), (780, "HR app", "hr.xls")):
        e.entity(cx, 420, prog, w=230, h=76, size=24)
        e.attr(cx, 600, f, w=220, h=70)
        e.line(cx, 458, cx, 565, head="end")
    for cx, prog in ((1120, "Sales app"), (1405, "Billing app"), (1690, "HR app")):
        e.entity(cx, 420, prog, w=230, h=76, size=24)
        e.line(cx, 458, 1405 + (cx - 1405) // 3, 562, head="end")
    e.entity(1405, 600, "DBMS", w=520, h=76)
    e.entity(1405, 760, "One shared database + catalog", w=520, h=76, size=24)
    e.line(1405, 638, 1405, 722, head="end")
    side = (pin_text(128, 300, 780, "File-based", 30, ACCENT, bold=True)
            + pin_text(1000, 300, 792, "Database approach", 30, BLUE, bold=True)
            + pin_box(950, 300, 2, 560, fill=LINE)
            + pin_text(128, 680, 780, "Each program defines its **own** file: the same data is stored three times, in three formats.", 26, BODY)
            + pin_text(1000, 830, 792, "Programs ask the DBMS; the data and its description are stored **once**.", 26, BODY))
    d.diagram("approaches", "Files to databases", "File-based vs database approach", e, side=side,
              notes="New diagram: the same three applications before and after a DBMS. Point at the duplicated customer data on the left and the single shared database on the right; every limitation on the previous slide disappears because the DBMS sits in the middle.")

    d.slide("definitions", "Basic definitions", "Database, DBMS, database system",
            row(card("Database", body="A collection of **related data** with a meaning, e.g. all students, courses and grades of a university.", icon="Database", size=30),
                card("DBMS", body="Software to **define, construct, manipulate and share** databases, e.g. PostgreSQL, Oracle, SQL Server, MySQL.", icon="Settings", size=30),
                card("Database system", body="The DBMS **plus** the database (and often the applications that use it).", icon="Globe", size=30))
            + callout("**Defining** = specifying data types and constraints. **Constructing** = storing the data. **Manipulating** = querying and updating it.", tone="blue"),
            notes="DBMS is a collection of programs that enables users to create and maintain a database. Defining a database involves specifying the data types and constraints. Constructing the database is storing the data on some storage medium. Manipulating includes querying the database to retrieve, update or delete specific data.")

    e = ERD()
    e.entity(960, 330, "Users / programmers", w=520, h=72)
    e.entity(960, 460, "Application programs / queries", w=620, h=72)
    e.entity(960, 610, "DBMS: query processor + storage manager", w=820, h=88)
    e.entity(700, 790, "Stored DB definition (metadata / catalog)", w=560, h=88, size=26)
    e.entity(1270, 790, "Stored database", w=420, h=88)
    e.line(960, 366, 960, 424, head="end")
    e.line(960, 496, 960, 566, head="end")
    e.line(800, 654, 760, 746, head="end")
    e.line(1120, 654, 1220, 746, head="end")
    side = (pin_box(400, 560, 1120, 300, border=ACCENT, dashed=True, radius=16, border_w=3)
            + pin_text(1540, 600, 260, "Database system", 26, ACCENT, bold=True)
            + pin_text(1540, 640, 260, "= DBMS software + data + metadata", 24, MUTED))
    d.diagram("dbsystem", "Basic definitions", "A database system, simplified", e, side=side,
              notes="Walk top-down: people use programs; programs send queries to the DBMS; the DBMS reads the catalog (metadata) to understand the data, then reads or writes the stored data. Applications never touch the files directly.")

    d.slide("functions", "The DBMS", "What a DBMS does for you",
            grid([card("Define", body="Data types, structures, constraints (DDL)", icon="Wrench"),
                  card("Store & retrieve", body="Efficient storage, indexes, a query language (SQL)", icon="Search"),
                  card("Share", body="Many users and programs on the same data", icon="Users"),
                  card("Concurrency control", body="Simultaneous updates without conflicts (transactions)", icon="Activity"),
                  card("Security", body="Who may see or change what (GRANT / REVOKE)", icon="Lock"),
                  card("Integrity", body="Constraints keep data valid (PK, FK, CHECK)", icon="Verified"),
                  card("Backup & recovery", body="Restore a consistent state after a crash", icon="Cloud"),
                  card("Data dictionary", body="A catalog describing every object (metadata)", icon="Book")], cols=4),
            notes="Original question to the class: 'What are the other functions of DBMS?' Answer: data security & integrity, concurrency, recovery, performance, data dictionary. Each maps to a later lesson: SQL (Lesson 4) covers DDL, DCL, transactions and indexes.")

    d.slide("proscons", "The DBMS", "Advantages and costs",
            row(card("Advantages", tone="blue", size=28, items=[
                "Controlled redundancy → no inconsistent copies",
                "Restricted unauthorized access",
                "Data shared by many users and apps",
                "Integrity constraints enforced centrally",
                "Backup and recovery built in",
                "Program–data independence; faster development"]),
                card("Costs to weigh", tone="accent", size=28, items=[
                    "Licenses can be expensive (open-source options: PostgreSQL, MySQL, SQLite)",
                    "Skilled staff and training (DBA, designers)",
                    "Overhead for very small or single-purpose apps",
                    "Central point of failure → needs backups and replication",
                    "Vendor lock-in: SQL dialects differ between products"])),
            notes="Updated: the original listed only 'expensive' and 'may be incompatible with other DBMS'. Today cost depends on the product (many are free and open source); the incompatibility point is really vendor lock-in through SQL dialects and proprietary features.")

    d.slide("users", "People", "Who works with a database",
            table(["Role", "What they do", "Example task"],
                  [["Database administrator (DBA)", "Installs, secures, tunes, backs up the DBMS", "Grant access; restore last night's backup"],
                   ["Database designer", "Designs the conceptual and logical schema", "Draw the ERD; map it to tables"],
                   ["System analyst", "Captures requirements from the business", "Write the narrative the ERD is built from"],
                   ["Application programmer", "Writes programs that use the database", "Build the payroll app with SQL inside"],
                   ["End user", "Queries and updates data through apps or reports", "Run the monthly sales report"]],
                  widths=[28, 38, 34], size=28))

    # ---------------- Part 2 ----------------
    d.divider("d2", "02", "Architecture & data models", "How a DBMS separates what users see from how data is stored, and why that matters.")

    e = ERD()
    for x, t in ((560, "External schema 1"), (960, "External schema 2"), (1360, "External schema 3")):
        e.entity(x, 330, t, w=340, h=80, size=26)
        e.line(x, 370, 960 + (x - 960) // 3, 476, head="none")
    e.entity(960, 520, "Conceptual schema", w=720, h=88)
    e.entity(960, 680, "Internal (physical) schema", w=720, h=88)
    e.entity(960, 840, "Stored database on disk", w=720, h=72, size=26)
    e.line(960, 564, 960, 636)
    e.line(960, 724, 960, 804)
    lab = ""
    for y, t in ((330, "External level"), (520, "Conceptual level"), (680, "Internal level")):
        lab += pin_text(128, y - 18, 240, t, 26, ACCENT, bold=True)
    for y, t in ((432, "external / conceptual mapping"), (600, "conceptual / internal mapping")):
        lab += pin_text(1340, y - 16, 420, t, 24, MUTED, italic=True)
    d.diagram("threeschema", "Architecture", "The three-schema architecture", e, side=lab,
              notes="Also called the ANSI/SPARC architecture. Each level is described by a schema; the DBMS maps requests and results between levels.")

    d.slide("levels", "Architecture", "What each level describes",
            table(["Level", "Answers", "Example in the COMPANY database"],
                  [["External (user view)", "What does *this* user see?", "HR sees name + salary; a project manager sees name + project + hours"],
                   ["Conceptual (logical)", "What data exists and how is it related?", "Tables EMPLOYEE, DEPARTMENT, PROJECT with keys and constraints"],
                   ["Internal (physical)", "How is it stored and accessed?", "Data files, pages, a B-tree index on SSN, compression"]],
                  widths=[24, 30, 46], size=28)
            + callout("**Mappings** translate a request from one level to the next (e.g. a view query → a query on base tables → page reads). They cost time, which is why some systems collapse levels.", tone="blue"),
            notes="External: deals with how users access the schema, e.g. a data input form or a view. Conceptual: the basic database model with tables and constraints. Internal: physical storage, files and indexes; it hides hardware and OS details from the data model.")

    e = ERD()
    for y, t in ((420, "External schemas (views)"), (600, "Conceptual schema"), (780, "Internal schema")):
        e.entity(660, y, t, w=480, h=86, size=26)
    e.line(660, 463, 660, 557)
    e.line(660, 643, 660, 737)
    side = (pin_text(128, 290, 1664, "The capacity to change the schema at one level **without changing the level above it**.", 30, INK)
            + pin_conn(400, 425, 400, 595, head="both", color=BLUE, width=4)
            + pin_text(128, 470, 260, "Logical independence", 26, BLUE, bold=True, align="right")
            + pin_conn(400, 605, 400, 775, head="both", color=ACCENT, width=4)
            + pin_text(128, 650, 260, "Physical independence", 26, ACCENT, bold=True, align="right")
            + pin_block(1000, 380, 792, col(
                card("Logical data independence", size=26, title_size=32, tone="blue",
                     body="Change the **conceptual** schema; external schemas and programs keep working.",
                     items=["Add a column `Email` to EMPLOYEE", "Split a table; old views still work"]),
                card("Physical data independence", size=26, title_size=32, tone="accent",
                     body="Change the **internal** schema; the conceptual schema stays the same.",
                     items=["Add an index on `Salary`", "Move data files to a faster disk"]), gap=20)))
    d.diagram("independence", "Architecture", "Data independence", e, side=side,
              notes="Completed: the original slide named the two types but only defined physical data independence. Logical independence is harder to achieve because programs depend on the structure they query; views are the main tool for it. The arrows show where each kind of independence protects the level above.")

    d.slide("models", "Data models", "Three kinds of data models",
            row(card("Conceptual (high level)", tag="Lesson 2", size=28, body="Close to how users think: **entities, attributes, relationships**.", items=["Example: an ERD"]),
                arrow_right(),
                card("Logical (representational)", tag="Lesson 3", size=28, body="How data is organized for a DBMS, independent of storage.", items=["Example: the relational model (tables)", "Others: document, graph"]),
                arrow_right(),
                card("Physical (low level)", tag="Lesson 4", size=28, body="How data is stored on disk and the **access paths** to find it.", items=["Example: files, pages, indexes"]), gap=16)
            + callout("A **data model** is a set of concepts used to describe the structure of a database, the relationships in it and the constraints on it.", tone="blue"),
            notes="Completed: the original showed only conceptual and physical models. The logical (representational / implementation) level, e.g. the relational model, is the bridge we will use when mapping ERDs to tables in Lesson 3.")

    d.slide("relational", "Data models", "A first look at the relational model",
            row(col(table(["SSN", "Fname", "Salary", "Dno"],
                          [["123456789", "John", "30000", "5"], ["333445555", "Franklin", "40000", "5"], ["999887777", "Alicia", "25000", "4"]],
                          widths=[30, 26, 22, 22], size=28),
                    p("Table **EMPLOYEE**", size=26, color=MUTED), gap=16, flex="3"),
                col(card(None, size=26, items=["**Relation** = table", "**Tuple** = row (one employee)", "**Attribute** = column",
                                               "**Domain** = allowed values of a column", "**Primary key** = SSN (unique per row)",
                                               "**Foreign key** = Dno → DEPARTMENT"]), flex="2"), gap=40),
            notes="Preview only: we formalize this in Lesson 3. Point out that Dno links each employee to a department row in another table.")

    # ---------------- Part 3 ----------------
    d.divider("d3", "03", "Beyond relational", "NoSQL stores, data warehouses, Big Data and where databases run.")

    d.slide("nosql", "Beyond relational", "Non-relational (NoSQL) databases",
            row(col(p("No fixed tables, rows or foreign keys. Each store uses a **data model optimized for one kind of data** and access pattern.", size=32),
                    ul(["NoSQL = **Not Only SQL**", "Usually schema-flexible", "Built to scale out across many servers",
                        "Some offer SQL-like query languages (e.g. Cassandra CQL)"], size=30), gap=24, flex="1"),
                code_block('{\n  "_id": 1042,\n  "name": "Mai",\n  "phones": ["010...", "011..."],\n  "address": { "city": "Giza" }\n}', size=28, flex="1", plain=True), gap=48),
            notes="Example on the right is a JSON document: note the multi-valued phones and the nested address. In a relational design those would become separate tables (Lesson 3 steps 6 and 1).")

    d.slide("nosqltypes", "Beyond relational", "Four families of NoSQL stores",
            table(["Family", "Data shape", "Examples", "Good for"],
                  [["Document", "JSON-like documents per key", "MongoDB, Couchbase", "Catalogs, content, user profiles"],
                   ["Key–value", "A dictionary: key → value", "Redis, DynamoDB", "Caching, sessions, shopping carts"],
                   ["Wide-column", "Rows whose columns can vary", "Cassandra, HBase", "Huge write-heavy data, time series"],
                   ["Graph", "Nodes + edges + properties", "Neo4j, Amazon Neptune", "Social networks, recommendations, fraud"]],
                  widths=[17, 29, 25, 29], size=28),
            notes="Document stores pair each key with a complex structure (a document). Key-value stores: each key maps to one value, like a dictionary; the simplest NoSQL type. Wide-column stores use tables, rows and columns, but column names and formats can vary per row. Graph stores use nodes, edges and properties for semantic queries.")

    d.slide("sqlvsnosql", "Beyond relational", "Relational or NoSQL?",
            table(["", "Relational (SQL)", "NoSQL"],
                  [["Schema", "Fixed, defined first", "Flexible, per record"],
                   ["Consistency", "ACID transactions", "Often *eventual* consistency (BASE); many now offer ACID too"],
                   ["Scaling", "Mostly up (bigger server); scale-out is possible", "Out (more servers) by design"],
                   ["Queries", "Rich SQL: joins, aggregates", "Fast lookups by key; joins limited"],
                   ["Pick it when", "Data is structured and related; correctness matters", "Huge volume, changing shape, simple access patterns"]],
                  widths=[18, 41, 41], size=28)
            + callout("Most real systems use **both** (*polyglot persistence*): e.g. PostgreSQL for orders and payments, Redis for sessions.", tone="blue"),
            notes="New slide: helps students decide rather than memorize. ACID is covered in Lesson 4.")

    d.slide("dw", "Beyond relational", "Data warehouses",
            p("A **data warehouse** is a separate database, built for **analysis**, that integrates historical data from many operational systems.", size=32)
            + table(["", "Operational DB (OLTP)", "Data warehouse (OLAP)"],
                    [["Purpose", "Run the business day to day", "Analyze the business over time"],
                     ["Typical query", "Insert one order; find one customer", "Total sales per region per year"],
                     ["Data", "Current, detailed, constantly updated", "Historical, summarized, loaded in batches"],
                     ["Design", "Normalized (Lesson 5)", "Star schema (facts + dimensions)"]],
                    widths=[18, 41, 41], size=28)
            + p("Data reaches the warehouse through **ETL**: Extract from sources → Transform (clean, unify) → Load.", size=28),
            notes="Completed: the original slide had only the title 'Data Warehouse'. Examples of products: Snowflake, Google BigQuery, Amazon Redshift, Azure Synapse.")

    d.slide("bigdata", "Beyond relational", "Big Data",
            callout("\u201cDatasets whose size is beyond the ability of typical database software tools to capture, store, manage, and analyze.\u201d", label="Definition:", size=30)
            + row(card("Volume", body="Terabytes to petabytes: more than one server can store or process.", icon="Database", size=28),
                  card("Velocity", body="Data arrives fast and continuously: clicks, sensors, transactions.", icon="Lightning", size=28),
                  card("Variety", body="Structured tables, text, images, video, logs, JSON.", icon="Star", size=28))
            + p("Two more Vs are often added: **Veracity** (can we trust it?) and **Value** (is it worth it?).", size=28)
            + p("Source of the definition: McKinsey Global Institute, *Big data: The next frontier for innovation, competition, and productivity*, May 2011.", size=24, color=MUTED),
            notes="Fixed: the original slide attributed a different definition ('data whose scale, distribution, diversity and/or timeliness require new technical architectures...') to this McKinsey report; the quote now on the slide is the report's own definition. Typical tools: Hadoop/HDFS and Spark for processing, data lakes on cloud object storage, streaming with Kafka.")

    d.slide("environments", "Beyond relational", "Where databases run",
            grid([card("Centralized / mainframe", body="One powerful machine; users connect from terminals."),
                  card("Client/server", body="The database lives on a server; each user's PC runs the client application."),
                  card("Three-tier / web", body="Browser → web/app server → database server. Only the server needs the app installed."),
                  card("Distributed", body="Data is spread over several sites but looks like one database to users."),
                  card("Cloud (DBaaS)", body="A managed service: the provider runs backups, patching and scaling, e.g. Amazon RDS, Azure SQL, Cloud SQL."),
                  card("Embedded", body="The database is a library inside the app: SQLite in every phone and browser.")], cols=3),
            notes="Updated: added cloud DBaaS and embedded databases, which are where most new databases run today. Mainframe: a powerful machine networked with dumb terminals. Client/server: a server holds the database, each user has a PC. Internet computing: the application is installed on a web server; users need only a browser.")

    e = ERD()
    for cx in (230, 450, 670):
        e.entity(cx, 420, "Client PC", w=190, h=72, size=24)
        e.line(cx, 456, 450 + (cx - 450) // 3, 646, head="end")
    e.entity(450, 690, "Database server", w=420, h=86)
    for y, t in ((400, "Browser"), (570, "Web / application server"), (740, "Database server")):
        e.entity(1400, y, t, w=520, h=86)
    e.line(1400, 443, 1400, 527, head="both")
    e.line(1400, 613, 1400, 697, head="both")
    side = (pin_text(128, 300, 700, "Two-tier (client/server)", 30, ACCENT, bold=True)
            + pin_text(1000, 300, 792, "Three-tier (web)", 30, BLUE, bold=True)
            + pin_box(900, 300, 2, 600, fill=LINE)
            + pin_text(128, 770, 720, "Each PC runs the application and talks to the database directly.", 26, BODY)
            + pin_text(1000, 820, 792, "Only the server runs the application; users need just a browser. The database is never exposed to the internet.", 26, BODY))
    d.diagram("tiers", "Beyond relational", "Two-tier vs three-tier", e, side=side,
              notes="New diagram for the 'Database environment' part of the original course. Mainframe: terminals talk to one powerful machine. Client/server: the database lives on a server and each PC runs the client. Internet computing: the application is installed on one web server; users only need a browser.")

    d.statement("statement", "A DBMS separates **what** the data means from **how** it is stored.",
                "Everything in this course builds on that idea: we design the meaning (ERD, tables, normalization) and let the DBMS handle storage.")

    d.takeaways("recap", [
        "File-based systems duplicate data and tie programs to file layouts.",
        "A **DBMS** defines, stores, shares and protects data; database + DBMS = database system.",
        "The **three-schema architecture** separates user views, logical design and physical storage.",
        "**Data independence** lets one level change without breaking the level above.",
        "Data models go from **conceptual** (ERD) to **logical** (tables) to **physical** (files, indexes).",
        "NoSQL, warehouses and Big Data **complement** relational databases rather than replace them."])

    d.exercises("practice", "Practice: Lesson 1", [
        ("Core", "A university keeps a separate student file in Admissions, Finance and the Library. List **three problems** this causes, with a concrete example of each."),
        ("Core", "Is an Excel workbook a DBMS? Argue **yes or no** using the DBMS functions slide."),
        ("Core", "Which **role** does each task: design the ERD, restore a backup, build the payroll app, run the monthly report?"),
        ("Stretch", "For a library database, give one change that needs **logical** data independence and one that needs **physical** data independence."),
        ("Stretch", "Choose a NoSQL family for: a shopping cart, friend-of-a-friend search, a product catalog with varying attributes, sensor readings."),
        ("Challenge", "Open db-fiddle.com (PostgreSQL), create a table and insert 3 rows. Which schema level did each statement touch?")])

    d.resources("study", "Go deeper: Lesson 1", [
        ("Book", "Elmasri & Navathe, Fundamentals of Database Systems (7th ed.)", "chapters 1–2: concepts and architecture", ""),
        ("Book", "C. J. Date, An Introduction to Database Systems (8th ed.)", "the classic text on the relational model", ""),
        ("Course", "CMU 15-445 Intro to Database Systems", "free lectures and slides on how a DBMS works inside", "https://15445.courses.cs.cmu.edu/"),
        ("Docs", "PostgreSQL tutorial", "install a real DBMS and try it", "https://www.postgresql.org/docs/current/tutorial.html"),
        ("Explore", "DB-Engines ranking", "which DBMS products are popular, by family", "https://db-engines.com/en/ranking")])

    return d
