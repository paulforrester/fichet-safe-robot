#!/usr/bin/env python3
"""
3D check for cad/fuse_holder.scad: body, lid (in place), fuse, fixed insert
A, screw/washer/wire stack A, sprung piston B (insert + wire + washer + screw
head) and the spring envelope, intersected pairwise with manifold3d with the
fuse in, pushed 2mm toward the spring (to lift it out), and removed.
Also checks the parts that must touch really do (fuse on both contact
faces), and that body/lid STLs are watertight.

    python3 cad/tools/fuse_holder_check.py
"""
import itertools, os, subprocess, sys, tempfile
import numpy as np, trimesh, manifold3d as mf

HERE = os.path.dirname(os.path.abspath(__file__))
SCAD = os.path.join(HERE, '..', 'fuse_holder.scad')
TOL = 0.05
PARTS = ['body', 'lid_placed', 'fuse', 'insA', 'screwA', 'piston', 'spring']
# designed contacts: spring sits on the piston's washer; screw stack sits on the insert
EXPECTED = {frozenset(p) for p in [('spring', 'piston'), ('screwA', 'insA')]}


def render(part, state, d):
    out = os.path.join(d, f'{part}_{state}.stl')
    r = subprocess.run(['openscad', '-o', out, '-D', f'part="{part}"', '-D', f'state="{state}"', SCAD],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out) or os.path.getsize(out) < 200:
        return None, None  # empty part (no fuse in "empty")
    m = trimesh.load(out)
    return m, mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                                   tri_verts=np.asarray(m.faces, np.uint32)))


def main():
    bad, worst = [], 0.0
    with tempfile.TemporaryDirectory() as d:
        for st in ('work', 'load', 'empty'):
            M = {}
            for p in PARTS:
                tm, mm = render(p, st, d)
                if mm is not None:
                    M[p] = (tm, mm)
            for a, b in itertools.combinations(M, 2):
                if frozenset((a, b)) in EXPECTED:
                    continue
                v = (M[a][1] ^ M[b][1]).volume()
                worst = max(worst, v)
                if v > TOL:
                    bad.append((a, b, st, v))
            msg = f'state {st:5s}: {len(M)} parts'
            if 'fuse' in M:
                f = M['fuse'][0].bounds
                ia = M['insA'][0].bounds
                pi = M['piston'][0].bounds
                gapA, gapB = f[0][0] - ia[1][0], pi[0][0] - f[1][0]
                msg += f', fuse to insert A {gapA:+.2f}mm, fuse to piston {gapB:+.2f}mm'
                if st == 'work' and (abs(gapA) > 0.01 or abs(gapB) > 0.01):
                    bad.append(('fuse', 'contacts', st, max(abs(gapA), abs(gapB))))
            print(msg)
        for p in ('body', 'lid'):
            tm, _ = render(p, 'work', d)
            print(f'{p}: watertight={tm.is_watertight}, bodies={len(tm.split(only_watertight=False))}, '
                  f'volume={tm.volume/1000:.2f} cm3, size={np.round(tm.extents, 1)}')
            if not tm.is_watertight:
                bad.append((p, 'not watertight', '-', 0))
    print(f'largest unexpected overlap {worst:.3f} mm^3 (tolerance {TOL})')
    for b in bad:
        print('  PROBLEM %s x %s (%s): %.3f' % b)
    print('RESULT:', 'PASS' if not bad else f'{len(bad)} PROBLEM(S)')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
