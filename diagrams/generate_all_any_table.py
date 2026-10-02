from html import escape
INK = "#1f2937"; MUTED = "#6b7280"; HEAD = "#0f172a"; DEPT5 = "#fef3c7"; YES = "#dcfce7"; GREEN = "#15803d"
FONT = "DejaVu Sans, Arial, sans-serif"; MONO = "DejaVu Sans Mono, monospace"
rows = [("Ahmed", 5, 3000), ("Omar", 5, 4000), ("Sara", 5, 5000), ("Mona", 4, 6000),
        ("Karim", 4, 2500), ("Laila", 1, 4500), ("Youssef", 1, 4000)]
sub = [s for _, d, s in rows if d == 5]
lo, hi = min(sub), max(sub)
checks = [("> ALL", "> " + str(hi), lambda s: all(s > v for v in sub)),
          ("< ALL", "< " + str(lo), lambda s: all(s < v for v in sub)),
          ("> ANY", "> " + str(lo), lambda s: any(s > v for v in sub)),
          ("= ANY", "same as IN", lambda s: any(s == v for v in sub))]
out = []
def text(x, y, s, size=15, weight="normal", color=INK, anchor="middle", font=FONT):
    out.append(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
               f'text-anchor="{anchor}" dominant-baseline="central" fill="{color}">{escape(str(s))}</text>')
def rect(x, y, w, h, fill, stroke="#e5e7eb", rx=0):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>')

# subquery banner
x0 = 30
rect(x0, 20, 840, 64, "#f8fafc", "#cbd5e1", 10)
text(x0 + 20, 41, "SELECT salary FROM employee WHERE dno = 5", 14, "bold", font=MONO, anchor="start")
text(x0 + 20, 64, "returns  { " + ", ".join(map(str, sub)) + " }", 14, color=MUTED, font=MONO, anchor="start")
for i, (label, val) in enumerate([("min", lo), ("max", hi)]):
    px = x0 + 620 + i * 110
    rect(px, 36, 96, 32, DEPT5, "#d97706", 16)
    text(px + 48, 52, f"{label} {val}", 14, "bold")

# table
cols = [("fname", 140), ("dno", 70), ("salary", 100)] + [(c[0], 132) for c in checks]
top, hh, rh = 110, 58, 42
tw = sum(w for _, w in cols)
cx = x0
for i, (name, w) in enumerate(cols):
    rect(cx, top, w, hh, HEAD, "#334155")
    if i < 3:
        text(cx + w / 2, top + hh / 2, name, 15, "bold", "#fff")
    else:
        text(cx + w / 2, top + 20, name, 16, "bold", "#fff", font=MONO)
        text(cx + w / 2, top + 41, checks[i - 3][1], 12, color="#cbd5e1")
    cx += w
for r, (fname, dno, sal) in enumerate(rows):
    y = top + hh + r * rh
    cx = x0
    for i, (name, w) in enumerate(cols):
        if i < 3:
            rect(cx, y, w, rh, DEPT5 if dno == 5 else "#fff")
            text(cx + w / 2, y + rh / 2, [fname, dno, sal][i], 15, "bold" if i == 2 else "normal")
        else:
            ok = checks[i - 3][2](sal)
            rect(cx, y, w, rh, YES if ok else "#fff")
            text(cx + w / 2, y + rh / 2, "✓" if ok else "—", 20 if ok else 14,
                 "bold", GREEN if ok else "#d1d5db")
        cx += w
out.append(f'<rect x="{x0}" y="{top}" width="{tw}" height="{hh + rh * len(rows)}" fill="none" stroke="#334155" stroke-width="1.2"/>')

# legend
ly = top + hh + rh * len(rows) + 30
rect(x0, ly - 9, 18, 18, DEPT5, "#d97706", 3); text(x0 + 28, ly, "dept 5 rows (what the subquery returns)", 13.5, color=MUTED, anchor="start")
rect(x0 + 340, ly - 9, 18, 18, YES, GREEN, 3); text(x0 + 368, ly, "row returned by  WHERE salary <column header> (subquery)", 13.5, color=MUTED, anchor="start")

W, H = 900, ly + 30
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       f'<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(out) + "</svg>")
open("diagrams/all-any-table.svg", "w").write(svg)
print(W, H)
