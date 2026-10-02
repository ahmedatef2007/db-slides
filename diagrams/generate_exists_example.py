from html import escape
INK = "#1f2937"; MUTED = "#6b7280"; HEAD = "#0f172a"; RED = "#b91c1c"; REDBG = "#fee2e2"
GREEN = "#15803d"; GREENBG = "#dcfce7"; PANEL = "#f8fafc"
FONT = "DejaVu Sans, Arial, sans-serif"; MONO = "DejaVu Sans Mono, monospace"
out = []
def text(x, y, s, size=14, weight="normal", color=INK, anchor="start", font=FONT, strike=False):
    deco = ' text-decoration="line-through"' if strike else ""
    out.append(f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
               f'text-anchor="{anchor}" dominant-baseline="central" fill="{color}"{deco}>{escape(str(s))}</text>')
def rect(x, y, w, h, fill, stroke="#e5e7eb", rx=0):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>')
RH = 34
def table(x, y, title, cols, rows, fills=None):
    """cols: [(header, width)]; rows: list of cell values (str or callable drawing at (cx, cy, w))."""
    text(x, y - 14, title, 13, "bold", MUTED, font=MONO)
    cx = x
    for h, w in cols:
        rect(cx, y, w, RH, HEAD, "#334155"); text(cx + w / 2, y + RH / 2, h, 13, "bold", "#fff", "middle")
        cx += w
    for r, row in enumerate(rows):
        cx, ry = x, y + RH * (r + 1)
        for c, (h, w) in enumerate(cols):
            rect(cx, ry, w, RH, (fills or {}).get(r, "#fff"))
            v = row[c]
            if callable(v): v(cx, ry + RH / 2, w)
            else: text(cx + w / 2, ry + RH / 2, v, 14, anchor="middle")
            cx += w
    tw = sum(w for _, w in cols)
    out.append(f'<rect x="{x}" y="{y}" width="{tw}" height="{RH * (len(rows) + 1)}" fill="none" stroke="#334155"/>')
def status(x, y, s, color):
    text(x, y, s, 13.5, "bold", color)

W, H = 1200, 330
# ---- panel A: DELETE ... NOT EXISTS
rect(10, 10, 585, H - 20, PANEL, "#cbd5e1", 10)
text(30, 38, "DELETE … WHERE NOT EXISTS", 16, "bold", font=MONO)
T = 90
table(30, T, "orders", [("supplier_id", 120)], [["1"], ["1"], ["2"]])
strike = lambda s: (lambda cx, cy, w: text(cx + w / 2, cy, s, 14, color=RED, anchor="middle", strike=True))
table(185, T, "suppliers", [("supplier_id", 110), ("supplier_name", 150)],
      [["1", "Acme"], ["2", "Bolt"], [strike("3"), strike("Cargo")]], {2: REDBG})
for r, (s, c) in enumerate([("✓ kept", GREEN), ("✓ kept", GREEN), ("✗ deleted", RED)]):
    status(458, T + RH * (r + 1) + RH / 2, s, c)
text(30, 250, "Cargo (3) has no order, so NOT EXISTS is true and the row is deleted.", 13, color=INK)
text(30, 274, "With NOT IN: one NULL in orders.supplier_id and", 13, color=RED)
text(30, 294, "nothing is deleted. NOT EXISTS still deletes Cargo.", 13, color=RED)

# ---- panel B: UPDATE ... WHERE EXISTS
ox = 605
rect(ox, 10, 585, H - 20, PANEL, "#cbd5e1", 10)
text(ox + 20, 38, "UPDATE … WHERE EXISTS", 16, "bold", font=MONO)
table(ox + 20, T, "customers", [("customer_id", 105), ("name", 90)], [["2", "Bolt Ltd"], ["3", "Cargo Co"]])
def change(old, new):
    def draw(cx, cy, w):
        text(cx + 14, cy, old, 14, color=MUTED, strike=True)
        text(cx + 14 + len(old) * 8.6 + 6, cy, "→ " + new, 14, "bold", GREEN)
    return draw
table(ox + 230, T, "suppliers", [("supplier_id", 95), ("supplier_name", 180)],
      [["1", "Acme"], ["2", change("Bolt", "Bolt Ltd")], ["3", change("Cargo", "Cargo Co")]], {1: GREENBG, 2: GREENBG})
for r, (s, c) in enumerate([("skipped", MUTED), ("updated", GREEN), ("updated", GREEN)]):
    status(ox + 515, T + RH * (r + 1) + RH / 2, s, c)
text(ox + 20, 250, "Acme (1) has no matching customer, so WHERE EXISTS skips it.", 13, color=INK)
text(ox + 20, 274, "Without WHERE EXISTS, the subquery finds no name", 13, color=RED)
text(ox + 20, 294, "for Acme, so its supplier_name becomes NULL.", 13, color=RED)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       f'<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(out) + "</svg>")
open("diagrams/exists-delete-update.svg", "w").write(svg)
