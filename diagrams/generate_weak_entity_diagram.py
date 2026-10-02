W, H = 1240, 1080
INK = "#1f2937"; MUTED = "#4b5563"; ENT = "#dbeafe"; REL = "#fef3c7"; ACC = "#dc2626"; CARD = "#f8fafc"
FONT = "DejaVu Sans, Arial, sans-serif"
out = []
def line(a, b, double=False, color=INK, w=1.6, dash=None):
    (x1, y1), (x2, y2) = a, b
    d = f' stroke-dasharray="{dash}"' if dash else ""
    if double:
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="6"/>')
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#fff" stroke-width="2"/>')
    else:
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"{d}/>')
def text(x, y, s, size=14, weight="normal", anchor="middle", color=INK, italic=False, under=None):
    st = ' font-style="italic"' if italic else ""
    out.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
               f'text-anchor="{anchor}" dominant-baseline="central" fill="{color}"{st}>{s}</text>')
    if under:
        w = len(s) * size * 0.29
        d = ' stroke-dasharray="4 3"' if under == "partial" else ""
        out.append(f'<line x1="{x-w}" y1="{y+11}" x2="{x+w}" y2="{y+11}" stroke="{INK}" stroke-width="1.4"{d}/>')
def badge(x, y, n):
    out.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{ACC}"/>')
    text(x, y + 1, str(n), 15, "bold", color="#fff")
shapes = []
def entity(name, c, weak=False, w=200, h=56):
    x, y = c
    s = f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="3" fill="{ENT}" stroke="{INK}" stroke-width="2"/>'
    if weak:
        s += f'<rect x="{x-w/2+6}" y="{y-h/2+6}" width="{w-12}" height="{h-12}" rx="2" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    shapes.append((s, (x, y, name, 17, "bold", None)))
def rel(name, c, weak=False, hw=80, hh=44):
    x, y = c
    pts = lambda a, b: f"{x},{y-b} {x+a},{y} {x},{y+b} {x-a},{y}"
    s = f'<polygon points="{pts(hw, hh)}" fill="{REL}" stroke="{INK}" stroke-width="2"/>'
    if weak:
        s += f'<polygon points="{pts(hw-13, hh-7)}" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    shapes.append((s, (x, y, name, 15, "bold", None)))
def attr(name, c, owner, key=None):
    x, y = c
    rx = max(48, len(name) * 5.2 + 20)
    line(c, owner)
    shapes.append((f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="24" fill="#fff" stroke="{INK}" stroke-width="1.6"/>',
                   (x, y, name, 14, "normal", key)))

# ---- title
text(40, 42, "Weak Entity Example: INSTRUCTOR holds OFFICE_HOUR", 24, "bold", "start")
text(40, 74, "OFFICE_HOUR cannot be identified on its own. It borrows its identity from the INSTRUCTOR who owns it.",
     14, anchor="start", color=MUTED)

# ---- ER diagram
diagram_start = len(out)
INS, HOLDS, OH = (250, 270), (590, 270), (930, 270)
line(INS, HOLDS); line(HOLDS, OH, double=True)
entity("INSTRUCTOR", INS); rel("holds", HOLDS, weak=True); entity("OFFICE_HOUR", OH, weak=True)
attr("instructor_id", (250, 145), INS, key="full"); attr("name", (250, 395), INS)
attr("weekday", (850, 145), OH, key="partial"); attr("room", (1020, 145), OH)
attr("start_time", (930, 395), OH, key="partial")
for s, t in shapes:
    out.append(s); text(*t[:3], size=t[3], weight=t[4], under=t[5])
text(420, 250, "1", 18, "bold", color=ACC); text(770, 250, "N", 18, "bold", color=ACC)
text(420, 296, "owner", 12, color=MUTED, italic=True); text(770, 300, "weak", 12, color=MUTED, italic=True)
diagram_end = len(out)
badge(1046, 236, 1); badge(590, 205, 2); badge(712, 300, 3); badge(1022, 418, 4); badge(758, 120, 4)
badge(140, 145, 5)

# ---- explanation cards
cards = [
    (1, "Weak entity (double rectangle)",
     ["OFFICE_HOUR has no key of its own.", "“Monday 10:00” is not unique:",
      "many instructors can hold office", "hours at that time."]),
    (2, "Identifying relationship (double diamond)",
     ["holds links each office hour to", "its owner (identifying) entity,", "INSTRUCTOR. This is what gives", "OFFICE_HOUR its identity."]),
    (3, "Total participation (double line)",
     ["Every OFFICE_HOUR must belong to", "an instructor. It cannot exist", "alone: delete the instructor and", "their office hours go too."]),
    (4, "Partial key (dashed underline)",
     ["weekday + start_time tell apart the", "office hours of the SAME instructor,", "but not across different", "instructors."]),
]
cw, ch, gap, top = 280, 190, 20, 480
for i, (n, title, lines) in enumerate(cards):
    x = 30 + i * (cw + gap)
    out.append(f'<rect x="{x}" y="{top}" width="{cw}" height="{ch}" rx="10" fill="{CARD}" stroke="#cbd5e1"/>')
    out.append(f'<rect x="{x}" y="{top}" width="5" height="{ch}" rx="2" fill="{ACC}"/>')
    badge(x + 32, top + 32, n)
    words = title.split(" (")
    text(x + 56, top + 25, words[0], 15, "bold", "start")
    text(x + 56, top + 44, "(" + words[1], 12, anchor="start", color=MUTED)
    for j, l in enumerate(lines):
        text(x + 22, top + 86 + j * 23, l, 13.5, anchor="start")

# ---- full key
top = 710
out.append(f'<rect x="30" y="{top}" width="560" height="340" rx="10" fill="{CARD}" stroke="#cbd5e1"/>')
out.append(f'<rect x="30" y="{top}" width="5" height="340" rx="2" fill="{ACC}"/>')
badge(62, top + 32, 5)
text(86, top + 32, "The full key of OFFICE_HOUR", 16, "bold", "start")
text(60, top + 78, "Owner's key + partial key:", 14, anchor="start", color=MUTED)
# key equation boxes
def pill(x, y, w, label, fill):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="40" rx="8" fill="{fill}" stroke="{INK}" stroke-width="1.4"/>')
    text(x + w / 2, y + 20, label, 14, "bold")
pill(60, top + 100, 140, "instructor_id", ENT); text(215, top + 120, "+", 20, "bold")
pill(230, top + 100, 110, "weekday", REL); text(355, top + 120, "+", 20, "bold")
pill(370, top + 100, 120, "start_time", REL)
text(130, top + 156, "from INSTRUCTOR", 12, color=MUTED, italic=True)
text(360, top + 156, "partial key of OFFICE_HOUR", 12, color=MUTED, italic=True)
text(60, top + 205, "Relational schema:", 14, anchor="start", color=MUTED)
sx, sy = 60, top + 245
parts = [("OFFICE_HOUR(", None), ("instructor_id", "full"), (", ", None), ("weekday", "full"),
         (", ", None), ("start_time", "full"), (", room)", None)]
for s, k in parts:
    w = len(s) * 8.4
    out.append(f'<text x="{sx}" y="{sy}" font-family="DejaVu Sans Mono, monospace" font-size="14" '
               f'dominant-baseline="central" fill="{INK}" font-weight="{"bold" if k else "normal"}">{s}</text>')
    if k: line((sx, sy + 11), (sx + w, sy + 11), w=1.4)
    sx += w
text(60, top + 290, "instructor_id is also a foreign key → INSTRUCTOR", 13.5, anchor="start")
text(60, top + 314, "(ON DELETE CASCADE matches the total participation).", 13.5, anchor="start", color=MUTED)

# ---- example table
tx, ty = 620, 710
out.append(f'<rect x="{tx}" y="{ty}" width="590" height="340" rx="10" fill="{CARD}" stroke="#cbd5e1"/>')
text(tx + 26, ty + 32, "Why the partial key is not enough", 16, "bold", "start")
cols = [("instructor_id", 150), ("weekday", 120), ("start_time", 130), ("room", 110)]
rows = [("101", "Mon", "10:00", "B-204", False), ("101", "Wed", "10:00", "B-204", False),
        ("102", "Mon", "10:00", "C-110", True)]
x0, y0, rh = tx + 40, ty + 64, 40
tw = sum(w for _, w in cols)
out.append(f'<rect x="{x0}" y="{y0}" width="{tw}" height="{rh}" fill="{ENT}" stroke="{INK}" stroke-width="1.2"/>')
for r, row in enumerate(rows):
    y = y0 + rh * (r + 1)
    fill = "#fee2e2" if r in (0, 2) else "#fff"
    out.append(f'<rect x="{x0}" y="{y}" width="{tw}" height="{rh}" fill="{fill}" stroke="{INK}" stroke-width="1.2"/>')
cx = x0
for c, (name, w) in enumerate(cols):
    text(cx + w / 2, y0 + rh / 2, name, 13.5, "bold")
    for r, row in enumerate(rows):
        text(cx + w / 2, y0 + rh * (r + 1) + rh / 2, row[c], 13.5)
    if c: line((cx, y0), (cx, y0 + rh * 4), w=1.2)
    cx += w
y = y0 + rh * 4 + 30
text(x0, y, "\u2022", 13.5, anchor="start"); text(x0 + 16, y, "Rows 1 and 3 both have Mon 10:00, so the", 13.5, anchor="start")
text(x0 + 16, y + 21, "partial key alone repeats.", 13.5, anchor="start")
text(x0, y + 50, "\u2022", 13.5, anchor="start"); text(x0 + 16, y + 50, "Adding the owner's instructor_id makes", 13.5, anchor="start")
text(x0 + 16, y + 71, "every row unique.", 13.5, anchor="start")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       f'<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(out) + "</svg>")
open("diagrams/weak-entity-office-hour.svg", "w").write(svg)

# diagram only, no callouts or explanation panels
snippet = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="120 95 1000 340" width="1000" height="340">'
           f'<rect x="120" y="95" width="1000" height="340" fill="#fff"/>' + "".join(out[diagram_start:diagram_end]) + "</svg>")
open("diagrams/weak-entity-office-hour-diagram.svg", "w").write(snippet)
