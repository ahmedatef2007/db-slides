W, H = 1000, 340
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
def attr(name, c, owner, key=False):
    x, y = c
    line(c, owner)
    rx = max(48, len(name) * 5.2 + 20)
    shapes.append((f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="24" fill="#fff" stroke="{INK}" stroke-width="1.6"/>',
                   (x, y, name, 14, "normal", key)))

INS, TEACH, CRS = (200, 175), (500, 175), (800, 175)
line(INS, TEACH); line(TEACH, CRS, double=True)
entity("INSTRUCTOR", INS); rel("teaches", TEACH); entity("COURSE", CRS)
attr("instructor_id", (200, 50), INS, key=True); attr("name", (200, 295), INS)
attr("course_code", (800, 50), CRS, key=True); attr("title", (730, 295), CRS); attr("credits", (880, 295), CRS)
for s, t in shapes:
    out.append(s); text(*t[:3], size=t[3], weight=t[4], under=t[5])
text(335, 152, "1", 18, "bold", ACC); text(665, 152, "N", 18, "bold", ACC)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       f'<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(out) + "</svg>")
open("diagrams/teaches-1n-diagram.svg", "w").write(svg)
