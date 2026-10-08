#!/usr/bin/env python3
"""Wiring schematic of the Fichet safe robot -> control/harness/schematic.pdf

A4 landscape, colour. Revision in each title block (from the REVISION file). Every connection is from control/wiring.md
(harness v1); where the two ever differ, wiring.md wins. RAMPS-internal
parts (F1, D1, pull-ups) are from the RAMPS 1.4 KiCad port's netlist.

No text is drawn below MIN_PT (8 pt), so the printed sheets stay legible:
Sheet.setfont() refuses anything smaller.

    python3 -m pip install reportlab        # once
    python3 control/harness/schematic.py    # writes control/harness/schematic.pdf
"""
import os
import sys

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

W, H = landscape(A4)          # 841.9 x 595.3 pt
MIN_PT = 8
DATE = "2026-10-08"
# project revision, from the REVISION file at the repo root
REV = open(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "REVISION")).read().strip()
BOTTOM = H - 82               # content above this; legend + title block below

# ---------------------------------------------------------------- fonts
# Liberation Sans (Arial metrics; has Ω µ → ×). Arial on a Mac works too.
FONT_CANDIDATES = [
    ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
     "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ("/System/Library/Fonts/Supplemental/Arial.ttf",
     "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]
for _reg, _bold in FONT_CANDIDATES:
    if os.path.exists(_reg) and os.path.exists(_bold):
        pdfmetrics.registerFont(TTFont("F", _reg))
        pdfmetrics.registerFont(TTFont("FB", _bold))
        break
else:
    sys.exit("no usable TrueType font found (see FONT_CANDIDATES)")

# ---------------------------------------------------------------- colours
INK = "#1A1A1A"
GREY = "#666666"
WARN = "#C62828"
NETS = {   # net class: (colour, line width)
    "12V":   ("#C62828", 1.8),
    "5V":    ("#E67E00", 1.6),
    "GND":   ("#1A1A1A", 1.4),
    "UART":  ("#1B8A3A", 1.5),
    "CTRL":  ("#1F4FB4", 1.3),   # STEP / DIR / EN, button
    "DIAG":  ("#8E3FB0", 1.4),
    "MOTOR": ("#8A5A1E", 1.5),
    "TIE":   ("#666666", 1.1),   # jumpers, ties, spare
}
NET_NAMES = [("12V", "+12 V"), ("5V", "+5 V (logic, VIO)"), ("GND", "GND"), ("UART", "UART bus"),
             ("CTRL", "STEP / DIR / EN, button"), ("DIAG", "DIAG (stall)"), ("MOTOR", "motor coils"),
             ("TIE", "jumper / tie / spare")]
FILL = {"module": "#E8EEF6", "build": "#FFF4CC", "ref": "#EFEFEF"}


class Sheet:
    """One A4 landscape page. Coordinates are points from the TOP-left corner."""

    def __init__(self, c, no, total, title, note=None):
        self.c, self.no, self.total, self.title = c, no, total, title
        self.frame(note)

    # ------------------------------------------------------------ basics
    def Y(self, y):
        return H - y

    def setfont(self, size, bold=False):
        if size < MIN_PT:
            raise ValueError(f"text below {MIN_PT} pt on sheet {self.no}")
        self.c.setFont("FB" if bold else "F", size)

    @staticmethod
    def tw(s, size=8, bold=False):
        return pdfmetrics.stringWidth(s, "FB" if bold else "F", size)

    def text(self, x, y, s, size=8, bold=False, color=INK, anchor="l"):
        """y is the text baseline."""
        c = self.c
        self.setfont(size, bold)
        c.setFillColor(HexColor(color))
        {"l": c.drawString, "c": c.drawCentredString, "r": c.drawRightString}[anchor](x, self.Y(y), s)

    def para(self, x, y, rows, size=8, color=INK, lead=None, anchor="l"):
        """rows: str, or (str, bold), or (str, bold, colour)."""
        lead = lead or round(size * 1.3, 1)
        for i, r in enumerate(rows):
            r = (r,) if isinstance(r, str) else r
            self.text(x, y + i * lead, r[0], size, r[1] if len(r) > 1 else False,
                      r[2] if len(r) > 2 else color, anchor)
        return y + len(rows) * lead

    def line(self, pts, color=INK, w=1.0, dash=None):
        c = self.c
        p = c.beginPath()
        p.moveTo(pts[0][0], self.Y(pts[0][1]))
        for x, y in pts[1:]:
            p.lineTo(x, self.Y(y))
        c.setStrokeColor(HexColor(color))
        c.setLineWidth(w)
        c.setDash(dash or [])
        c.setLineCap(1)
        c.setLineJoin(1)
        c.drawPath(p, stroke=1, fill=0)
        c.setDash([])

    def wire(self, pts, net):
        col, w = NETS[net]
        self.line(pts, col, w)

    def hwire_hop(self, x1, x2, y, hops, net):
        """Horizontal wire x1 -> x2 (x1 < x2) with a hop over each x in hops."""
        col, w = NETS[net]
        c, r = self.c, 4.5
        p = c.beginPath()
        p.moveTo(x1, self.Y(y))
        for hx in sorted(hops):
            p.lineTo(hx - r, self.Y(y))
            p.arcTo(hx - r, self.Y(y) - r, hx + r, self.Y(y) + r, startAng=180, extent=-180)
        p.lineTo(x2, self.Y(y))
        c.setStrokeColor(HexColor(col))
        c.setLineWidth(w)
        c.setLineCap(1)
        c.drawPath(p, stroke=1, fill=0)

    def vwire_hop(self, x, y1, y2, hops, net):
        """Vertical wire y1 -> y2 (y1 < y2, top to bottom) with a hop at each y in hops."""
        col, w = NETS[net]
        c, r = self.c, 4.5
        p = c.beginPath()
        p.moveTo(x, self.Y(y1))
        for hy in sorted(hops):
            p.lineTo(x, self.Y(hy - r))
            p.arcTo(x - r, self.Y(hy) - r, x + r, self.Y(hy) + r, startAng=90, extent=-180)
        p.lineTo(x, self.Y(y2))
        c.setStrokeColor(HexColor(col))
        c.setLineWidth(w)
        c.setLineCap(1)
        c.drawPath(p, stroke=1, fill=0)

    def dot(self, x, y, net):
        self.c.setFillColor(HexColor(NETS[net][0]))
        self.c.circle(x, self.Y(y), 2.7, stroke=0, fill=1)

    def rect(self, x, y, w, h, stroke=INK, fill=None, lw=1.0, dash=None, r=0):
        c = self.c
        c.setStrokeColor(HexColor(stroke))
        c.setLineWidth(lw)
        c.setDash(dash or [])
        if fill:
            c.setFillColor(HexColor(fill))
        if r:
            c.roundRect(x, self.Y(y + h), w, h, r, stroke=1, fill=1 if fill else 0)
        else:
            c.rect(x, self.Y(y + h), w, h, stroke=1, fill=1 if fill else 0)
        c.setDash([])

    def poly(self, pts, stroke=INK, fill=None, lw=1.0):
        c = self.c
        p = c.beginPath()
        p.moveTo(pts[0][0], self.Y(pts[0][1]))
        for x, y in pts[1:]:
            p.lineTo(x, self.Y(y))
        p.close()
        c.setStrokeColor(HexColor(stroke))
        c.setLineWidth(lw)
        if fill:
            c.setFillColor(HexColor(fill))
        c.drawPath(p, stroke=1, fill=1 if fill else 0)

    def circle(self, x, y, r, stroke=INK, fill=None, lw=1.2):
        c = self.c
        c.setStrokeColor(HexColor(stroke))
        c.setLineWidth(lw)
        if fill:
            c.setFillColor(HexColor(fill))
        c.circle(x, self.Y(y), r, stroke=1, fill=1 if fill else 0)

    # ------------------------------------------------------------ frame, legend
    def frame(self, note):
        self.rect(14, 14, W - 28, H - 28, lw=1.2)
        self.text(24, 36, self.title, 15, True)
        if note:
            self.text(24, 52, note, 9, color=GREY)
        bx, by, bw, bh = W - 290, H - 76, 276, 62
        self.rect(bx, by, bw, bh, lw=1.0, fill="#FFFFFF")
        self.line([(bx, by + 20), (bx + bw, by + 20)], INK, 0.6)
        self.line([(bx, by + 41), (bx + bw, by + 41)], INK, 0.6)
        self.text(bx + 6, by + 14, "Fichet safe robot — wiring schematic", 9, True)
        self.text(bx + bw - 6, by + 14, f"Sheet {self.no} of {self.total}", 9, True, anchor="r")
        self.text(bx + 6, by + 35, self.title, 9)
        self.text(bx + 6, by + 56, f"{DATE} · revision {REV} · from control/wiring.md", 8, color=GREY)
        # legend: three rows, left of the title block
        x0, y = 24, H - 58
        rows = [NET_NAMES[:4], NET_NAMES[4:]]
        for row in rows:
            cx = x0
            for key, name in row:
                col, w = NETS[key]
                self.line([(cx, y - 3), (cx + 18, y - 3)], col, w + 0.8)
                self.text(cx + 22, y, name, 8)
                cx += 22 + self.tw(name) + 14
            y += 13
        cx = x0
        for key, name in [("module", "bought module"), ("build", "board you build"),
                          ("ref", "already on the RAMPS / Mega: nothing to buy")]:
            self.rect(cx, y - 8, 18, 9, stroke=GREY, fill=FILL[key], lw=0.6)
            self.text(cx + 22, y, name, 8)
            cx += 22 + self.tw(name) + 14

    # ------------------------------------------------------------ building blocks
    def board(self, x, y, w, h, label, kind="build", sub=None):
        self.rect(x, y, w, h, stroke=GREY, fill=FILL[kind], lw=0.9,
                  dash=None if kind == "module" else [4, 2], r=4)
        self.text(x + 7, y + 13, label, 9, True)
        if sub:
            self.text(x + 7, y + 24, sub, 8, color=GREY)

    def ic(self, x, y, w, left=(), right=(), pitch=21, pad=13, stub=10, fill="#FFFFFF"):
        """Box with pins. left/right: lists of (key, label) or None for an empty row.
        Returns ({key: (x, y) of the pin's outer end}, box height)."""
        n = max(len(left), len(right), 1)
        h = 2 * pad + (n - 1) * pitch
        self.rect(x, y, w, h, fill=fill, lw=1.3)
        pins = {}
        for side, items in (("l", left), ("r", right)):
            for i, p in enumerate(items):
                if not p:
                    continue
                py = y + pad + i * pitch
                if side == "l":
                    self.line([(x - stub, py), (x, py)], INK, 1.0)
                    self.text(x + 4, py + 3, p[1], 8)
                    pins[p[0]] = (x - stub, py)
                else:
                    self.line([(x + w, py), (x + w + stub, py)], INK, 1.0)
                    self.text(x + w - 4, py + 3, p[1], 8, anchor="r")
                    pins[p[0]] = (x + w + stub, py)
        return pins, h

    def conn(self, x, y, labels, side="l", pitch=20, pad=10, w=20, stub=6, fill="#FFFFFF"):
        """Connector: one box, one row per pin, labels[i] written inside.
        side 'l', 'r' or 'lr': where the stubs are. Returns {(label, side): (x, y)}."""
        n = len(labels)
        h = 2 * pad + (n - 1) * pitch
        self.rect(x, y, w, h, fill=fill, lw=1.3)
        pins = {}
        for i, lab in enumerate(labels):
            py = y + pad + i * pitch
            self.text(x + w / 2, py + 3, lab, 8, True, anchor="c")
            if "l" in side:
                self.line([(x - stub, py), (x, py)], INK, 1.0)
                pins[(lab, "l")] = (x - stub, py)
            if "r" in side:
                self.line([(x + w, py), (x + w + stub, py)], INK, 1.0)
                pins[(lab, "r")] = (x + w + stub, py)
        return pins, h

    # ------------------------------------------------------------ symbols
    def gnd(self, x, y):
        col = NETS["GND"][0]
        self.line([(x, y), (x, y + 6)], col, 1.4)
        for i, half in enumerate((7, 4.5, 2)):
            self.line([(x - half, y + 6 + i * 3), (x + half, y + 6 + i * 3)], col, 1.4)

    def flag(self, x, y, label, net, up=True):
        """Power flag on a vertical lead: bar + label above (up) or below."""
        col = NETS[net][0]
        d = -1 if up else 1
        self.line([(x, y), (x, y + d * 8)], col, NETS[net][1])
        self.line([(x - 6, y + d * 8), (x + 6, y + d * 8)], col, 1.8)
        self.text(x, y + d * 8 + (-4 if up else 11), label, 8, True, col, anchor="c")

    def tag(self, x, y, label, net, side="r"):
        """Net label in a rounded box attached at (x, y): side 'r' extends right, 'l' left."""
        col = NETS[net][0]
        tw = self.tw(label, 8, True) + 8
        bx = x if side == "r" else x - tw
        self.rect(bx, y - 6.5, tw, 13, stroke=col, fill="#FFFFFF", lw=1.0, r=3)
        self.text(bx + tw / 2, y + 3, label, 8, True, col, anchor="c")
        return bx + tw if side == "r" else bx

    def offpage(self, x, y, label, net, side="r"):
        """Off-sheet connector (arrow shape) attached at (x, y), pointing away."""
        col = NETS[net][0]
        tw = self.tw(label, 8) + 10
        h = 13
        if side == "r":
            pts = [(x, y - h / 2), (x + tw, y - h / 2), (x + tw + 7, y), (x + tw, y + h / 2), (x, y + h / 2)]
            tx = x + 5
        else:
            pts = [(x, y - h / 2), (x - tw, y - h / 2), (x - tw - 7, y), (x - tw, y + h / 2), (x, y + h / 2)]
            tx = x - tw + 5
        self.poly(pts, stroke=col, fill="#FFFFFF", lw=1.0)
        self.text(tx, y + 3, label, 8, False, col)
        return x + tw + 7 if side == "r" else x - tw - 7

    def nc(self, x, y):
        self.line([(x - 3.5, y - 3.5), (x + 3.5, y + 3.5)], GREY, 1.2)
        self.line([(x - 3.5, y + 3.5), (x + 3.5, y - 3.5)], GREY, 1.2)

    def res_h(self, x1, x2, y, net, label, above=True, lift=8):
        """IEC resistor on a horizontal wire (x1 < x2)."""
        xm = (x1 + x2) / 2
        self.wire([(x1, y), (xm - 12, y)], net)
        self.wire([(xm + 12, y), (x2, y)], net)
        self.rect(xm - 12, y - 4.5, 24, 9, fill="#FFFFFF", lw=1.3)
        self.text(xm, y - lift if above else y + 16, label, 8, True, anchor="c")

    def res_v(self, x, y1, y2, net, label, left=True):
        """IEC resistor on a vertical wire (y1 < y2)."""
        ym = (y1 + y2) / 2
        self.wire([(x, y1), (x, ym - 12)], net)
        self.wire([(x, ym + 12), (x, y2)], net)
        self.rect(x - 4.5, ym - 12, 9, 24, fill="#FFFFFF", lw=1.3)
        self.text(x - 9 if left else x + 9, ym + 3, label, 8, True, anchor="r" if left else "l")

    def ptc_h(self, x1, x2, y, label, net="12V"):
        """Resettable fuse (PTC) on a horizontal wire."""
        self.res_h(x1, x2, y, net, label, lift=13)
        xm = (x1 + x2) / 2
        self.line([(xm - 16, y + 8), (xm - 10, y + 8), (xm + 12, y - 8)], INK, 1.0)

    def cap_v(self, x, y1, y2, label_rows, side=1):
        """Polarised capacitor, vertical, + at the top: 12 V above, GND below."""
        ym = (y1 + y2) / 2
        self.wire([(x, y1), (x, ym - 3)], "12V")
        self.wire([(x, ym + 3), (x, y2)], "GND")
        self.line([(x - 8, ym - 3), (x + 8, ym - 3)], INK, 1.8)
        self.rect(x - 8, ym + 2, 16, 2.6, stroke=INK, fill=INK, lw=0.6)
        self.text(x - 11, ym - 5, "+", 8, True, anchor="c")
        self.para(x + 13 if side > 0 else x - 13, ym - 1, label_rows, 8, anchor="l" if side > 0 else "r")

    def diode_v(self, x, y1, y2, label_rows):
        """Diode on a vertical wire, anode at the top (y1), cathode at the bottom."""
        ym = (y1 + y2) / 2
        self.wire([(x, y1), (x, ym - 6)], "12V")
        self.wire([(x, ym + 6), (x, y2)], "12V")
        self.poly([(x - 7, ym - 6), (x + 7, ym - 6), (x, ym + 6)], stroke=INK, fill=INK)
        self.line([(x - 7, ym + 6), (x + 7, ym + 6)], INK, 1.8)
        self.para(x - 12, ym - 1, label_rows, 8, anchor="r")

    def button_v(self, x, y1, y2, label_rows):
        """Normally open push button on a vertical wire, signal at the top, GND at the bottom."""
        ym = (y1 + y2) / 2
        self.wire([(x, y1), (x, ym - 9)], "CTRL")
        self.wire([(x, ym + 9), (x, y2)], "GND")
        self.circle(x, ym - 9, 1.8)
        self.circle(x, ym + 9, 1.8)
        self.line([(x + 6, ym - 11), (x + 6, ym + 11)], INK, 1.5)
        self.line([(x + 6, ym), (x + 13, ym)], INK, 1.5)
        self.line([(x + 13, ym - 4), (x + 13, ym + 4)], INK, 1.5)
        self.para(x + 19, ym - 1, label_rows, 8)

    @staticmethod
    def motor_r(leads):
        return max(20, (max(leads) - min(leads)) / 2 + 4)

    def motor(self, cx, cy, leads, x_in, rows):
        """2-phase stepper: circle with M; the 4 leads come in from x_in at y = leads
        and end on the circle (its radius is set so all four reach it)."""
        r = self.motor_r(leads)
        for py in leads:
            dy = py - cy
            self.wire([(x_in, py), (cx - (r * r - dy * dy) ** 0.5, py)], "MOTOR")
        self.circle(cx, cy, r, fill="#FFFFFF", lw=1.5)
        self.text(cx, cy + 5, "M", 14, True, anchor="c")
        self.para(cx, cy + r + 13, rows, 8, anchor="c")

    def jumper(self, x, y, fitted):
        """RAMPS jumper pair seen as a symbol: signal pad at x (right), +5 V pad to its left."""
        self.rect(x - 3, y - 3, 6, 6, fill="#FFFFFF", lw=1.0)
        self.rect(x - 15, y - 3, 6, 6, fill="#FFFFFF", lw=1.0)
        if fitted:
            self.rect(x - 17, y - 5, 22, 10, stroke=INK, lw=1.8, r=2)
        self.wire([(x - 15, y), (x - 21, y)], "5V")
        self.text(x - 23, y + 3, "+5 V", 8, True, NETS["5V"][0], anchor="r")


# ====================================================================== sheet 1
def sheet_overview(s):
    blue = "#4F72A8"
    s.rect(138, 72, 486, 318, stroke=blue, lw=1.5, dash=[6, 3], r=6)
    s.text(146, 87, "DIAL UNIT  (on the door, over the 3 dial holes) — all the electronics", 9, True, blue)
    s.rect(640, 72, 180, 318, stroke=blue, lw=1.5, dash=[6, 3], r=6)
    s.text(650, 87, "KEY TURNER  (over the key)", 9, True, blue)

    def blk(x, y, w, h, title, rows, kind="module"):
        s.rect(x, y, w, h, stroke=INK, fill=FILL[kind], lw=1.1, r=3)
        s.text(x + 6, y + 14, title, 9, True)
        s.para(x + 6, y + 27, rows, 8)

    blk(20, 100, 96, 58, "Mac (USB)", ["logger.py, Arduino IDE", "USB-C -> USB-B"], "ref")
    blk(20, 286, 96, 70, "Power supply", ["Ledmo HTY-1200500", "12 V, 5 A max", "5.5 x 2.1 mm, centre +"], "ref")
    blk(150, 98, 142, 64, "Arduino Mega 2560 R3", ["the controller", "sheets 2, 6"])
    blk(150, 178, 142, 108, "RAMPS 1.4 (on the Mega)", ["X, Y, Z, E0 driver sockets", "endstop + AUX-4 headers",
                                                        "5 A input fuse feeds all 4", "D1 -> Mega VIN",
                                                        "sheets 2, 3, 4, 6"])
    blk(316, 98, 136, 196, "Drivers x 4", ["BTT TMC2209 V1.3", "in RAMPS X, Y, Z, E0", "",
                                            "X = dial A (top-left)", "Y = dial B (top-right)",
                                            "Z = dial C (bottom)", "E0 = key", "",
                                            "UART addresses 0,1,2,3", "DIAG mod on all 4",
                                            "sheets 3, 4"])
    blk(468, 98, 140, 196, "Motors x 4", ["17HE19-2004S", "plug into the RAMPS", "motor headers", "",
                                           "A,B,C: dial plugs,", "14T -> 28T gears", "",
                                           "key: on the key axis", "", "sheets 3, 4"])
    blk(150, 306, 294, 70, "Hub board (you build)", ["just the UART junction (revision 2026-10-08.1):",
                                                      "R1 1 kOhm (the only UART resistor), and the",
                                                      "bus node where RX2 + all 4 PDN_UART meet",
                                                      "sheet 6"], "build")
    blk(648, 150, 164, 90, "Key motor", ["17HE19-2004S", "on the key axis", "", "its own ~1 m cable",
                                          "-> RAMPS E0 motor header", "sheet 4"])

    def lab(x, y, t, net):
        s.text(x, y, t, 8, True, NETS[net][0])

    s.wire([(116, 128), (150, 128)], "5V"); lab(116, 122, "USB", "5V")
    s.wire([(116, 320), (150, 320)], "12V"); lab(116, 314, "12 V", "12V")
    s.wire([(221, 162), (221, 178)], "CTRL")
    s.wire([(292, 220), (316, 220)], "CTRL"); lab(282, 214, "STEP", "CTRL")
    s.wire([(452, 220), (468, 220)], "MOTOR")
    s.wire([(221, 286), (221, 306)], "UART")
    s.wire([(300, 306), (300, 298), (380, 298), (380, 294)], "UART")
    # the key motor's own cable: key turner -> RAMPS E0 motor header (the only inter-unit wire)
    s.wire([(608, 220), (648, 195)], "MOTOR")
    s.text(628, 180, "~1 m cable", 8, True, NETS["MOTOR"][0], anchor="c")

    y = 410
    s.text(24, y, "Sheets", 10, True)
    s.para(24, y + 15, ["1  Overview (this sheet)", "2  Power: 12 V, 5 V, GND",
                        "3  Drivers A and B on the RAMPS", "4  Driver C and the key driver (E0)",
                        "5  DIAG-mod and UART-tap details",
                        "6  Mega + RAMPS headers, hub (UART bus)", "7  Pin map, jumpers, currents, parts"], 8)
    s.text(300, y, "Rules", 10, True)
    s.para(300, y + 15, ["Make every connection with power off (USB unplugged, 12 V off).",
                         "Never plug or unplug a motor with 12 V on (the key motor cable included).",
                         "Power up: USB first, then 12 V. Power down: 12 V first.",
                         "Never fit an MS3 jumper: on the V1.3 that pin is the UART line.",
                         "Emergency stop: pull the 12 V plug.  `!` aborts a move.",
                         "VERIFY = not yet checked on the bench (control/bringup.md).",
                         "Revision 2026-10-08.1: key driver in E0, no remote board or cable.",
                         "If this disagrees with control/wiring.md, wiring.md wins."], 8)


# ====================================================================== sheet 2
def sheet_power(s):
    # PSU and DC jack straight into the RAMPS "5A" terminal (no hub split)
    s.rect(24, 112, 94, 72, fill=FILL["ref"], r=3)
    s.para(30, 126, [("PSU", True), "Ledmo HTY-1200500", "12 V, 5 A max", "5.5 x 2.1, centre +"], 8)
    s.rect(136, 116, 72, 64, fill=FILL["module"], r=3)
    s.para(142, 130, [("DC jack", True), "5.5 x 2.1 ->", "screw terminal", ("VERIFY + / -", True, WARN)], 8)
    s.wire([(118, 136), (136, 136)], "12V")
    s.wire([(118, 170), (136, 170)], "GND")
    s.wire([(208, 136), (552, 136)], "12V")
    s.text(380, 131, "20 AWG red  ->  RAMPS '5A' +", 8, True, NETS["12V"][0], anchor="c")
    s.wire([(208, 170), (552, 170)], "GND")
    s.text(380, 165, "20 AWG black ->  RAMPS '5A' -", 8, True, anchor="c")
    s.para(24, 212, [("Revision 2026-10-08.1:", True),
                     "12 V goes straight from the PSU adapter into",
                     "the RAMPS '5A' terminal. The hub no longer",
                     "splits 12 V and has no fuse: RAMPS's own 5 A",
                     "fuse feeds all four drivers.",
                     "",
                     ("Not the Mega's own barrel jack: that feeds", True, WARN),
                     ("only the Mega (VIN). The drivers get 12 V", True, WARN),
                     ("only through the RAMPS '5A' input; D1 passes", True, WARN),
                     ("power from there to the Mega, never back.", True, WARN)], 8)

    # RAMPS 12 V
    s.board(530, 72, 290, 262, "RAMPS 1.4 - 12 V (already on the board)", "ref",
            "from the RAMPS 1.4 KiCad netlist (control/wiring.md log, 2026-10-07)")
    s.wire([(552, 136), (552, 136)], "12V")
    s.rect(552, 127, 22, 54, fill="#FFFFFF", lw=1.3)
    s.text(563, 141, "+", 9, True, NETS["12V"][0], anchor="c")
    s.text(563, 157, "5A", 8, True, anchor="c")
    s.text(563, 175, "-", 9, True, anchor="c")
    s.text(563, 194, "X4", 8, True, anchor="c")
    s.ptc_h(574, 646, 136, "RAMPS F1: MF-R500, 5 A (feeds all 4 drivers)")
    s.wire([(646, 136), (800, 136)], "12V")
    s.text(796, 131, "+12 V", 8, True, NETS["12V"][0], anchor="r")
    s.wire([(574, 170), (590, 170), (590, 214), (782, 214)], "GND")
    for i, lab in enumerate(["X", "Y", "Z", "E0"]):
        x = 660 + i * 38
        s.dot(x, 136, "12V")
        s.wire([(x, 136), (x, 152)], "12V")
        s.rect(x - 15, 152, 30, 34, fill="#FFFFFF", lw=1.1)
        s.text(x, 165, f"{lab}:VM", 8, True, anchor="c")
        s.text(x, 180, "GND", 8, anchor="c")
        s.wire([(x, 186), (x, 214)], "GND")
        s.dot(x, 214, "GND")
    s.text(552, 236, "Driver sockets X, Y, Z, E0: VM and GND (sheets 3, 4).", 8)
    s.text(552, 247, "C3, C4, C6, C7, C9, C10 (100 uF) sit on this +12 V rail.", 8)
    s.dot(800, 136, "12V")
    s.diode_v(800, 160, 268, [("D1", True), "1N4004"])
    s.wire([(800, 136), (800, 160)], "12V")
    s.text(800, 280, "-> Mega VIN", 8, True, NETS["12V"][0], anchor="r")
    s.para(540, 296, ["'11A' input (heated bed, through RAMPS F2): not used.",
                      "Fuses: PSU 5 A max; RAMPS F1 5 A (all 4 drivers + Mega VIN).",
                      "Revision 2026-10-08.1: no separate key-branch fuse."], 8, color=GREY)

    # 5 V
    s.board(24, 346, 796, 166, "5 V logic (VIO) - from the Mega", "ref",
            "VIO powers only each driver's I/O pins; its logic runs from its own VM (12 V)")
    s.rect(40, 384, 112, 66, fill=FILL["module"], r=3)
    s.para(46, 398, [("Arduino Mega 2560", True), "5 V from USB, or its", "regulator (from VIN)"], 8)
    s.wire([(152, 404), (790, 404)], "5V")
    s.text(160, 399, "+5 V rail (RAMPS VCC)", 8, True, NETS["5V"][0])
    taps = [(320, "VIO of X, Y, Z, E0", "sheets 3, 4"), (520, "MS1 / MS2 jumpers", "sheets 3, 4"),
            (710, "endstop headers' '+' pins", "sheet 6")]
    for x, t1, t2 in taps:
        s.dot(x, 404, "5V")
        s.wire([(x, 404), (x, 424)], "5V")
        s.text(x, 436, t1, 8, anchor="c")
        s.text(x, 447, t2, 8, color=GREY, anchor="c")
    s.wire([(96, 450), (96, 462)], "GND")
    s.gnd(96, 462)
    s.para(40, 486, ["All four drivers get VIO from the same 5 V rail in their sockets (revision 2026-10-08.1): no 5 V over a cable any more.",
                     "Power order: USB first (Mega + every VIO), then 12 V. Off: 12 V first. The firmware waits until all 4 drivers answer."], 8)


# ====================================================================== sheets 3, 4
def driver_column(s, x0, sock, title, motor_name, addr, ms1, ms2, step, dirn, en, diag_hdr, diag_pin):
    """One RAMPS socket with its BTT TMC2209 V1.3 and motor; column ~395 pt wide."""
    s.text(x0, 70, f"Socket {sock} - {title}", 11, True)
    s.text(x0, 83, f"UART address {addr} - BTT TMC2209 V1.3 with the DIAG mod", 8, color=GREY)
    bx, by, bw = x0 + 150, 140, 116
    left = [("EN", "EN"), ("MS1", "MS1"), ("MS2", "MS2"), ("PDN", "PDN_UART [MS3]"),
            ("TX", "TX [RST]"), ("CLK", "CLK [SLP]"), ("STEP", "STEP"), ("DIR", "DIR"),
            None, ("DIAG", "DIAG *"), ("INDEX", "INDEX *")]
    right = [("VM", "VM [VMOT]"), ("G1", "GND"), ("A2", "A2 [2B]"), ("A1", "A1 [2A]"),
             ("B1", "B1 [1A]"), ("B2", "B2 [1B]"), ("VIO", "VIO [VDD]"), ("G2", "GND")]
    p, h = s.ic(bx, by, bw, left, right, pitch=21, pad=13)
    s.text(bx + bw / 2, by - 6, "BTT TMC2209 V1.3", 9, True, anchor="c")
    s.text(bx + bw - 4, by + h - 8, "* top-edge pins", 8, color=GREY, anchor="r")
    ctrl = NETS["CTRL"][0]
    x, y = p["EN"]
    s.wire([(x, y), (x0 + 50, y)], "CTRL")
    s.text(x0, y + 3, f"{en}", 8, True, ctrl)
    s.dot(x0 + 112, y, "CTRL")
    s.res_v(x0 + 112, y - 34, y, "5V", "10 k (on RAMPS)")
    s.flag(x0 + 112, y - 34, "+5 V", "5V")
    for key, fitted in (("MS1", ms1), ("MS2", ms2)):
        x, y = p[key]
        s.wire([(x, y), (x0 + 93, y)], "TIE")
        s.jumper(x0 + 90, y, fitted)
        s.text(x0 + 100, y - 4, "jumper ON" if fitted else "no jumper", 8, True, INK if fitted else GREY)
    x, y = p["PDN"]
    s.wire([(x, y), (x0 + 104, y)], "UART")
    s.offpage(x0 + 104, y, "UART bus (sheet 6)", "UART", side="l")
    xt, yt = p["TX"]; xc, yc = p["CLK"]
    s.wire([(xt, yt), (x0 + 126, yt), (x0 + 126, yc), (xc, yc)], "TIE")
    s.dot(x0 + 126, yc, "TIE")
    s.text(x0 + 120, (yt + yc) / 2 + 3, "RAMPS ties RST-SLP", 8, color=GREY, anchor="r")
    for key, lab in (("STEP", step), ("DIR", dirn)):
        x, y = p[key]
        s.wire([(x, y), (x0 + 50, y)], "CTRL")
        s.text(x0, y + 3, lab, 8, True, ctrl)
    x, y = p["DIAG"]
    s.wire([(x, y), (x0 + 120, y)], "DIAG")
    s.offpage(x0 + 120, y, f"{diag_hdr} S = {diag_pin} (sheet 6)", "DIAG", side="l")
    x, y = p["INDEX"]
    s.nc(x - 3, y)
    s.text(x - 10, y + 3, "cut off", 8, color=GREY, anchor="r")
    x, y = p["VM"]
    s.tag(x, y, "+12 V", "12V")
    for k in ("G1", "G2"):
        s.tag(*p[k], "GND", "GND")
    s.tag(*p["VIO"], "+5 V", "5V")
    hx = bx + bw + 22
    ys = [p[k][1] for k in ("A2", "A1", "B1", "B2")]
    s.rect(hx, ys[0] - 9, 15, ys[3] - ys[0] + 18, fill="#FFFFFF", lw=1.2)
    for i, k in enumerate(("A2", "A1", "B1", "B2")):
        s.wire([p[k], (hx, ys[i])], "MOTOR")
        s.text(hx + 7.5, ys[i] + 3, str(i + 1), 8, True, anchor="c")
    r = s.motor_r(ys)
    s.motor(hx + 15 + 6 + r, (ys[0] + ys[3]) / 2, ys, hx + 15, [(motor_name, True), f"{sock} motor header"])
    s.para(x0, by + h + 22, [
        (f"Jumpers under socket {sock}: MS1 {'ON' if ms1 else 'off'}, MS2 {'ON' if ms2 else 'off'}, "
         "MS3 off (never fit MS3)", True),
        "UART lead: clipped onto the MS3 jumper pin, signal side (sheet 5).",
        f"STEP {step} - DIR {dirn} - EN {en}. The RAMPS pull-up keeps the driver",
        "off until the firmware pulls EN low.",
        f"DIAG lead (the mod, sheet 5) -> {diag_hdr} S pin: {diag_pin}, an interrupt pin.",
        "Motor 17HE19-2004S: header pins 1-2 = one coil, 3-4 = the other.",
    ], 8)


def sheet_dials_ab(s):
    driver_column(s, 24, "X", "dial A (top-left)", "Motor A", 0, False, False, "D54", "D55", "D38", "X_MIN", "D3")
    s.line([(418, 64), (418, 450)], "#BBBBBB", 0.8, dash=[3, 3])
    driver_column(s, 430, "Y", "dial B (top-right)", "Motor B", 1, True, False, "D60", "D61", "D56", "X_MAX", "D2")
    s.para(24, 468, [
        "[ ] = the RAMPS / StepStick socket name of that pin. Fit each driver with EN, DIR, VM and GND matching the RAMPS silkscreen: a reversed driver is destroyed.",
        "The BTT V1.3 puts PDN_UART in the socket's MS3 position. TX: R10 is not fitted, so TX connects to nothing. Don't bridge R10.",
        "CLK: the RAMPS ties the socket's RST and SLP pins (= TX and CLK on the V1.3). With R10 open, CLK sees only its 20 k pull-down -> internal clock.",
        "Motor currents are set over UART: 1.0 A RMS, hold 0.5 A. If a motor buzzes instead of turning, swap the middle two wires in its plug.",
    ], 8)


def sheet_dial_c_key(s):
    driver_column(s, 24, "Z", "dial C (bottom)", "Motor C", 2, False, True, "D46", "D48", "D62", "Z_MIN", "D18")
    s.line([(418, 64), (418, 450)], "#BBBBBB", 0.8, dash=[3, 3])
    driver_column(s, 430, "E0", "the key turner", "Key motor", 3, True, True, "D26", "D28", "D24", "Z_MAX", "D19")
    s.para(24, 468, [
        ("Revision 2026-10-08.1: the key driver is an ordinary driver in the RAMPS E0 socket, like the dials.", True),
        "E0 address 3 = MS1 + MS2 jumpers ON. The key's STEP/DIR/EN are D26/D28/D24 (Marlin pins_RAMPS.h E0_STEP/DIR/ENABLE).",
        "The key motor's own ~1 m cable plugs into the E0 motor header. Use it as supplied; shorten it only if the key's StallGuard reads too dull (bench stage 5).",
        "Key current: 0.6 A RMS to start, hold 0.3 A. E0's MS3 jumper pin and DIAG mod are VERIFY items (bench stages 1, 3) like the dials'.",
    ], 8)


def sheet_details(s):
    # --- DIAG mod detail (top view, not to scale)
    x0 = 24
    s.text(x0, 70, "DIAG mod (all four drivers)", 11, True)
    s.text(x0, 83, "BTT TMC2209 V1.3 seen from above - not to scale", 8, color=GREY)
    bx, by, bw, bh = x0 + 66, 146, 112, 170
    s.rect(bx, by, bw, bh, stroke=INK, fill="#3F6E3F", lw=1.2, r=3)
    s.rect(bx + 26, by + 46, 60, 60, stroke="#BBBBBB", fill="#555555", lw=0.8)
    s.text(bx + 56, by + 80, "chip", 8, True, "#FFFFFF", anchor="c")
    lnames = ["EN", "MS1", "MS2", "RX", "TX", "CLK", "STEP", "DIR"]
    rnames = ["VM", "GND", "A2", "A1", "B1", "B2", "VIO", "GND"]
    for i in range(8):
        py = by + 16 + i * 20
        s.circle(bx + 9, py, 4, stroke="#DDDDDD", fill="#C9A227", lw=0.8)
        s.circle(bx + bw - 9, py, 4, stroke="#DDDDDD", fill="#C9A227", lw=0.8)
        s.text(bx - 6, py + 3, lnames[i], 8, anchor="r")
        s.text(bx + bw + 6, py + 3, rnames[i], 8)
    s.circle(bx + 72, by + 16, 7, stroke="#DDDDDD", fill="#B0B0B0", lw=0.8)
    s.text(bx + 72, by + 36, "pot", 8, True, "#FFFFFF", anchor="c")
    ix, dx_ = bx + 27, bx + 45
    for px in (ix, dx_):
        s.circle(px, by + 16, 4, stroke="#DDDDDD", fill="#C9A227", lw=0.8)
    s.text(ix - 6, by - 6, "INDEX", 8, True, anchor="r")
    s.line([(ix - 4, by - 4), (ix, by + 12)], GREY, 0.8)
    s.wire([(dx_, by + 16), (dx_, by - 30), (x0 + 280, by - 30)], "DIAG")
    s.dot(dx_, by + 16, "DIAG")
    s.text(dx_ + 4, by - 34, "half an F-F jumper, soldered on top", 8, True, NETS["DIAG"][0])
    s.text(x0 + 284, by - 27, "-> endstop S pin", 8, True, NETS["DIAG"][0])
    s.text(dx_ + 4, by - 9, "DIAG", 8, True)
    s.para(x0 + 210, by + 4, [("Steps (before the heatsink):", True),
                             "1. Cut the two pins that point DOWN",
                             "   (INDEX, DIAG) flush with their spacer.",
                             "2. Strip and tin half an F-F jumper.",
                             "3. Solder it to the TOP joint of DIAG:",
                             "   2nd pin from the EN corner",
                             "   (silkscreen 'DIAG').",
                             "4. Keep the iron off the trimmer pot",
                             "   next to it.",
                             ("VERIFY which pin is DIAG: bring-up", True, WARN),
                             ("stage 3 (`ping` + a hand stall).", True, WARN),
                             "Revision 2026-10-08.1: all four",
                             "drivers get this mod (the key too)."], 8)
    # --- UART tap detail
    ty = 350
    s.text(x0, ty, "UART tap: the MS3 jumper pin (each socket)", 11, True)
    s.text(x0, ty + 13, "RAMPS jumper block under a driver socket - not to scale", 8, color=GREY)
    jx, jy = x0 + 70, ty + 46
    s.rect(jx - 14, jy - 12, 64, 84, stroke=GREY, fill=FILL["ref"], lw=0.8, r=3)
    for i, nm in enumerate(["MS1", "MS2", "MS3"]):
        py = jy + 8 + i * 24
        s.rect(jx - 4, py - 4, 8, 8, fill="#C9A227", lw=0.8)
        s.rect(jx + 26, py - 4, 8, 8, fill="#C9A227", lw=0.8)
        s.text(jx - 20, py + 3, nm, 8, True, anchor="r")
    s.text(jx, jy - 16, "signal", 8, anchor="c")
    s.text(jx + 30, jy - 16, "+5 V", 8, True, NETS["5V"][0], anchor="c")
    py3 = jy + 8 + 2 * 24
    s.wire([(jx, py3), (jx, py3 + 30), (jx + 90, py3 + 30)], "UART")
    s.dot(jx, py3, "UART")
    s.text(jx + 94, py3 + 33, "F-F jumper -> hub BUS pin (sheet 6)", 8, True, NETS["UART"][0])
    s.para(jx + 60, jy + 4, ["Pads 1, 3, 5 = MS1, MS2, MS3 of the socket;",
                             "pads 2, 4, 6 = +5 V (RAMPS KiCad netlist).",
                             "Signal side = nearer the driver's EN / STEP / DIR row.",
                             ("VERIFY on your Fasizi board: `ping` (bring-up",
                              True, WARN), ("stage 1). The wrong pin is +5 V: harmless.", True, WARN),
                             ("Never fit a jumper on MS3.", True, WARN),
                             "All four sockets (X, Y, Z, E0) tap here."], 8)
    # right column: the key motor cable (the only inter-unit wire)
    kx = 470
    s.text(kx, 70, "Key motor cable (the only wire between the units)", 11, True)
    s.text(kx, 83, "revision 2026-10-08.1", 8, color=GREY)
    s.board(kx, 100, 330, 150, "Key turner -> dial unit", "ref",
            "the motor's own ~1 m cable, 4 wires + connector")
    s.circle(kx + 60, 175, 22, fill="#FFFFFF", lw=1.5)
    s.text(kx + 60, 180, "M", 14, True, anchor="c")
    s.text(kx + 60, 210, "key motor", 8, True, anchor="c")
    for i in range(4):
        yy = 150 + i * 16
        s.wire([(kx + 82, yy), (kx + 250, yy)], "MOTOR")
        s.text(kx + 255, yy + 3, f"coil wire {i + 1}", 8)
    s.rect(kx + 250, 138, 56, 74, stroke=INK, fill="#FFFFFF", lw=1.0, r=3)
    s.text(kx + 278, 150, "E0", 9, True, anchor="c")
    s.text(kx + 278, 163, "motor", 8, anchor="c")
    s.text(kx + 278, 174, "header", 8, anchor="c")
    s.text(kx + 278, 192, "on the", 8, color=GREY, anchor="c")
    s.text(kx + 278, 203, "RAMPS", 8, color=GREY, anchor="c")
    s.para(kx, 270, [
        "Plugs into the E0 motor header like a dial motor.",
        "Use the supplied ~1 m cable as it is; shorten it only if the key's",
        "StallGuard reads too dull to find the stop (bench stage 5).",
        ("Never plug or unplug it with 12 V on.", True, WARN),
        "If the motor buzzes instead of turning, swap its middle two wires.",
        "",
        ("Revision 2026-10-08.1 replaced the 6-conductor inter-unit signal", True),
        ("cable and the remote driver board with this one motor cable.", True),
    ], 8)


# ====================================================================== sheet 6
def sheet_signals(s):
    P, Y0 = 19, 134
    row = lambda i: Y0 + i * P
    rows = [
        (0, "D15", "S", "TIE"), (1, "GND", "-", "GND"), (2, "+5 V", "+", "5V"),
        (4, "D17 RX2", "17", "UART"), (5, "D16 TX2", "18", "UART"),
        (8, "D19 (irq)", "S", "DIAG"),
        (10, "D3 (irq)", "S", "DIAG"), (11, "D2 (irq)", "S", "DIAG"), (12, "D18 (irq)", "S", "DIAG"),
        (14, "D14", "S", "CTRL"), (15, "GND", "-", "GND"),
        (17, "D13", None, "CTRL"),
    ]
    s.board(24, 72, 222, 436, "RAMPS 1.4 on the Mega", "ref", "endstop headers: S signal, - GND, + 5 V")
    mx, mw = 40, 76
    s.rect(mx, row(0) - 14, mw, row(17) - row(0) + 28, fill=FILL["module"], lw=1.3)
    s.text(mx + mw / 2, row(0) - 19, "Mega 2560", 9, True, anchor="c")
    hx, hw = 164, 62
    for a_, b_, name in [(0, 2, "Y_MAX"), (4, 5, "AUX-4"), (8, 8, "Z_MAX"), (10, 10, "X_MIN"),
                         (11, 11, "X_MAX"), (12, 12, "Z_MIN"), (14, 15, "Y_MIN")]:
        s.rect(hx, row(a_) - 8.5, hw, row(b_) - row(a_) + 17, fill="#FFFFFF", lw=1.3)
        s.text(hx + 5, (row(a_) + row(b_)) / 2 + 3, name, 8, True)
    hdr = {}
    for i, mlab, hlab, net in rows:
        y = row(i)
        s.text(mx + mw - 4, y + 3, mlab, 8, anchor="r")
        s.line([(mx + mw, y), (mx + mw + 8, y)], INK, 1.0)
        if hlab is None:
            s.line([(mx + mw + 8, y), (mx + mw + 24, y)], NETS[net][0], 0.9)
            s.text(mx + mw + 28, y + 3, "on-board LED 'L' (status)", 8)
            continue
        s.line([(mx + mw + 8, y), (hx, y)], NETS[net][0], 0.9)
        s.text(hx + hw - 6, y + 3, hlab, 8, True, anchor="r")
        s.line([(hx + hw, y), (hx + hw + 8, y)], INK, 1.0)
        hdr[i] = (hx + hw + 8, y)
    s.text(mx + mw + 12, row(6) + 3, "RAMPS traces", 8, color=GREY)
    s.nc(hdr[0][0] + 4, hdr[0][1])
    s.text(hdr[0][0] + 11, hdr[0][1] + 3, "spare", 8, color=GREY)
    # DIAG leads come IN from the drivers (short arrows, left of the hub)
    for i, lab in ((8, "key DIAG (sheet 4)"), (10, "dial A DIAG (sheet 3)"),
                   (11, "dial B DIAG (sheet 3)"), (12, "dial C DIAG (sheet 4)")):
        x, y = hdr[i]
        s.wire([(x, y), (x + 12, y)], "DIAG")
        s.offpage(x + 12, y, lab, "DIAG")
    # start/stop button on Y_MIN
    xs, ys = hdr[14]; xg, yg = hdr[15]
    s.wire([(xs, ys), (xs + 30, ys)], "CTRL")
    s.wire([(xg, yg), (xg + 12, yg), (xg + 12, yg + 24), (xs + 30, yg + 24)], "GND")
    s.button_v(xs + 30, ys, yg + 24, [("S1", True), "start / stop"])

    # ---- hub board = UART junction only (top-right) ----
    hb_x, hb_y, hb_w, hb_h = 470, 72, 350, 226
    s.board(hb_x, hb_y, hb_w, hb_h, "Hub board (you build) - the UART junction", "build",
            "just R1 and the bus node (revision 2026-10-08.1)")
    px = hb_x + 70                     # male-pin column
    def hy(k): return hb_y + 50 + k * 24
    labels = ["TX2", "BUS", "BUS", "BUS", "BUS", "BUS"]   # k0 TX2 (via R1), k1 RX2, k2..5 X/Y/Z/E0 PDN
    s.rect(px, hy(0) - 9, 34, hy(5) - hy(0) + 18, fill="#FFFFFF", lw=1.3)
    for k, lab in enumerate(labels):
        y = hy(k)
        s.text(px + 17, y + 3, lab, 8, True, anchor="c")
        s.line([(px - 6, y), (px, y)], INK, 1.0)
        s.line([(px + 34, y), (px + 40, y)], INK, 1.0)
    # TX2 and RX2 from the Mega (long traces across)
    s.wire([hdr[5], (hdr[5][0] + 10, hdr[5][1]), (hdr[5][0] + 10, hy(0)), (px - 6, hy(0))], "UART")
    s.wire([hdr[4], (hdr[4][0] + 18, hdr[4][1]), (hdr[4][0] + 18, hy(1)), (px - 6, hy(1))], "UART")
    s.text(px - 44, hy(0) + 3, "<- D16", 8, NETS["UART"][0])
    s.text(px - 44, hy(1) + 3, "<- D17", 8, NETS["UART"][0])
    # the four PDN taps come in from the left as offpage arrows
    for k, (sock, sh) in enumerate([("X", 3), ("Y", 3), ("Z", 4), ("E0", 4)], start=2):
        s.wire([(px - 6, hy(k)), (px - 10, hy(k))], "UART")
        s.offpage(px - 10, hy(k), f"{sock} MS3 pin (sheet {sh})", "UART", side="l")
    # R1 on TX2 -> bus node; everything else straight to the bus node
    xr, xn = px + 40, hb_x + hb_w - 60
    s.wire([(xr, hy(0)), (xr + 6, hy(0))], "UART")
    s.res_h(xr + 6, xr + 70, hy(0), "UART", "R1 1 kOhm")
    s.wire([(xr + 70, hy(0)), (xn, hy(0))], "UART")
    for k in range(1, 6):
        s.wire([(xr, hy(k)), (xn, hy(k))], "UART")
        s.dot(xn, hy(k), "UART")
    s.wire([(xn, hy(0)), (xn, hy(5))], "UART")
    s.dot(xn, hy(0), "UART")
    s.text(xn - 4, hy(5) + 18, "bus node", 8, True, NETS["UART"][0], anchor="c")

    # ---- notes (lower-right, clear of the DIAG arrows on the left) ----
    s.para(470, 320, [("Notes", True),
        "One 1 kOhm in total: TX2 -> R1 -> bus. RX2 and every driver's PDN_UART",
        "sit straight on the bus (TMC2209 datasheet Fig. 4.1). The Mega hears",
        "its own transmissions; TMCStepper skips that echo. SENDDELAY >= 2.",
        "Addresses by MS1 / MS2: X 0, Y 1, Z 2, E0 (key) 3. Bus at 115200 baud.",
        "(irq) = an interrupt pin. DIAG is a pulse: the firmware latches it with",
        "attachInterrupt on D2, D3, D18, D19 (Arduino interrupt numbers 0,1,5,4).",
        "Inputs use the Mega's internal pull-ups: an unplugged DIAG reads high =",
        "'stalled', so the firmware refuses to move (fail safe).",
        "Button S1 (Y_MIN): pauses a run; resumes or starts one when idle.",
        ("Revision 2026-10-08.1: the hub is only the UART junction now - no 12 V,", True),
        ("no fuse, no Phoenix header, no key STEP (key STEP is D26 in E0).", True),
        "STEP / DIR / EN of all four drivers: sheets 3, 4."], 8)


# ====================================================================== sheet 7
def sheet_tables(s):
    def table(x, y, cols, widths, rows, title):
        s.text(x, y, title, 10, True)
        y += 7
        rh = 13
        s.rect(x, y, sum(widths), rh, stroke=GREY, fill="#DDE5F0", lw=0.6)
        cx = x
        for col, wdt in zip(cols, widths):
            s.text(cx + 4, y + rh - 4, col, 8, True)
            cx += wdt
        y += rh
        for i, r in enumerate(rows):
            if i % 2:
                s.rect(x, y, sum(widths), rh, stroke="#F3F6FA", fill="#F3F6FA", lw=0.1)
            cx = x
            for v, wdt in zip(r, widths):
                v = (v,) if isinstance(v, str) else v
                s.text(cx + 4, y + rh - 4, v[0], 8, v[1] if len(v) > 1 else False, v[2] if len(v) > 2 else INK)
                cx += wdt
            y += rh
        s.rect(x, y - rh * (len(rows) + 1), sum(widths), rh * (len(rows) + 1), stroke=GREY, lw=0.6)
        return y

    pin_rows = [
        ("Dial A STEP / DIR / EN", "D54 / D55 / D38", "RAMPS X socket"),
        ("Dial B STEP / DIR / EN", "D60 / D61 / D56", "RAMPS Y socket"),
        ("Dial C STEP / DIR / EN", "D46 / D48 / D62", "RAMPS Z socket"),
        ("Key STEP / DIR / EN", "D26 / D28 / D24", "RAMPS E0 socket"),
        ("Dial A DIAG", "D3 (interrupt)", "X_MIN header, S"),
        ("Dial B DIAG", "D2 (interrupt)", "X_MAX header, S"),
        ("Dial C DIAG", "D18 (interrupt)", "Z_MIN header, S"),
        ("Key DIAG", "D19 (interrupt)", "Z_MAX header, S (E0 DIAG mod)"),
        ("UART TX2", "D16", "AUX-4 pin 18 -> hub R1"),
        ("UART RX2", "D17", "AUX-4 pin 17 -> hub bus"),
        ("Drivers' PDN_UART", "-", "MS3 jumper pins X,Y,Z,E0 -> bus"),
        ("Start / stop button", "D14 (pull-up)", "Y_MIN header, S and -"),
        ("Status LED", "D13", "on-board LED 'L'"),
        ("Spare", "D15 / D23", "Y_MAX S / AUX-4 16"),
        ("USB serial (the log)", "D0 / D1", "USB: keep free"),
    ]
    table(24, 70, ["Function", "Mega pin", "Where it connects"], [138, 94, 178], pin_rows,
          "Pin map (control/wiring.md 1; Marlin pins_RAMPS.h) - revision 2026-10-08.1")
    jmp = [("X", "A (top-left)", "off", "off", "off", "0"),
           ("Y", "B (top-right)", "ON", "off", "off", "1"),
           ("Z", "C (bottom)", "off", "ON", "off", "2"),
           ("E0", "key", "ON", "ON", "off", "3")]
    table(452, 70, ["Socket", "Role", "MS1", "MS2", "MS3", "Address"], [50, 82, 48, 48, 48, 50], jmp,
          "Driver jumpers and UART addresses (2)")
    s.text(452, 157, "Never fit an MS3 jumper. Socket E1 stays empty.", 8, True, WARN)
    cur = [("Dials A, B, C", "1.0 A RMS", "0.5 A", "until the dial torque is measured"),
           ("Key", "0.6 A RMS", "0.3 A", "then 2 x the measured minimum, <= 1.0 A"),
           ("Firmware ceiling", "1.2 A", "-", "BTT: active cooling above 1.2 A")]
    table(452, 180, ["Driver", "Run", "Hold", "Why"], [78, 58, 38, 178], cur, "Motor currents, set over UART (7)")
    HAVE = ("have", False, GREY)
    ORDERED = ("ordered", False, INK)
    parts = [("Hub", "R1", "1 kOhm: the only UART resistor (TX2 -> bus)", HAVE),
             ("Hub", "-", "male pins x 6: 5V BUS TX2 BUS BUS BUS (UART only)", HAVE),
             ("PSU", "-", "DC jack 5.5 x 2.1 mm -> screw terminal, -> RAMPS 5A", ORDERED),
             ("PSU", "-", "20 AWG red + black, adapter -> RAMPS 5A terminal", ORDERED),
             ("RAMPS", "S1", "7 mm push button (start / stop)", HAVE),
             ("Wiring", "-", "F-F jumpers, ~20 x 10-20 cm", ORDERED),
             ("Key", "-", "the motor's own ~1 m cable -> E0 motor header", HAVE),
             ("Hub", "-", "perfboard (kit): a few cm square", HAVE)]
    yp = table(452, 262, ["Where", "Ref", "Part", "Status"], [48, 28, 252, 42], parts,
               "Parts you fit (5, 10) - full list: docs/bom.md")
    s.para(452, yp + 13, ["Revision 2026-10-08.1 removed the remote driver board, the 6-conductor",
                          "cable + Phoenix connectors, the hub 12 V branch + fuse, and C1a/C1b.",
                          "RAMPS F1, F2, D1, the six 100 uF and the 10 k pull-ups are on the RAMPS."], 8, color=GREY)
    s.text(24, 330, "Power order (8)", 10, True)
    s.para(24, 345, ["1. Make every connection with power off (USB unplugged, 12 V off).",
                     "2. Before the first power-up: every driver's VREF pot to minimum.",
                     "3. Power up: USB first, then 12 V.   4. Power down: 12 V first, then USB.",
                     "5. Never plug or unplug a motor with 12 V on (the key motor cable too).",
                     "6. Emergency stop: pull the 12 V plug."], 8)
    s.text(24, 426, "VERIFY on the bench (control/bringup.md)", 10, True)
    s.para(24, 441, ["Which MS3 jumper pin is the signal side (stage 1, `ping`), all four sockets.",
                     "Which top-edge pin is DIAG (stage 3).   The key answers at address 3 (E0).",
                     "The key's StallGuard through the 1 m motor cable (stage 5); shorten if dull.",
                     "Multimeter: DC-jack + / - before the first power-up.",
                     "Sources: control/wiring.md - Marlin pins_RAMPS.h, TMC2209 datasheet rev 1.09,",
                     "BTT TMC2209 V1.3 manual + schematic, RAMPS 1.4 KiCad netlist."], 8)


SHEETS = [
    ("Overview", "What connects to what. Each block is drawn in full on the sheet named in it.", sheet_overview),
    ("Power: 12 V, 5 V, GND", "12 V goes from the PSU straight into the RAMPS '5A' input (its own 5 A fuse feeds all "
     "four drivers). 5 V logic comes from the Mega.", sheet_power),
    ("Drivers A and B on the RAMPS", "[ ] = the RAMPS socket name of that pin. All connections to the left are on "
     "the RAMPS or by jumper.", sheet_dials_ab),
    ("Dial driver C and the key driver (E0)", "The key driver is an ordinary driver in the E0 socket "
     "(revision 2026-10-08.1).", sheet_dial_c_key),
    ("DIAG-mod and UART-tap details; the key motor cable", None, sheet_details),
    ("Mega + RAMPS headers, hub (UART bus)", "Thin lines = RAMPS traces. Thick lines = your jumper wires "
     "(F-F, 10-20 cm) and hub-board wiring.", sheet_signals),
    ("Pin map, jumpers, currents, parts", None, sheet_tables),
]


def main(out):
    c = canvas.Canvas(out, pagesize=(W, H), initialFontName="F", initialFontSize=MIN_PT)
    c.setTitle("Fichet safe robot - wiring schematic")
    c.setAuthor("Claude, for Paul")
    c.setSubject(f"Wiring, drawn from control/wiring.md, revision {REV}")
    for i, (title, note, fn) in enumerate(SHEETS, 1):
        fn(Sheet(c, i, len(SHEETS), title, note))
        c.showPage()
    c.save()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "schematic.pdf"))
