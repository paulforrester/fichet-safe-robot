#!/usr/bin/env python3
"""Wiring schematic of the Fichet safe robot -> control/harness/schematic.pdf

A4 landscape, colour, 7 sheets. Every connection is from control/wiring.md
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
DATE = "2026-10-07"
REV = "5"
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
        self.text(bx + 6, by + 56, f"{DATE} · rev {REV} · from control/wiring.md (harness v1)", 8, color=GREY)
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
    s.rect(138, 72, 470, 318, stroke=blue, lw=1.5, dash=[6, 3], r=6)
    s.text(146, 87, "DIAL UNIT  (on the door, over the 3 dial holes)", 9, True, blue)
    s.rect(624, 72, 196, 318, stroke=blue, lw=1.5, dash=[6, 3], r=6)
    s.text(634, 87, "KEY TURNER  (over the key)", 9, True, blue)

    def blk(x, y, w, h, title, rows, kind="module"):
        s.rect(x, y, w, h, stroke=INK, fill=FILL[kind], lw=1.1, r=3)
        s.text(x + 6, y + 14, title, 9, True)
        s.para(x + 6, y + 27, rows, 8)

    blk(20, 100, 96, 58, "Mac (USB)", ["logger.py, Arduino IDE", "USB-C → USB-B"], "ref")
    blk(20, 286, 96, 70, "Power supply", ["Ledmo HTY-1200500", "12 V, 5 A max", "5.5 × 2.1 mm, centre +"], "ref")
    blk(150, 98, 142, 64, "Arduino Mega 2560 R3", ["the controller", "sheets 2, 5"])
    blk(150, 178, 142, 94, "RAMPS 1.4 (on the Mega)", ["X, Y, Z driver sockets", "endstop + AUX-4 headers",
                                                       "5 A input fuse, D1 → VIN", "sheets 2, 3, 4, 5"])
    blk(316, 98, 128, 174, "Dial drivers × 3", ["BTT TMC2209 V1.3", "in RAMPS X, Y, Z", "",
                                                  "X = dial A (top-left)", "Y = dial B (top-right)",
                                                  "Z = dial C (bottom)", "", "UART addresses 0, 1, 2",
                                                  "DIAG mod", "sheets 3, 4"])
    blk(468, 98, 124, 174, "Dial motors × 3", ["17HE19-2004S", "on the RAMPS X, Y, Z", "motor headers", "",
                                                 "14T → 28T gears", "turn the dial plugs", "", "sheets 3, 4"])
    blk(150, 290, 294, 86, "Hub board (you build)", ["12 V split: RAMPS, and the key branch through F1 (PTC 1.1 A)",
                                                      "UART bus node, R1 1 kΩ (the only UART resistor)",
                                                      "jumpers for key STEP / DIAG, 5 V, GND",
                                                      "J3: 8-pin Phoenix header for the cable · sheets 2, 5"], "build")
    blk(640, 98, 166, 150, "Remote driver board", ["(you build)", "BTT TMC2209 V1.3, address 3",
                                                    "EN, DIR, CLK → GND", "MS1, MS2 → +5 V", "C1 100 µF on VM",
                                                    "J1: 8-pin Phoenix", "sheet 6"], "build")
    blk(640, 272, 166, 64, "Key motor", ["17HE19-2004S", "on the key axis · sheet 6"])

    def lab(x, y, t, net):
        s.text(x, y, t, 8, True, NETS[net][0])

    s.wire([(116, 128), (150, 128)], "5V")
    lab(116, 122, "USB", "5V")
    s.wire([(116, 320), (150, 320)], "12V")
    lab(116, 314, "12 V", "12V")
    s.wire([(221, 162), (221, 178)], "CTRL")
    s.wire([(292, 214), (316, 214)], "CTRL")
    lab(294, 208, "STEP", "CTRL")
    s.wire([(444, 214), (468, 214)], "MOTOR")
    s.wire([(221, 272), (221, 290)], "UART")
    s.wire([(300, 290), (300, 280), (380, 280), (380, 272)], "UART")
    # cable: hub -> remote board
    s.wire([(444, 326), (458, 326)], "12V")
    s.wire([(444, 333), (458, 333)], "UART")
    s.wire([(598, 326), (612, 326), (612, 190), (640, 190)], "12V")
    s.wire([(598, 333), (619, 333), (619, 197), (640, 197)], "UART")
    s.rect(458, 312, 140, 34, stroke=INK, fill="#FFFFFF", lw=1.0, r=3)
    s.text(528, 326, "Inter-unit cable, ~300 mm", 8, True, anchor="c")
    s.text(528, 338, "6 cores + shield · sheet 6", 8, anchor="c")
    s.wire([(760, 248), (760, 272)], "MOTOR")

    y = 410
    s.text(24, y, "Sheets", 10, True)
    s.para(24, y + 15, ["1  Overview (this sheet)", "2  Power: 12 V, 5 V, GND", "3  Dial drivers A and B on the RAMPS",
                        "4  Dial driver C; DIAG-mod and UART-tap details",
                        "5  Mega + RAMPS headers, hub board, UART bus", "6  Inter-unit cable and key turner",
                        "7  Pin map, jumpers, currents, parts"], 8)
    s.text(300, y, "Rules", 10, True)
    s.para(300, y + 15, ["Make every connection with power off (USB unplugged, 12 V off).",
                         "Never plug or unplug a motor or the cable with 12 V on.",
                         "Power up: USB first, then 12 V. Power down: 12 V first.",
                         "Never fit an MS3 jumper: on the V1.3 that pin is the UART line.",
                         "Emergency stop: pull the 12 V plug.  `!` aborts a move.",
                         "VERIFY = not yet checked on the bench (control/bringup.md).",
                         "Line colour = what a net does. Sheet 6 shows the cable's own colours.",
                         "If this disagrees with control/wiring.md, wiring.md wins."], 8)


# ====================================================================== sheet 2
def sheet_power(s):
    # PSU and DC jack
    s.rect(24, 112, 94, 72, fill=FILL["ref"], r=3)
    s.para(30, 126, [("PSU", True), "Ledmo HTY-1200500", "12 V, 5 A max", "5.5 × 2.1, centre +"], 8)
    s.rect(136, 116, 72, 64, fill=FILL["module"], r=3)
    s.para(142, 130, [("DC jack", True), "5.5 × 2.1 →", "screw terminal", ("VERIFY + / −", True, WARN)], 8)
    s.wire([(118, 136), (136, 136)], "12V")
    s.wire([(118, 170), (136, 170)], "GND")
    s.para(24, 210, [("Not the Mega's own barrel", True, WARN), ("jack: that feeds only the", True, WARN),
                     ("Mega (VIN). The drivers get", True, WARN), ("12 V only through the", True, WARN),
                     ("RAMPS '5A' input; D1 passes", True, WARN), ("power from there to the", True, WARN),
                     ("Mega, never back.", True, WARN)], 8)

    # hub board, power part
    s.board(222, 72, 286, 262, "Hub board (you build) — power", "build", "12V IN, 12V OUT: 20 AWG red + black pairs")
    s.wire([(208, 136), (290, 136)], "12V")
    s.wire([(208, 170), (270, 170)], "GND")
    s.text(212, 131, "+", 9, True, NETS["12V"][0])
    s.text(212, 165, "−", 9, True)
    s.text(230, 150, "12V IN", 8, True)
    s.dot(290, 136, "12V")
    s.dot(270, 170, "GND")
    s.wire([(290, 136), (546, 136)], "12V")
    s.text(398, 131, "12V OUT +  →  RAMPS '5A' +", 8, True, NETS["12V"][0], anchor="c")
    s.wire([(270, 170), (546, 170)], "GND")
    s.text(398, 165, "12V OUT −  →  RAMPS '5A' −", 8, True, anchor="c")
    # key branch: + down (hop over GND), PTC, J3-1
    s.vwire_hop(290, 136, 236, [170], "12V")
    s.wire([(290, 236), (300, 236)], "12V")
    s.ptc_h(300, 420, 236, "hub F1: PTC 1.1 A hold, ≥ 16 V")
    s.wire([(420, 236), (434, 236)], "12V")
    s.wire([(270, 170), (270, 290)], "GND")
    s.wire([(270, 254), (434, 254)], "GND")
    s.dot(270, 254, "GND")
    s.wire([(270, 290), (434, 290)], "GND")
    j3, _ = s.conn(440, 226, ["1", "2", "4", "8"], side="l", pitch=18, pad=10, w=20)
    s.text(450, 220, "J3", 9, True, anchor="c")
    s.wire([(418, 272), (434, 272)], "5V")
    s.offpage(418, 272, "+5 V from Y_MAX + (sheet 5)", "5V", side="l")
    for i, t in enumerate(["+12 V", "GND", "+5 V", "shield"]):
        s.text(465, 239 + i * 18, t, 8, color=GREY)
    s.text(230, 312, "J3 → the inter-unit cable (sheet 6). Shield drain J3-8 goes to GND here only.", 8)
    s.text(230, 323, "J3-5, 6, 7 (signals): sheet 5. J3-3 is empty.", 8, color=GREY)

    # RAMPS
    s.board(530, 72, 290, 262, "RAMPS 1.4 — 12 V (already on the board)", "ref", "from the RAMPS 1.4 KiCad netlist (control/wiring.md log, 2026-10-07)")
    s.wire([(546, 136), (552, 136)], "12V")
    s.wire([(546, 170), (552, 170)], "GND")
    s.rect(552, 127, 22, 54, fill="#FFFFFF", lw=1.3)
    s.text(563, 141, "+", 9, True, NETS["12V"][0], anchor="c")
    s.text(563, 157, "5A", 8, True, anchor="c")
    s.text(563, 175, "−", 9, True, anchor="c")
    s.text(563, 194, "X4", 8, True, anchor="c")
    s.ptc_h(574, 646, 136, "RAMPS F1: MF-R500, 5 A")
    s.wire([(646, 136), (800, 136)], "12V")
    s.text(796, 131, "+12 V", 8, True, NETS["12V"][0], anchor="r")
    s.wire([(574, 170), (590, 170), (590, 214), (742, 214)], "GND")
    for i, lab in enumerate(["X", "Y", "Z"]):
        x = 660 + i * 40
        s.dot(x, 136, "12V")
        s.wire([(x, 136), (x, 152)], "12V")
        s.rect(x - 15, 152, 30, 34, fill="#FFFFFF", lw=1.1)
        s.text(x, 165, f"{lab}: VM", 8, True, anchor="c")
        s.text(x, 180, "GND", 8, anchor="c")
        s.wire([(x, 186), (x, 214)], "GND")
        s.dot(x, 214, "GND")
    s.text(552, 236, "Driver sockets X, Y, Z: VM and GND (sheets 3, 4).", 8)
    s.text(552, 247, "C3, C4, C6, C7, C9, C10 (100 µF) sit on this +12 V rail.", 8)
    s.dot(800, 136, "12V")
    s.diode_v(800, 160, 268, [("D1", True), "1N4004"])
    s.wire([(800, 136), (800, 160)], "12V")
    s.text(800, 280, "→ Mega VIN", 8, True, NETS["12V"][0], anchor="r")
    s.para(540, 296, ["'11A' input (heated bed, through RAMPS F2): not used.",
                      "Fuses: PSU 5 A max · RAMPS F1 5 A (the 3 dial drivers + Mega VIN)",
                      "· hub F1 1.1 A (the key branch only)."], 8, color=GREY)

    # 5 V
    s.board(24, 346, 796, 166, "5 V logic (VIO) — from the Mega", "ref",
            "VIO powers only each driver's I/O pins; its logic runs from its own VM (12 V)")
    s.rect(40, 384, 112, 66, fill=FILL["module"], r=3)
    s.para(46, 398, [("Arduino Mega 2560", True), "5 V from USB, or its", "regulator (from VIN)"], 8)
    s.wire([(152, 404), (790, 404)], "5V")
    s.text(160, 399, "+5 V rail (RAMPS VCC)", 8, True, NETS["5V"][0])
    taps = [(300, "VIO of sockets X, Y, Z", "sheets 3, 4"), (440, "MS1 / MS2 jumpers", "sheets 3, 4"),
            (580, "endstop headers' '+' pins", "sheet 5"), (720, "Y_MAX + → hub → J3-4", "sheets 5, 6")]
    for x, t1, t2 in taps:
        s.dot(x, 404, "5V")
        s.wire([(x, 404), (x, 424)], "5V")
        s.text(x, 436, t1, 8, anchor="c")
        s.text(x, 447, t2, 8, color=GREY, anchor="c")
    s.wire([(96, 450), (96, 462)], "GND")
    s.gnd(96, 462)
    s.para(40, 486, ["Remote driver: its VIO comes over the cable (orange), so its logic inputs are never more than 0.5 V above its VIO "
                     "(TMC2209 datasheet, abs. max.).",
                     "Power order: USB first (Mega + every VIO), then 12 V. Off: 12 V first. The firmware waits until all 4 drivers answer."], 8)


# ====================================================================== sheets 3, 4
def driver_column(s, x0, sock, dial, addr, ms1, ms2, step, dirn, en, diag_hdr, diag_pin):
    """One RAMPS socket with its BTT TMC2209 V1.3 and motor; column ~395 pt wide."""
    s.text(x0, 70, f"Socket {sock} — dial {dial}", 11, True)
    s.text(x0, 83, f"UART address {addr} · BTT TMC2209 V1.3 with the DIAG mod", 8, color=GREY)
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
    # EN with the RAMPS 10 k pull-up
    x, y = p["EN"]
    s.wire([(x, y), (x0 + 50, y)], "CTRL")
    s.text(x0, y + 3, f"{en}", 8, True, ctrl)
    s.dot(x0 + 112, y, "CTRL")
    s.res_v(x0 + 112, y - 34, y, "5V", "10 k (on RAMPS)")
    s.flag(x0 + 112, y - 34, "+5 V", "5V")
    # MS1 / MS2 jumpers
    for key, fitted in (("MS1", ms1), ("MS2", ms2)):
        x, y = p[key]
        s.wire([(x, y), (x0 + 93, y)], "TIE")
        s.jumper(x0 + 90, y, fitted)
        s.text(x0 + 100, y - 4, "jumper ON" if fitted else "no jumper", 8, True, INK if fitted else GREY)
    # PDN_UART -> bus
    x, y = p["PDN"]
    s.wire([(x, y), (x0 + 104, y)], "UART")
    s.offpage(x0 + 104, y, "UART bus (sheet 5)", "UART", side="l")
    # TX / CLK tied by the RAMPS (RST-SLP)
    xt, yt = p["TX"]
    xc, yc = p["CLK"]
    s.wire([(xt, yt), (x0 + 126, yt), (x0 + 126, yc), (xc, yc)], "TIE")
    s.dot(x0 + 126, yc, "TIE")
    s.text(x0 + 120, (yt + yc) / 2 + 3, "RAMPS ties RST–SLP", 8, color=GREY, anchor="r")
    for key, lab in (("STEP", step), ("DIR", dirn)):
        x, y = p[key]
        s.wire([(x, y), (x0 + 50, y)], "CTRL")
        s.text(x0, y + 3, lab, 8, True, ctrl)
    x, y = p["DIAG"]
    s.wire([(x, y), (x0 + 120, y)], "DIAG")
    s.offpage(x0 + 120, y, f"{diag_hdr} S = {diag_pin} (sheet 5)", "DIAG", side="l")
    x, y = p["INDEX"]
    s.nc(x - 3, y)
    s.text(x - 10, y + 3, "cut off", 8, color=GREY, anchor="r")
    # right side
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
    s.motor(hx + 15 + 6 + r, (ys[0] + ys[3]) / 2, ys, hx + 15, [(f"Motor {dial[0]}", True), f"{sock} motor header"])
    # notes under the box
    s.para(x0, by + h + 22, [
        (f"Jumpers under socket {sock}: MS1 {'ON' if ms1 else 'off'}, MS2 {'ON' if ms2 else 'off'}, "
         "MS3 off (never fit MS3)", True),
        "UART lead: clipped onto the MS3 jumper pin, signal side (sheet 4).",
        f"STEP {step} · DIR {dirn} · EN {en}. The RAMPS pull-up keeps the driver",
        "off until the firmware pulls EN low.",
        f"DIAG lead (the mod, sheet 4) → {diag_hdr} S pin: {diag_pin}, an interrupt pin.",
        "Motor 17HE19-2004S: header pins 1–2 = one coil, 3–4 = the other.",
    ], 8)


def sheet_dials_ab(s):
    driver_column(s, 24, "X", "A (top-left)", 0, False, False, "D54", "D55", "D38", "X_MIN", "D3")
    s.line([(418, 64), (418, 450)], "#BBBBBB", 0.8, dash=[3, 3])
    driver_column(s, 430, "Y", "B (top-right)", 1, True, False, "D60", "D61", "D56", "X_MAX", "D2")
    s.para(24, 468, [
        "[ ] = the RAMPS / StepStick socket name of that pin. Fit each driver with EN, DIR, VM and GND matching the RAMPS silkscreen: a reversed driver is destroyed.",
        "The BTT V1.3 puts PDN_UART in the socket's MS3 position. TX: R10 is not fitted, so TX connects to nothing. Don't bridge R10.",
        "CLK: the RAMPS ties the socket's RST and SLP pins (= TX and CLK on the V1.3). With R10 open, CLK sees only its 20 k pull-down → internal clock.",
        "Motor currents are set over UART: 1.0 A RMS, hold 0.5 A. If a motor buzzes instead of turning, swap the middle two wires in its plug.",
    ], 8)


def sheet_dial_c_details(s):
    driver_column(s, 24, "Z", "C (bottom)", 2, False, True, "D46", "D48", "D62", "Z_MIN", "D18")
    s.line([(418, 64), (418, 506)], "#BBBBBB", 0.8, dash=[3, 3])
    # --- DIAG mod detail (top view, not to scale)
    x0 = 434
    s.text(x0, 70, "DIAG mod (the 3 dial drivers)", 11, True)
    s.text(x0, 83, "BTT TMC2209 V1.3 seen from above · not to scale", 8, color=GREY)
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
    # trimmer pot next to DIAG (control/wiring.md §6.1 layout: EN IDX DIAG [pot] VM)
    s.circle(bx + 72, by + 16, 7, stroke="#DDDDDD", fill="#B0B0B0", lw=0.8)
    s.text(bx + 72, by + 36, "pot", 8, True, "#FFFFFF", anchor="c")
    # INDEX and DIAG along the top edge, 2.54 and 5.08 mm from EN
    ix, dx_ = bx + 27, bx + 45
    for px in (ix, dx_):
        s.circle(px, by + 16, 4, stroke="#DDDDDD", fill="#C9A227", lw=0.8)
    s.text(ix - 6, by - 6, "INDEX", 8, True, anchor="r")
    s.line([(ix - 4, by - 4), (ix, by + 12)], GREY, 0.8)
    s.wire([(dx_, by + 16), (dx_, by - 30), (x0 + 280, by - 30)], "DIAG")
    s.dot(dx_, by + 16, "DIAG")
    s.text(dx_ + 4, by - 34, "half an F–F jumper, soldered on top", 8, True, NETS["DIAG"][0])
    s.text(x0 + 284, by - 27, "→ endstop S pin", 8, True, NETS["DIAG"][0])
    s.text(dx_ + 4, by - 9, "DIAG", 8, True)
    s.para(x0 + 210, by + 4, [("Steps (before the heatsink):", True),
                             "1. Cut the two pins that point DOWN",
                             "   (INDEX, DIAG) flush with their spacer.",
                             "2. Strip and tin half an F–F jumper.",
                             "3. Solder it to the TOP joint of DIAG:",
                             "   2nd pin from the EN corner",
                             "   (silkscreen 'DIAG').",
                             "4. Keep the iron off the trimmer pot",
                             "   next to it.",
                             ("VERIFY which pin is DIAG: bring-up", True, WARN),
                             ("stage 3 (`ping` + a hand stall).", True, WARN),
                             "The key driver needs no mod: its",
                             "pins plug into a socket (sheet 6)."], 8)
    # --- UART tap detail
    ty = 350
    s.text(x0, ty, "UART tap: the MS3 jumper pin (each socket)", 11, True)
    s.text(x0, ty + 13, "RAMPS jumper block under a driver socket · not to scale", 8, color=GREY)
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
    s.text(jx + 94, py3 + 33, "F–F jumper → hub BUS pin (sheet 5)", 8, True, NETS["UART"][0])
    s.para(jx + 60, jy + 4, ["Pads 1, 3, 5 = MS1, MS2, MS3 of the socket;",
                             "pads 2, 4, 6 = +5 V (RAMPS KiCad netlist).",
                             "Signal side = nearer the driver's EN / STEP / DIR row.",
                             ("VERIFY on your Fasizi board: `ping` (bring-up",
                              True, WARN), ("stage 1). The wrong pin is +5 V: harmless.", True, WARN),
                             ("Never fit a jumper on MS3.", True, WARN)], 8)


# ====================================================================== sheet 5
def sheet_signals(s):
    P, Y0 = 19, 134            # row pitch and first row
    row = lambda i: Y0 + i * P
    # (row, Mega pin, RAMPS header pin label, net)
    rows = [
        (0, "D15", "S", "TIE"), (1, "GND", "−", "GND"), (2, "+5 V", "+", "5V"),
        (3, "D23", "16", "CTRL"), (4, "D17 RX2", "17", "UART"), (5, "D16 TX2", "18", "UART"),
        (9, "D19 (irq)", "S", "DIAG"),
        (11, "D3 (irq)", "S", "DIAG"), (12, "D2 (irq)", "S", "DIAG"), (13, "D18 (irq)", "S", "DIAG"),
        (15, "D14", "S", "CTRL"), (16, "GND", "−", "GND"),
        (18, "D13", None, "CTRL"),
    ]
    # RAMPS + Mega
    s.board(24, 72, 222, 436, "RAMPS 1.4 on the Mega", "ref", "endstop headers: S signal, − GND, + 5 V")
    mx, mw = 40, 76
    s.rect(mx, row(0) - 14, mw, row(18) - row(0) + 28, fill=FILL["module"], lw=1.3)
    s.text(mx + mw / 2, row(0) - 19, "Mega 2560", 9, True, anchor="c")
    hx, hw = 164, 62
    for a_, b_, name in [(0, 2, "Y_MAX"), (3, 5, "AUX-4"), (9, 9, "Z_MAX"), (11, 11, "X_MIN"),
                         (12, 12, "X_MAX"), (13, 13, "Z_MIN"), (15, 16, "Y_MIN")]:
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
    s.text(mx + mw + 12, row(7) + 3, "RAMPS traces", 8, color=GREY)
    s.nc(hdr[0][0] + 4, hdr[0][1])
    s.text(hdr[0][0] + 11, hdr[0][1] + 3, "spare", 8, color=GREY)
    for i, lab in ((11, "dial A DIAG lead (sheet 3)"), (12, "dial B DIAG lead (sheet 3)"),
                   (13, "dial C DIAG lead (sheet 4)")):
        x, y = hdr[i]
        s.wire([(x, y), (x + 14, y)], "DIAG")
        s.offpage(x + 14, y, lab, "DIAG")
    xs, ys = hdr[15]
    xg, yg = hdr[16]
    s.wire([(xs, ys), (xs + 34, ys)], "CTRL")
    s.wire([(xg, yg), (xg + 14, yg), (xg + 14, yg + 26), (xs + 34, yg + 26)], "GND")
    s.button_v(xs + 34, ys, yg + 26, [("S1", True), "start / stop"])

    # hub board, signal part
    hb_bottom = row(9) + 24
    s.board(304, 72, 516, hb_bottom - 72, "Hub board (you build) — signals", "build",
            "2.54 mm male pins for the jumper ends; keep R1 right at the TX2 pin")
    px = 352                   # male pin column; the jumper side is on its left
    pins = [(1, "GND"), (2, "5V"), (3, "STEP"), (4, "BUS"), (5, "TX2"), (6, "BUS"), (7, "BUS"), (8, "BUS"), (9, "DIAG")]
    s.rect(px, row(1) - 8.5, 34, row(9) - row(1) + 17, fill="#FFFFFF", lw=1.3)
    for i, lab in pins:
        y = row(i)
        s.text(px + 17, y + 3, lab, 8, True, anchor="c")
        s.line([(px - 6, y), (px, y)], INK, 1.0)
        s.line([(px + 34, y), (px + 40, y)], INK, 1.0)
    for i, net in ((1, "GND"), (2, "5V"), (3, "CTRL"), (4, "UART"), (5, "UART"), (9, "DIAG")):
        s.wire([hdr[i], (px - 6, row(i))], net)
    for i, sock, sh in ((6, "X", 3), (7, "Y", 3), (8, "Z", 4)):
        s.wire([(px - 6, row(i)), (px - 10, row(i))], "UART")
        s.offpage(px - 10, row(i), f"{sock} MS3 pin (sheet {sh})", "UART", side="l")
    xr, xn, xb, xa, xd, xj = px + 40, 476, 504, 526, 548, 596
    s.wire([(xr, row(5)), (xr + 6, row(5))], "UART")
    s.res_h(xr + 6, xr + 70, row(5), "UART", "R1  1 kΩ")
    s.wire([(xr + 70, row(5)), (xn, row(5))], "UART")
    s.wire([(xr, row(4)), (xn, row(4))], "UART")
    for i in (6, 7, 8):
        s.wire([(xr, row(i)), (xn, row(i))], "UART")
        s.dot(xn, row(i), "UART")
    s.wire([(xn, row(4)), (xn, row(8))], "UART")
    s.dot(xn, row(4), "UART")
    s.dot(xn, row(5), "UART")
    s.text(xn + 6, row(7) + 3, "bus node", 8, True, NETS["UART"][0])
    j3, _ = s.conn(xj, row(0) - 10, [str(i) for i in range(1, 9)], side="l", pitch=P, pad=10, w=22)
    s.text(xj + 11, row(0) - 15, "J3", 9, True, anchor="c")
    J = {k: j3[(str(k), "l")] for k in range(1, 9)}
    s.wire([(xr, row(1)), J[2]], "GND")
    s.wire([(xr, row(2)), (xa, row(2)), (xa, J[4][1]), J[4]], "5V")
    s.wire([(xr, row(3)), (xb, row(3)), (xb, J[5][1]), J[5]], "CTRL")
    s.wire([(xn, row(5)), J[6]], "UART")
    s.wire([(xr, row(9)), (xd, row(9)), (xd, J[7][1]), J[7]], "DIAG")
    s.nc(J[3][0] - 4, J[3][1])
    s.wire([J[8], (J[8][0] - 12, J[8][1])], "GND")
    s.gnd(J[8][0] - 12, J[8][1])
    s.wire([J[1], (J[1][0] - 18, J[1][1])], "12V")
    s.offpage(J[1][0] - 18, J[1][1], "+12 V from F1 PTC (sheet 2)", "12V", side="l")
    for k, t in [(1, "+12 V"), (2, "GND"), (3, "empty"), (4, "+5 V"), (5, "KEY STEP"), (6, "UART"),
                 (7, "KEY DIAG"), (8, "shield drain")]:
        s.text(xj + 28, J[k][1] + 3, t, 8, color=GREY)
    s.text(xj + 11, row(7) + 26, "→ cable (sheet 6)", 8, True, anchor="c")

    # notes
    s.para(420, row(10) + 14, [("Notes", True),
        "One 1 kΩ in total: TX2 → R1 → bus. RX2 and every driver's PDN_UART sit",
        "straight on the bus (TMC2209 datasheet Fig. 4.1). The Mega hears its own",
        "transmissions; TMCStepper skips that echo. SENDDELAY ≥ 2 on every driver.",
        "Addresses by MS1 / MS2: X 0, Y 1, Z 2, key 3. Bus at 115200 baud.",
        "(irq) = an interrupt pin. DIAG is a pulse: the firmware latches it with",
        "attachInterrupt on D2, D3, D18, D19 (Arduino interrupt numbers 0, 1, 5, 4).",
        "Inputs use the Mega's internal pull-ups: an unplugged DIAG reads high =",
        "'stalled', so the firmware refuses to move (fail safe).",
        "Button S1 (Y_MIN): pauses a run; resumes or starts one when idle.",
        "Shield drain J3-8: GND at this end only. Hub GND = 12V IN − (sheet 2).",
        "The hub's 12 V parts (12V IN, 12V OUT, F1) are on sheet 2.",
        "STEP / DIR / EN of X, Y, Z: sheets 3, 4.  AUX-4 15, 14 (D25, D27): reserved."], 8)


# ====================================================================== sheet 6
def sheet_cable_key(s):
    rows = [("1", "+12 V (after hub F1)", "12V", "#C62828", "red"),
            ("2", "GND", "GND", "#1A1A1A", "black"),
            ("3", "empty", "TIE", None, "—"),
            ("4", "+5 V (VIO)", "5V", "#F28C28", "orange"),
            ("5", "KEY STEP", "CTRL", "#F2C500", "yellow"),
            ("6", "UART bus", "UART", "#2E9E4A", "green"),
            ("7", "KEY DIAG", "DIAG", "#FFFFFF", "white"),
            ("8", "shield drain", "TIE", "#8C8C8C", "shield")]
    P, Y0 = 22, 140
    ry = {r[0]: Y0 + i * P for i, r in enumerate(rows)}
    # hub J3
    s.board(24, 72, 158, 260, "Hub board — J3", "build", "dial end (sheet 5)")
    j3, _ = s.conn(144, Y0 - 11, [r[0] for r in rows], side="r", pitch=P, pad=11, w=20)
    s.text(154, Y0 - 17, "J3", 9, True, anchor="c")
    for r in rows:
        col = NETS[r[2]][0] if r[2] != "TIE" else GREY
        s.text(138, ry[r[0]] + 3, r[1], 8, True, col, anchor="r")
    # cable
    x1, x2 = 170, 392
    s.rect(206, Y0 - 26, 142, 8 * P + 22, stroke=GREY, fill="#F6F6F6", lw=0.8, dash=[3, 2], r=8)
    s.text(277, Y0 - 31, "cable, ~300 mm, straight through", 8, True, anchor="c")
    for lab, _, net, col, cname in rows:
        y = ry[lab]
        if col is None:
            s.nc(x1 + 6, y)
            s.nc(x2 - 6, y)
            s.text(277, y + 3, "no conductor", 8, color=GREY, anchor="c")
            continue
        if cname == "shield":
            s.line([(x1, y), (330, y)], col, 2.4, dash=[5, 3])
            s.line([(330, y), (330, y + 10)], col, 2.4)
            s.text(326, y + 16, "folded back under heat shrink", 8, color=GREY, anchor="r")
            s.nc(x2 - 6, y)
            continue
        s.line([(x1, y), (x2, y)], "#1A1A1A", 4.4)
        s.line([(x1, y), (x2, y)], col, 2.9)
        s.text(277, y - 5, cname, 8, True, anchor="c")
    s.para(24, 350, ["QUARKZMAN 22 AWG shielded, 6 conductors.",
                     "Line colours on this sheet's cable = the real",
                     "conductor colours. Cut ~300 mm; strip 30 mm of",
                     "jacket at each end. Mark pin 1 on both plugs.",
                     ("VERIFY the plug fits only one way.", True, WARN),
                     "Reversed, dial pin 1 (12 V) would meet the",
                     "remote's empty pin 8: no 12 V reaches logic.",
                     "Zip-tie within ~20 mm of each plug, clear of",
                     "the key cap."], 8)

    # remote board
    s.board(380, 72, 440, 434, "Remote driver board (you build) — key turner", "build",
            "perfboard ~70 × 30 mm · driver in female headers (layout: control/wiring.md §6.1)")
    j1, _ = s.conn(398, Y0 - 11, [r[0] for r in rows], side="lr", pitch=P, pad=11, w=20)
    s.text(408, Y0 - 17, "J1", 9, True, anchor="c")
    J = {r[0]: j1[(r[0], "r")] for r in rows}
    dx, dw, dyb = 580, 104, 174            # driver box
    left = [("EN", "EN"), ("MS1", "MS1"), ("MS2", "MS2"), ("RX", "RX = PDN_UART"), ("TX", "TX"),
            ("CLK", "CLK"), ("STEP", "STEP"), ("DIR", "DIR"), None, ("DIAG", "DIAG *"), ("IDX", "INDEX *")]
    right = [("VM", "VM"), ("G1", "GND"), ("A2", "A2"), ("A1", "A1"), ("B1", "B1"), ("B2", "B2"),
             ("VIO", "VIO"), ("G2", "GND")]
    p, h = s.ic(dx, dyb, dw, left, right, pitch=21, pad=13)
    s.text(dx + dw / 2, dyb - 20, "BTT TMC2209 V1.3", 9, True, anchor="c")
    s.text(dx + dw / 2, dyb - 8, "key driver · UART address 3", 8, color=GREY, anchor="c")
    s.text(dx + dw - 4, dyb + h - 8, "* top-edge pins", 8, color=GREY, anchor="r")
    # ties on the left
    for k in ("EN", "CLK", "DIR"):
        x, y = p[k]
        s.wire([(x, y), (x - 8, y)], "GND")
        s.tag(x - 8, y, "GND", "GND", side="l")
    for k in ("MS1", "MS2"):
        x, y = p[k]
        s.wire([(x, y), (x - 8, y)], "5V")
        s.tag(x - 8, y, "+5 V", "5V", side="l")
    s.nc(p["TX"][0] - 3, p["TX"][1])
    s.nc(p["IDX"][0] - 3, p["IDX"][1])
    # J1 -> driver
    s.tag(*J["2"], "GND", "GND")
    s.tag(*J["4"], "+5 V", "5V")
    s.nc(J["3"][0] + 4, J["3"][1])
    s.nc(J["8"][0] + 4, J["8"][1])
    xd, xs, xu = 470, 488, 506
    yst, yrx, ydg = p["STEP"][1], p["RX"][1], p["DIAG"][1]
    # STEP: J1-5 -> down to STEP (passes under the UART run, drawn with a hop on UART)
    s.wire([J["5"], (xs, ry["5"]), (xs, yst), p["STEP"]], "CTRL")
    s.hwire_hop(J["6"][0], xu, ry["6"], [xs], "UART")
    s.wire([(xu, ry["6"]), (xu, yrx), p["RX"]], "UART")
    s.wire([J["7"], (xd, ry["7"]), (xd, ydg), p["DIAG"]], "DIAG")
    # 12 V -> VM with C1
    xv = dx + dw + 34
    yvm = p["VM"][1]
    s.wire([J["1"], (xv, ry["1"]), (xv, yvm), p["VM"]], "12V")
    s.wire([(xv, ry["1"]), (xv + 30, ry["1"])], "12V")
    s.dot(xv, ry["1"], "12V")
    s.cap_v(xv + 30, ry["1"], ry["1"] + 44, [("C1", True), "100 µF", "≥ 25 V"], side=1)
    s.gnd(xv + 30, ry["1"] + 44)
    for k in ("G1", "G2"):
        s.tag(*p[k], "GND", "GND")
    s.tag(*p["VIO"], "+5 V", "5V")
    # motor header J2 + key motor
    hx = dx + dw + 22
    ys = [p[k][1] for k in ("A2", "A1", "B1", "B2")]
    s.rect(hx, ys[0] - 9, 15, ys[3] - ys[0] + 18, fill="#FFFFFF", lw=1.2)
    for i, k in enumerate(("A2", "A1", "B1", "B2")):
        s.wire([p[k], (hx, ys[i])], "MOTOR")
        s.text(hx + 7.5, ys[i] + 3, str(i + 1), 8, True, anchor="c")
    r = s.motor_r(ys)
    s.motor(hx + 15 + 8 + r, (ys[0] + ys[3]) / 2, ys, hx + 15, [("Key motor", True), "17HE19-2004S", "on J2 (1 × 4)"])
    s.para(398, 424, [
        "EN → GND: always on; the firmware switches it off with CHOPCONF.TOFF = 0.",
        "DIR → GND: direction set over UART (GCONF.shaft, read back before every move).",
        "MS1, MS2 → +5 V: UART address 3.   CLK → GND: internal clock.",
        "DIAG: its own down-pointing pin, in a 1×2 socket with INDEX: no mod needed.  TX: nothing (R10 not fitted).",
        ("VERIFY: lay the driver on the perfboard before soldering the headers (INDEX / DIAG on the 2.54 mm grid?).", True, WARN),
        ("Before the first power-up: VREF pot to minimum (EN is tied low, so the driver", True),
        ("is on at its power-up current until the firmware sets 0.6 A RMS).", True),
        "J1-3, J1-8: not connected. J2: RAMPS motor-header order; if the motor buzzes, swap its middle two wires.",
    ], 8)


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
        ("Dial A DIAG", "D3 (interrupt)", "X_MIN header, S"),
        ("Dial B DIAG", "D2 (interrupt)", "X_MAX header, S"),
        ("Dial C DIAG", "D18 (interrupt)", "Z_MIN header, S"),
        ("Key DIAG (cable)", "D19 (interrupt)", "Z_MAX header, S, via the hub"),
        ("Key STEP (cable)", "D23", "AUX-4 pin 16, via the hub"),
        ("UART TX2", "D16", "AUX-4 pin 18 → hub R1"),
        ("UART RX2", "D17", "AUX-4 pin 17 → hub bus"),
        ("Dial drivers' PDN_UART", "—", "MS3 jumper pins X, Y, Z → hub bus"),
        ("Start / stop button", "D14 (pull-up)", "Y_MIN header, S and −"),
        ("5 V + GND for the remote", "5 V, GND", "Y_MAX header, + and −"),
        ("Status LED", "D13", "on-board LED 'L'"),
        ("Spare", "D15", "Y_MAX header, S"),
        ("Reserved: key DIR, key EN", "D25, D27", "AUX-4 pins 15, 14"),
        ("USB serial (the log)", "D0 / D1", "USB: keep free"),
    ]
    table(24, 70, ["Function", "Mega pin", "Where it connects"], [138, 94, 178], pin_rows,
          "Pin map (control/wiring.md §1; Marlin pins_RAMPS.h)")
    jmp = [("X", "A (top-left)", "off", "off", "off", "0"),
           ("Y", "B (top-right)", "ON", "off", "off", "1"),
           ("Z", "C (bottom)", "off", "ON", "off", "2"),
           ("remote", "key", "to 5 V", "to 5 V", "n/a", "3")]
    table(452, 70, ["Socket", "Dial", "MS1", "MS2", "MS3", "Address"], [50, 82, 48, 48, 48, 50], jmp,
          "Driver jumpers and UART addresses (§2)")
    s.text(452, 157, "Never fit an MS3 jumper. Sockets E0 and E1 stay empty.", 8, True, WARN)
    cur = [("Dials A, B, C", "1.0 A RMS", "0.5 A", "until the dial torque is measured"),
           ("Key", "0.6 A RMS", "0.3 A", "then 2 × the measured minimum, ≤ 1.0 A"),
           ("Firmware ceiling", "1.2 A", "—", "BTT: active cooling above 1.2 A")]
    table(452, 180, ["Driver", "Run", "Hold", "Why"], [78, 58, 38, 178], cur, "Motor currents, set over UART (§7)")
    HAVE = ("have", False, GREY)
    ORDERED = ("ordered", False, INK)
    parts = [("Hub", "F1", "PTC fuse ~1.1 A hold, ≥ 16 V (for now: 1.6 A glass fuse)", ORDERED),
             ("Hub", "R1", "1 kΩ: the only UART resistor (TX2 → bus)", HAVE),
             ("Hub", "J3", "Phoenix-style 5.08 mm 8-pin header + plug", HAVE),
             ("Hub", "—", "male pins × 9: GND 5V STEP TX2 BUS×4 DIAG", HAVE),
             ("Hub", "—", "12V IN / 12V OUT: 20 AWG red + black", ORDERED),
             ("Remote", "J1", "Phoenix-style 5.08 mm 8-pin header + plug", HAVE),
             ("Remote", "C1", "100 µF, ≥ 25 V, low-ESR electrolytic", ORDERED),
             ("Remote", "J2", "1 × 4 male header (key motor)", HAVE),
             ("Remote", "—", "female headers 2 × (1 × 8) + 1 × (1 × 2)", HAVE),
             ("Both", "—", "perfboard (kit): ~50 × 30 and ~70 × 30 mm", HAVE),
             ("PSU", "—", "DC jack 5.5 × 2.1 mm → screw terminal", ORDERED),
             ("Wiring", "—", "F–F jumpers, ~20 × 10–20 cm", ORDERED),
             ("RAMPS", "S1", "7 mm push button (start / stop)", HAVE)]
    yp = table(452, 262, ["Board", "Ref", "Part", "Status"], [48, 28, 252, 42], parts,
               "Parts you fit (§5, §6, §10) · full list: docs/bom.md")
    s.para(452, yp + 13, ["Fuses, diode, capacitors and resistors drawn in grey on sheets 2–4",
                          "(RAMPS F1, F2, D1, the six 100 µF, the 10 k pull-ups) are already on the RAMPS."], 8, color=GREY)
    s.text(24, 330, "Power order (§8)", 10, True)
    s.para(24, 345, ["1. Make every connection with power off (USB unplugged, 12 V off).",
                     "2. Before the first power-up: every driver's VREF pot to minimum.",
                     "3. Power up: USB first, then 12 V.   4. Power down: 12 V first, then USB.",
                     "5. Never plug or unplug a motor or the cable with 12 V on.",
                     "6. Emergency stop: pull the 12 V plug."], 8)
    s.text(24, 426, "VERIFY on the bench (control/bringup.md)", 10, True)
    s.para(24, 441, ["Which MS3 jumper pin is the signal side (stage 1, `ping`).",
                     "Which top-edge pin is DIAG (stage 3).   Phoenix plug keying.",
                     "Remote board: INDEX / DIAG on the 2.54 mm grid (before soldering headers).",
                     "Multimeter: DC-jack + / −; 5 V and 12 V polarity at the hub and remote board",
                     "before plugging the driver in; cable continuity.",
                     "Sources: control/wiring.md — Marlin pins_RAMPS.h, TMC2209 datasheet rev 1.09,",
                     "BTT TMC2209 V1.3 manual + schematic, RAMPS 1.4 KiCad netlist."], 8)


SHEETS = [
    ("Overview", "What connects to what. Each block is drawn in full on the sheet named in it.", sheet_overview),
    ("Power: 12 V, 5 V, GND", "12 V comes in at the hub board and splits: the RAMPS (its own 5 A fuse) and the key branch "
     "(1.1 A PTC). 5 V logic comes from the Mega.", sheet_power),
    ("Dial drivers A and B on the RAMPS", "[ ] = the RAMPS socket name of that pin. All connections to the left are on "
     "the RAMPS or by jumper.", sheet_dials_ab),
    ("Dial driver C; DIAG-mod and UART-tap details", None, sheet_dial_c_details),
    ("Mega + RAMPS headers, hub board, UART bus", "Thin lines = RAMPS traces. Thick lines = your jumper wires "
     "(F–F, 10–20 cm) and hub-board wiring.", sheet_signals),
    ("Inter-unit cable and key turner", "Straight through: the same pin number at both ends. 12 V off before "
     "plugging or unplugging the cable.", sheet_cable_key),
    ("Pin map, jumpers, currents, parts", None, sheet_tables),
]


def main(out):
    c = canvas.Canvas(out, pagesize=(W, H), initialFontName="F", initialFontSize=MIN_PT)
    c.setTitle("Fichet safe robot — wiring schematic")
    c.setAuthor("Claude, for Paul")
    c.setSubject("Harness v1, drawn from control/wiring.md")
    for i, (title, note, fn) in enumerate(SHEETS, 1):
        fn(Sheet(c, i, len(SHEETS), title, note))
        c.showPage()
    c.save()


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "schematic.pdf"))
