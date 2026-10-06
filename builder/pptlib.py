"""PowerPoint backend for the lesson builders, styled on the ITI "Lesson 3 Enhanced" template.

Exposes the same API as lib.py (card, row, table, code_block, ERD, Deck, ...), but every call
returns a layout node instead of HTML. Deck.write() lays the nodes out on the template's
20" x 11.25" canvas (1920 x 1080 px, 1 px = 9525 EMU) and saves a .pptx.

build_pptx.py imports the lesson modules with this module installed as `lib`.
"""
import copy
import math
import re

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Pt

# ---- template palette (from the Lesson 3 Enhanced deck) ----
PAPER = PAPER2 = CARD = "#FFFFFF"
SOFT = "#F8FAFC"
LINE = "#E2E8F0"
INK = "#0F172A"
BODY = "#334155"
MUTED = "#64748B"
FAINT = "#94A3B8"
ACCENT = ACCENT_FILL = "#C8102E"
ACCENT_TINT = "#FDECEF"
ACCENT_ON_INK = "#F87171"
BLUE = "#0E8A8A"
BLUE_TINT = "#E6F4F4"
AMBER, AMBER_TINT = "#B45309", "#FEF3C7"
ON_INK, ON_INK_MUTED = "#FFFFFF", "#CBD5E1"
CODE_BG, CODE_TEXT, CODE_KW, CODE_STR, CODE_CM = SOFT, INK, BLUE, AMBER, MUTED

DISPLAY = "Arial"
SANS = "Calibri"
MONO = "Courier New"
PAD = ""

EMU = 9525
FS = 0.92         # body text scale relative to the web decks
LEFT, RIGHT, WIDTH = 96, 1824, 1728
BOTTOM = 1016
LECTURER = ("Lecturer: Rana Salah", "rsalah@mcit.gov.eg · Room 3005")
CREDITS = ("Based on original slides by", "Shahinaz S. Azab · edited by Mona Saleh · Rana Salah")

EM = {SANS: 0.46, DISPLAY: 0.49, MONO: 0.6}


def rgb(h):
    return RGBColor.from_string(h.lstrip("#").upper())


def esc(s):
    return s


# ---------------------------------------------------------------- markup
def runs_of(text):
    """`code`, **bold**, *italic* -> [(text, {b, i, code})]."""
    out = []
    pos = 0
    pat = re.compile(r"`(.+?)`|\*\*(.+?)\*\*|(?<![\w*])\*(?![\s)])(.+?)\*(?!\w)")
    for m in pat.finditer(text):
        if m.start() > pos:
            out.append((text[pos:m.start()], {}))
        if m.group(1) is not None:
            out.append((m.group(1), {"code": True}))
        elif m.group(2) is not None:
            for t, f in runs_of(m.group(2)):
                out.append((t, dict(f, b=True)))
        else:
            out.append((m.group(3), {"i": True}))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], {}))
    return out


def plain(text):
    return "".join(t for t, _ in runs_of(text))


def text_lines(text, font, sz, w):
    """Estimated wrapped line count for one paragraph."""
    if w <= 0:
        return 1
    width = 0.0
    for t, f in runs_of(text):
        em = EM[MONO] if f.get("code") or font == MONO else EM.get(font, 0.52)
        if f.get("b"):
            em *= 1.06
        width += len(t) * em * sz
    return max(1, math.ceil(width * 1.05 / w))


def set_run(run, text, size, color, font, bold=False, italic=False, underline=False, code=False):
    run.text = text
    f = run.font
    f.size = Pt(size * 0.75)
    f.bold = bold
    f.italic = italic
    f.underline = underline
    f.color.rgb = rgb(color)
    f.name = MONO if code else font


def add_runs(par, text, size, color, font, bold=False, italic=False, code_color=None, underline=False):
    for t, f in runs_of(text):
        set_run(par.add_run(), t, size, (code_color or color) if f.get("code") else color, font,
                bold=bold or f.get("b", False), italic=italic or f.get("i", False), underline=underline,
                code=f.get("code", False))


def textbox(slide, x, y, w, h, name=None):
    tb = slide.shapes.add_textbox(Emu(int(x * EMU)), Emu(int(y * EMU)), Emu(int(max(w, 4) * EMU)), Emu(int(max(h, 4) * EMU)))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.auto_size = None
    if name:
        tb.name = name
    return tb, tf


def set_bullet(par, kind, sz, n=1):
    pPr = par._p.get_or_add_pPr()
    ind = int(sz * 1.1 * EMU)
    pPr.set("marL", str(ind))
    pPr.set("indent", str(-ind))
    for tag in ("a:buNone", "a:buChar", "a:buAutoNum"):
        for e in pPr.findall(qn(tag)):
            pPr.remove(e)
    if kind == "num":
        el = etree.SubElement(pPr, qn("a:buAutoNum"))
        el.set("type", "arabicPeriod")
    else:
        el = etree.SubElement(pPr, qn("a:buChar"))
        el.set("char", "•")


def _drop_style(shp):
    """Remove the theme style reference (it adds a drop shadow and theme colors)."""
    st = shp._element.find(qn("p:style"))
    if st is not None:
        shp._element.remove(st)


def rect(slide, x, y, w, h, fill=None, line=None, line_w=1, dash=False, shape=MSO_SHAPE.RECTANGLE, double=False, radius=None):
    shp = slide.shapes.add_shape(shape, Emu(int(x * EMU)), Emu(int(y * EMU)), Emu(int(max(w, 1) * EMU)), Emu(int(max(h, 1) * EMU)))
    if fill:
        shp.fill.solid()
        shp.fill.fore_color.rgb = rgb(fill)
    else:
        shp.fill.background()
    if line:
        shp.line.color.rgb = rgb(line)
        shp.line.width = Emu(int(line_w * EMU))
        if dash:
            shp.line.dash_style = MSO_LINE_DASH_STYLE.DASH
        if double:
            shp.line._get_or_add_ln().set("cmpd", "dbl")
    else:
        shp.line.fill.background()
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        shp.adjustments[0] = min(0.5, radius / max(1, min(w, h)))
    _drop_style(shp)
    tf = shp.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return shp


def connector(slide, x1, y1, x2, y2, color=INK, width=3, head="none", dash=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Emu(int(x1 * EMU)), Emu(int(y1 * EMU)), Emu(int(x2 * EMU)), Emu(int(y2 * EMU)))
    _drop_style(c)
    c.line.color.rgb = rgb(color)
    c.line.width = Emu(int(width * EMU))
    if dash:
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    if head in ("end", "both"):
        ln = c.line._get_or_add_ln()
        t = etree.SubElement(ln, qn("a:tailEnd"))
        t.set("type", "triangle")
        if head == "both":
            h = etree.SubElement(ln, qn("a:headEnd"))
            h.set("type", "triangle")
    return c


# ---------------------------------------------------------------- nodes
class Node:
    flex = "1"
    width = None
    pin = False

    def __add__(self, other):
        return Stack.join(self, other)

    def __radd__(self, other):
        return Stack.join(other, self)

    def measure(self, w, s):
        return 0

    def draw(self, sl, x, y, w, h, s):
        pass


class Stack(Node):
    def __init__(self, items, gap=None):
        self.items, self.gap = items, gap

    @staticmethod
    def join(a, b):
        items = []
        for z in (a, b):
            if z is None or (isinstance(z, str) and z == ""):
                continue
            if isinstance(z, str):
                raise TypeError(f"raw HTML reached the PowerPoint backend: {z[:60]}")
            if isinstance(z, Stack) and z.gap is None:
                items.extend(z.items)
            else:
                items.append(z)
        return Stack(items)

    def flow(self):
        return [i for i in self.items if not i.pin]

    def measure(self, w, s, gap=32):
        g = self.gap if self.gap is not None else gap
        f = self.flow()
        return sum(i.measure(w, s) for i in f) + g * s * max(0, len(f) - 1)

    def draw(self, sl, x, y, w, h, s, gap=32):
        g = self.gap if self.gap is not None else gap
        cy = y
        for i in self.items:
            if i.pin:
                i.draw(sl, 0, 0, 0, 0, 1)
                continue
            ih = i.measure(w, s)
            i.draw(sl, x, cy, w, ih, s)
            cy += ih + g * s


def flatten(children):
    out = []
    for c in children:
        if c is None or (isinstance(c, str) and c == ""):
            continue
        if isinstance(c, str):
            raise TypeError(f"raw HTML reached the PowerPoint backend: {c[:60]}")
        out.append(c)
    return out


class Text(Node):
    def __init__(self, paras, size=30, color=BODY, font=SANS, bold=False, italic=False, align="left",
                 line=1.3, bullet=None, upper=False, para_gap=0.35, code_color=INK, spacing=0):
        self.paras = paras if isinstance(paras, list) else [paras]
        self.size, self.color, self.font, self.bold, self.italic = size, color, font, bold, italic
        self.align, self.line, self.bullet, self.upper = align, line, bullet, upper
        self.para_gap, self.code_color, self.spacing = para_gap, code_color, spacing

    def sz(self, s, w=None):
        sz = max(17, self.size * FS * s)
        if w:
            words = [x for p_ in self.paras for x in plain(p_).split()]
            if words:
                longest = max(len(x) for x in words)
                em = EM.get(self.font, 0.5) * (1.08 if self.bold else 1.0)
                cap = (w - (sz * 1.1 if self.bullet else 0)) / (longest * em * 1.08)
                sz = min(sz, max(14, cap))
        return sz

    def measure(self, w, s):
        sz = self.sz(s, w)
        ind = sz * 1.1 if self.bullet else 0
        n = sum(text_lines(p_.upper() if self.upper else p_, self.font, sz, w - ind) for p_ in self.paras)
        return n * sz * self.line + (len(self.paras) - 1) * sz * self.para_gap + sz * 0.15

    def draw(self, sl, x, y, w, h, s):
        sz = self.sz(s, w)
        _, tf = textbox(sl, x, y, w, max(h, self.measure(w, s)))
        tf.vertical_anchor = MSO_ANCHOR.TOP
        for k, ptext in enumerate(self.paras):
            par = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            par.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}[self.align]
            par.line_spacing = self.line * 0.86
            if k:
                par.space_before = Pt(sz * self.para_gap * 0.75)
            if self.bullet:
                set_bullet(par, self.bullet, sz)
            add_runs(par, ptext.upper() if self.upper else ptext, sz, self.color, self.font, self.bold, self.italic,
                     code_color=self.code_color)
            if self.spacing:
                for r in par.runs:
                    r.font._rPr.set("spc", str(int(self.spacing * 100)))


class Spacer(Node):
    def __init__(self, h):
        self.h = h

    def measure(self, w, s):
        return self.h * s


TONES = {
    None: (CARD, LINE, INK, BODY),
    "card": (CARD, LINE, INK, BODY),
    "accent": (ACCENT_TINT, "#F5C2CB", ACCENT, BODY),
    "blue": (BLUE_TINT, "#B7DCDC", BLUE, BODY),
    "ink": (INK, INK, ON_INK, ON_INK_MUTED),
    "amber": (AMBER_TINT, "#F3D58A", AMBER, BODY),
}


class Box(Node):
    """A bordered container holding a vertical stack of nodes."""

    def __init__(self, children, tone=None, flex="1", pad=32, gap=12, header=None):
        self.children = flatten(children)
        self.tone, self.flex, self.pad, self.gap, self.header = tone, flex, pad, gap, header

    def inner(self, w, s):
        return w - 2 * self.pad * s

    def measure(self, w, s):
        iw = self.inner(w, s)
        h = sum(c.measure(iw, s) for c in self.children) + self.gap * s * max(0, len(self.children) - 1)
        return h + 2 * self.pad * s

    def draw(self, sl, x, y, w, h, s):
        bg, bd, _, _ = TONES.get(self.tone, TONES[None])
        rect(sl, x, y, w, h, fill=bg, line=bd, line_w=1.5)
        cy = y + self.pad * s
        iw = self.inner(w, s)
        for c in self.children:
            ch = c.measure(iw, s)
            c.draw(sl, x + self.pad * s, cy, iw, ch, s)
            cy += ch + self.gap * s


def card(title, body=None, items=None, tone="card", size=26, title_size=36, flex="1", icon=None, tag=None):
    _, _, tc, bc = TONES.get(tone, TONES[None])
    kids = []
    if tag:
        kids.append(Text(tag, size=24, color=ACCENT if tone != "ink" else ACCENT_ON_INK, font=DISPLAY, bold=True))
    if title:
        kids.append(Text(title, size=min(title_size, 34), color=tc, font=DISPLAY, bold=True, line=1.2))
    if body:
        kids.append(Text(body, size=size, color=bc, code_color=tc if tone != "card" else INK))
    if items:
        kids.append(Text(items, size=size, color=bc, bullet="dot", para_gap=0.25))
    return Box(kids, tone=tone, flex=flex, pad=30, gap=12)


def pill(text, color=ACCENT, bg=ACCENT_TINT):
    return Text(text, size=24, color=color, font=DISPLAY, bold=True)


class Row(Node):
    def __init__(self, children, gap=24, align="stretch"):
        self.children, self.gap, self.align = flatten(children), gap, align

    def _flex_widths(self, w, s):
        g = self.gap * s * max(0, len(self.children) - 1)
        fixed = sum(c.width for c in self.children if c.width)
        flexes = [float(str(c.flex).split()[0]) if not c.width else 0 for c in self.children]
        tot = sum(flexes) or 1
        free = max(0, w - g - fixed)
        return [c.width if c.width else free * f / tot for c, f in zip(self.children, flexes)]

    def widths(self, w, s):
        ws = self._flex_widths(w, s)
        # tables never get narrower than their longest words need; take the room from the others
        need = [c.min_width(s) if hasattr(c, "min_width") else 0 for c in self.children]
        short = sum(max(0, n - x) for n, x in zip(need, ws))
        if short > 0:
            spare = [x if not n and not c.width else 0 for c, x, n in zip(self.children, ws, need)]
            tot = sum(spare) or 1
            ws = [max(n, x) if n else x - short * sp / tot
                  for c, x, n, sp in zip(self.children, ws, need, spare)]
        return ws

    def measure(self, w, s):
        return max([c.measure(cw, s) for c, cw in zip(self.children, self.widths(w, s))] + [0])

    def draw(self, sl, x, y, w, h, s):
        cx = x
        for c, cw in zip(self.children, self.widths(w, s)):
            ch = c.measure(cw, s)
            if self.align == "center" or isinstance(c, Arrow):
                c.draw(sl, cx, y + (h - ch) / 2, cw, ch, s)
            else:
                c.draw(sl, cx, y, cw, h if isinstance(c, (Box, Col)) else ch, s)
            cx += cw + self.gap * s


def row(*children, gap=24, align="stretch"):
    return Row(children, gap=gap, align=align)


class Col(Node):
    def __init__(self, children, gap=24, flex="1"):
        self.children, self.gap, self.flex = flatten(children), gap, flex

    def measure(self, w, s):
        return sum(c.measure(w, s) for c in self.children) + self.gap * s * max(0, len(self.children) - 1)

    def draw(self, sl, x, y, w, h, s):
        cy = y
        for c in self.children:
            ch = c.measure(w, s)
            c.draw(sl, x, cy, w, ch, s)
            cy += ch + self.gap * s


def _col_min_width(self, s):
    return max([c.min_width(s) for c in self.children if hasattr(c, "min_width")] + [0])


Col.min_width = _col_min_width


def col(*children, gap=24, flex="1"):
    return Col(children, gap=gap, flex=flex)


class Grid(Node):
    def __init__(self, children, cols=3, gap=24):
        self.children, self.cols, self.gap = flatten(children), cols, gap

    def rows(self):
        return [self.children[i:i + self.cols] for i in range(0, len(self.children), self.cols)]

    def cw(self, w, s):
        return (w - self.gap * s * (self.cols - 1)) / self.cols

    def measure(self, w, s):
        cw = self.cw(w, s)
        rs = self.rows()
        return sum(max(c.measure(cw, s) for c in r) for r in rs) + self.gap * s * max(0, len(rs) - 1)

    def draw(self, sl, x, y, w, h, s):
        cw = self.cw(w, s)
        cy = y
        for r in self.rows():
            rh = max(c.measure(cw, s) for c in r)
            for k, c in enumerate(r):
                c.draw(sl, x + k * (cw + self.gap * s), cy, cw, rh, s)
            cy += rh + self.gap * s


def grid(children, cols=3, gap=24):
    return Grid(children, cols=cols, gap=gap)


def _cell_border(cell, color=LINE, w=1):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        ln = etree.SubElement(tcPr, qn(tag))
        ln.set("w", str(int(w * EMU)))
        sf = etree.SubElement(ln, qn("a:solidFill"))
        c = etree.SubElement(sf, qn("a:srgbClr"))
        c.set("val", color.lstrip("#"))


class Table(Node):
    def __init__(self, headers, rows, widths=None, size=26):
        self.headers, self.rows = headers, [[str(c) for c in r] for r in rows]
        n = len(headers)
        self.pct = widths or [100 / n] * n
        self.size = size
        self.flex = str(max(1.0, n * 0.7))  # beside other nodes, a table takes space by its column count

    def sz(self, s):
        return max(17, self.size * FS * s)

    def min_width(self, s):
        sz = self.sz(s)
        tot = 0
        for k, p_ in enumerate(self.pct):
            words = [x for r in [self.headers] + self.rows for x in plain(r[k]).split()] or [""]
            col_need = max(len(x) for x in words) * EM[SANS] * 1.15 * sz + sz * 1.2
            tot = max(tot, col_need / (p_ / 100))
        return tot

    def row_heights(self, w, s):
        sz = self.sz(s)
        out = []
        for r, is_head in [(self.headers, True)] + [(r, False) for r in self.rows]:
            lines = 1
            for c, p_ in zip(r, self.pct):
                cw = w * p_ / 100 - sz * 1.0
                lines = max(lines, text_lines(c, DISPLAY if is_head else SANS, sz, cw))
            out.append(lines * sz * 1.22 + sz * 0.75)
        return out

    def measure(self, w, s):
        return sum(self.row_heights(w, s))

    def draw(self, sl, x, y, w, h, s):
        sz = self.sz(s)
        hs = self.row_heights(w, s)
        gf = sl.shapes.add_table(len(hs), len(self.headers), Emu(int(x * EMU)), Emu(int(y * EMU)),
                                 Emu(int(w * EMU)), Emu(int(sum(hs) * EMU)))
        tbl = gf.table
        tblPr = tbl._tbl.tblPr
        for a in ("bandRow", "firstRow"):
            tblPr.set(a, "0")
        sid = tblPr.find(qn("a:tableStyleId"))
        if sid is not None:
            sid.text = "{5940675A-B579-460E-94D1-54222C63F5DA}"  # "No Style, Table Grid"
        for k, p_ in enumerate(self.pct):
            tbl.columns[k].width = Emu(int(w * p_ / 100 * EMU))
        for ri, (r, rh) in enumerate(zip([self.headers] + self.rows, hs)):
            tbl.rows[ri].height = Emu(int(rh * EMU))
            for ci, txt in enumerate(r):
                cell = tbl.cell(ri, ci)
                cell.fill.solid()
                cell.fill.fore_color.rgb = rgb(INK if ri == 0 else (CARD if ri % 2 else SOFT))
                cell.margin_left = cell.margin_right = Emu(int(sz * 0.5 * EMU))
                cell.margin_top = cell.margin_bottom = Emu(int(sz * 0.3 * EMU))
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                par = cell.text_frame.paragraphs[0]
                add_runs(par, txt, sz, ON_INK if ri == 0 else BODY, DISPLAY if ri == 0 else SANS, bold=ri == 0)
                _cell_border(cell)


def table(headers, rows, widths=None, size=26, underline_cols=()):
    return Table(headers, rows, widths, size)


SQL_KW = set("""SELECT FROM WHERE AND OR NOT IN IS NULL AS ON JOIN INNER LEFT RIGHT FULL OUTER CROSS
GROUP BY HAVING ORDER ASC DESC DISTINCT INSERT INTO VALUES UPDATE SET DELETE CREATE TABLE ALTER DROP
TRUNCATE ADD COLUMN CONSTRAINT PRIMARY KEY FOREIGN REFERENCES UNIQUE CHECK DEFAULT INDEX VIEW REPLACE
WITH OPTION GRANT REVOKE TO ALL ANY EXISTS BETWEEN LIKE UNION INTERSECT EXCEPT MINUS CASE WHEN THEN ELSE
END BEGIN COMMIT ROLLBACK SAVEPOINT TRANSACTION COUNT SUM AVG MIN MAX OVER PARTITION RANK DENSE_RANK
ROW_NUMBER LIMIT FETCH FIRST ROWS ONLY OFFSET CASCADE RESTRICT ROLE IF RECURSIVE NUMBER INT INTEGER
VARCHAR CHAR DATE DECIMAL NUMERIC SMALLINT BIGINT BOOLEAN TIMESTAMP TEXT FLOAT LAG LEAD COALESCE
SCHEMA AUTHORIZATION USER USING NATURAL CURRENT_DATE WORK SERIAL IDENTITY GENERATED ALWAYS VARCHAR2
NVARCHAR TIME TYPE MODIFY TOP""".split())


def sql_tokens(line):
    out = []
    for t in re.findall(r"--.*$|'[^']*'?|\"[^\"]*\"|\d+(?:\.\d+)?|[A-Za-z_][A-Za-z0-9_#]*|\s+|.", line):
        if t.startswith("--"):
            out.append((t, CODE_CM, False, True))
        elif t.startswith("'") or re.fullmatch(r"\d+(?:\.\d+)?", t):
            out.append((t, CODE_STR, False, False))
        elif t.upper() in SQL_KW and re.fullmatch(r"[A-Za-z_]+", t):
            out.append((t, CODE_KW, True, False))
        else:
            out.append((t, CODE_TEXT, False, False))
    return out


class Code(Node):
    def __init__(self, code, size=26, flex=None, width=None, plain=False):
        self.lines = code.strip("\n").split("\n")
        longest = max(len(l) for l in self.lines)
        self.size, self.width, self.plain = size, width, plain
        # beside other nodes, code takes room in proportion to its longest line
        self.flex = flex if flex not in (None, "1") else str(max(1.0, longest / 24))
        self.pad = 28

    def sz(self, w, s):
        sz = max(16, self.size * FS * s)
        longest = max(len(l) for l in self.lines)
        avail = w - 2 * self.pad
        if longest * 0.6 * sz > avail:
            sz = max(14, avail / (longest * 0.6 * 1.02))
        return sz

    def measure(self, w, s):
        return len(self.lines) * self.sz(w, s) * 1.32 + 2 * self.pad

    def draw(self, sl, x, y, w, h, s):
        sz = self.sz(w, s)
        rect(sl, x, y, w, max(h, self.measure(w, s)), fill=CODE_BG, line=LINE, line_w=1.5)
        _, tf = textbox(sl, x + self.pad, y + self.pad, w - 2 * self.pad, len(self.lines) * sz * 1.32)
        tf.word_wrap = False
        for k, ln in enumerate(self.lines):
            par = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            par.line_spacing = 1.1
            lead = len(ln) - len(ln.lstrip(" "))
            body = ln[lead:]
            if lead:
                set_run(par.add_run(), " " * lead, sz, CODE_TEXT, MONO)
            toks = [(body, CODE_TEXT, False, False)] if self.plain else sql_tokens(body)
            for t, c, b, i in toks:
                set_run(par.add_run(), t, sz, c, MONO, bold=b, italic=i)
            if not ln.strip():
                set_run(par.add_run(), " ", sz, CODE_TEXT, MONO)


def code_block(code, size=26, flex=None, width=None, plain=False):
    c = Code(code, size, flex, None, plain)
    if width:
        c.width = width
    return c


class Callout(Node):
    def __init__(self, text, tone="accent", label=None, size=28):
        self.text, self.tone, self.label, self.size = text, tone, label, size

    def colors(self):
        return (AMBER_TINT, AMBER) if self.tone == "accent" else (BLUE_TINT, BLUE)

    def body(self):
        t = Text(self.text, size=self.size, color=INK)
        return t

    def measure(self, w, s):
        lab = (self.label + " ") if self.label else ""
        return Text(lab + self.text, size=self.size).measure(w - 64 * s, s) + 40 * s

    def draw(self, sl, x, y, w, h, s):
        bg, fg = self.colors()
        rect(sl, x, y, w, h, fill=bg)
        rect(sl, x, y, 5, h, fill=fg)
        _, tf = textbox(sl, x + 32 * s, y + 20 * s, w - 64 * s, h - 40 * s)
        par = tf.paragraphs[0]
        par.line_spacing = 1.12
        sz = max(17, self.size * FS * s)
        if self.label:
            set_run(par.add_run(), self.label + " ", sz, fg, DISPLAY, bold=True)
        add_runs(par, self.text, sz, INK, SANS)


def callout(text, tone="accent", label=None, size=28):
    return Callout(text, tone, label, size)


def p(text, size=30, color=BODY, extra="", raw=False):
    return Text(text, size=size, color=color, bold="font-weight:600" in extra, upper="uppercase" in extra,
                font=DISPLAY if "font-weight:600" in extra else SANS)


def ul(items, size=30, color=BODY, gap=None):
    return Text(items, size=size, color=color, bullet="dot", para_gap=0.25)


def ol(items, size=30, color=BODY):
    return Text(items, size=size, color=color, bullet="num", para_gap=0.25)


def eyebrow(text):
    return Text(text, size=22, color=ACCENT, font=DISPLAY, bold=True, upper=True, spacing=1)


def box(children, tone=None, flex="1", pad="24px 32px", gap=8):
    return Box(children, tone=tone, flex=flex, pad=26, gap=gap)


class SchemaLine(Node):
    def __init__(self, name, cols, size=28):
        self.name, self.cols, self.size = name, cols, size

    def parts(self):
        out = [(self.name, INK, True), ("(", MUTED, False)]
        for k, c in enumerate(self.cols):
            pk = c.startswith("_") and c.endswith("_")
            c = c[1:-1] if pk else c
            fk = c.endswith("*")
            c = c[:-1] if fk else c
            tag = " (PK, FK)" if pk and fk else " (PK)" if pk else " (FK)" if fk else ""
            color = BLUE if fk else ACCENT if pk else INK
            out.append((c + tag + ("," if k < len(self.cols) - 1 else ""), color, pk or fk))
        out.append((")", MUTED, False))
        return out

    def text(self):
        return " ".join(t for t, _, _ in self.parts())

    def measure(self, w, s):
        sz = max(16, self.size * FS * 0.92 * s)
        return math.ceil(len(self.text()) * 0.6 * sz * 1.04 / w) * sz * 1.3 + 4

    def draw(self, sl, x, y, w, h, s):
        sz = max(16, self.size * FS * 0.92 * s)
        _, tf = textbox(sl, x, y, w, h)
        par = tf.paragraphs[0]
        par.line_spacing = 1.1
        for k, (t, c, b) in enumerate(self.parts()):
            set_run(par.add_run(), (" " if k else "") + t, sz, c, MONO, bold=b)


def schema_line(name, cols, size=28):
    return SchemaLine(name, cols, size)


class KeyLegend(Node):
    def measure(self, w, s):
        return 24 * FS * s * 1.4

    def draw(self, sl, x, y, w, h, s):
        sz = max(17, 24 * FS * s)
        _, tf = textbox(sl, x, y, w, h)
        par = tf.paragraphs[0]
        for t, c, f in (("col (PK)", ACCENT, MONO), (" = primary key   ·   ", MUTED, SANS), ("col (FK)", BLUE, MONO), (" = foreign key", MUTED, SANS)):
            set_run(par.add_run(), t, sz, c, f, bold=f == MONO)


def key_legend():
    return KeyLegend()


class Arrow(Node):
    width = 64

    def measure(self, w, s):
        return 40

    def draw(self, sl, x, y, w, h, s):
        rect(sl, x + 8, y + h / 2 - 20, 48, 40, fill=LINE, shape=MSO_SHAPE.RIGHT_ARROW)


def arrow_right():
    return Arrow()


# ---- absolutely positioned pieces (canvas px) ----
class Pin(Node):
    pin = True


class PinText(Pin):
    def __init__(self, x, y, w, text, size=24, color=BODY, bold=False, italic=False, align="left", font=None, underline=False):
        self.a = (x, y, w)
        self.t = Text(text, size=size, color=color or BODY, bold=bold, italic=italic, align=align,
                      font=font if font in (MONO, DISPLAY) else SANS)

    def draw(self, sl, *_):
        x, y, w = self.a
        self.t.draw(sl, x, y, w, self.t.measure(w, 1), 1)


def pin_text(x, y, w, text, size=24, color=None, bold=False, italic=False, align="left", font=None, underline=False):
    return PinText(x, y, w, text, size, color, bold, italic, align, font, underline)


class PinBox(Pin):
    def __init__(self, x, y, w, h, fill, border, dashed, radius, border_w, text, text_size, text_color, font, underline):
        self.args = (x, y, w, h, fill, border, dashed, radius, border_w, text, text_size, text_color, font, underline)

    def draw(self, sl, *_):
        x, y, w, h, fill, border, dashed, radius, bw, text, ts, tc, font, ul_ = self.args
        shp = rect(sl, x, y, w, h, fill=fill, line=border, line_w=bw, dash=dashed,
                   shape=MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE, radius=radius)
        if text is not None:
            tf = shp.text_frame
            tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            par = tf.paragraphs[0]
            par.alignment = PP_ALIGN.CENTER
            set_run(par.add_run(), text, ts * FS, tc or INK, font if font in (MONO, DISPLAY) else SANS, underline=ul_, bold=ul_)


def pin_box(x, y, w, h, fill=None, border=None, dashed=False, radius=0, border_w=2, text=None, text_size=24,
            text_color=None, font=None, underline=False):
    return PinBox(x, y, w, h, fill, border, dashed, radius, border_w, text, text_size, text_color, font, underline)


class PinConn(Pin):
    def __init__(self, *a):
        self.a = a

    def draw(self, sl, *_):
        x1, y1, x2, y2, head, color, width = self.a
        connector(sl, x1, y1, x2, y2, color=color or INK, width=width, head=head)


def pin_conn(x1, y1, x2, y2, head="none", color=None, width=3):
    return PinConn(x1, y1, x2, y2, head, color, width)


class PinBlock(Pin):
    def __init__(self, x, y, w, node):
        self.x, self.y, self.w, self.node = x, y, w, node

    def draw(self, sl, *_):
        self.node.draw(sl, self.x, self.y, self.w, self.node.measure(self.w, 1), 1)


def pin_block(x, y, w, content):
    return PinBlock(x, y, w, content)


# ---------------------------------------------------------------- ERD (Chen notation)
class ERDNode(Pin):
    def __init__(self, ops):
        self.ops = ops

    def draw(self, sl, *_):
        for order in (0, 1, 2):
            for o, fn in self.ops:
                if o == order:
                    fn(sl)


class ERD:
    def __init__(self):
        self.ops = []

    def entity(self, cx, cy, label, w=260, h=88, weak=False, size=28):
        def f(sl):
            shp = rect(sl, cx - w / 2, cy - h / 2, w, h, fill=CARD, line=INK, line_w=7 if weak else 2.5, double=weak)
            self._label_in(shp, label, size, INK, bold=True, font=DISPLAY)
        self.ops.append((1, f))
        return (cx, cy, w, h)

    def rel(self, cx, cy, label, w=240, h=120, ident=False, size=24):
        def f(sl):
            shp = rect(sl, cx - w / 2, cy - h / 2, w, h, fill=ACCENT_TINT, line=ACCENT, line_w=7 if ident else 2.5,
                       double=ident, shape=MSO_SHAPE.DIAMOND)
            self._label_in(shp, label, size, INK, bold=True, font=DISPLAY, room=w * 0.78)
        self.ops.append((1, f))

    def attr(self, cx, cy, label, w=180, h=64, kind="plain", size=24):
        def f(sl):
            shp = rect(sl, cx - w / 2, cy - h / 2, w, h, fill=BLUE_TINT, line=BLUE, line_w=6 if kind == "multi" else 2,
                       dash=kind == "derived", double=kind == "multi", shape=MSO_SHAPE.OVAL)
            self._label_in(shp, label, size, INK, underline=kind == "key", room=w * 0.86)
        self.ops.append((1, f))

    def line(self, x1, y1, x2, y2, double=False, color=INK, head="none", dashed=False):
        def f(sl):
            if not double:
                connector(sl, x1, y1, x2, y2, color=color, width=2.5, head=head, dash=dashed)
            else:
                dx, dy = x2 - x1, y2 - y1
                L = math.hypot(dx, dy) or 1
                ox, oy = -dy / L * 5, dx / L * 5
                for sgn in (1, -1):
                    connector(sl, x1 + sgn * ox, y1 + sgn * oy, x2 + sgn * ox, y2 + sgn * oy, color=color, width=2.5)
        self.ops.append((0, f))

    def text(self, cx, cy, t, size=26, color=INK, w=80, bold=True):
        def f(sl):
            node = Text(t, size=size, color=color, bold=bold, align="center", font=DISPLAY if bold else SANS)
            hh = node.measure(w, 1)
            node.draw(sl, cx - w / 2, cy - hh / 2, w, hh, 1)
        self.ops.append((2, f))

    @staticmethod
    def _label_in(shp, label, size, color, bold=False, font=SANS, underline=False, room=None):
        """Single-line label centred on the shape, shrunk until it fits `room` px."""
        w = shp.width / EMU
        room = room or (w - 16)
        em = EM.get(font, 0.5) * (1.08 if bold else 1.0)
        sz = min(size * FS, room / (max(1, len(label)) * em * 1.05))
        tf = shp.text_frame
        tf.word_wrap = False
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        par = tf.paragraphs[0]
        par.alignment = PP_ALIGN.CENTER
        set_run(par.add_run(), label, sz, color, font, bold=bold, underline=underline)

    def html(self):
        return ERDNode(self.ops)


def schema_dummy():
    pass


# ---------------------------------------------------------------- deck
class SlideSpec:
    def __init__(self, kind, sid, **kw):
        self.kind, self.sid, self.kw = kind, sid, kw


class Deck:
    closing = None      # (eyebrow, title_plain, title_hl, title_rest, text) set by build_pptx
    lecturer = None     # overrides LECTURER for one deck
    cover_split = None  # (plain, highlighted)

    def __init__(self, lesson_no, short, title):
        self.n, self.short, self.title = lesson_no, short, title
        self.specs = []
        self.sections = []
        self._pending = None

    def _add(self, spec):
        if self._pending:
            self.sections.append((self._pending, spec.sid))
            self._pending = None
        self.specs.append(spec)

    def section_start(self, desc):
        self._pending = desc

    # -- templates, same signatures as lib.Deck --
    def cover(self, sid, title, subtitle, topics, notes=""):
        self._add(SlideSpec("cover", sid, title=title, subtitle=subtitle, topics=topics, notes=notes))

    def divider(self, sid, num, title, desc, notes=""):
        self._pending = (num, title, desc)
        self._add(SlideSpec("divider", sid, num=num, title=title, desc=desc, notes=notes))

    def slide(self, sid, eyebrow_, title, body, notes="", bg=PAPER, gap=40):
        self._add(SlideSpec("content", sid, eyebrow=eyebrow_, title=title, body=body, notes=notes, gap=gap))

    def statement(self, sid, text, sub="", notes=""):
        self._add(SlideSpec("statement", sid, text=text, sub=sub, notes=notes))

    def diagram(self, sid, eyebrow_, title, erd, caption=None, notes="", side=None):
        body = erd.html()
        if caption:
            body = body + pin_text(LEFT, 960, WIDTH, caption, 24, MUTED)
        if side:
            body = body + side
        self.slide(sid, eyebrow_, title, body, notes=notes)

    def takeaways(self, sid, items, notes=""):
        self._add(SlideSpec("takeaways", sid, items=items, notes=notes))

    def exercises(self, sid, title, items, notes="", eyebrow="Practice · optional"):
        kids = []
        for i, (lvl, txt) in enumerate(items):
            c = {"Core": BLUE, "Stretch": ACCENT, "Challenge": INK}[lvl]
            kids.append(Box([Text(f"Q{i + 1} · {lvl}", size=24, color=c, font=DISPLAY, bold=True, upper=True),
                             Text(txt, size=26, color=INK)], pad=28, gap=10))
        self.slide(sid, eyebrow, title, grid(kids, cols=3 if len(items) % 3 == 0 else 2, gap=24), notes=notes)

    def resources(self, sid, title, items, notes=""):
        self._add(SlideSpec("resources", sid, title=title, items=items, notes=notes))

    def thanks(self, sid="thanks", notes=""):
        self._add(SlideSpec("thanks", sid, notes=notes))

    def _thanks(self, sl):
        bg = sl.background.fill
        bg.solid()
        bg.fore_color.rgb = rgb(INK)
        Text("ITI · Database Fundamentals", size=30 / FS, color=ACCENT_ON_INK, font=DISPLAY, bold=True, upper=True,
             align="center").draw(sl, LEFT, 400, WIDTH, 44, 1)
        Text("Thank You !", size=140 / FS, color=ON_INK, font=DISPLAY, bold=True, align="center", line=1).draw(sl, LEFT, 470, WIDTH, 180, 1)

    # -- drawing --
    def _frame(self, sl, eyebrow_, title, num, total):
        eb = (eyebrow_ or "").upper()
        ebw = min(900, len(eb) * 0.6 * 22 * 0.95 + 20)
        Text(eb, size=22 / FS, color=ACCENT, font=DISPLAY, bold=True).draw(sl, LEFT, 90, ebw + 40, 32, 1)
        connector(sl, LEFT + ebw + 48, 103, 1735, 103, color=LINE, width=2)
        Text(f"{num:02d}/{total:02d}", size=24 / FS, color=FAINT, font=MONO, align="right").draw(sl, 1712, 88, 112, 36, 1)
        t = Text(title, size=54 / FS, color=INK, font=DISPLAY, bold=True, line=1.12)
        th = t.measure(WIDTH, 1)
        t.draw(sl, LEFT, 140, WIDTH, th, 1)
        return 140 + th

    def _content(self, sl, sp, num, total):
        top = self._frame(sl, sp.kw["eyebrow"], sp.kw["title"], num, total) + 52
        body = sp.kw["body"]
        if not isinstance(body, Stack):
            body = Stack([body])
        gap = min(40, sp.kw.get("gap", 40)) * 0.85
        avail = BOTTOM - top
        s = 1.0
        for s in (1.4, 1.3, 1.22, 1.15, 1.08, 1.0, 0.94, 0.88, 0.82, 0.76, 0.7, 0.65, 0.6):
            if body.measure(WIDTH, s, gap) <= avail:
                break
        body.draw(sl, LEFT, top, WIDTH, avail, s, gap)

    def _cover(self, sl, sp):
        rect(sl, LEFT, 88, 14, 52, fill=ACCENT)
        Text(f"ITI · Database Fundamentals · Lesson {self.n}", size=24 / FS, color=MUTED, font=DISPLAY, bold=True,
             upper=True).draw(sl, 130, 100, 1400, 36, 1)
        plain_, hl = self.cover_split or ("", sp.kw["title"])
        _, tf = textbox(sl, LEFT, 330, 1728, 300)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        par = tf.paragraphs[0]
        par.line_spacing = 0.95
        sz = 120 if len(plain_ + hl) <= 22 else 100 if len(plain_ + hl) <= 30 else 84
        if plain_:
            set_run(par.add_run(), plain_, sz, INK, DISPLAY, bold=True)
        set_run(par.add_run(), hl, sz, ACCENT, DISPLAY, bold=True)
        Text(sp.kw["subtitle"], size=34 / FS, color=BODY).draw(sl, LEFT, 650, 1500, 60, 1)
        lect = self.lecturer or LECTURER
        Text(lect[0], size=26 / FS, color=INK, font=DISPLAY, bold=True).draw(sl, LEFT, 932, 900, 36, 1)
        Text(lect[1], size=26 / FS, color=BODY).draw(sl, LEFT, 974, 900, 36, 1)
        Text(CREDITS[0], size=24 / FS, color=MUTED, align="right").draw(sl, 924, 938, 900, 34, 1)
        Text(CREDITS[1], size=24 / FS, color=BODY, align="right").draw(sl, 924, 976, 900, 34, 1)

    def _agenda(self, sl, num, total):
        self._frame(sl, f"{num:02d} · Agenda", "What this lesson covers", num, total)
        secs = self.sections
        half = math.ceil(len(secs) / 2) if len(secs) > 4 else len(secs)
        colw = (WIDTH - 80) / (2 if len(secs) > 4 else 1)
        for k, ((nn, title, desc), _) in enumerate(secs):
            c, r = (k // half, k % half)
            x = LEFT + c * (colw + 80)
            y = 300 + r * 150
            Text(nn, size=30 / FS, color=ACCENT, font=DISPLAY, bold=True).draw(sl, x, y, 70, 40, 1)
            Text(title, size=32 / FS, color=INK, font=DISPLAY, bold=True).draw(sl, x + 80, y, colw - 80, 44, 1)
            Text(desc, size=24 / FS, color=MUTED).draw(sl, x + 80, y + 48, colw - 80, 70, 1)
            connector(sl, x, y + 132, x + colw, y + 132, color=LINE, width=1.5)

    def _divider(self, sl, sp, num, total):
        Text(f"Section {sp.kw['num']}", size=24 / FS, color=ACCENT, font=DISPLAY, bold=True, upper=True).draw(sl, LEFT, 90, 600, 34, 1)
        connector(sl, LEFT + 260, 103, 1735, 103, color=LINE, width=2)
        Text(f"{num:02d}/{total:02d}", size=24 / FS, color=FAINT, font=MONO, align="right").draw(sl, 1712, 88, 112, 36, 1)
        Text(sp.kw["num"], size=200 / FS, color=ACCENT, font=DISPLAY, bold=True, line=1).draw(sl, LEFT, 300, 600, 240, 1)
        Text(sp.kw["title"], size=84 / FS, color=INK, font=DISPLAY, bold=True, line=1.05).draw(sl, LEFT, 560, 1600, 200, 1)
        Text(sp.kw["desc"], size=32 / FS, color=BODY).draw(sl, LEFT, 760, 1400, 120, 1)

    def _dark(self, sl, eyebrow_, big, sub, footer_left="ITI · Database Fundamentals", footer_right="Thank you — questions?", label=None):
        bg = sl.background.fill
        bg.solid()
        bg.fore_color.rgb = rgb(INK)
        Text(eyebrow_, size=24 / FS, color=ACCENT_ON_INK, font=DISPLAY, bold=True, upper=True).draw(sl, LEFT, 90, 800, 34, 1)
        connector(sl, LEFT + min(800, len(eyebrow_) * 15 + 40), 101, 1824, 101, color="#1E293B", width=2)
        y = 330
        if label:
            Text(label, size=26 / FS, color=FAINT, font=DISPLAY, bold=True, upper=True).draw(sl, LEFT, y, 900, 36, 1)
            y += 44
        t = Text(big, size=84 / FS, color=ON_INK, font=DISPLAY, bold=True, line=1.02)
        th = t.measure(1500, 1)
        _, tf = textbox(sl, LEFT, y, 1500, th)
        par = tf.paragraphs[0]
        par.line_spacing = 0.9
        for txt, f in runs_of(big):
            set_run(par.add_run(), txt, 84, ACCENT_ON_INK if (f.get("b") or f.get("code")) else ON_INK, DISPLAY, bold=True)
        if sub:
            _, tf2 = textbox(sl, LEFT, y + th + 60, 1300, 140)
            par2 = tf2.paragraphs[0]
            par2.line_spacing = 1.2
            for txt, f in runs_of(sub):
                set_run(par2.add_run(), txt, 32, "#5EEAD4" if f.get("code") else ON_INK_MUTED, MONO if f.get("code") else SANS,
                        bold=f.get("b", False))
        Text(footer_left, size=24 / FS, color=FAINT).draw(sl, LEFT, 976, 800, 34, 1)
        Text(footer_right, size=24 / FS, color=FAINT, align="right").draw(sl, 1024, 976, 800, 34, 1)

    def _takeaways(self, sl, sp, num, total):
        self._frame(sl, f"{num:02d} · Recap", "What to walk out remembering", num, total)
        items = sp.kw["items"]
        y = 300
        rh = min(108, (BOTTOM - 300) / len(items))
        for k, t in enumerate(items):
            Text(f"{k + 1:02d}", size=30 / FS, color=ACCENT, font=DISPLAY, bold=True).draw(sl, LEFT, y + 18, 80, 40, 1)
            Text(t, size=30 / FS, color=INK).draw(sl, LEFT + 90, y + 18, WIDTH - 90, rh - 24, 1)
            connector(sl, LEFT, y + rh, RIGHT, y + rh, color=LINE, width=1.5)
            y += rh

    def _resources(self, sl, sp, num, total):
        self._frame(sl, f"{num:02d} · Study more", sp.kw["title"], num, total)
        items = sp.kw["items"]
        y = 300
        rh = min(118, (BOTTOM - 300) / len(items))
        for kind, name, why, url in items:
            Text(kind, size=22 / FS, color=ACCENT, font=DISPLAY, bold=True, upper=True).draw(sl, LEFT, y + 22, 200, 34, 1)
            _, tf = textbox(sl, LEFT + 220, y + 16, WIDTH - 220, rh - 20)
            par = tf.paragraphs[0]
            set_run(par.add_run(), name, 28, INK, DISPLAY, bold=True)
            add_runs(par, " — " + why, 26, BODY, SANS)
            if url:
                par2 = tf.add_paragraph()
                r = par2.add_run()
                set_run(r, url.replace("https://", "").rstrip("/"), 24, BLUE, MONO)
                r.hyperlink.address = url
            connector(sl, LEFT, y + rh, RIGHT, y + rh, color=LINE, width=1.5)
            y += rh

    def write(self, out_path, template):
        prs = Presentation(template)
        lst = prs.slides._sldIdLst
        for sld in list(lst):
            prs.part.drop_rel(sld.get(qn("r:id")))
            lst.remove(sld)
        layout = prs.slide_layouts[0]
        # cover, agenda, ... , closing
        order = [self.specs[0], SlideSpec("agenda", "agenda")] + self.specs[1:]
        thanks = [sp for sp in order if sp.kind == "thanks"]
        order = [sp for sp in order if sp.kind != "thanks"]
        if self.closing:
            order.append(SlideSpec("closing", "closing"))
        order += thanks
        total = len(order)
        for num, sp in enumerate(order, 1):
            sl = prs.slides.add_slide(layout)
            for ph in list(sl.placeholders):
                ph._element.getparent().remove(ph._element)
            k = sp.kind
            if k == "cover":
                self._cover(sl, sp)
            elif k == "agenda":
                self._agenda(sl, num, total)
            elif k == "divider":
                self._divider(sl, sp, num, total)
            elif k == "content":
                self._content(sl, sp, num, total)
            elif k == "statement":
                self._dark(sl, "Key idea", sp.kw["text"], sp.kw["sub"], footer_right=f"Lesson {self.n} · {self.short}")
            elif k == "takeaways":
                self._takeaways(sl, sp, num, total)
            elif k == "resources":
                self._resources(sl, sp, num, total)
            elif k == "closing":
                eb, label, big, sub = self.closing
                self._dark(sl, eb, big, sub, label=label)
            elif k == "thanks":
                self._thanks(sl)
            notes = sp.kw.get("notes", "") if hasattr(sp, "kw") else ""
            if notes and notes.strip():
                sl.notes_slide.notes_text_frame.text = notes.strip()
        prs.save(out_path)
        return total


class PinEllipse(Pin):
    def __init__(self, *a):
        self.a = a

    def draw(self, sl, *_):
        x, y, w, h, fill, border, bw, dashed = self.a
        rect(sl, x, y, w, h, fill=fill, line=border, line_w=bw, dash=dashed, shape=MSO_SHAPE.OVAL)


def pin_ellipse(x, y, w, h, fill=None, border=None, border_w=3, dashed=False):
    return PinEllipse(x, y, w, h, fill, border, border_w, dashed)
