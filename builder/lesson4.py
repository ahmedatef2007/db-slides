from lib import *


def build():
    d = Deck(4, "Structured Query Language", "Lesson 4 · SQL")

    def code_side(sid, eyebrow, title, code, side, notes="", size=26):
        longest = max(len(l) for l in code.strip("\n").split("\n"))
        if longest * 0.6 * size + 80 > 1180:
            size = 24
        width = int(min(1180, max(900, longest * 0.6 * size + 96)))
        assert longest * 0.6 * size + 80 <= 1180, (sid, longest)
        d.slide(sid, eyebrow, title, row(code_block(code, size=size, width=width), col(*side, flex="1", gap=16), gap=32), notes=notes)

    def code_result(sid, eyebrow, title, code, headers, rows_, widths=None, caption="Result", notes="", size=26, intro=None):
        res = col(p(caption, size=24, color=MUTED, extra="font-weight:600;text-transform:uppercase;letter-spacing:2px"),
                  table(headers, rows_, widths=widths, size=24), gap=12, flex="1")
        body = (p(intro, size=28) if intro else "") + row(code_block(code, size=size, flex="1"), res, gap=32)
        d.slide(sid, eyebrow, title, body, notes=notes, gap=32)

    d.cover("cover", "Structured Query Language",
            "Define, change, query and protect data with SQL, using the COMPANY database.",
            ["DDL", "DML", "SELECT", "Joins", "Subqueries", "GROUP BY", "Views", "Indexes", "Transactions"])

    d.slide("objectives", "Lesson 4", "By the end of this lesson you can",
            grid([card(None, body=t, tag=f"{i + 1:02d}", size=30) for i, t in enumerate([
                "Explain **transactions** and the ACID properties",
                "Create and change tables with **DDL** and constraints",
                "Insert, update and delete rows **safely**",
                "Write queries with **filters, joins and subqueries**",
                "Summarize data with **GROUP BY, HAVING** and window functions",
                "Use **views, indexes** and **GRANT/REVOKE**"])], cols=3))

    # ---------------- 01 foundations ----------------
    d.divider("d1", "01", "SQL foundations", "The four families of SQL statements, transactions, schemas, data types and constraints.")

    d.slide("families", "Foundations", "Four families of SQL statements",
            grid([card("DDL", body="Data **Definition**: structure", items=["CREATE", "ALTER", "DROP", "TRUNCATE"], tone="blue", size=28),
                  card("DML", body="Data **Manipulation**: rows", items=["SELECT", "INSERT", "UPDATE", "DELETE"], size=28),
                  card("DCL", body="Data **Control**: permissions", items=["GRANT", "REVOKE"], size=28),
                  card("TCL", body="Transaction **Control**", items=["COMMIT", "ROLLBACK", "SAVEPOINT"], tone="accent", size=28)], cols=4)
            + callout("SQL is a **declarative** language: you say *what* you want; the DBMS's optimizer decides *how* to get it.", tone="blue"),
            notes="Added TCL, which the original slides used (rollback in the TRUNCATE notes) without naming. Some books also separate SELECT as DQL (data query language).")

    d.slide("transactions", "Transactions", "Transactions and ACID",
            p("A **transaction** is a logical unit of work: one or more reads/writes (INSERT, UPDATE, DELETE) that must succeed or fail **together**.", size=30)
            + grid([card("Atomicity", body="All or nothing: a half-finished transfer is undone.", tag="A", size=26),
                    card("Consistency", body="Moves the database from one valid state to another; constraints hold.", tag="C", size=26),
                    card("Isolation", body="Concurrent transactions don't see each other's partial work.", tag="I", size=26),
                    card("Durability", body="Once committed, changes survive crashes.", tag="D", size=26)], cols=4),
            notes="Atomicity: performed in its entirety or not at all. Consistency preservation: if executed completely without interference, it takes the database from one consistent state to another. Isolation: it should appear to run alone even though many run concurrently. Durability: committed changes must not be lost because of any failure.")

    code_side("txexample", "Transactions", "A transaction in practice",
              """BEGIN;  -- or BEGIN TRANSACTION / implicit in Oracle

UPDATE account SET balance = balance - 500
WHERE  acc_no = 'A-101';

UPDATE account SET balance = balance + 500
WHERE  acc_no = 'B-202';

COMMIT;     -- make both changes permanent
-- ROLLBACK;  would undo both instead""",
              [card("Why both or none?", body="If the system crashes after the first UPDATE, 500 would vanish. The transaction guarantees **atomicity**.", size=26),
               callout("Oracle starts a transaction automatically with the first DML; SQL Server and PostgreSQL run each statement alone (**autocommit**) unless you BEGIN.", tone="blue", size=24)],
              notes="New slide: the original defined transactions but never showed COMMIT/ROLLBACK.")

    code_side("schema", "Foundations", "Database schema",
              """CREATE SCHEMA hr AUTHORIZATION ahmed;

CREATE TABLE hr.employee ( ... );

SELECT * FROM hr.employee;""",
              [card(None, body="A **schema** is a named group of related objects (tables, views, indexes…) inside a database.", size=28),
               card(None, body="It has **one owner** who can change the structure of any object in it. A schema is not a person, but it is associated with a database user.", size=28)],
              notes="In Oracle each user automatically owns a schema with the same name. In SQL Server the default schema is dbo; in PostgreSQL it is public.")

    d.slide("datatypes", "Foundations", "Common data types across DBMSs",
            table(["Kind", "Standard SQL", "Oracle", "SQL Server", "PostgreSQL / MySQL"],
                  [["Fixed text", "CHAR(n)", "CHAR(n)", "CHAR(n), NCHAR(n)", "CHAR(n)"],
                   ["Variable text", "VARCHAR(n)", "VARCHAR2(n)", "VARCHAR(n), NVARCHAR(n)", "VARCHAR(n), TEXT"],
                   ["Whole number", "INTEGER", "NUMBER(p)", "INT, BIGINT", "INTEGER, BIGINT"],
                   ["Exact decimal", "DECIMAL(p,s)", "NUMBER(p,s)", "DECIMAL(p,s)", "NUMERIC / DECIMAL(p,s)"],
                   ["Date", "DATE", "DATE (also stores time)", "DATE", "DATE"],
                   ["Date + time", "TIMESTAMP", "TIMESTAMP", "DATETIME2", "TIMESTAMP / DATETIME"],
                   ["True / false", "BOOLEAN", "BOOLEAN (23ai+)", "BIT", "BOOLEAN"]],
                  widths=[17, 18, 21, 22, 22], size=24)
            + p("Use **VARCHAR** for names and addresses (CHAR pads with spaces) and **DECIMAL** for money (FLOAT is approximate).", size=26),
            notes="Updated: the original only listed alphanumeric, numeric and date/time. The examples in the original used CHAR(50) for names; VARCHAR is the better default.")

    # ---------------- 02 DDL ----------------
    d.divider("d2", "02", "Defining structure (DDL)", "CREATE, ALTER, DROP and TRUNCATE.")

    code_side("create", "DDL", "CREATE TABLE",
              """CREATE TABLE students (
  id          INT          PRIMARY KEY,
  first_name  VARCHAR(50)  NOT NULL,
  last_name   VARCHAR(50)  NOT NULL,
  email       VARCHAR(100) UNIQUE,
  city        VARCHAR(50)  DEFAULT 'Cairo',
  birth_date  DATE,
  gpa         DECIMAL(3,2) CHECK (gpa BETWEEN 0 AND 4)
);""",
              [card("Syntax", body="CREATE TABLE name (column TYPE [constraint], …, [table constraints]);", size=26),
               callout("Every column gets a **type**; constraints can be written inline or at the end.", tone="blue", size=26)],
              notes="Modernized from the original Students example (NUMBER(15), CHAR(50)), now with UNIQUE, DEFAULT and CHECK.")

    code_side("createcompany", "DDL", "Named constraints and foreign keys",
              """CREATE TABLE department (
  dnumber   INT         CONSTRAINT pk_dept PRIMARY KEY,
  dname     VARCHAR(30) NOT NULL CONSTRAINT uq_dname UNIQUE,
  mgr_ssn   CHAR(9)
);

CREATE TABLE employee (
  ssn       CHAR(9)      CONSTRAINT pk_emp PRIMARY KEY,
  fname     VARCHAR(30)  NOT NULL,
  salary    DECIMAL(10,2) CONSTRAINT ck_sal CHECK (salary > 0),
  super_ssn CHAR(9)      REFERENCES employee (ssn),
  dno       INT          NOT NULL,
  CONSTRAINT fk_emp_dept FOREIGN KEY (dno)
      REFERENCES department (dnumber)
);""",
              [callout("**Name your constraints**: error messages then say *ck_sal* instead of *SYS_C00123*.", tone="blue", size=26),
               callout("A FK must reference a **PRIMARY KEY or UNIQUE** column.", size=26),
               callout("department.mgr_ssn → employee is added later with ALTER: the two tables reference each other.", tone="blue", size=26)],
              size=24)

    code_side("alter", "DDL", "ALTER TABLE",
              """ALTER TABLE students ADD phone VARCHAR(20);

ALTER TABLE students DROP COLUMN phone;

ALTER TABLE department
  ADD CONSTRAINT fk_dept_mgr FOREIGN KEY (mgr_ssn)
      REFERENCES employee (ssn);

-- change a column's type (syntax varies):
ALTER TABLE students ALTER COLUMN city TYPE VARCHAR(80);  -- PostgreSQL
ALTER TABLE students MODIFY city VARCHAR2(80);            -- Oracle""",
              [card(None, body="ALTER changes the **structure** of an existing table: add or drop columns and constraints, change types.", size=28),
               callout("Existing rows get **NULL** (or the DEFAULT) in a new column.", tone="blue", size=26)],
              size=24)

    d.slide("alterex", "DDL", "ALTER example",
            row(col(p("Before", size=24, color=MUTED, extra="font-weight:600"),
                    table(["LastName", "FirstName", "Address"], [["Pettersen", "Kari", "Storgt 20"]], size=26), flex="1", gap=12),
                col(p("After", size=24, color=MUTED, extra="font-weight:600"),
                    table(["LastName", "FirstName", "Address", "City"], [["Pettersen", "Kari", "Storgt 20", "NULL"]], size=26), flex="1", gap=12), gap=40)
            + code_block("ALTER TABLE students ADD city VARCHAR(30);", size=30))

    code_side("drop", "DDL", "DROP TABLE",
              """DROP TABLE students;

DROP TABLE IF EXISTS students;   -- PostgreSQL, MySQL, SQL Server 2016+

DROP TABLE department CASCADE CONSTRAINTS;  -- Oracle
DROP TABLE department CASCADE;              -- PostgreSQL""",
              [card(None, body="Removes the table **and its data, indexes and constraints**. There is no undo (except backups or Oracle's recycle bin).", size=28),
               callout("A table referenced by a foreign key cannot be dropped unless you drop the FK first or use CASCADE.", size=26)])

    d.slide("truncate", "DDL", "TRUNCATE vs DELETE vs DROP",
            table(["", "DELETE", "TRUNCATE", "DROP"],
                  [["Family", "DML", "DDL", "DDL"],
                   ["Removes", "Chosen rows (WHERE)", "All rows", "Rows + the table itself"],
                   ["WHERE clause", "Yes", "No", "No"],
                   ["Rollback", "Yes, until COMMIT", "Oracle, MySQL: no (auto-commit). SQL Server, PostgreSQL: yes inside a transaction", "Generally no"],
                   ["Speed on big tables", "Slower (row by row, logged)", "Fast (deallocates pages)", "Fast"],
                   ["Fires DELETE triggers", "Yes", "No", "No"]],
                  widths=[22, 24, 34, 20], size=24),
            notes="Fixed: the original said TRUNCATE 'can't be rolled back because it's a DDL statement'. That is true in Oracle and MySQL but not in SQL Server or PostgreSQL, where TRUNCATE inside an explicit transaction can be rolled back. Also TRUNCATE usually fails on a table referenced by a foreign key, and resets identity columns in SQL Server.")

    # ---------------- 03 DML ----------------
    d.divider("d3", "03", "Changing data (DML)", "INSERT, UPDATE and DELETE, and how not to update every row by accident.")

    code_side("insert", "DML", "INSERT",
              """-- all columns, in table order
INSERT INTO students
VALUES (1, 'Ahmed', 'Saleh', 'ahmed@iti.eg', 'Alex', '2003-05-14', 3.40);

-- chosen columns (others get NULL or DEFAULT)
INSERT INTO students (id, first_name, last_name)
VALUES (2, 'Mona', 'Hassan');

-- several rows at once
INSERT INTO students (id, first_name, last_name) VALUES
  (3, 'Ali', 'Samir'), (4, 'Mai', 'Adel');

-- rows from a query
INSERT INTO alumni (id, name)
SELECT id, first_name FROM students WHERE gpa >= 3.5;""",
              [callout("Always **list the columns**: the statement keeps working if someone adds a column later.", tone="blue", size=26),
               callout("Dates in **ISO format** 'YYYY-MM-DD' are understood by every DBMS.", size=26)],
              size=24,
              notes="Modernized: the original used 'Jan-10-1999' style dates, which depend on the DBMS's date format settings.")

    code_result("insertex", "DML", "INSERT with missing columns",
                "INSERT INTO students (last_name, city)\nVALUES ('Hassan', 'Assiut');",
                ["LastName", "FirstName", "Address", "City"],
                [["El-Sayed", "Mohamed", "Nasr City", "Cairo"], ["Saleh", "Ahmed", "Moharam Bek", "Alex."], ["**Hassan**", "NULL", "NULL", "**Assiut**"]],
                notes="Columns not listed get NULL (or their DEFAULT). If a missing column is NOT NULL without a default, the INSERT fails.")

    d.slide("update", "DML", "UPDATE",
            row(code_block("""UPDATE store_information
SET    sales = 500
WHERE  store_name = 'Los Angeles'
  AND  sale_date  = '1999-01-08';""", size=26, flex="1"),
                col(p("Before", size=24, color=MUTED, extra="font-weight:600"),
                    table(["store_name", "sales", "sale_date"], [["Los Angeles", "1500", "1999-01-05"], ["San Diego", "250", "1999-01-07"],
                                                                 ["Los Angeles", "**300**", "1999-01-08"], ["Boston", "700", "1999-01-08"]], size=24),
                    p("After", size=24, color=MUTED, extra="font-weight:600"),
                    table(["store_name", "sales", "sale_date"], [["Los Angeles", "1500", "1999-01-05"], ["San Diego", "250", "1999-01-07"],
                                                                 ["Los Angeles", "**500**", "1999-01-08"], ["Boston", "700", "1999-01-08"]], size=24),
                    flex="1", gap=10), gap=32),
            notes="Fixed: in the original slide the SET value (500) and the result (300) did not match; the Before table already showed 500. Before now shows 300 and After shows 500.")

    code_side("updatesafe", "DML", "Update safely",
              """-- several columns at once
UPDATE students
SET    address = '241 El-Haram', city = 'Giza'
WHERE  last_name = 'El-Sayed';

-- based on the current value
UPDATE employee SET salary = salary * 1.10 WHERE dno = 5;

-- DANGER: no WHERE = every row changes
UPDATE employee SET salary = 0;""",
              [card("A safe habit", icon="Warning", size=26, items=["Run the WHERE as a **SELECT** first", "Wrap it in a **transaction**",
                                                                    "Check the row count, then COMMIT"])],
              size=24)

    d.slide("delete", "DML", "DELETE",
            row(code_block("DELETE FROM store_information\nWHERE  store_name = 'Los Angeles';", size=26, flex="1"),
                col(p("Before", size=24, color=MUTED, extra="font-weight:600"),
                    table(["store_name", "sales", "sale_date"], [["Los Angeles", "1500", "1999-01-05"], ["San Diego", "250", "1999-01-07"],
                                                                 ["Los Angeles", "500", "1999-01-08"], ["Boston", "700", "1999-01-08"]], size=24),
                    p("After", size=24, color=MUTED, extra="font-weight:600"),
                    table(["store_name", "sales", "sale_date"], [["San Diego", "250", "1999-01-07"], ["Boston", "700", "1999-01-08"]], size=24),
                    flex="1", gap=10), gap=32)
            + callout("Without WHERE, DELETE removes **all rows** (the table stays). Deleting a parent row fails if child rows reference it, unless the FK says ON DELETE CASCADE.", size=26),
            gap=32)

    # ---------------- 04 SELECT ----------------
    d.divider("d4", "04", "Querying one table", "SELECT, filtering, NULLs, sorting and computed columns.")

    d.slide("select", "SELECT", "Anatomy of a query",
            row(code_block("""SELECT   dno, COUNT(*) AS n      -- 5
FROM     employee                -- 1
WHERE    salary > 20000          -- 2
GROUP BY dno                     -- 3
HAVING   COUNT(*) > 2            -- 4
ORDER BY n DESC;                 -- 6""", size=28, flex="3"),
                col(card("Logical order", size=26, items=["1 FROM: pick the table(s)", "2 WHERE: filter rows", "3 GROUP BY: form groups",
                                                          "4 HAVING: filter groups", "5 SELECT: compute columns", "6 ORDER BY: sort"]), flex="2"), gap=32),
            notes="New slide: the written order (SELECT first) is not the evaluation order. This explains why a column alias defined in SELECT cannot be used in WHERE but can be used in ORDER BY.")

    code_side("simple", "SELECT", "Simple queries",
              """SELECT *
FROM   department;

SELECT ssn, fname, dno
FROM   employee;

SELECT dnumber, dname
FROM   department
WHERE  dname = 'Research';""",
              [callout("`SELECT *` is fine for exploring, but list columns in real code.", tone="blue", size=26),
               callout("String literals use **single quotes**. Whether 'research' = 'Research' depends on the DBMS's collation.", size=26)])

    d.slide("distinct", "SELECT", "DISTINCT removes duplicate rows",
            table(["EmpNo", "Name", "DNo", "JobID"], [["100", "Ahmed", "2", "Sales_Rep"], ["200", "Mai", "2", "IT_PROG"],
                                                      ["300", "Ali", "2", "Sales_Rep"], ["400", "Mahmoud", "3", "Sales_Rep"]], size=24)
            + row(col(code_block("SELECT DISTINCT dno\nFROM employees;", size=26),
                      table(["DNo"], [["2"], ["3"]], size=24), gap=12),
                  col(code_block("SELECT DISTINCT dno, job_id\nFROM employees;", size=26),
                      table(["DNo", "JobID"], [["2", "Sales_Rep"], ["2", "IT_PROG"], ["3", "Sales_Rep"]], size=24), gap=12), gap=32),
            notes="DISTINCT applies to the whole row of selected columns, not just the first column.", gap=24)

    d.slide("operators", "SELECT", "Comparison and pattern operators",
            row(table(["Operator", "Meaning", "Example"],
                      [["= <> != < <= > >=", "Compare values", "salary > 1000"],
                       ["BETWEEN a AND b", "In range, **inclusive**", "salary BETWEEN 1000 AND 3000"],
                       ["IN (list)", "Equals any value in the list", "dno IN (1, 4, 5)"],
                       ["LIKE pattern", "_ = one char, % = any run of chars", "fname LIKE '_s%'"],
                       ["IS NULL", "Value is missing", "super_ssn IS NULL"]],
                      widths=[28, 36, 36], size=24), gap=24)
            + code_block("""SELECT fname, salary FROM employee WHERE salary BETWEEN 1000 AND 3000;
SELECT ssn, fname    FROM employee WHERE super_ssn IN ('333445555', '987654321');
SELECT fname         FROM employee WHERE fname LIKE '_s%';   -- 2nd letter is s""", size=24),
            notes="Original note examples: BETWEEN with dates and NOT BETWEEN. ALL is a subquery operator; it is covered with subqueries.")

    d.slide("nulls", "SELECT", "NULL: the missing value",
            row(col(card(None, size=28, items=["NULL means *unknown* or *not applicable*, not 0 or ''",
                                               "Any comparison with NULL is **UNKNOWN**, so the row is filtered out",
                                               "Use **IS NULL / IS NOT NULL**, never = NULL",
                                               "`COALESCE(x, 0)` replaces NULL with a default"]), flex="1"),
                code_block("""-- employees with no supervisor
SELECT fname FROM employee
WHERE  super_ssn IS NULL;

-- WRONG: returns nothing
SELECT fname FROM employee
WHERE  super_ssn = NULL;

SELECT fname, COALESCE(commission, 0)
FROM   employee;""", size=26, flex="1"), gap=32),
            notes="New slide: NULL handling was missing from the original and causes many real bugs. Also warn: NOT IN (subquery) returns no rows if the subquery returns a NULL; prefer NOT EXISTS.")

    code_side("logical", "SELECT", "AND, OR, NOT and precedence",
              """SELECT ssn, fname, salary
FROM   employee
WHERE  salary > 5000
  AND  title NOT LIKE '%manager';

-- AND binds tighter than OR:
WHERE  salary > 5000 AND salary < 10000
   OR  title NOT LIKE '%manager'

-- say what you mean with parentheses:
WHERE  salary > 5000
  AND (salary < 10000 OR title NOT LIKE '%manager')""",
              [card("Precedence", size=28, items=["NOT", "AND", "OR"]),
               callout("The two last WHERE clauses return **different** rows. Use parentheses whenever you mix AND and OR.", size=26)],
              size=24)

    code_side("arith", "SELECT", "Expressions and column aliases",
              """SELECT fname, salary, salary + 300
FROM   employee;

SELECT fname,
       salary,
       10 * (salary + 300) AS proposed_salary
FROM   employee;""",
              [card("Precedence", size=28, items=["* and / before + and -", "Parentheses first"]),
               callout("Aliases with spaces need quotes: **AS \"Proposed salary\"**.", tone="blue", size=26)])

    code_side("orderby", "SELECT", "ORDER BY and limiting rows",
              """SELECT   fname, dno, hire_date
FROM     employee
ORDER BY hire_date DESC;

SELECT   fname, dno, salary
FROM     employee
ORDER BY dno ASC, salary DESC;

-- top 3 earners
SELECT   fname, salary FROM employee
ORDER BY salary DESC
FETCH FIRST 3 ROWS ONLY;   -- standard, Oracle 12c+, PostgreSQL
-- SQL Server: SELECT TOP 3 …   MySQL: … LIMIT 3""",
              [callout("**ASC** is the default. Each column can have its own direction.", tone="blue", size=26),
               callout("Without ORDER BY, row order is **not guaranteed**.", size=26)],
              size=24)

    code_side("case", "SELECT", "CASE: if-then-else inside a query",
              """SELECT fname, salary,
       CASE
         WHEN salary >= 40000 THEN 'High'
         WHEN salary >= 25000 THEN 'Medium'
         ELSE 'Low'
       END AS salary_band
FROM   employee;""",
              [card(None, body="CASE returns the first matching branch. It can be used in SELECT, WHERE, ORDER BY and inside aggregates.", size=28),
               callout("`SUM(CASE WHEN sex = 'F' THEN 1 ELSE 0 END)` counts women per group.", tone="blue", size=26)],
              notes="New slide: CASE is standard SQL and very common in reports.")

    # ---------------- 05 joins ----------------
    d.divider("d5", "05", "Joining tables", "Combine rows from several tables: inner, outer, self, non-equi and cross joins.")

    d.slide("jointypes", "Joins", "Types of join",
            grid([card("INNER JOIN", body="Only rows with a **match in both** tables.", tone="blue", size=26),
                  card("LEFT OUTER JOIN", body="All rows of the **left** table + matches; NULLs where none.", size=26),
                  card("RIGHT OUTER JOIN", body="All rows of the **right** table + matches; NULLs where none.", size=26),
                  card("FULL OUTER JOIN", body="**All rows of both** tables, matched where possible, NULLs elsewhere.", size=26),
                  card("CROSS JOIN", body="Cartesian product: **every** row with **every** row.", size=26),
                  card("SELF JOIN", body="A table joined to **itself** using two aliases.", size=26)], cols=3),
            notes="Fixed: the original defined FULL JOIN as 'Return rows when there is a match in one of the tables'. A FULL OUTER JOIN returns all rows from both tables: matched pairs, plus unmatched rows from each side padded with NULLs.")

    d.slide("innerjoin", "Joins", "Inner join: two syntaxes",
            p("Retrieve the name and address of employees who work for the **Research** department.", size=28)
            + row(col(p("Older style (join condition in WHERE)", size=24, color=MUTED, extra="font-weight:600"),
                      code_block("""SELECT fname, lname, address
FROM   employee, department
WHERE  dname = 'Research'
  AND  dnumber = dno;""", size=26), gap=12),
                  col(p("ANSI JOIN syntax (recommended)", size=24, color=BLUE, extra="font-weight:600"),
                      code_block("""SELECT e.fname, e.lname, e.address
FROM   employee e
JOIN   department d ON d.dnumber = e.dno
WHERE  d.dname = 'Research';""", size=26), gap=12), gap=32)
            + callout("The ANSI form keeps **join conditions** (ON) apart from **filters** (WHERE) and works the same for outer joins. Forgetting the condition in the old style silently creates a Cartesian product.", tone="blue", size=26),
            gap=28,
            notes="Modernized: the original used only the comma (theta) join syntax.")

    code_side("ambiguous", "Joins", "Ambiguous columns and table aliases",
              """-- both tables have a column called name and id
SELECT d.name AS department, e.id, e.name, e.salary
FROM   department d
JOIN   employee   e ON d.id = e.dept_id
ORDER  BY d.name;""",
              [card(None, body="When two tables share a column name, **prefix** it: `department.name` or with an alias `d.name`.", size=28),
               callout("Prefixing **every** column makes queries easier to read and avoids errors when a new column is added.", tone="blue", size=26)],
              notes="The original claimed prefixing improves performance; the main benefit is clarity and avoiding ambiguity errors.")

    code_side("selfjoin", "Joins", "Self join: employees and their supervisors",
              """SELECT e.fname AS employee,
       s.fname AS supervisor
FROM   employee e
JOIN   employee s ON e.super_ssn = s.ssn;

-- full names:  e.fname || ' ' || e.lname   (standard, Oracle, PostgreSQL)
--              CONCAT(e.fname, ' ', e.lname)  (SQL Server, MySQL)""",
              [card(None, body="Two **aliases** of the same table play two roles: **e** = employee, **s** = supervisor.", size=28),
               callout("Swap the condition (**s.super_ssn = e.ssn**) and the roles swap: you would list supervisors as employees.", size=26),
               callout("Use LEFT JOIN to also list employees with **no** supervisor.", tone="blue", size=26)],
              size=24)

    code_result("outerjoin", "Joins", "Outer join: keep unmatched rows",
                """SELECT e.name  AS employee,
       d.id    AS dept_id,
       d.name  AS department
FROM   employees e
RIGHT  JOIN departments d
       ON e.dept_id = d.id;""",
                ["Employee", "Dept_ID", "Department"],
                [["Ahmed Ali", "100", "IT"], ["Mohamed Samir", "200", "Marketing"], ["Mona Selim", "100", "IT"], ["NULL", "300", "HR"]],
                intro="Display all departments, **even those with no employees**.",
                notes="Oracle's old notation WHERE e.dept_id(+) = d.id is equivalent to this RIGHT JOIN. The same result: departments d LEFT JOIN employees e.")

    d.slide("nonequi", "Joins", "Equi-join and non-equi-join",
            row(col(card(None, size=26, items=["**Equi-join**: condition uses = (d.dnumber = e.dno)", "**Non-equi-join**: any other operator (BETWEEN, <, >=)"]),
                    code_block("""SELECT e.name, e.salary, j.grade
FROM   employees  e
JOIN   job_grades j
  ON   e.salary BETWEEN j.low_sal AND j.high_sal;""", size=26), gap=20, flex="1"),
                col(p("employees", size=24, color=MUTED, extra="font-weight:600"),
                    table(["EmpNo", "Name", "Salary"], [["100", "Ahmed", "5000"], ["200", "Mai", "3000"]], size=24),
                    p("job_grades", size=24, color=MUTED, extra="font-weight:600"),
                    table(["LowSal", "HighSal", "Grade"], [["1000", "3999", "B"], ["4000", "7000", "A"]], size=24),
                    p("Result: Ahmed 5000 **A** · Mai 3000 **B**", size=26), gap=12, flex="1"), gap=40),
            notes="Small fix: the grade ranges in the original overlapped at 4000 (1000-4000 and 4000-7000), so a salary of exactly 4000 would match both grades. Ranges now do not overlap.")

    code_side("crossjoin", "Joins", "Cartesian product (CROSS JOIN)",
              """SELECT e.fname, p.pname
FROM   employee e
CROSS  JOIN project p;

-- the same thing by accident:
SELECT e.fname, p.pname
FROM   employee e, project p;   -- no join condition""",
              [card(None, body="Every row of the first table paired with **every** row of the second: 8 employees × 6 projects = **48 rows**.", size=28),
               callout("Useful on purpose for generating combinations (e.g. all sizes × all colors); usually a sign of a **missing join condition**.", size=26)],
              notes="Completes the original's one-line mention of the Cartesian product.")

    # ---------------- 06 subqueries ----------------
    d.divider("d6", "06", "Subqueries & set operators", "Queries inside queries, EXISTS, UNION and friends, and CTEs.")

    d.slide("subq", "Subqueries", "Sub-queries (nested queries)",
            row(card(None, size=28, items=["A complete SELECT **inside** another statement",
                                           "A simple subquery runs **once**, before the outer query",
                                           "Usually in **WHERE** or **HAVING**",
                                           "In **FROM** it is a derived table (an *inline view*)",
                                           "Single-row subqueries use = < >; multi-row ones use IN, ANY, ALL"]),
                code_block("""-- employees working in Giza
SELECT fname
FROM   employee
WHERE  dno IN (SELECT dnumber
               FROM   dept_locations
               WHERE  dlocation = 'Giza');""", size=26, flex="1"), gap=32))

    code_side("subq2", "Subqueries", "Subqueries returning one value",
              """-- department of the highest-paid employee
SELECT dname
FROM   department
WHERE  dnumber = (SELECT dno
                  FROM   employee
                  WHERE  salary = (SELECT MAX(salary)
                                   FROM   employee));""",
              [card(None, body="Subqueries can nest. Read them **inside out**: the max salary → whose department → its name.", size=28),
               callout("If a single-row subquery returns **more than one** row (two top earners in different departments), = fails. Use IN to be safe.", size=26)])

    code_side("allany", "Subqueries", "ALL and ANY",
              """-- earn more than EVERY employee in dept 5
SELECT lname, fname
FROM   employee
WHERE  salary > ALL (SELECT salary
                     FROM   employee
                     WHERE  dno = 5);

-- the same with an aggregate:
WHERE  salary > (SELECT MAX(salary)
                 FROM employee WHERE dno = 5);""",
              [table(["Form", "Means"], [["> ALL (…)", "> the maximum"], ["< ALL (…)", "< the minimum"], ["> ANY (…)", "> the minimum"],
                                         ["= ANY (…)", "same as IN"]], size=26)],
              size=24,
              notes="Completes the original: ANY/SOME was missing. Note: if the subquery returns no rows, > ALL is TRUE for every row while > (SELECT MAX…) compares with NULL and returns nothing.")

    code_side("exists", "Subqueries", "Correlated subqueries and EXISTS",
              """-- suppliers who have at least one order
SELECT *
FROM   suppliers s
WHERE  EXISTS (SELECT 1
               FROM   orders o
               WHERE  o.supplier_id = s.supplier_id);

-- employees with no dependents
SELECT fname
FROM   employee e
WHERE  NOT EXISTS (SELECT 1
                   FROM   dependent d
                   WHERE  d.essn = e.ssn);""",
              [card("Correlated", body="The inner query refers to the **outer** row (s.supplier_id), so it is evaluated **once per outer row**.", size=26),
               card("EXISTS", body="TRUE as soon as the subquery returns **at least one row**; the selected columns don't matter.", size=26)],
              size=24)

    code_side("existsdml", "Subqueries", "EXISTS in DELETE and UPDATE",
              """-- remove suppliers that never had an order
DELETE FROM suppliers s
WHERE  NOT EXISTS (SELECT 1 FROM orders o
                   WHERE o.supplier_id = s.supplier_id);

-- copy names from customers where ids match
UPDATE suppliers s
SET    supplier_name = (SELECT c.name FROM customers c
                        WHERE c.customer_id = s.supplier_id)
WHERE  EXISTS (SELECT 1 FROM customers c
               WHERE c.customer_id = s.supplier_id);""",
              [callout("The WHERE EXISTS in the UPDATE prevents setting the name to **NULL** for suppliers with no matching customer.", tone="blue", size=26),
               callout("Prefer **NOT EXISTS** over NOT IN: NOT IN returns nothing if the subquery contains a NULL.", size=26)],
              size=24)

    d.slide("setops", "Set operators", "UNION, INTERSECT, EXCEPT",
            row(table(["Operator", "Returns", "Duplicates"],
                      [["UNION", "Rows in either query", "Removed"], ["UNION ALL", "Rows in either query", "Kept (faster)"],
                       ["INTERSECT", "Rows in both queries", "Removed"], ["EXCEPT (MINUS in Oracle)", "Rows in the first but not the second", "Removed"]],
                      widths=[34, 42, 24], size=24),
                code_block("""-- departments in Giza or managed by 333445555
SELECT dnumber FROM department
WHERE  mgr_ssn = '333445555'
UNION
SELECT dnumber FROM dept_locations
WHERE  dlocation = 'Giza';""", size=24, flex="1"), gap=32)
            + callout("Both queries need the **same number of columns** with **compatible types**; the result uses the column names of the **first** query.", tone="blue", size=26),
            notes="Completes the original, which covered only UNION and UNION ALL. Example 2 from the original: SELECT name FROM employees UNION SELECT name FROM employees_retired (current and previous employees).")

    code_side("cte", "Subqueries", "Common table expressions (WITH)",
              """WITH dept_avg AS (
  SELECT dno, AVG(salary) AS avg_sal
  FROM   employee
  GROUP  BY dno
)
SELECT e.fname, e.salary, d.avg_sal
FROM   employee e
JOIN   dept_avg d ON d.dno = e.dno
WHERE  e.salary > d.avg_sal;""",
              [card(None, body="A **CTE** names a subquery so you can read the query top to bottom, and reuse it.", size=28),
               callout("Supported by Oracle, SQL Server, PostgreSQL and MySQL 8+. `WITH RECURSIVE` can walk hierarchies like the supervisor chain.", tone="blue", size=26)],
              notes="New slide: modern SQL feature that makes subquery-heavy queries readable.")

    # ---------------- 07 aggregation ----------------
    d.divider("d7", "07", "Summarizing data", "Aggregate functions, GROUP BY, HAVING and window functions.")

    code_side("aggs", "Aggregation", "Aggregate (group) functions",
              """SELECT SUM(salary), MAX(salary),
       MIN(salary), AVG(salary)
FROM   employee;

SELECT COUNT(*)           AS employees,
       COUNT(super_ssn)   AS with_supervisor,
       COUNT(DISTINCT dno) AS departments
FROM   employee;

SELECT COUNT(*)
FROM   employee e
JOIN   department d ON d.dnumber = e.dno
WHERE  d.dname = 'Research';""",
              [card(None, body="Aggregates take **many rows** and return **one value** per group: COUNT, SUM, AVG, MIN, MAX.", size=26),
               callout("They **ignore NULLs**: COUNT(*) counts rows, COUNT(col) counts non-null values. AVG(commission) ignores employees with no commission.", size=26)],
              size=24)

    code_result("groupby", "Aggregation", "GROUP BY",
                """SELECT   dno,
         COUNT(*)    AS employees,
         AVG(salary) AS avg_salary
FROM     employee
GROUP BY dno;""",
                ["dno", "employees", "avg_salary"], [["5", "4", "33250"], ["4", "3", "31000"], ["1", "1", "55000"]],
                intro="For each department: its number, how many employees, and their average salary.",
                notes="Rule: every column in SELECT must be either in GROUP BY or inside an aggregate. Result values are from the COMPANY sample data in Elmasri & Navathe.")

    code_side("having", "Aggregation", "HAVING filters groups",
              """-- projects with more than two employees
SELECT   p.pnumber, p.pname, COUNT(*) AS staff
FROM     project  p
JOIN     works_on w ON w.pno = p.pnumber
GROUP BY p.pnumber, p.pname
HAVING   COUNT(*) > 2
ORDER BY p.pnumber;""",
              [table(["WHERE", "HAVING"], [["Filters **rows**", "Filters **groups**"], ["Before grouping", "After grouping"], ["No aggregates", "Uses aggregates"]], size=26),
               callout("Put conditions that don't need an aggregate in **WHERE**: fewer rows to group.", tone="blue", size=24)])

    code_result("window", "Aggregation", "Window functions: aggregates without collapsing rows",
                """SELECT dno, fname, salary,
       RANK() OVER (PARTITION BY dno
                    ORDER BY salary DESC) AS rank_in_dept,
       AVG(salary) OVER (PARTITION BY dno) AS dept_avg
FROM   employee;""",
                ["dno", "fname", "salary", "rank", "dept_avg"],
                [["5", "Franklin", "40000", "1", "33250"], ["5", "Ramesh", "38000", "2", "33250"], ["5", "John", "30000", "3", "33250"],
                 ["4", "Jennifer", "43000", "1", "31000"]],
                intro="Keep every employee row **and** show their rank and the department average.",
                notes="New slide: window functions (OVER, PARTITION BY) are standard SQL supported by all major DBMSs. GROUP BY would return one row per department; a window keeps one row per employee.")

    # ---------------- 08 security, views, indexes ----------------
    d.divider("d8", "08", "Security, views & indexes", "Control access, simplify queries and speed up searches.")

    code_side("dcl", "DCL", "GRANT and REVOKE",
              """GRANT SELECT ON employee TO ahmed;
GRANT ALL    ON department TO mary, ahmed;
GRANT SELECT ON employee TO ahmed WITH GRANT OPTION;

REVOKE UPDATE ON department FROM mary;
REVOKE ALL    ON department FROM mary, ahmed;

-- roles group privileges
CREATE ROLE hr_reader;
GRANT SELECT ON employee TO hr_reader;
GRANT hr_reader TO ahmed;""",
              [card(None, body="**Privileges**: SELECT, INSERT, UPDATE, DELETE, REFERENCES, ALL.", size=26),
               callout("**WITH GRANT OPTION** lets the receiver grant the privilege to others.", tone="blue", size=26),
               callout("Grant to **roles**, not individual users: easier to manage.", size=26)],
              size=24,
              notes="Modernized: the original wrote GRANT SELECT ON TABLE employees; the TABLE keyword is optional in most DBMSs. Roles are new.")

    d.slide("views", "Views", "Views: virtual tables",
            row(card("What a view is", size=28, items=["A **stored SELECT** with a name", "Contains **no data** of its own", "Based on **base tables** (or other views)",
                                                      "Queried like a table"]),
                card("Why use views", tone="blue", size=28, items=["**Restrict access**: show only some columns or rows", "**Simplify** complex joins for users",
                                                                   "**Data independence**: apps survive table changes", "**Different views** of the same data per user group"])),
            notes="Views are the main tool for the external level of the three-schema architecture (Lesson 1) and for logical data independence.")

    d.slide("viewtypes", "Views", "Simple vs complex views",
            table(["Feature", "Simple view", "Complex view"],
                  [["Number of tables", "One", "One or more"], ["Contains functions", "No", "Yes"], ["Contains groups of data", "No", "Yes"],
                   ["DML through the view", "Yes", "Not always"]], widths=[40, 30, 30], size=28)
            + callout("You can INSERT, UPDATE or DELETE through a simple view; complex views (joins, GROUP BY, DISTINCT, aggregates) are usually **read-only**.", tone="blue"))

    code_side("createview", "Views", "Create, query, change, drop",
              """CREATE VIEW vw_work_hrs AS
SELECT e.fname, e.lname, p.pname, w.hours
FROM   employee e
JOIN   works_on w ON w.essn = e.ssn
JOIN   project  p ON p.pnumber = w.pno;

SELECT fname, lname, hours FROM vw_work_hrs;

CREATE OR REPLACE VIEW vw_work_hrs AS
SELECT ... WHERE e.dno = 5;   -- Oracle, PostgreSQL, MySQL
-- SQL Server: CREATE OR ALTER VIEW

DROP VIEW vw_work_hrs;""",
              [card("Syntax", body="CREATE VIEW name [(columns)] AS subquery [WITH CHECK OPTION];", size=26)],
              size=24)

    code_side("checkoption", "Views", "WITH CHECK OPTION",
              """CREATE VIEW v_supplier AS
SELECT *
FROM   suppliers
WHERE  status > 15
WITH CHECK OPTION;

-- rejected: the new row would disappear from the view
UPDATE v_supplier SET status = 10 WHERE s_id = 'S1';""",
              [card(None, body="INSERTs and UPDATEs through the view must produce rows that **still satisfy** the view's WHERE (status > 15).", size=28)])

    d.slide("indexes", "Indexes", "Indexes",
            row(col(card(None, size=28, items=["Speed up finding rows that match a **search condition**", "Can cover **one or several** columns",
                                               "Created by you, or **automatically** for PRIMARY KEY and UNIQUE", "Used and maintained by the DBMS"]), flex="1"),
                col(p("Index on City → rows of SUPPLIER", size=24, color=MUTED, extra="font-weight:600"),
                    row(table(["City (sorted)"], [["Athens"], ["London"], ["London"], ["Paris"], ["Paris"]], size=24),
                        table(["S#", "Name", "Status", "City"], [["S1", "Smith", "20", "London"], ["S2", "Jones", "10", "Paris"], ["S3", "Blake", "30", "Paris"],
                                                                 ["S4", "Clark", "20", "London"], ["S5", "Adams", "30", "Athens"]], size=24), gap=24), gap=12, flex="1"), gap=40),
            notes="Like the index at the back of a book: sorted keys with pointers to the rows, so the DBMS doesn't scan the whole table.")

    d.slide("indexrules", "Indexes", "When to create an index",
            row(card("Create an index when", tone="blue", size=26, items=["The column has a **wide range** of values",
                                                                          "The column has **many NULLs** and you search the non-null values",
                                                                          "Columns are often used **together** in WHERE or JOIN",
                                                                          "The table is **large** and most queries return **< 2–4%** of rows"]),
                card("Avoid an index when", tone="accent", size=26, items=["The table is **small**",
                                                                           "The column is rarely used in conditions",
                                                                           "Most queries return **> 2–4%** of rows",
                                                                           "The table is **updated very often**",
                                                                           "The column is used inside an **expression** (unless function-based)"]))
            + callout("Every INSERT, UPDATE and DELETE must also update every index. **More indexes is not always better.**", size=26),
            notes="Fixed: in the original slide, the four 'create an index when' rules were listed under 'Do not create an index when'. The notes had them right. To enforce uniqueness, define a UNIQUE constraint; a unique index is then created automatically.")

    code_side("createindex", "Indexes", "Creating and removing indexes",
              """CREATE INDEX emp_salary_idx ON employee (salary);

-- composite: helps WHERE dno = ? AND lname = ?
CREATE INDEX emp_dno_lname_idx ON employee (dno, lname);

CREATE UNIQUE INDEX emp_email_uq ON employee (email);

DROP INDEX emp_salary_idx;            -- Oracle, PostgreSQL
DROP INDEX emp_salary_idx ON employee; -- SQL Server, MySQL""",
              [callout("Column order matters in a composite index: it helps queries on **dno** or **dno + lname**, not on lname alone.", tone="blue", size=26),
               callout("Check whether a query uses an index with **EXPLAIN** (PostgreSQL, MySQL) or the execution plan (Oracle, SQL Server).", size=26)],
              size=24)

    d.statement("statement", "Write SQL that says **what** you want, test it on a **SELECT** first, and wrap changes in a **transaction**.")

    d.takeaways("recap", [
        "SQL has four families: **DDL, DML, DCL, TCL**; transactions give ACID guarantees.",
        "Constraints (PK, FK, UNIQUE, NOT NULL, CHECK) belong **in the table definition**.",
        "UPDATE and DELETE without WHERE affect **every row**: test first.",
        "Use **ANSI JOIN … ON**; outer joins keep unmatched rows with NULLs.",
        "WHERE filters rows, **HAVING** filters groups; windows keep rows.",
        "Views simplify and secure; indexes speed reads but cost writes."])

    d.exercises("practice", "Practice: Lesson 4 (COMPANY database)", [
        ("Core", "List the names of employees in department 5 who earn between 30,000 and 40,000, highest first."),
        ("Core", "For each project: its name, number of employees and total hours. Only projects with total hours > 50."),
        ("Core", "List every department with its manager's name, including departments with **no** manager."),
        ("Stretch", "Find employees who earn more than the **average of their own department** (CTE or correlated subquery)."),
        ("Stretch", "Find employees who work on **every** project controlled by department 5 (NOT EXISTS twice)."),
        ("Challenge", "Give a 10% raise to employees in Research inside a transaction, verify the result, then ROLLBACK.")])

    d.resources("study", "Go deeper: Lesson 4", [
        ("Practice", "SQLBolt", "short interactive lessons with exercises", "https://sqlbolt.com/"),
        ("Practice", "PostgreSQL Exercises", "graded query exercises on a real schema", "https://pgexercises.com/"),
        ("Tutorial", "Mode SQL Tutorial", "from basics to window functions", "https://mode.com/sql-tutorial/"),
        ("Docs", "PostgreSQL docs: SQL language", "the reference for every statement", "https://www.postgresql.org/docs/current/sql.html"),
        ("Docs", "Microsoft T-SQL reference", "SQL Server syntax and examples", "https://learn.microsoft.com/en-us/sql/t-sql/language-reference"),
        ("Read", "Use The Index, Luke", "how indexes really work, free online", "https://use-the-index-luke.com/")])

    return d
