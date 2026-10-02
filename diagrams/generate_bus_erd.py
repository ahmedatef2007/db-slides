W, H = 1240, 700
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

BUS, ROU, TWN, DRV = (190, 230), (640, 230), (1070, 230), (640, 560)
RUNS, PASSES, DRIVES, LAST = (405, 230), (860, 230), (480, 400), (800, 400)
# double line = total participation: every bus has a route, every route has a driver
line(BUS, RUNS, double=True); line(RUNS, ROU)
line(ROU, PASSES); line(PASSES, TWN)
line(ROU, DRIVES, double=True); line(DRIVES, DRV)
line(ROU, LAST); line(LAST, DRV)
entity("BUS", BUS); entity("ROUTE", ROU); entity("TOWN", TWN); entity("DRIVER", DRV)
rel("runs", RUNS, hw=66, hh=38); rel("passes", PASSES, hw=72, hh=38)
rel("drives", DRIVES, hw=74, hh=40); rel("last_route", LAST, hw=88, hh=40)
# BUS: options is multi-valued
attr("number", (70, 110), BUS, key=True); attr("chairs", (190, 80), BUS); attr("brand", (315, 110), BUS)
attr("options", (130, 345), BUS, multi=True)
# ROUTE
attr("route_id", (470, 110), ROU, key=True); attr("km", (575, 70), ROU); attr("start", (680, 65), ROU)
attr("end", (780, 90), ROU); attr("duration", (870, 140), ROU)
# TOWN: name is unique
attr("name", (1000, 110), TWN, key=True); attr("station", (1150, 110), TWN)
# drives keeps the allocation history
attr("start_date", (285, 370), DRIVES); attr("end_date", (300, 450), DRIVES)
# DRIVER
attr("driver_id", (430, 560), DRV, key=True); attr("name", (495, 650), DRV); attr("salary", (620, 670), DRV)
attr("hire_date", (755, 660), DRV); attr("grade", (875, 625), DRV); attr("mobile", (865, 545), DRV)
for s, t in shapes:
    out.append(s); text(*t[:3], size=t[3], weight=t[4], under=t[5])
text(318, 208, "N", 18, "bold", ACC); text(505, 208, "1", 18, "bold", ACC)
text(765, 208, "M", 18, "bold", ACC); text(946, 208, "N", 18, "bold", ACC)
text(545, 300, "M", 18, "bold", ACC); text(540, 495, "N", 18, "bold", ACC)
text(732, 295, "1", 18, "bold", ACC); text(738, 500, "N", 18, "bold", ACC)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       f'<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(out) + "</svg>")
open("diagrams/bus-erd.svg", "w").write(svg)
