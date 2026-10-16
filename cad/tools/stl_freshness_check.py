#!/usr/bin/env python3
"""
Re-render every STL in cad/ from its source and compare it with the file in
the repo (volume, area, bounds, face count), so a part whose source changed
but whose STL wasn't re-exported is caught (2026-10-11: the motor plate went
out without its windows that way). Also flags an STL with no source and a
print_*.scad with no STL.

    python3 cad/tools/stl_freshness_check.py          # ~2-3 min, 8 renders in parallel
"""
import os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
import numpy as np, trimesh

CAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
# STL name -> source .scad (cad/), where the name doesn't follow print_<name>.scad
SOURCES = {
    'dial_drivetrain': 'print_drivetrain', 'dial_front_assembly': 'print_front_assembly',
    'dial_motor_sled': 'print_motor_sled', 'dial_pattern_test': 'print_dial_pattern_test',
    'dial_unit_housing': 'dial_unit_housing', 'key_turner_housing': 'key_turner_housing',
    'magnet_retainers': 'print_magnet_retainer', 'mega_base_fit_test': 'mega_base_fit_test',
    'printed_thread_test': 'printed_thread_test', 'standoff_screw_fit_test': 'standoff_screw_fit_test',
    'tube_socket_test_key_set': 'tube_socket_test_key_set',
    'dial_plug_taper_test': 'dial_plug_taper_test',
}


def source_for(name):
    s = SOURCES.get(name, 'print_' + name)
    return s if os.path.exists(os.path.join(CAD, s + '.scad')) else None


def render(args):
    name, src, out = args
    r = subprocess.run(['openscad', '-q', '-o', out, os.path.join(CAD, src + '.scad')], capture_output=True, text=True)
    return name, r.returncode


def main():
    stls = sorted(f[:-4] for f in os.listdir(CAD) if f.endswith('.stl'))
    prints = sorted(f[6:-5] for f in os.listdir(CAD) if f.startswith('print_') and f.endswith('.scad'))
    used = {source_for(n) for n in stls}
    bad = []
    for p in prints:
        if 'print_' + p not in used:
            print(f'  MISSING  print_{p}.scad has no STL'); bad.append(p)
    with tempfile.TemporaryDirectory() as d:
        jobs = []
        for n in stls:
            src = source_for(n)
            if src is None:
                print(f'  NO SRC   {n}.stl'); bad.append(n); continue
            jobs.append((n, src, os.path.join(d, n + '.stl')))
        with ThreadPoolExecutor(8) as ex:
            rc = dict(ex.map(render, jobs))
        for n, src, out in jobs:
            if rc[n] != 0:
                print(f'  RENDER ERROR  {n} ({src}.scad)'); bad.append(n); continue
            a, b = trimesh.load(os.path.join(CAD, n + '.stl')), trimesh.load(out)
            dv, da = b.volume - a.volume, b.area - a.area
            db = float(np.abs(b.bounds - a.bounds).max())
            stale = abs(dv) > 1e-3 * max(1, abs(a.volume)) or abs(da) > 1e-3 * max(1, a.area) or db > 1e-3 \
                or len(a.faces) != len(b.faces)
            if stale:
                bad.append(n)
            print(f'  {"STALE" if stale else "ok   "}    {n:26s} dV={dv/1000:+.4f}cm3 dA={da:+.2f}mm2 '
                  f'faces {len(a.faces)}/{len(b.faces)} watertight={b.is_watertight}')
    print('RESULT:', 'ALL CURRENT' if not bad else f'{len(bad)} PROBLEM(S): ' + ', '.join(bad))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
