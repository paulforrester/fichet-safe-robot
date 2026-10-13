#!/usr/bin/env python3
"""
Electronics-deck check (dial_unit_housing.scad section 9, v3.1). Replaces
button_mount_check.py (2026-10-09), whose board position was hard-coded.

Written 2026-10-12 after the v3 deck went out with its barrel cradle on top of
a deck-screw countersink and an access hole under the board: the earlier
checks only compared a few hand-picked pairs. This one compares EVERY deck
feature with every other feature on the same face, checks the board outline
(Mega + RAMPS + USB/jack, from the RAMPS KiCad file) against every hole a
screwdriver has to reach, and verifies the rendered STL.

Reads all positions from OpenSCAD's own LAYOUT echo, so it checks what will
print.

    python3 cad/tools/deck_check.py
"""
import ast, itertools, math, os, re, subprocess, sys, tempfile
import numpy as np, trimesh
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.join(HERE, '..')
SCAD = os.path.join(CAD, 'dial_unit_housing.scad')
PRINT = os.path.join(CAD, 'print_electronics_deck.scad')

# Nearest Mega header pad EDGE to each mounting hole centre, mm, from the
# Mega shield footprint U1 in matt3u/RAMPS-1.4_KiCad ea33bdf (index = mega_hole_pts)
PAD_EDGE = [18.34, 7.92, 3.10, 4.37]
PAD_MARGIN = 0.6   # post edge to the nearest header pad (2026-10-12: 0.8 -> 0.6 for the 4.33mm bore)
NEMA_HALF = 42.3 / 2
M6_HEAD_R, BUTTON_NUT_R, BUTTON_BODY_R = 7.0, 11.3 / 2, 5.0
LEG_R = 6.0          # deck legs (on the motor plate) touching the deck underside
M6_CLEAR_R = 6.4 / 2
MIN_GAP = 2.0        # default clearance between any two features on one face


def layout():
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, 'o.echo')
        subprocess.run(['openscad', '-o', out, '-D', 'show_print_layout=false', SCAD],
                       capture_output=True, text=True, check=True)
        txt = open(out).read()
    return {k: v for k, v in ast.literal_eval(re.search(r'LAYOUT = (\[.*\])', txt).group(1))}


def rect(c, ang, L, W):
    return affinity.rotate(box(c[0] - L/2, c[1] - W/2, c[0] + L/2, c[1] + W/2), ang, origin=tuple(c))


def main():
    L = layout()
    bad = []
    def row(name, v, need, extra=''):
        ok = v >= need - 1e-9
        print(f'  {"ok  " if ok else "FAIL"} {v:7.2f}  {name} (need >= {need}){extra}')
        if not ok:
            bad.append(name)

    rot, off = L['mega_place']
    mega_o, ramps_o, jack = L['board_outlines']
    def place(g):
        return affinity.translate(affinity.rotate(g, rot, origin=(0, 0)), *off)
    board = place(unary_union([box(*mega_o[0], *mega_o[1]), box(*ramps_o[0], *ramps_o[1]),
                               box(mega_o[0][0] - jack, mega_o[0][1], mega_o[0][0], mega_o[1][1])]))
    legs = L['deck_leg_pts']; joints = L['joint_pts']
    acc_idx, acc_d = L['joint_access']
    post_h, post_d, rest_pt, rest_d, ins_d, ins_depth, clr_d, hole_depth = L['posts']
    bolts = L['mega_bolt_pts_rot']; holes_all = L['mega_hole_pts_rot']
    (bpt, b_hole, b_rec_d, b_rec_h), (wpt, w_d, w_lobe) = L['button'], L['wire_hole']
    bc, bdir, bl, bw, tgap, tw, tt = L['barrel']
    t = L['deck_thickness']

    # ---- the rendered deck (authoritative outline) ----
    with tempfile.TemporaryDirectory() as d:
        stl = os.path.join(d, 'deck.stl')
        subprocess.run(['openscad', '-o', stl, PRINT], capture_output=True, text=True, check=True)
        m = trimesh.load(stl)
    # outline slice at 2.5mm: below the barrel saddle's floor (3mm), which is open at the edge
    sec = m.section(plane_origin=[0, 0, 2.5], plane_normal=[0, 0, 1])
    loops = [Polygon(p[:, :2]) for p in sec.discrete]
    deck = Polygon(max(loops, key=lambda q: q.area).exterior)

    # ---- named features on each face ----
    u = (math.cos(math.radians(bdir)), math.sin(math.radians(bdir))); v = (-u[1], u[0])
    saddle = rect(bc, bdir, bl, bw)
    slots = [rect((bc[0] + s*tgap/2*v[0], bc[1] + s*tgap/2*v[1]), bdir, tw, tt) for s in (-1, 1)]
    top = {}      # things cut into / standing on the top face
    for n, p in zip('ABC', legs):
        top[f'deck screw {n} countersink'] = Point(p).buffer(M6_HEAD_R, 64)
    for i in acc_idx:
        top[f'access hole {i}'] = Point(joints[i]).buffer(acc_d/2, 64)
    for k, p in enumerate(bolts):
        top[f'bolt post {k}'] = Point(p).buffer(post_d[k]/2, 64)
    top['rest post'] = Point(rest_pt).buffer(rest_d/2, 64)
    top['barrel saddle'] = saddle
    for k, s in enumerate(slots):
        top[f'tie slot {k}'] = s
    top['button nut'] = Point(bpt).buffer(BUTTON_NUT_R, 64)
    top['wire hole'] = Point(wpt).buffer(w_d/2, 64)

    under = {}    # things on / cut into the underside
    for n, p in zip('ABC', legs):
        under[f'deck leg {n}'] = Point(p).buffer(LEG_R, 64)
    for i in acc_idx:
        under[f'access hole {i}'] = Point(joints[i]).buffer(acc_d/2, 64)
    for k, p in enumerate(bolts):
        under[f'post bore {k} (floor {t + post_h - hole_depth:.1f}mm)'] = Point(p).buffer(clr_d/2, 32)
    for k, s in enumerate(slots):
        under[f'tie slot {k}'] = s
    under['button recess'] = Point(bpt).buffer(b_rec_d/2, 64)
    under['wire hole'] = Point(wpt).buffer(w_d/2, 64)
    joined = set()

    print('every pair of features on the TOP face (gap between edges):')
    worst = sorted((a[1].distance(b[1]), a[0], b[0]) for a, b in itertools.combinations(top.items(), 2))
    for dd, a, b in worst[:6]:
        row(f'{a} <-> {b}', dd, MIN_GAP)
    for dd, a, b in worst[6:]:
        if dd < MIN_GAP:
            row(f'{a} <-> {b}', dd, MIN_GAP)
    print(f'  ({len(worst)} pairs, the 6 closest shown)')

    print('\nevery pair of features on the UNDERSIDE:')
    worst = sorted((a[1].distance(b[1]), a[0], b[0]) for a, b in itertools.combinations(under.items(), 2)
                   if frozenset((a[0], b[0])) not in joined)
    for dd, a, b in worst[:6]:
        row(f'{a} <-> {b}', dd, 1.5)
    for dd, a, b in worst[6:]:
        if dd < 1.5:
            row(f'{a} <-> {b}', dd, 1.5)
    print(f'  ({len(worst)} pairs, the 6 closest shown)')

    print('\nthe board (Mega + RAMPS outline + USB/jack) vs what must be reached from above:')
    for i in acc_idx:
        row(f'access hole {i} edge to the board', board.distance(top[f'access hole {i}']), 3.0)
    for n in 'AC':
        row(f'deck screw {n} countersink to the board', board.distance(top[f'deck screw {n} countersink']), 2.0)
    covB = top['deck screw B countersink'].intersection(board).area / top['deck screw B countersink'].area
    print(f'  info   deck screw B: {covB*100:.0f}% under the board (by design: driven before the boards go on)')
    for name in ['barrel saddle', 'tie slot 0', 'tie slot 1', 'button nut', 'wire hole']:
        row(f'{name} to the board', board.distance(top[name]), 2.0)

    print('\nposts:')
    for k, p in enumerate(bolts):
        hi = L['mega_bolt_pts_rot'].index(p)
        idx = [i for i, q in enumerate(holes_all) if np.allclose(q, p)][0]
        row(f'bolt post {k} radius vs nearest Mega header pad', PAD_EDGE[idx] - post_d[k]/2, PAD_MARGIN)
    ridx = [i for i, q in enumerate(holes_all) if np.allclose(q, rest_pt)][0]
    row('rest post radius vs nearest Mega header pad', PAD_EDGE[ridx] - rest_d/2, PAD_MARGIN)
    row('insert bore wall (post radius - bore radius)', min(post_d)/2 - ins_d/2, 1.5)
    row('bore floor above the deck underside', t + post_h - hole_depth, 1.0)
    smin, smax = 12.0 + 4.0, 12.0 + hole_depth - 0.5
    print(f'  info   M3 screw length: >= {smin:.0f}mm (4mm in the insert) and <= {smax:.1f}mm (no bottoming); '
          f'post top {post_h}mm above the deck')

    print('\ncradle, button, wire hole vs the deck edge:')
    edge = deck.exterior
    # v3.2: the saddle is open at its outer end (the deck ends with the square
    # body, so the adapter's tapered socket end overhangs freely). Its sides and
    # inner end must still sit >= 1.5mm inside the deck.
    saddle_in = rect((bc[0] - 1.0*u[0], bc[1] - 1.0*u[1]), bdir, bl - 2.0, bw)
    row('barrel saddle sides + inner end inside the deck (1 = yes, 1.5mm wall)', 1.0 if deck.buffer(-1.5).contains(saddle_in) else 0.0, 1.0)
    for k, s in enumerate(slots):
        row(f'tie slot {k} inside the deck (wall to edge)', min(edge.distance(Point(c)) for c in s.exterior.coords) if deck.contains(s) else -1, 1.5)
    o = (bc[0] + bl/2*u[0], bc[1] + bl/2*u[1])
    sock = LineString([(o[0] + 0.3*u[0], o[1] + 0.3*u[1]), (o[0] + 23*u[0], o[1] + 23*u[1])])
    row('saddle open at the outer end: deck under the socket (mm, negative = deck in the way)', 0 if not sock.intersects(deck) else -sock.intersection(deck).length, 0)
    # the adapter's screw terminals face the RAMPS power terminal: short leads,
    # nowhere near the button (v3.1 routed them across it)
    term = Polygon(L['ramps_power_terminal'])
    ie = Point(bc[0] - bl/2*u[0], bc[1] - bl/2*u[1])
    gap = ie.distance(term)
    row('adapter terminal end to the RAMPS power terminal, mm (need <= 15)', 15 - gap, 0, f'   [gap {gap:.1f}mm]')
    lead = LineString([ie, term.centroid])
    row('adapter-to-RAMPS lead path to the button nut', lead.distance(top['button nut']), 10.0)
    row('button recess wall to the deck edge', edge.distance(Point(bpt)) - b_rec_d/2, 2.0)
    row('button nut to nearest M6 head', min(Point(bpt).distance(Point(p)) for p in legs) - M6_HEAD_R - BUTTON_NUT_R, 1.0)
    cans = unary_union([affinity.translate(affinity.rotate(box(-NEMA_HALF, -NEMA_HALF, NEMA_HALF, NEMA_HALF), r, origin=(0, 0)), *p)
                        for p, r in zip(L['motor_pts'], L['motor_rot'])])
    row('button body (below the deck) to the motor cans, plan view', cans.distance(Point(bpt)) - BUTTON_BODY_R, 3.0)
    row('wire hole wall to the deck edge', edge.distance(Point(wpt)) - w_d/2, 2.0)
    # v3.2: no groove; the button sits beside the wire hole so its leads only
    # cross a few mm of deck underside (Paul, 2026-10-13)
    run = Point(bpt).distance(Point(wpt)) - b_rec_d/2 - w_d/2
    row('button recess to wire hole, deck the leads cross (mm, need <= 6)', 6 - run, 0, f'   [{run:.1f}mm]')
    row('button nut to the board outline (finger room)', board.distance(top['button nut']), 6.0)

    print('\nrendered STL:')
    nb = len(m.split(only_watertight=False))
    row('watertight (1 = yes)', 1.0 if m.is_watertight else 0.0, 1.0)
    row('one body (bodies - 1, negated)', -(nb - 1), 0)
    def holes_at(z):
        s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        out = []
        for p in s.discrete:
            c = p[:, :2].mean(axis=0); out.append((c, 2*np.mean(np.linalg.norm(p[:, :2] - c, axis=1))))
        return out
    def found(z, pt, want, tol=0.25):
        return any(np.linalg.norm(c - np.array(pt)) < 1.0 and abs(dia - want) < tol for c, dia in holes_at(z))
    ztop = t + post_h - 0.5
    for k, p in enumerate(bolts):
        row(f'insert bore {k} at the post top (found = 1)', 1.0 if found(ztop, p, ins_d) else 0.0, 1.0)
        row(f'post bore {k} is blind: no hole at z=0.5 (1 = blind)', 0.0 if found(0.5, p, clr_d) else 1.0, 1.0)
    # slice the recess at 2.3 (inside its 2.5mm depth) and the holes near the top
    row('button recess at z=2.3 (found = 1)', 1.0 if found(2.3, bpt, b_rec_d, 0.2) else 0.0, 1.0)
    row('button hole at z=3.8 (found = 1)', 1.0 if found(3.8, bpt, b_hole, 0.2) else 0.0, 1.0)
    row('wire hole at z=3.8 (found = 1)', 1.0 if found(3.8, wpt, w_d, 0.2) else 0.0, 1.0)
    for i in acc_idx:
        row(f'access hole {i} through the deck (found = 1)', 1.0 if found(t - 0.3, joints[i], acc_d) and found(0.3, joints[i], acc_d) else 0.0, 1.0)

    print('\nRESULT:', 'PASS' if not bad else f'{len(bad)} PROBLEM(S): ' + '; '.join(bad))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
