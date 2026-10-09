#!/usr/bin/env python3
"""
Check for the start/stop button mount on the electronics deck
(dial_unit_housing.scad, button_pt / wire_hole_pt; housing_decisions.md,
2026-10-09).

Reads every position from OpenSCAD's own LAYOUT echo, rebuilds the deck
outline, the Mega base plate (estimated from its published overall size,
114 x 57.5mm), the motor cans under the deck and the deck legs, and checks:
  - button: recess wall to the deck edge, distance to every deck leg's M6
    head, clear of the base plate (estimate), not above a motor can;
  - wire hole: wall to the deck edge, clear of the base plate (estimate);
  - the rendered deck STL: watertight; a slice inside the recess (z 1.2) and
    one above it (z 3.8) show holes of the right size at the right places.

    python3 cad/tools/button_mount_check.py
"""
import os, subprocess, sys, tempfile, re, ast
import numpy as np, trimesh
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.join(HERE, '..')
SCAD = os.path.join(CAD, 'dial_unit_housing.scad')
PRINT = os.path.join(CAD, 'print_electronics_deck.scad')

# Mega board frame (centred), Eagle hole pattern; base plate estimate:
# 114 x 57.5mm (SparkFun), flange past the jack end (holes at board x -5.5)
MEGA_ROT, MEGA_OFF = 244, np.array([-2.5, -5])
BASE_X, BASE_Y = (-61.2, 52.8), (-28.75, 28.75)
NEMA_HALF = 42.3 / 2
MIN = dict(edge=2.0, leg_head=1.0, base=3.0, can=3.0)   # mm, worst-case gaps required


def layout():
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, 'o.echo')
        subprocess.run(['openscad', '-o', out, '-D', 'show_print_layout=false', SCAD],
                       capture_output=True, text=True, check=True)
        txt = open(out).read()
    m = re.search(r'LAYOUT = (\[.*\])', txt)
    return {k: v for k, v in ast.literal_eval(m.group(1))}


def place(p):
    a = np.radians(MEGA_ROT); c, s = np.cos(a), np.sin(a)
    return np.array([p[0]*c - p[1]*s, p[0]*s + p[1]*c]) + MEGA_OFF


def main():
    L = layout()
    bad = []
    legs = L['deck_leg_pts']
    (bpt, b_hole, b_rec_d, b_rec_h), (wpt, w_d, w_lobe) = L['button'], L['wire_hole']
    t = L['deck_thickness']
    circ = ([Point(*p).buffer(11, 64) for p in L['mega_hole_pts_rot']] +
            [Point(*p).buffer(7.5, 64) for p in L['mega_base_hole_pts_rot']] +
            [Point(*p).buffer(14, 64) for p in legs] + [Point(*wpt).buffer(w_lobe, 64)])
    deck = unary_union(circ).convex_hull
    base = Polygon([place(p) for p in [(BASE_X[0], BASE_Y[0]), (BASE_X[1], BASE_Y[0]),
                                       (BASE_X[1], BASE_Y[1]), (BASE_X[0], BASE_Y[1])]])
    cans = unary_union([affinity.translate(affinity.rotate(box(-NEMA_HALF, -NEMA_HALF, NEMA_HALF, NEMA_HALF),
                                                           r, origin=(0, 0)), *p)
                        for p, r in zip(L['motor_pts'], L['motor_rot'])])
    B, W = Point(*bpt), Point(*wpt)
    nut_r = 11.3 / 2
    rep = [
        ('button recess wall to deck edge', deck.exterior.distance(B) - b_rec_d/2, MIN['edge']),
        ('button nut to nearest M6 head (r7)', min(B.distance(Point(*p)) for p in legs) - 7 - nut_r, MIN['leg_head']),
        ('button nut to base plate (estimate)', base.distance(B) - nut_r, MIN['base']),
        ('button body (r5) to motor cans, plan view', cans.distance(B) - b_rec_d/2, MIN['can']),
        ('wire hole wall to deck edge', deck.exterior.distance(W) - w_d/2, MIN['edge']),
        ('wire hole to base plate (estimate)', base.distance(W) - w_d/2, MIN['base']),
    ]
    for name, v, need in rep:
        ok = v >= need
        print(f'{name:45s} {v:6.2f} mm  (need >= {need})  {"ok" if ok else "PROBLEM"}')
        if not ok:
            bad.append(name)
    print(f'button web above the recess: {t - b_rec_h:.2f} mm; thread above the deck: {6 - (t - b_rec_h):.2f} mm '
          f'(washer 1.05 + nut)')

    # rendered STL
    with tempfile.TemporaryDirectory() as d:
        stl = os.path.join(d, 'deck.stl')
        subprocess.run(['openscad', '-o', stl, PRINT], capture_output=True, text=True, check=True)
        m = trimesh.load(stl)
    print(f'deck STL: watertight={m.is_watertight}, bodies={len(m.split(only_watertight=False))}, '
          f'volume={m.volume/1000:.2f} cm3')
    if not m.is_watertight:
        bad.append('deck not watertight')

    def hole_d_at(z, pt):
        sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        poly, _ = sec.to_planar() if False else (None, None)
        paths = sec.discrete
        best = None
        for path in paths:
            c = path[:, :2].mean(axis=0)
            if np.linalg.norm(c - np.array(pt)) < 1.0:
                dia = 2 * np.mean(np.linalg.norm(path[:, :2] - c, axis=1))
                best = dia
        return best

    for z, pt, want, what in [(1.2, bpt, b_rec_d, 'button recess'), (3.8, bpt, b_hole, 'button hole'),
                              (1.2, wpt, w_d, 'wire hole (bottom)'), (3.8, wpt, w_d, 'wire hole (top)')]:
        got = hole_d_at(z, pt)
        ok = got is not None and abs(got - want) < 0.15
        print(f'{what:20s} at z={z}: {"none" if got is None else f"{got:.2f}"} mm (want {want})  {"ok" if ok else "PROBLEM"}')
        if not ok:
            bad.append(what)
    print('RESULT:', 'PASS' if not bad else f'{len(bad)} PROBLEM(S): ' + ', '.join(bad))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
