#!/usr/bin/env python3
"""
UART pigtail drawing (control/harness/uart_pigtail.svg).

Revision 2026-10-08.2: the hub board is replaced by a small harness, the
"UART pigtail": six leads, each ending in a female Dupont, joined in one
soldered splice. The TX2 lead carries the 1 kOhm resistor R1 in line. This is
the TMC2209 single-wire UART bus (datasheet Fig. 4.1): TX2 -> 1 kOhm -> bus;
RX2 and every driver's PDN_UART on the bus. Reference: control/wiring.md §5.

    python3 control/harness/uart_pigtail.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REV = open(os.path.join(ROOT, "REVISION")).read().strip()

W, H = 1040, 640
C = {'uart': '#27ae60', 'ink': '#2c3e50', 'pale': '#7f8c8d', 'res': '#bdc3c7',
     'shrink': '#34495e', 'dupont': '#2c3e50', 'tape': '#f9e79f', 'box': '#eef2f3'}


def main():
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" font-family="Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="white"/>']

    def txt(x, y, t, size=12, bold=False, col=None, anc='start'):
        b = ' font-weight="bold"' if bold else ''
        s.append(f'<text x="{x:.0f}" y="{y:.0f}" font-size="{size}"{b} '
                 f'fill="{col or C["ink"]}" text-anchor="{anc}">{t}</text>')

    def line(x0, y0, x1, y1, col=None, w=2.6):
        s.append(f'<path d="M{x0:.0f},{y0:.0f} L{x1:.0f},{y1:.0f}" fill="none" '
                 f'stroke="{col or C["uart"]}" stroke-width="{w}" stroke-linecap="round"/>')

    # ---- title ----
    txt(40, 42, 'UART pigtail — replaces the hub board', 24, True)
    txt(W - 40, 30, f'Revision {REV}', 11, col=C['pale'], anc='end')
    txt(40, 68, 'Six leads, each with a female Dupont end, joined in one soldered splice. '
        'R1 (1 kΩ) sits in line in the TX2 lead.', 12.5)
    txt(40, 86, 'The TMC2209 single-wire UART bus (datasheet Fig. 4.1): TX2 → 1 kΩ → bus; '
        'RX2 and every driver\'s PDN_UART on the bus.', 12.5)
    txt(40, 104, 'Reference: control/wiring.md §5. Build steps: docs/manual.md §2.5.', 12.5, col=C['pale'])

    # ---- leads ----
    leads = [('TX2', 'AUX-4 pin 18 (D16)', True),
             ('RX2', 'AUX-4 pin 17 (D17)', False),
             ('A', 'RX pin of the X driver (dial A, addr 0)', False),
             ('B', 'RX pin of the Y driver (dial B, addr 1)', False),
             ('C', 'RX pin of the Z driver (dial C, addr 2)', False),
             ('KEY', 'RX pin of the E0 driver (key, addr 3)', False)]
    x_end = 330          # female Dupont housings
    x_spl = 660          # splice
    y_spl = 330
    y0, dy = 160, 58
    for k, (tag, dest, has_r) in enumerate(leads):
        y = y0 + k * dy
        # destination text, left of the housing
        txt(x_end - 64, y - 3, dest, 11.5, anc='end')
        txt(x_end - 64, y + 12, 'top of the tall RX pin, 4th from EN' if tag in ('A', 'B', 'C', 'KEY')
            else 'male header pin on the RAMPS', 9.5, col=C['pale'], anc='end')
        # Dupont housing + tape label
        s.append(f'<rect x="{x_end-52}" y="{y-9}" width="40" height="18" rx="2" fill="{C["dupont"]}"/>')
        s.append(f'<rect x="{x_end-12}" y="{y-8}" width="34" height="16" rx="2" fill="{C["tape"]}" '
                 f'stroke="{C["ink"]}" stroke-width="0.8"/>')
        txt(x_end + 5, y + 4, tag, 9.5, True, anc='middle')
        # wire: straight run, then fan into the splice
        xa = x_end + 22
        xb = x_spl - 120
        if has_r:
            r0, r1 = xa + 40, xa + 110
            line(xa, y, r0, y)
            s.append(f'<rect x="{r0}" y="{y-10}" width="{r1-r0}" height="20" rx="4" fill="{C["res"]}" '
                     f'stroke="{C["ink"]}" stroke-width="1.3"/>')
            for bx in (r0 + 16, r0 + 30, r0 + 44):
                s.append(f'<line x1="{bx}" y1="{y-10}" x2="{bx}" y2="{y+10}" stroke="{C["ink"]}" stroke-width="1"/>')
            txt((r0 + r1) / 2, y - 16, 'R1 1 kΩ', 11, True, anc='middle')
            # heat shrink over the resistor
            s.append(f'<rect x="{r0-10}" y="{y-13}" width="{r1-r0+20}" height="26" rx="6" fill="none" '
                     f'stroke="{C["shrink"]}" stroke-width="1.2" stroke-dasharray="4 3"/>')
            line(r1, y, xb, y)
        else:
            line(xa, y, xb, y)
        line(xb, y, x_spl - 20, y_spl)

    # splice: heat-shrink body
    s.append(f'<rect x="{x_spl-24}" y="{y_spl-22}" width="64" height="44" rx="10" fill="{C["shrink"]}"/>')
    s.append(f'<circle cx="{x_spl}" cy="{y_spl}" r="7" fill="{C["uart"]}" stroke="white" stroke-width="1.5"/>')
    line(x_spl + 20, y_spl + 22, x_spl + 50, y_spl + 112, C['pale'], 1)
    txt(x_spl + 50, y_spl + 128, 'splice = the bus node', 12, True, C['uart'], 'middle')
    txt(x_spl + 50, y_spl + 144, 'solder, heat shrink,', 10, col=C['pale'], anc='middle')
    txt(x_spl + 50, y_spl + 158, 'zip-tie to the deck', 10, col=C['pale'], anc='middle')

    # ---- check box ----
    bx, by, bw, bh = 770, 150, 240, 250
    s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="{C["box"]}" stroke="{C["pale"]}"/>')
    txt(bx + 14, by + 26, 'Check before fitting', 14, True)
    rows = ['Multimeter on Ω, pigtail loose:',
            'TX2 → RX2: about 1 kΩ',
            'TX2 → A, B, C, KEY: about 1 kΩ each',
            'RX2 → A, B, C, KEY: about 0 Ω each',
            '',
            'Then tug each lead at the splice.',
            '',
            'Lengths: measure AUX-4 → each',
            'driver\'s RX pin; cut each lead to',
            'that + a few cm, splice near the',
            'middle of the RAMPS.']
    for k, r in enumerate(rows):
        txt(bx + 14, by + 52 + k * 17, r, 10.5, k in (1, 2, 3))

    # ---- notes ----
    ny = 520
    txt(40, ny, 'Making the leads: cut one end off each of six F–F jumpers (or use jumper halves if they are long enough).', 11.5)
    txt(40, ny + 18, 'Every lead keeps its factory-crimped female end, so a driver can still be unplugged (pull its lead off RX first). Nothing on TX or CLK.', 11.5)
    txt(40, ny + 36, 'No 12 V, no 5 V, no GND on the pigtail: all six are signals. The drivers and the Mega share ground through the RAMPS.', 11.5)
    txt(40, H - 16, 'Generated by control/harness/uart_pigtail.py from control/wiring.md section 5.', 9.5, col=C['pale'])

    s.append('</svg>')
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uart_pigtail.svg')
    open(out, 'w').write('\n'.join(s))
    print('wrote', out)


if __name__ == '__main__':
    main()
