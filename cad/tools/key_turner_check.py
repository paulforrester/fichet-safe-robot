#!/usr/bin/env python3
"""
Checks for the key-turner unit (v2, 5:1 geared, 2026-10-18):

1. 3D: key dummy (built from Paul's caliper readings) + cap + key shaft
   (60T gear) + pinion + bearings + washer + screw + motor + frame,
   intersected pairwise with manifold3d at several key angles (0..100deg CW)
   and key-axis offsets up to the coupling's 2.5mm design range. Reports any
   pair overlapping by > TOL mm^3.
2. Extent toward the dial unit: nothing but the key past x = 43mm.
3. 2D gear mesh from the SCAD's own tooth outlines (KG_*_PROFILE echoes):
   no overlap through one pinion tooth pitch (zero backlash and as printed),
   still none with the centre distance 0.15mm short; contact ratio >= 1.2.

    python3 cad/tools/key_turner_check.py
Needs: openscad, trimesh, manifold3d, shapely.
"""
import itertools, json, math, os, re, subprocess, sys, tempfile
import numpy as np, trimesh, manifold3d as mf
from shapely.geometry import Polygon
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
ASM = os.path.join(HERE, '..', 'key_turner_assembled.scad')
SCAD = os.path.join(HERE, '..', 'key_turner_housing.scad')
TOL = 0.5
DIAL_SIDE_LIMIT = 43.0
PARTS = ["base", "plate", "key", "cap", "shaft", "washer", "screw", "bearings", "pinion", "motor", "rmags"]
EXPECTED = {frozenset(('pinion', 'motor')),      # D-bore on the shaft (the dummy shaft is round)
            frozenset(('screw', 'shaft'))}       # the screw cuts its own thread in the pilot
NOT_DIAL_SIDE = {"key"}


def render(part, ang, off, d):
    out = os.path.join(d, f'{part}_{ang}_{off[0]}_{off[1]}.stl')
    subprocess.run(['openscad', '-o', out, '-D', f'part="{part}"', '-D', f'angle={ang}',
                    '-D', f'offx={off[0]}', '-D', f'offy={off[1]}', ASM], check=True, capture_output=True)
    m = trimesh.load(out)
    return m, mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                                  tri_verts=np.asarray(m.faces, np.uint32)))


def echoes():
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, 'o.echo')
        subprocess.run(['openscad', '-o', out, '-D', 'show_print_layout=false', SCAD], check=True, capture_output=True)
        txt = open(out).read()
    vals = {}
    for m in re.finditer(r'^ECHO: (\w+) = (.*)$', txt, re.M):
        vals[m.group(1)] = json.loads(m.group(2))
    return vals


def mesh_check(gear_pts, pinion_pts, Ng, Np, cd, n=90):
    G0, P0 = Polygon(gear_pts), Polygon(pinion_pts)
    assert G0.is_valid and P0.is_valid, 'gear profile polygon is self-intersecting'
    ov, gmin, gmax = 0.0, 1e9, 0.0
    for k in range(n):
        tp = k / n * 360 / Np
        P = affinity.rotate(P0, tp, origin=(0, 0))
        G = affinity.translate(affinity.rotate(G0, 180 + 180 / Ng - tp * Np / Ng, origin=(0, 0)), cd, 0)
        ov = max(ov, P.intersection(G).area)
        dd = P.distance(G); gmin = min(gmin, dd); gmax = max(gmax, dd)
    return ov, gmin, gmax


def contact_ratio(m, Ng, Np, xg, xp, pa):
    a = math.radians(pa)
    rbp, rbg = m * Np / 2 * math.cos(a), m * Ng / 2 * math.cos(a)
    rap, rag = m * (Np / 2 + 1 + xp), m * (Ng / 2 + 1 + xg)
    cd = m * (Ng + Np) / 2
    return (math.sqrt(rap**2 - rbp**2) + math.sqrt(rag**2 - rbg**2) - cd * math.sin(a)) / (math.pi * m * math.cos(a))


def main():
    fails = 0
    poses = [(a, o) for a in (0, 50, 100) for o in ((0, 0), (2.5, 0), (0, 2.5), (1.75, 1.75), (-1.75, 1.75))]
    worst, bad, xmax = 0.0, [], {}
    with tempfile.TemporaryDirectory() as d:
        for ang, off in poses:
            r = {p: render(p, ang, off, d) for p in PARTS}
            m = {p: v[1] for p, v in r.items()}
            for p, (tm, _) in r.items():
                if p not in NOT_DIAL_SIDE:
                    xmax[p] = max(xmax.get(p, -1e9), float(tm.bounds[1][0]))
            for x, y in itertools.combinations(PARTS, 2):
                if frozenset((x, y)) in EXPECTED:
                    continue
                v = (m[x] ^ m[y]).volume()
                worst = max(worst, v)
                if v > TOL:
                    bad.append((x, y, ang, off, v))
            print(f'angle {ang:3d}deg offset {off}: {len(PARTS)*(len(PARTS)-1)//2 - len(EXPECTED)} pairs')
    print(f'largest overlap {worst:.3f} mm^3 (tolerance {TOL})')
    for b in bad:
        print('  OVERLAP %s x %s at angle %s offset %s: %.2f mm^3' % b)
    fails += len(bad)

    far = max(xmax.values())
    ok = far <= DIAL_SIDE_LIMIT
    fails += not ok
    print(f'\n{"ok  " if ok else "FAIL"} furthest toward the dials: x = {far:.2f}mm ({max(xmax, key=xmax.get)}; limit {DIAL_SIDE_LIMIT})')

    e = echoes()
    L = {k: v for k, v in e['KEY_TURNER']}
    m_, Ng, Np, xg, xp, pa, bl, cd = L['gear']
    print('\ngear mesh (SCAD-generated tooth outlines, one full pinion tooth pitch):')
    ov0, g0, G0 = mesh_check(e['KG_GEAR_PROFILE_NOBL'], e['KG_PINION_PROFILE_NOBL'], Ng, Np, cd)
    ov, g, G = mesh_check(e['KG_GEAR_PROFILE'], e['KG_PINION_PROFILE'], Ng, Np, cd)
    ovm, gm, _ = mesh_check(e['KG_GEAR_PROFILE'], e['KG_PINION_PROFILE'], Ng, Np, cd - 0.15)
    cr = contact_ratio(m_, Ng, Np, xg, xp, pa)
    rows = [(ov0 < 1e-3 and g0 < 1e-3, f'zero backlash: overlap {ov0:.4f}mm2, flank gap {g0:.4f}-{G0:.4f}mm (conjugate: both ~0)'),
            (ov < 1e-6 and g > 0.05, f'as printed ({bl}mm backlash): overlap {ov:.4f}mm2, flank gap {g:.3f}-{G:.3f}mm'),
            (ovm < 1e-6, f'centre distance 0.15mm SHORT (print/position tolerance): overlap {ovm:.4f}mm2, gap {gm:.3f}mm'),
            (cr >= 1.2, f'contact ratio {cr:.2f} (>= 1.2)')]
    for ok, txt in rows:
        fails += not ok; print(f'  {"ok  " if ok else "FAIL"} {txt}')
    print(f'  backlash at the key: {math.degrees(bl / (m_ * Ng / 2)):.2f} deg; ratio {Ng / Np:g}:1')

    print('\nRESULT:', 'NO INTERFERENCE, MESH OK' if not fails else f'{fails} FAILURES')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
