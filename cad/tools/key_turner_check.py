#!/usr/bin/env python3
"""
3D check for the key-turner unit: key dummy (built from Paul's caliper
readings) + cap + hub + motor + frame, intersected pairwise with manifold3d
at several key angles (0..100deg CW) and motor-axis offsets up to the
coupling's 2.5mm design range. Reports any pair overlapping by > TOL mm^3.

    python3 cad/tools/key_turner_check.py
"""
import itertools, os, subprocess, sys, tempfile
import numpy as np, trimesh, manifold3d as mf

HERE = os.path.dirname(os.path.abspath(__file__))
ASM = os.path.join(HERE, '..', 'key_turner_assembled.scad')
TOL = 0.5
PARTS = ['base', 'plate', 'key', 'cap', 'hub', 'motor']
EXPECTED = {frozenset(('hub', 'motor'))}          # D-bore on the shaft (designed fit)


def render(part, ang, off, d):
    out = os.path.join(d, f'{part}_{ang}_{off[0]}_{off[1]}.stl')
    subprocess.run(['openscad', '-o', out, '-D', f'part="{part}"', '-D', f'angle={ang}',
                    '-D', f'offx={off[0]}', '-D', f'offy={off[1]}', ASM], check=True, capture_output=True)
    m = trimesh.load(out)
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                               tri_verts=np.asarray(m.faces, np.uint32)))


def main():
    poses = [(a, o) for a in (0, 50, 100) for o in ((0, 0), (2.5, 0), (0, 2.5), (1.75, 1.75), (-1.75, 1.75))]
    worst, bad = 0.0, []
    with tempfile.TemporaryDirectory() as d:
        for ang, off in poses:
            m = {p: render(p, ang, off, d) for p in PARTS}
            for x, y in itertools.combinations(PARTS, 2):
                if frozenset((x, y)) in EXPECTED:
                    continue
                v = (m[x] ^ m[y]).volume()
                worst = max(worst, v)
                if v > TOL:
                    bad.append((x, y, ang, off, v))
            print(f'angle {ang:3d}deg offset {off}: {len(PARTS)*(len(PARTS)-1)//2 - 1} pairs')
    print(f'largest overlap {worst:.3f} mm^3 (tolerance {TOL})')
    for b in bad:
        print('  OVERLAP %s x %s at angle %s offset %s: %.2f mm^3' % b)
    print('RESULT:', 'NO INTERFERENCE' if not bad else f'{len(bad)} OVERLAPS')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
