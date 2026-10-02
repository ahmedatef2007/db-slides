W, H = 1240, 750
INK = "#1f2937"; ENT = "#dbeafe"; REL = "#fef3c7"; ACC = "#dc2626"; FONT = "DejaVu Sans, Arial, sans-serif"
out = []
def line(a, b, double=False):
    (x1, y1), (x2, y2) = a, b
    if double:
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="6"/>')
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#fff" stroke-width="2"/>')
    else:
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="1.6"/>')
def text(x, y, s, size=14, weight="normal", color=INK, under=False):
    out.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
               f'text-anchor="middle" dominant-baseline="central" fill="{color}">{s}</text>')
    if under:
        w = len(s) * size * 0.29
        out.append(f'<line x1="{x-w}" y1="{y+11}" x2="{x+w}" y2="{y+11}" stroke="{INK}" stroke-width="1.4"/>')
shapes = []
def entity(name, c, w=200, h=56):
    x, y = c
    shapes.append((f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="3" fill="{ENT}" stroke="{INK}" stroke-width="2"/>',
                   (x, y, name, 17, "bold", False)))
def rel(name, c, hw=80, hh=44):
    x, y = c
    shapes.append((f'<polygon points="{x},{y-hh} {x+hw},{y} {x},{y+hh} {x-hw},{y}" fill="{REL}" stroke="{INK}" stroke-width="2"/>',
                   (x, y, name, 15, "bold", False)))
def attr(name, c, owner, key=False, multi=False):
    x, y = c
    line(c, owner)
    rx = max(48, len(name) * 5.2 + 20) + (14 if multi else 0)
    s = f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="24" fill="#fff" stroke="{INK}" stroke-width="1.6"/>'
    if multi:  # double ellipse = multi-valued attribute
        s += f'<ellipse cx="{x}" cy="{y}" rx="{rx-6}" ry="18" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    shapes.append((s, (x, y, name, 14, "normal", key)))

BR, CU, AC, TX = (260, 250), (620, 250), (1050, 250), (620, 580)
OWNS, MAKES, AT = (835, 250), (620, 420), (260, 580)
# relationships (double line = total participation)
line(CU, OWNS, double=True); line(OWNS, AC, double=True)
line(CU, MAKES); line(MAKES, TX, double=True)
line(BR, AT); line(AT, TX, double=True)
entity("BRANCH", BR); entity("CUSTOMER", CU); entity("ACCOUNT", AC); entity("TRANSACTION", TX)
rel("owns", OWNS, hw=70, hh=40); rel("makes", MAKES, hw=70, hh=40); rel("at", AT, hw=60, hh=36)
# BRANCH: name and address are both unique
attr("name", (115, 125), BR, key=True); attr("address", (245, 90), BR, key=True); attr("phone", (365, 130), BR)
# CUSTOMER: phone is multi-valued
attr("customer_id", (535, 110), CU, key=True); attr("name", (655, 90), CU); attr("address", (775, 120), CU)
attr("phone", (790, 370), CU, multi=True)
# ACCOUNT
attr("account_no", (960, 115), AC, key=True); attr("balance", (1120, 115), AC); attr("last_tx_date", (1110, 385), AC)
# TRANSACTION
attr("tx_no", (420, 680), TX, key=True); attr("type", (530, 705), TX); attr("tx_date", (650, 710), TX)
attr("tx_time", (775, 705), TX); attr("amount", (885, 680), TX)
for s, t in shapes:
    out.append(s); text(*t[:3], size=t[3], weight=t[4], under=t[5])
text(740, 228, "1", 18, "bold", ACC); text(930, 228, "1", 18, "bold", ACC)
text(640, 345, "1", 18, "bold", ACC); text(642, 505, "N", 18, "bold", ACC)
text(280, 470, "1", 18, "bold", ACC); text(400, 558, "N", 18, "bold", ACC)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       f'<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(out) + "</svg>")
open("diagrams/bank-erd.svg", "w").write(svg)
