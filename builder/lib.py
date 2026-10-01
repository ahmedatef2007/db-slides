"""Slide builder for the Database Fundamentals course decks.

Each lesson module builds a Deck from the templates below and writes
`<out>/project/deck.json` + `<out>/project/slides/<id>.html` in the Slides
artifact format (1920x1080 sections, inline styles only). Colors and type
come from the "Database Course" design system (design-system/project/tokens.json).
"""
import html
import json
import os
import re

# ---- design tokens (mirrors design-system/project/tokens.json) ----
PAPER, PAPER2, CARD, LINE = "#F7F5F0", "#EDE9DF", "#FFFDF8", "#DDD6C8"
INK, BODY, MUTED = "#14213D", "#3F4A5C", "#5F6879"
ACCENT, ACCENT_FILL, ACCENT_TINT, ACCENT_ON_INK = "#B04A17", "#E07A3F", "#FCEBDD", "#F2A65A"
BLUE, BLUE_TINT = "#2B5FB4", "#E6EEFA"
ON_INK, ON_INK_MUTED = "#F7F5F0", "#B9C3D6"
CODE_BG, CODE_TEXT, CODE_KW, CODE_STR, CODE_CM = "#1B2638", "#E8ECF2", "#F2A65A", "#9FD0F5", "#94A0B4"

DISPLAY = "'Space Grotesk', Arial, sans-serif"
SANS = "'IBM Plex Sans', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Courier New', monospace"

FACES = {
    "space-grotesk": {"family": "Space Grotesk",
                      "href": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400..700&display=swap"},
    "ibm-plex-sans": {"family": "IBM Plex Sans",
                      "href": "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&display=swap"},
    "jetbrains-mono": {"family": "JetBrains Mono",
                       "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"},
}

DS_URL = "https://claude.ai/artifact/WdbVXkRa43NmX6n2AKuXTF"
DS_VERSION = "1790852595-4915"
DS_FOLDER = "databasecourse"

PAD = "padding:128px 128px 160px"


def esc(s):
    return html.escape(s, quote=False)


def attr(s):
    return html.escape(s, quote=True)


# ---- inline mini-markup for prose: **bold**, `sql`, *italic* ----
def md(s, code_color=None):
    code_color = code_color or BLUE
    s = esc(s)
    codes = []

    def keep(m):
        codes.append(m.group(1))
        return f"\x00{len(codes) - 1}\x00"
    s = re.sub(r"`(.+?)`", keep, s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?![\s)])(.+?)\*(?!\w)", r"<i>\1</i>", s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: f'<span style="color:{code_color}"><b>{codes[int(m.group(1))]}</b></span>', s)
    return s


def md_on_ink(s):
    return md(s, code_color=ACCENT_ON_INK)


# ---- SQL highlighting ----
SQL_KW = set("""SELECT FROM WHERE AND OR NOT IN IS NULL AS ON JOIN INNER LEFT RIGHT FULL OUTER CROSS
GROUP BY HAVING ORDER ASC DESC DISTINCT INSERT INTO VALUES UPDATE SET DELETE CREATE TABLE ALTER DROP
TRUNCATE ADD COLUMN CONSTRAINT PRIMARY KEY FOREIGN REFERENCES UNIQUE CHECK DEFAULT INDEX VIEW REPLACE
WITH OPTION GRANT REVOKE TO ALL ANY EXISTS BETWEEN LIKE UNION INTERSECT EXCEPT MINUS CASE WHEN THEN ELSE
END BEGIN COMMIT ROLLBACK SAVEPOINT TRANSACTION COUNT SUM AVG MIN MAX OVER PARTITION RANK DENSE_RANK
ROW_NUMBER LIMIT FETCH FIRST ROWS ONLY OFFSET CASCADE RESTRICT ROLE IF RECURSIVE NUMBER INT INTEGER
VARCHAR CHAR DATE DECIMAL NUMERIC SMALLINT BIGINT BOOLEAN TIMESTAMP TEXT FLOAT LAG LEAD COALESCE
NOT_NULL SCHEMA AUTHORIZATION USER USING NATURAL CURRENT_DATE TRANSACTION WORK SERIAL IDENTITY
GENERATED ALWAYS VARCHAR2 NVARCHAR TIME""".split())


def hl_line(line):
    """Highlight one line of SQL; returns HTML (leading spaces kept as nbsp)."""
    out = []
    lead = len(line) - len(line.lstrip(" "))
    out.append("&#160;" * lead)
    rest = line[lead:]
    tokens = re.findall(r"--.*$|'[^']*'?|\"[^\"]*\"|\d+(?:\.\d+)?|[A-Za-z_][A-Za-z0-9_#]*|\s+|.", rest)
    for t in tokens:
        if t.startswith("--"):
            out.append(f'<span style="color:{CODE_CM}">{esc(t)}</span>')
        elif t.startswith("'") or re.fullmatch(r"\d+(?:\.\d+)?", t):
            out.append(f'<span style="color:{CODE_STR}">{esc(t)}</span>')
        elif t.upper() in SQL_KW and re.fullmatch(r"[A-Za-z_]+", t):
            out.append(f'<span style="color:{CODE_KW}">{esc(t)}</span>')
        elif t.isspace():
            # keep runs of spaces visible inside code
            out.append(" " if len(t) == 1 else "&#160;" * (len(t) - 1) + " ")
        else:
            out.append(esc(t))
    return "".join(out) or "&#160;"


def code_block(code, size=26, flex=None, width=None, plain=False):
    lines = code.strip("\n").split("\n")
    rows = []
    for ln in lines:
        body = esc(ln).replace("  ", "&#160; ") if plain else hl_line(ln)
        rows.append(f'<p style="font-family:{MONO};font-size:{size}px;line-height:1.5;color:{CODE_TEXT};white-space:nowrap">{body}</p>')
    st = f"background:{CODE_BG};border-radius:16px;padding:36px 40px;display:flex;flex-direction:column;gap:0px"
    if flex:
        st += f";flex:{flex}"
    if width:
        st += f";width:{width}px;flex:none"
    return f'<div style="{st}">' + "".join(rows) + "</div>"


# ---- building blocks ----
def heading(eyebrow, title, on_ink=False, size=64):
    ec = ACCENT_ON_INK if on_ink else ACCENT
    tc = ON_INK if on_ink else INK
    eb = (f'<p style="font-family:{SANS};font-size:24px;font-weight:600;letter-spacing:2px;'
          f'text-transform:uppercase;color:{ec}">{esc(eyebrow)}</p>') if eyebrow else ""
    return (f'<div style="display:flex;flex-direction:column;gap:12px">{eb}'
            f'<h2 style="font-family:{DISPLAY};font-size:{size}px;font-weight:600;line-height:1.15;color:{tc}">{md(title)}</h2></div>')


def p(text, size=30, color=BODY, extra="", raw=False):
    return f'<p style="font-size:{size}px;line-height:1.45;color:{color}{";" + extra if extra else ""}">{text if raw else md(text)}</p>'


def ul(items, size=30, color=BODY, gap=None):
    lis = "".join(f"<li>{md(i)}</li>" for i in items)
    return f'<ul style="font-size:{size}px;line-height:1.5;color:{color}">{lis}</ul>'


def ol(items, size=30, color=BODY):
    lis = "".join(f"<li>{md(i)}</li>" for i in items)
    return f'<ol style="font-size:{size}px;line-height:1.5;color:{color}">{lis}</ol>'


def card(title, body=None, items=None, tone="card", size=26, title_size=36, flex="1", icon=None, tag=None):
    bg, border, tc = CARD, LINE, INK
    if tone == "accent":
        bg, border, tc = ACCENT_TINT, "#F0C9AC", ACCENT
    elif tone == "blue":
        bg, border, tc = BLUE_TINT, "#C3D3EE", BLUE
    elif tone == "ink":
        bg, border, tc = INK, INK, ON_INK
    bc = ON_INK_MUTED if tone == "ink" else BODY
    inner = ""
    if icon or tag:
        row = ""
        if icon:
            row += f'<x-icon name="{icon}" style="color:{ACCENT if tone != "ink" else ACCENT_ON_INK};width:48px;height:48px"></x-icon>'
        if tag:
            row += pill(tag)
        inner += f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center">{row}</div>'
    if title:
        inner += f'<h3 style="font-family:{DISPLAY};font-size:{title_size}px;font-weight:600;line-height:1.2;color:{tc}">{md(title)}</h3>'
    if body:
        mk = md_on_ink if tone == "ink" else md
        inner += f'<p style="font-size:{size}px;line-height:1.4;color:{bc}">{mk(body)}</p>'
    if items:
        inner += f'<ul style="font-size:{size}px;line-height:1.45;color:{bc}">' + "".join(f"<li>{md(i)}</li>" for i in items) + "</ul>"
    fl = f"flex:{flex};" if flex else ""
    return (f'<div style="{fl}display:flex;flex-direction:column;gap:12px;background:{bg};'
            f'padding:36px;border:1px solid {border};border-radius:16px">{inner}</div>')


def pill(text, color=ACCENT, bg=ACCENT_TINT):
    return (f'<p style="font-size:24px;font-weight:600;color:{color};background:{bg};padding:6px 18px;'
            f'border-radius:999px;white-space:nowrap">{esc(text)}</p>')


def row(*children, gap=24, align="stretch"):
    return f'<div style="display:flex;flex-direction:row;gap:{gap}px;align-items:{align}">' + "".join(children) + "</div>"


def col(*children, gap=24, flex="1"):
    return f'<div style="flex:{flex};display:flex;flex-direction:column;gap:{gap}px">' + "".join(children) + "</div>"


def grid(children, cols=3, gap=24):
    return (f'<div style="display:grid;grid-template-columns:repeat({cols}, 1fr);gap:{gap}px">'
            + "".join(children) + "</div>")


def table(headers, rows, widths=None, size=26, underline_cols=()):
    n = len(headers)
    widths = widths or [round(100 / n)] * n
    h = "".join(f'<th style="width:{w}%">{md(c)}</th>' for c, w in zip(headers, widths))
    out = [f'<tr style="background:{PAPER2}">{h}</tr>']
    for r in rows:
        cells = []
        for i, c in enumerate(r):
            cells.append(f"<td>{md(str(c))}</td>")
        out.append(f'<tr style="background:{CARD}">' + "".join(cells) + "</tr>")
    return (f'<table style="font-family:{SANS};font-size:{size}px;color:{BODY};border:1px solid {LINE};'
            f'border-radius:8px">' + "".join(out) + "</table>")


def callout(text, tone="accent", label=None, size=28):
    bg, bd, lc = (ACCENT_TINT, "#F0C9AC", ACCENT) if tone == "accent" else (BLUE_TINT, "#C3D3EE", BLUE)
    lab = f'<b><span style="color:{lc}">{esc(label)}</span></b> ' if label else ""
    return (f'<div style="background:{bg};border:1px solid {bd};border-radius:16px;padding:24px 32px">'
            f'<p style="font-size:{size}px;line-height:1.45;color:{BODY}">{lab}{md(text)}</p></div>')


def schema_line(name, cols, size=28):
    """Relation schema like EMPLOYEE(<u>SSN</u>, Name, DNO→DEPARTMENT). Use _x_ for PK, x* for FK."""
    parts = []
    for c in cols:
        pk = c.startswith("_") and c.endswith("_")
        if pk:
            c = c[1:-1]
        fk = c.endswith("*")
        if fk:
            c = c[:-1]
        t = esc(c)
        if fk:
            t = f'<span style="color:{BLUE}"><i>{t}</i></span>'
        if pk:
            t = f"<u><b>{t}</b></u>"
        parts.append(t)
    return (f'<p style="font-family:{MONO};font-size:{size}px;line-height:1.5;color:{BODY}">'
            f'<b><span style="color:{INK}">{esc(name)}</span></b> ( ' + ", ".join(parts) + " )</p>")


# ---- ERD drawing (Chen notation), pinned to the slide canvas ----
class ERD:
    def __init__(self):
        self.lines, self.shapes, self.labels = [], [], []

    def entity(self, cx, cy, label, w=260, h=88, weak=False, size=28):
        border = f"8px double {INK}" if weak else f"3px solid {INK}"
        self.shapes.append(
            f'<div style="position:absolute;left:{cx - w // 2}px;top:{cy - h // 2}px;width:{w}px;height:{h}px;'
            f'background:{CARD};border:{border};display:flex;align-items:center;justify-content:center">'
            f'<p style="font-family:{DISPLAY};font-size:{size}px;font-weight:600;color:{INK};text-align:center">{esc(label)}</p></div>')
        return (cx, cy, w, h)

    def rel(self, cx, cy, label, w=240, h=120, ident=False, size=24):
        border = f"8px double {ACCENT}" if ident else f"3px solid {ACCENT}"
        self.shapes.append(
            f'<x-shape kind="diamond" style="position:absolute;left:{cx - w // 2}px;top:{cy - h // 2}px;width:{w}px;height:{h}px;'
            f'background:{ACCENT_TINT};border:{border}"></x-shape>')
        self._label(cx, cy, label, w - 40, size, INK, bold=True)

    def attr(self, cx, cy, label, w=180, h=64, kind="plain", size=24):
        border = {"plain": f"2px solid {BLUE}", "key": f"2px solid {BLUE}", "multi": f"6px double {BLUE}",
                  "derived": f"2px dashed {BLUE}", "composite": f"2px solid {BLUE}"}[kind]
        self.shapes.append(
            f'<x-shape kind="ellipse" style="position:absolute;left:{cx - w // 2}px;top:{cy - h // 2}px;width:{w}px;height:{h}px;'
            f'background:{BLUE_TINT};border:{border}"></x-shape>')
        self._label(cx, cy, label, w - 16, size, INK, underline=(kind == "key"))

    def line(self, x1, y1, x2, y2, double=False, color=INK, head="none", dashed=False):
        dash = ";border-style:dashed" if dashed else ""
        if not double:
            self.lines.append(f'<x-connector x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" head="{head}" '
                              f'style="color:{color};border-width:3px{dash}"></x-connector>')
        else:
            # two parallel lines offset perpendicular to the segment
            import math
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy) or 1
            ox, oy = -dy / L * 5, dx / L * 5
            for s in (1, -1):
                self.lines.append(f'<x-connector x1="{round(x1 + s * ox)}" y1="{round(y1 + s * oy)}" '
                                  f'x2="{round(x2 + s * ox)}" y2="{round(y2 + s * oy)}" head="none" '
                                  f'style="color:{color};border-width:3px"></x-connector>')

    def text(self, cx, cy, t, size=26, color=INK, w=80, bold=True):
        self._label(cx, cy, t, w, size, color, bold=bold)

    def _label(self, cx, cy, t, w, size, color, bold=False, underline=False):
        inner = esc(t)
        if underline:
            inner = f"<u>{inner}</u>"
        if bold:
            inner = f"<b>{inner}</b>"
        top = round(cy - size * 0.68)
        self.labels.append(
            f'<p style="position:absolute;left:{round(cx - w / 2)}px;top:{top}px;width:{round(w)}px;'
            f'font-family:{SANS};font-size:{size}px;line-height:1.3;color:{color};text-align:center">{inner}</p>')

    def html(self):
        return "".join(self.lines + self.shapes + self.labels)


# ---- slide wrapper ----
def section(sid, inner, bg=PAPER, notes="", footer=True, layout=None, transition="fade"):
    layout = layout or f"{PAD};display:flex;flex-direction:column;gap:40px"
    a = f"<aside>{esc(notes.strip())}</aside>" if notes.strip() else ""
    f = "{{FOOTER}}" if footer else ""
    return (f'<section id="{sid}" data-transition="{transition}" style="background:{bg};color:{BODY};'
            f'font-family:{SANS};{layout}">{inner}{f}{a}</section>')


class Deck:
    def __init__(self, lesson_no, short, title):
        self.n, self.short, self.title = lesson_no, short, title
        self.slides = []          # (id, html)
        self.sections = {}        # key -> {description, start}
        self._pending_section = None

    def section_start(self, description):
        self._pending_section = description

    def add(self, sid, html_):
        assert re.fullmatch(r"[A-Za-z0-9_-]{1,64}", sid), sid
        assert sid not in [s for s, _ in self.slides], f"duplicate id {sid}"
        if self._pending_section:
            self.sections[f"s{len(self.sections) + 1}"] = {"description": self._pending_section, "start": sid}
            self._pending_section = None
        self.slides.append((sid, html_))

    # ---------- templates ----------
    def cover(self, sid, title, subtitle, topics, notes=""):
        tps = "".join(
            f'<p style="font-size:26px;color:{ON_INK};border:1px solid #3A4A6B;padding:8px 22px;border-radius:999px;white-space:nowrap">{esc(t)}</p>'
            for t in topics)
        inner = (
            f'<div style="position:absolute;right:0px;top:0px;width:520px;height:1080px;background:#1E2D4F"></div>'
            f'<div style="position:absolute;right:128px;top:128px;width:264px;height:200px;background:{ACCENT_FILL};border-radius:16px"></div>'
            f'<div style="position:absolute;right:0px;top:380px;width:200px;height:240px;background:{BLUE}"></div>'
            f'<p style="position:absolute;right:120px;bottom:96px;width:300px;font-family:{DISPLAY};font-size:400px;font-weight:700;line-height:1;color:#2A3B61;text-align:right">{self.n}</p>'
            f'<div style="display:flex;flex-direction:column;gap:24px;width:1180px">'
            f'<p style="font-size:26px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:{ACCENT_ON_INK}">Database Fundamentals · Lesson {self.n}</p>'
            f'<h1 style="font-family:{DISPLAY};font-size:110px;font-weight:600;line-height:1.02;color:{ON_INK}">{esc(title)}</h1>'
            f'<p style="font-size:36px;line-height:1.4;color:{ON_INK_MUTED}">{esc(subtitle)}</p></div>'
            f'<div style="flex:1"></div>'
            f'<div style="display:flex;flex-direction:row;flex-wrap:wrap;gap:16px;width:1180px">{tps}</div>'
            f'<p style="font-size:24px;color:{ON_INK_MUTED};width:1180px">Original slides by Shahinaz S. Azab · edited by Mona Saleh &amp; Rana Salah (ITI) · revised edition 2026</p>'
        )
        self.add(sid, section(sid, inner, bg=INK, notes=notes, footer=False,
                              layout="padding:128px;display:flex;flex-direction:column;gap:32px"))

    def divider(self, sid, num, title, desc, notes=""):
        self.section_start(desc)
        inner = (
            f'<div style="position:absolute;left:0px;top:0px;width:24px;height:1080px;background:{ACCENT_FILL}"></div>'
            f'<p style="font-family:{DISPLAY};font-size:200px;font-weight:700;line-height:1;color:{ACCENT_ON_INK}">{esc(num)}</p>'
            f'<h2 style="font-family:{DISPLAY};font-size:96px;font-weight:600;line-height:1.05;color:{ON_INK}">{esc(title)}</h2>'
            f'<p style="font-size:36px;line-height:1.4;color:{ON_INK_MUTED};width:1300px">{esc(desc)}</p>')
        self.add(sid, section(sid, inner, bg=INK, notes=notes, footer=False,
                              layout="padding:128px;display:flex;flex-direction:column;justify-content:center;gap:32px"))

    def slide(self, sid, eyebrow, title, body, notes="", bg=PAPER, gap=40):
        self.add(sid, section(sid, heading(eyebrow, title) + body, bg=bg, notes=notes,
                              layout=f"{PAD};display:flex;flex-direction:column;gap:{gap}px"))

    def statement(self, sid, text, sub="", notes=""):
        inner = (f'<h2 style="font-family:{DISPLAY};font-size:84px;font-weight:600;line-height:1.1;color:{INK};width:1500px">{md(text)}</h2>'
                 + (f'<p style="font-size:36px;line-height:1.4;color:{INK};width:1400px">{md(sub)}</p>' if sub else ""))
        self.add(sid, section(sid, inner, bg=ACCENT_FILL, notes=notes, footer=False,
                              layout="padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px"))

    def diagram(self, sid, eyebrow, title, erd, caption=None, notes="", side=None):
        body = erd.html()
        if caption:
            body += (f'<p style="position:absolute;left:128px;bottom:112px;width:1664px;font-size:24px;color:{MUTED}">{md(caption)}</p>')
        if side:
            body += side
        self.slide(sid, eyebrow, title, body, notes=notes)

    def takeaways(self, sid, items, notes=""):
        cards = [card(None, body=t, tag=f"{i + 1:02d}", size=28) for i, t in enumerate(items)]
        cols = 3 if len(items) in (3, 6) else 2
        self.slide(sid, "Recap", "Key takeaways", grid(cards, cols=cols), notes=notes, bg=PAPER2)

    def exercises(self, sid, title, items, notes="", eyebrow="Practice · optional"):
        """items: list of (level, text). level in Core/Stretch/Challenge."""
        colors = {"Core": (BLUE, BLUE_TINT), "Stretch": (ACCENT, ACCENT_TINT), "Challenge": (INK, "#D9DEE8")}
        cards = []
        for i, (lvl, txt) in enumerate(items):
            c, b = colors[lvl]
            cards.append(
                f'<div style="display:flex;flex-direction:column;gap:12px;background:{CARD};padding:28px 32px;border:1px solid {LINE};border-radius:16px">'
                f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center">'
                f'<p style="font-family:{DISPLAY};font-size:32px;font-weight:700;color:{INK}">{i + 1}</p>{pill(lvl, c, b)}</div>'
                f'<p style="font-size:26px;line-height:1.4;color:{BODY}">{md(txt)}</p></div>')
        cols = 2 if len(items) > 3 else len(items)
        self.slide(sid, eyebrow, title, grid(cards, cols=cols, gap=20), notes=notes, bg=PAPER2, gap=32)

    def resources(self, sid, title, items, notes=""):
        """items: list of (kind, name, why, url)."""
        rows = []
        for kind, name, why, url in items:
            link = f'<a href="{attr(url)}">{esc(url.replace("https://", "").rstrip("/"))}</a>' if url else ""
            rows.append(
                f'<div style="display:flex;flex-direction:row;gap:24px;align-items:center;background:{CARD};padding:18px 28px;border:1px solid {LINE};border-radius:16px">'
                f'<p style="font-size:24px;font-weight:600;color:{ACCENT};width:150px;text-transform:uppercase;letter-spacing:1px">{esc(kind)}</p>'
                f'<div style="flex:1;display:flex;flex-direction:column;gap:4px">'
                f'<p style="font-size:28px;line-height:1.3;color:{INK}"><b>{esc(name)}</b> — {md(why)}</p>'
                + (f'<p style="font-size:24px;line-height:1.3;color:{BLUE}">{link}</p>' if link else "")
                + "</div></div>")
        self.slide(sid, "Study more", title, '<div style="display:flex;flex-direction:column;gap:14px">' + "".join(rows) + "</div>",
                   notes=notes, bg=PAPER2, gap=32)

    # ---------- output ----------
    def write(self, out_dir, created_at):
        sd = os.path.join(out_dir, "project", "slides")
        os.makedirs(sd, exist_ok=True)
        for f in os.listdir(sd):
            os.remove(os.path.join(sd, f))
        total = len(self.slides)
        for i, (sid, h) in enumerate(self.slides, 1):
            foot = (f'<p style="position:absolute;left:128px;bottom:64px;width:1200px;font-size:24px;color:{MUTED}">'
                    f'Lesson {self.n} · {esc(self.short)}</p>'
                    f'<p style="position:absolute;right:128px;bottom:64px;width:200px;font-size:24px;color:{MUTED};text-align:right">{i} / {total}</p>')
            h = h.replace("{{FOOTER}}", foot)
            assert h.count("<section") == 1
            with open(os.path.join(sd, f"{sid}.html"), "w") as fh:
                fh.write(h + "\n")
        deck = {
            "v": 4,
            "createdOnFiles": {"v": 1, "at": created_at},
            "lists": "css",
            "title": self.title,
            "cover": self.slides[0][0],
            "order": [s for s, _ in self.slides],
            "sections": self.sections,
            "faces": FACES,
            "designSystems": [{"title": "Database Course", "namespace": DS_FOLDER, "artifact": DS_URL,
                               "version": DS_VERSION, "copiedAt": created_at}],
        }
        with open(os.path.join(out_dir, "project", "deck.json"), "w") as fh:
            json.dump(deck, fh, indent=1, ensure_ascii=False)
        return total
