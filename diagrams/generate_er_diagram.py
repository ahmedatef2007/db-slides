W, H = 1240, 940
INK = "#1f2937"; ENT = "#dbeafe"; REL = "#fef3c7"; ATT = "#ffffff"; FONT = "DejaVu Sans, Arial, sans-serif"
out = []
def line(a, b, double=False, dash=False):
    (x1, y1), (x2, y2) = a, b
    if double:
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="6"/>')
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#fff" stroke-width="2"/>')
    else:
        out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="1.6"/>')
def text(x, y, s, size=14, weight="normal", under=None, style=""):
    out.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
               f'text-anchor="middle" dominant-baseline="central" fill="{INK}" {style}>{s}</text>')
    if under:
        w = len(s) * size * 0.31
        dash = ' stroke-dasharray="4 3"' if under == "partial" else ""
        out.append(f'<line x1="{x-w}" y1="{y+10}" x2="{x+w}" y2="{y+10}" stroke="{INK}" stroke-width="1.3"{dash}/>')
shapes = []
def entity(name, c, weak=False, w=160, h=52):
    x, y = c
    s = f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="3" fill="{ENT}" stroke="{INK}" stroke-width="2"/>'
    if weak:
        s += f'<rect x="{x-w/2+5}" y="{y-h/2+5}" width="{w-10}" height="{h-10}" rx="2" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    shapes.append((s, (x, y, name, 15, "bold", None)))
def rel(name, c, weak=False, hw=72, hh=38):
    x, y = c
    pts = lambda a, b: f"{x},{y-b} {x+a},{y} {x},{y+b} {x-a},{y}"
    s = f'<polygon points="{pts(hw, hh)}" fill="{REL}" stroke="{INK}" stroke-width="2"/>'
    if weak:
        s += f'<polygon points="{pts(hw-11, hh-6)}" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    shapes.append((s, (x, y, name, 13, "bold", None)))
def attr(name, c, owner, key=None, multi=False, derived=False, rx=None):
    x, y = c
    rx = rx or max(40, len(name) * 4.6 + 16); ry = 20
    line(c, owner)
    dash = ' stroke-dasharray="6 4"' if derived else ""
    s = f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{ATT}" stroke="{INK}" stroke-width="1.6"{dash}/>'
    if multi:
        s += f'<ellipse cx="{x}" cy="{y}" rx="{rx-5}" ry="{ry-5}" fill="none" stroke="{INK}" stroke-width="1.4"/>'
    shapes.append((s, (x, y, name, 13, "normal", key)))
def card(x, y, s): text(x, y, s, 15, "bold", style='font-style="italic"')

EMP, DEP, PRJ, DPT = (300, 230), (1000, 230), (1000, 560), (560, 810)
WF, MG, CT, WO, SV, DO = (680, 115), (680, 250), (1000, 395), (680, 470), (230, 490), (560, 650)

# relationship lines (drawn under shapes)
line(EMP, WF, double=True); line(WF, DEP, double=True)
line(EMP, MG); line(MG, DEP, double=True)
line(DEP, CT); line(CT, PRJ, double=True)
line(EMP, WO, double=True); line(WO, PRJ, double=True)
line((250, 250), (160, 490)); line((290, 250), (300, 490))
line((360, 255), DO); line(DO, DPT, double=True)

entity("EMPLOYEE", EMP); entity("DEPARTMENT", DEP); entity("PROJECT", PRJ); entity("DEPENDENT", DPT, weak=True)
rel("WORKS_FOR", WF); rel("MANAGES", MG); rel("CONTROLS", CT); rel("WORKS_ON", WO)
rel("SUPERVISION", SV, hw=82); rel("DEPENDENTS_OF", DO, weak=True, hw=92, hh=42)

# EMPLOYEE attributes
NAME = (175, 115)
attr("Fname", (70, 40), NAME); attr("Minit", (175, 30), NAME); attr("Lname", (280, 40), NAME)
attr("Name", NAME, EMP); attr("Sex", (300, 140), EMP); attr("Address", (410, 140), EMP)
attr("Ssn", (95, 190), EMP, key="full"); attr("Bdate", (95, 245), EMP); attr("Salary", (95, 300), EMP)
# DEPARTMENT attributes
attr("Name", (880, 135), DEP, key="full"); attr("Number", (1000, 120), DEP)
attr("Locations", (1130, 135), DEP, multi=True)
attr("NumberOfEmployees", (1130, 320), DEP, derived=True)
# MANAGES / WORKS_ON attributes
attr("StartDate", (560, 185), MG); attr("Hours", (770, 415), WO)
# PROJECT attributes
attr("Name", (875, 650), PRJ, key="full"); attr("Number", (1000, 670), PRJ); attr("Location", (1125, 650), PRJ)
# DEPENDENT attributes
attr("Name", (420, 885), DPT, key="partial"); attr("Sex", (520, 900), DPT)
attr("BirthDate", (630, 900), DPT); attr("Relationship", (760, 885), DPT)

for s, t in shapes:
    out.append(s); text(*t[:3], size=t[3], weight=t[4], under=t[5])

# cardinalities
card(560, 140, "N"); card(800, 135, "1")
card(590, 230, "1"); card(800, 228, "1")
card(1018, 300, "1"); card(1018, 480, "N")
card(500, 330, "M"); card(815, 482, "N")
card(150, 420, "1"); card(318, 450, "N")
text(160, 360, "supervisor", 12, style='font-style="italic"'); text(352, 410, "supervisee", 12, style='font-style="italic"')
card(508, 505, "1"); card(578, 732, "N")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       f'<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(out) + "</svg>")
open("/home/user/db-slides/diagrams/company-er-diagram.svg", "w").write(svg)
