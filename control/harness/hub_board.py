#!/usr/bin/env python3
"""
Hub-board layout diagram (control/harness/hub_board.svg).

A top-down placement drawing of the dial-end hub board from
control/wiring.md section 5: a ~50 x 30 mm perfboard that splits the 12 V
supply, carries the one UART resistor R1 and the UART bus node, and holds the
8-pin Phoenix header for the inter-unit cable. The interim 5x20 mm fuse holder
is a separate printed part beside it.

Not a PCB layout — a placement guide so Paul can see what sits where. The
links shown are nets; on a perfboard they are point-to-point wires underneath.

    python3 control/harness/hub_board.py
"""
import os

SCALE = 8.0
MARGIN = 48
# board in mm
BW_MM, BH_MM = 52, 34
BX, BY = MARGIN, 150          # board top-left in px
BW, BH = BW_MM * SCALE, BH_MM * SCALE
RIGHT = BX + BW + 210         # right-hand net-list column x
W = RIGHT + 360
H = BY + BH + 230

C = {
    '12V': '#c0392b', '5V': '#e67e22', 'GND': '#2c3e50',
    'STEP': '#f1c40f', 'UART': '#27ae60', 'DIAG': '#8e44ad',
    'board': '#eef2f3', 'edge': '#7f8c8d', 'ink': '#2c3e50', 'pale': '#95a5a6',
}


def main():
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" '
         f'viewBox="0 0 {W:.0f} {H:.0f}" font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W:.0f}" height="{H:.0f}" fill="white"/>']

    def txt(x, y, t, size=12, bold=False, col=None, anc='start'):
        w = ' font-weight="bold"' if bold else ''
        s.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}"{w} '
                 f'fill="{col or C["ink"]}" text-anchor="{anc}">{t}</text>')

    def box(x, y, w, h, fill, stroke=None, rx=4):
        s.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}" '
                 f'fill="{fill}" stroke="{stroke or C["ink"]}" stroke-width="1.5"/>')

    def pad(x, y, net, r=6):
        col = C.get(net, C['pale'])
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{col}" stroke="{C["ink"]}" stroke-width="1.2"/>')

    def wire(x0, y0, x1, y1, net):
        s.append(f'<path d="M{x0:.0f},{y0:.0f} L{x1:.0f},{y1:.0f}" fill="none" '
                 f'stroke="{C[net]}" stroke-width="2.6" stroke-linecap="round"/>')

    def orth(x0, y0, x1, y1, net, midx=None):
        mx = midx if midx is not None else (x0 + x1) / 2
        s.append(f'<path d="M{x0:.0f},{y0:.0f} H{mx:.0f} V{y1:.0f} H{x1:.0f}" fill="none" '
                 f'stroke="{C[net]}" stroke-width="2.6" stroke-linejoin="round"/>')

    # ---- title ----
    txt(MARGIN, 42, 'Hub board — dial end', 24, True)
    txt(MARGIN, 68, 'The 12 V split point. Holds the one UART resistor (R1) and the UART bus node, and carries the cable header.', 12.5)
    txt(MARGIN, 86, '~50 x 30 mm perfboard, seen from the component side. Nets shown; on a perfboard they are point-to-point wires underneath.', 12.5)
    txt(MARGIN, 104, 'Layout is a guide — place parts to suit your board. The one rule: keep R1 right at the TX2 pin and the bus node short.', 12.5, col=C['ink'])

    # ---- board ----
    box(BX, BY, BW, BH, C['board'], C['edge'], rx=8)

    # zone A: power terminals (left)
    ax = BX + 26
    pad(ax, BY + 46, '12V'); txt(ax + 14, BY + 50, '12V IN +', 11, True)
    pad(ax, BY + 70, 'GND'); txt(ax + 14, BY + 74, '12V IN -', 11, True)
    txt(ax - 6, BY + 22, 'from PSU (DC-jack adapter)', 9.5, col=C['pale'])
    pad(ax, BY + 150, '12V'); txt(ax + 14, BY + 154, '12V OUT +', 11, True)
    pad(ax, BY + 174, 'GND'); txt(ax + 14, BY + 178, '12V OUT -', 11, True)
    txt(ax - 6, BY + 196, 'to RAMPS "5A" terminal, 20 AWG', 9.5, col=C['pale'])
    wire(ax, BY + 46, ax, BY + 150, '12V')   # IN+ feeds OUT+ (raw 12 V)
    txt(ax - 18, BY + 100, 'raw', 9, col=C['12V']); txt(ax - 18, BY + 112, '12 V', 9, col=C['12V'])

    # GND rail along the board bottom
    rail_y = BY + BH - 20
    s.append(f'<line x1="{BX+16:.0f}" y1="{rail_y:.0f}" x2="{BX+BW-16:.0f}" y2="{rail_y:.0f}" '
             f'stroke="{C["GND"]}" stroke-width="3.4"/>')
    txt(BX + BW/2, rail_y + 18, 'GND rail', 11, True, C['GND'], 'middle')
    wire(ax, BY + 70, ax, rail_y, 'GND')
    wire(ax, BY + 174, ax, rail_y, 'GND')

    # zone B: R1 + bus node (middle)
    mx = BX + BW * 0.66
    box(mx - 34, BY + 54, 68, 26, '#d9dde0', C['ink'])
    txt(mx, BY + 71, 'R1  1k', 11.5, True, C['ink'], 'middle')
    busx, busy = mx + 4, BY + 118
    pad(busx, busy, 'UART', 7); txt(busx, busy + 22, 'UART bus node', 10, True, C['UART'], 'middle')
    wire(mx + 30, BY + 67, busx, busy, 'UART')     # R1 → bus

    # zone C: header pins to the RAMPS (a labelled 1x6 male strip)
    hx = BX + BW * 0.40
    hdr = [('TX2', 'UART'), ('BUS', 'UART'), ('STEP', 'STEP'),
           ('DIAG', 'DIAG'), ('5V', '5V'), ('GND', 'GND')]
    txt(hx, BY + 46, 'header pins', 10, True, C['ink'], 'middle')
    txt(hx, BY + 59, '(F-F jumpers to RAMPS)', 8.5, col=C['pale'], anc='middle')
    for i, (nm, net) in enumerate(hdr):
        y = BY + 76 + i * 18
        pad(hx, y, net, 5)
        txt(hx - 10, y + 4, nm, 10, True, C['ink'], 'end')
    # R1 sits between the TX2 header pin and the bus; draw TX2->R1 and bus->BUS pin
    wire(hx, BY + 64, mx - 30, BY + 67, 'UART')          # TX2 pin → R1 left
    wire(busx, busy, hx, BY + 64 + 18, 'UART')           # bus node → BUS pin

    # zone D: Phoenix 8-pin header on the right edge of the board
    phx = BX + BW - 26
    box(phx - 12, BY + 40, 24, 170, '#34495e', C['ink'])
    txt(phx, BY + 32, 'Phoenix 8-pin', 10, True, C['ink'], 'middle')
    pins = [('1', '12V'), ('2', 'GND'), ('3', 'pale'), ('4', '5V'),
            ('5', 'STEP'), ('6', 'UART'), ('7', 'DIAG'), ('8', 'GND')]
    phy0 = BY + 54
    for i, (n, net) in enumerate(pins):
        y = phy0 + i * 20
        pad(phx, y, net, 5)
        txt(phx - 16, y + 4, n, 9.5, col=C['ink'], anc='end')
    txt(phx, phy0 + 8*20 + 2, 'to cable', 9.5, col=C['pale'], anc='middle')

    # ---- off-board fuse, above the board ----
    fy = BY - 42
    box(BX + 150, fy, 300, 34, 'white', C['12V'])
    s.append(f'<rect x="{BX+150:.0f}" y="{fy:.0f}" width="300" height="34" rx="4" fill="none" '
             f'stroke="{C["12V"]}" stroke-width="2" stroke-dasharray="6 4"/>')
    txt(BX + 300, fy + 15, 'F1 fuse holder — separate printed part', 10.5, True, C['12V'], 'middle')
    txt(BX + 300, fy + 29, '1.1 A PTC when it arrives; for now the 1.6 A glass fuse', 9.5, col=C['ink'], anc='middle')

    # ---- the net list on the right ----
    lx = RIGHT
    txt(lx, 150, 'What lands where', 15, True)
    rows = [
        ('12V', 'Pin 1  +12 V', 'PSU + → F1 holder in; F1 out → Phoenix pin 1'),
        ('GND', 'Pin 2  GND', 'GND rail (PSU -, OUT -, Y_MAX -, shield)'),
        ('pale', 'Pin 3  empty', 'left open — keeps 12 V away from 5 V logic'),
        ('5V', 'Pin 4  +5 V', 'header 5V pin ← RAMPS Y_MAX +'),
        ('STEP', 'Pin 5  KEY_STEP', 'header STEP pin ← AUX-4 16 (D23)'),
        ('UART', 'Pin 6  UART', 'bus node ← RX2 (D17) + X/Y/Z PDN_UART'),
        ('DIAG', 'Pin 7  KEY_DIAG', 'header DIAG pin ← Z_MAX S (D19)'),
        ('GND', 'Pin 8  shield', 'shield drain → GND rail (dial end only)'),
    ]
    y = 178
    for net, a, b in rows:
        pad(lx + 7, y - 4, net, 6)
        txt(lx + 22, y, a, 12, True)
        txt(lx + 22, y + 15, b, 10, col=C['ink'])
        y += 40
    txt(lx, y + 4, 'R1 (1 k): TX2 pin (D16 / AUX-4 18) → R1 → bus node.', 11)
    txt(lx, y + 20, 'Bus node also joins RX2 and each dial driver\'s PDN_UART (its MS3 jumper pin).', 10)
    txt(lx, y + 40, 'Header pins: 2.54 mm male. RAMPS side uses F-F jumpers (~10 cm).', 10)
    txt(lx, y + 56, 'Everything marked - on a pad goes to the GND rail.', 10)

    # ---- legend ----
    ly = H - 70
    txt(MARGIN, ly, 'Net colours', 13, True)
    leg = [('12V', '12 V'), ('5V', '5 V / VIO'), ('GND', 'GND'),
           ('STEP', 'KEY_STEP'), ('UART', 'UART bus'), ('DIAG', 'KEY_DIAG (white in cable)')]
    for i, (net, lab) in enumerate(leg):
        x = MARGIN + (i % 6) * 150
        pad(x + 6, ly + 20, net, 6)
        txt(x + 18, ly + 24, lab, 10.5)
    txt(MARGIN, H - 12, 'Generated by control/harness/hub_board.py from control/wiring.md section 5.', 9.5, col=C['pale'])

    s.append('</svg>')
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hub_board.svg')
    open(out, 'w').write('\n'.join(s))
    print('wrote', out)


if __name__ == '__main__':
    main()
