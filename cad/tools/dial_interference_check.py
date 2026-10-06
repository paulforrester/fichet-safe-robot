#!/usr/bin/env python3
"""
3D interference check for the assembled v2 dial unit.

    python3 cad/tools/dial_interference_check.py [--quick]

Renders every part IN ITS ASSEMBLED POSITION from cad/dial_unit_assembled.scad
(the printed parts plus plain-solid dummies of the motors, bearings and M3
screw heads), then intersects every pair with manifold3d and reports any
pair that overlaps by more than a hair. Moving parts (gear-shafts, pinions,
motor shafts) are re-rendered at several gear phases and at both ends of the
gear-shaft's 7mm spring travel, so the check covers the whole range of motion
— not one lucky pose.

Touching faces (a leg standing on a plate, a spacer on a bearing ring) are
expected and come out at ~0 volume; anything above TOL mm^3 is reported.
Needs: openscad, python3 with numpy, trimesh, manifold3d.
"""
import argparse, itertools, os, subprocess, sys, tempfile
import numpy as np
import trimesh
import manifold3d as mf

HERE = os.path.dirname(os.path.abspath(__file__))
ASM = os.path.join(HERE, '..', 'dial_unit_assembled.scad')
TOL = 0.5   # mm^3

STATIC = ['front', 'sled', 'deck', 'rmags'] + [f'{p}{i}' for p in ('bearings', 'm3heads') for i in range(3)]
MOVING = [f'{p}{i}' for p in ('gearshaft', 'pinion', 'motor') for i in range(3)]

# pairs that are SUPPOSED to share space (designed fits), skipped:
EXPECTED = {frozenset((f'pinion{i}', f'motor{i}')) for i in range(3)}    # D-bore on the shaft (fit 0.15, checked in 2D)


def render(part, retract, phase, d):
    out = os.path.join(d, f'{part}_{retract}_{phase}.stl')
    if not os.path.exists(out):
        subprocess.run(['openscad', '-o', out, '-D', f'part="{part}"', '-D', f'retract={retract}',
                        '-D', f'phase={phase}', '-D', 'show_magnets=false', ASM],
                       check=True, capture_output=True)
    m = trimesh.load(out)
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, dtype=np.float32),
                               tri_verts=np.asarray(m.faces, dtype=np.uint32)))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--quick', action='store_true'); a = ap.parse_args()
    poses = [(0, 0), (7, 0)] if a.quick else [(r, p) for r in (0, 3.5, 7) for p in (0, 6.4, 12.9, 19.3)]
    worst = 0.0; bad = []
    with tempfile.TemporaryDirectory() as d:
        stat = {p: render(p, 0, 0, d) for p in STATIC}
        for x, y in itertools.combinations(STATIC, 2):
            v = (stat[x] ^ stat[y]).volume()
            worst = max(worst, v)
            if v > TOL: bad.append((x, y, 0, 0, v))
        print(f'static parts: {len(STATIC)} parts, {len(STATIC)*(len(STATIC)-1)//2} pairs checked')
        for r, ph in poses:
            mov = {p: render(p, r, ph, d) for p in MOVING}
            n = 0
            for x in MOVING:
                for y in STATIC + MOVING:
                    if y == x or (y in MOVING and MOVING.index(y) < MOVING.index(x)) or frozenset((x, y)) in EXPECTED:
                        continue
                    other = stat[y] if y in stat else mov[y]
                    v = (mov[x] ^ other).volume(); n += 1
                    worst = max(worst, v)
                    if v > TOL: bad.append((x, y, r, ph, v))
            print(f'pose retract={r}mm phase={ph}deg: {n} pairs checked')
    print(f'\nlargest overlap found: {worst:.3f} mm^3 (tolerance {TOL})')
    for x, y, r, ph, v in bad:
        print(f'  OVERLAP {x} x {y} at retract={r} phase={ph}: {v:.2f} mm^3')
    print('RESULT:', 'NO INTERFERENCE' if not bad else f'{len(bad)} OVERLAPPING PAIR(S)')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
