W, H = 1240, 610
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

MOD, USES, PRT = (220, 210), (620, 210), (1020, 210)
PAT, FAC = (220, 390), (560, 390)
# double line = total participation: every model uses parts and has exactly one factory
line(MOD, USES, double=True); line(USES, PRT)
line(MOD, PAT, double=True); line(PAT, FAC)
entity("MODEL", MOD); rel("uses", USES); entity("PART", PRT)
rel("produced_at", PAT, hw=88, hh=42); entity("FACTORY", FAC)
# MODEL: name is unique
attr("name", (80, 90), MOD, key=True); attr("suffix", (220, 70), MOD); attr("engine_size", (370, 95), MOD)
# PART: images is multi-valued
attr("part_id", (890, 85), PRT, key=True); attr("description", (1040, 70), PRT); attr("year", (1170, 105), PRT)
attr("images", (1130, 320), PRT, multi=True)
# FACTORY: identified by its city; computer_system is composite
CS = (890, 440)
attr("os", (790, 545), CS); attr("dbms", (900, 560), CS); attr("internet", (1015, 540), CS)
attr("city", (420, 520), FAC, key=True); attr("machines", (545, 545), FAC); attr("capacity", (675, 530), FAC)
attr("computer_system", CS, FAC)
for s, t in shapes:
    out.append(s); text(*t[:3], size=t[3], weight=t[4], under=t[5])
text(380, 188, "M", 18, "bold", ACC); text(860, 188, "N", 18, "bold", ACC)
text(242, 300, "N", 18, "bold", ACC); text(410, 368, "1", 18, "bold", ACC)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       f'<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(out) + "</svg>")
open("diagrams/car-erd.svg", "w").write(svg)
