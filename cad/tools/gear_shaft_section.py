#!/usr/bin/env python3
"""
Section drawing of one dial's gear-shaft joint (revision 2026-10-17.2):
shaft, gear, the M3x10 countersunk, spring and bearings, cut through the
axis across the hex flats, z from the door face. For Paul (he has no
OpenSCAD) and the manual.

    python3 cad/tools/gear_shaft_section.py      # -> docs/gear_shaft_section.png

Shaft and gear are rendered from cad/dial_unit_housing.scad and cut with
trimesh; every number on the drawing is read from the SCAD's echo output
(TAPER_HEX / LAYOUT), not typed here. The screw, spring and bearings are
plain outlines at their nominal sizes (ISO 10642 head, QUARKZMAN 0.5 x 7).
Needs: openscad, trimesh, shapely, matplotlib.
"""
import ast, os, re, subprocess, tempfile
import numpy as np, trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.join(HERE, '..')
OUT = os.path.join(CAD, '..', 'docs', 'gear_shaft_section.png')

SCAD = '''use <{cad}/dial_unit_housing.scad>
part = "gear";
if (part == "gear") dial_gear();
if (part == "shaft") translate([0, 0, gear_z1_ - shaft_end_z_]) dial_shaft_tail_frame();
'''


def echo():
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, 'e.echo')
        subprocess.run(['openscad', '-o', out, '-D', 'show_print_layout=false',
                        os.path.join(CAD, 'dial_unit_housing.scad')], check=True, capture_output=True)
        txt = open(out).read()
    def grab(name):
        m = re.search(r'ECHO: ' + name + r' = (.*)', txt)
        return ast.literal_eval(m.group(1).replace('true', 'True').replace('false', 'False'))
    L = {k: v for k, v in grab('LAYOUT')}
    return L, {k[0]: k[1:] for k in grab('TAPER_HEX')}


def main():
    L, T = echo()
    bh, gz0, gz1, pz0, pz1, ctop = L['z'][:6]
    (tj, tcorner, hz0, send, wz0, wz1, hang, af_thr, lead, pilot0, tip, cskd, wall, csk_top,
     pocket_d, pocket_h) = L['shaft_tail']
    af_big, af_end = T['af'][0], T['af'][1]
    spring_fwd = T['spring'][0]
    lip = L['plug'][2]
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, 's.scad')
        open(src, 'w').write(SCAD.format(cad=os.path.abspath(CAD)).replace('gear_z1_', str(gz1)).replace('shaft_end_z_', str(send)))
        parts = {}
        for p in ('gear', 'shaft'):
            stl = os.path.join(d, p + '.stl')
            subprocess.run(['openscad', '-q', '-o', stl, '-D', f'part="{p}"', src], check=True, capture_output=True)
            sec = trimesh.load(stl).section(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])   # x = 0: across the flats
            # planar coords (u, v) = (y, z in the gear's frame)
            p2, _ = sec.to_2D(to_2D=np.array([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0], [0, 0, 0, 1]], float))
            parts[p] = p2

    fig, ax = plt.subplots(figsize=(11.69, 6.2), dpi=150)
    def draw_planar(p2, fc, ec, z):
        def tr(coords):
            xy = np.asarray(coords)
            return np.c_[gz1 - xy[:, 1], xy[:, 0]]                           # (z_asm, y)
        for poly in p2.polygons_full:
            ax.add_patch(MPoly(tr(poly.exterior.coords), closed=True, fc=fc, ec=ec, lw=0.8, zorder=z))
            for ring in poly.interiors:
                ax.add_patch(MPoly(tr(ring.coords), closed=True, fc='white', ec=ec, lw=0.8, zorder=z + 0.1))
    draw_planar(parts['gear'], '#f2b880', '#a0522d', 2)
    draw_planar(parts['shaft'], '#9ec5e8', '#1f4e79', 3)
    # bearings (outline only), 608: 8 x 22 x 7
    for k in range(2):
        z0 = lip + 7 * k
        for s in (1, -1):
            ax.add_patch(MPoly([[z0, s * 4], [z0 + 7, s * 4], [z0 + 7, s * 11], [z0, s * 11]], fc='#e6e6e6', ec='#777', lw=0.6, zorder=1))
    # screw: ISO 10642 M3 head (6.72, 90deg) flush at the pocket floor, shank 3.0 to the tip
    hk = (6.72 - 3.0) / 2
    for s in (1, -1):
        ax.add_patch(MPoly([[wz1, 0], [wz1, s * 3.36], [wz1 - hk, s * 1.5], [tip, s * 1.5], [tip, 0]],
                           fc='#8c8c8c', ec='#333', lw=0.7, zorder=4))
    # spring 0.5 x 7: wire band 3.0-3.5 from the pocket floor to the sled pocket floor
    for s in (1, -1):
        ax.add_patch(MPoly([[wz1, s * 3.0], [wz1 + spring_fwd, s * 3.0], [wz1 + spring_fwd, s * 3.5], [wz1, s * 3.5]],
                           fc='#d9534f', ec='#a33', lw=0.5, alpha=0.6, zorder=1))
    ax.axhline(0, color='#555', lw=0.5, ls='-.', zorder=0)
    ax.axvline(0, color='k', lw=1.2); ax.text(-0.3, 12.5, 'door face', ha='right', fontsize=8)
    ax.axvline(ctop, color='#555', lw=0.8, ls='--'); ax.text(ctop + 0.3, 12.5, f'motor sled face ({ctop})', fontsize=8)

    def note(xy, txt, xyt):
        ax.annotate(txt, xy=xy, xytext=xyt, fontsize=8, arrowprops=dict(arrowstyle='-', lw=0.6, color='#333'),
                    ha='left', va='center', zorder=6)
    note((hz0 + 0.5, af_big / 2), f'tapered hex, {hang:g}° per flat:\n{af_big:.2f} → {af_end:.2f} across the flats\n(corners trimmed to {tcorner:.2f} < 8 bore)', (3, 14.5))
    note((pilot0 + 1.0, 0.6), f'M3 pilot Ø2.7 (first {lead:g} mm Ø3.4)', (24, -9.5))
    note(((send + wz0) / 2, -1.9), f'{wz0 - send:.1f} mm gap: the taper wedges, not the end', (24, -12.5))
    note((bh - 0.5, -3.6), f'{bh - hz0:.1f} mm to the journal shoulder', (2, -14.5))
    note((wz1 - cskd / 2, -2.6), f'back wall {wall:g} mm, 90° countersink Ø{csk_top:g}', (24, -6.5))
    note((wz1 - 0.6, 1.9), f'M3×10 countersunk, head flush with the {pocket_h:g} mm pocket floor', (24, 6.5))
    note((wz1 + 6, 3.4), f'spring 0.5 × 7 × 20: {spring_fwd:g} mm installed', (26, 10))
    note((gz0 + 3, 12), 'gear 28T', (20.5, 15.5))
    note((-5, 4.5), 'T2 plug', (-7.5, 9))
    note((bh + 0.8, 5.3), 'boss on the rear bearing\'s inner ring\n(forward stop)', (8, 17.5))
    ax.set_xlim(-8.5, 40); ax.set_ylim(-16.5, 19.5); ax.set_aspect('equal')
    ax.set_xlabel('z from the door face (mm)'); ax.set_yticks([])
    rev = open(os.path.join(CAD, '..', 'REVISION')).read().strip()
    ax.set_title(f'Dial gear-shaft joint, section across the hex flats (revision {rev}) — cad/dial_unit_housing.scad §8', fontsize=10)
    fig.tight_layout(); fig.savefig(OUT); print('wrote', os.path.relpath(OUT))


if __name__ == '__main__':
    main()
