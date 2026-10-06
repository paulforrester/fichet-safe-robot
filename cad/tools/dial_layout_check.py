#!/usr/bin/env python3
"""
Clearance + gear-mesh check for cad/dial_unit_housing.scad (v2, geared).

    python3 cad/tools/dial_layout_check.py              # check the SCAD as it is
    python3 cad/tools/dial_layout_check.py --optimise AB AC BC [--seed N]
        # re-search motor_dir / motor_rot / joint_pts / deck_leg_pts for new
        # caliper hole distances, print the SCAD lines to paste, then re-run
        # the plain check.

Reads every position straight from OpenSCAD's own echo output (the LAYOUT /
*_PROFILE echoes at the end of dial_unit_housing.scad), so the numbers
checked here are the numbers that get printed — nothing is restated.
Needs: openscad on PATH, python3 with numpy + shapely.
Every clearance printed is the margin LEFT OVER after the required minimum
in its line (so >= 0 passes); the requirement itself is in the label.
"""
import argparse, itertools, json, math, os, random, re, subprocess, sys, tempfile
import numpy as np
from shapely.geometry import Point, Polygon
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
SCAD = os.path.join(HERE, '..', 'dial_unit_housing.scad')

NEMA_HALF = (42.3 + 1.5) / 2        # can + the 1.5mm relief the sled uses (half-width)
BOLT_R = 31 / 2 * math.sqrt(2)      # bolt-hole radius from the motor axis
LEG_R, CSK_R, CB_R = 6.0, 7.0, 3.36  # CB_R: M3 countersunk head (ISO 6.72, bigger than the 6.3 mouth) on the sled's inner face
SPRING_R, BOSS_REC_R, PINION_HUB_R = 4.3, 11.5, 6.0


def openscad_echo(scad=SCAD, defines=()):
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, 'o.echo')
        cmd = ['openscad', '-o', out] + [a for k, v in defines for a in ('-D', f'{k}={v}')] + [scad]
        subprocess.run(cmd, check=True, capture_output=True)
        txt = open(out).read()
    vals = {}
    for m in re.finditer(r'^ECHO: (\w+) = (.*)$', txt, re.M):
        vals[m.group(1)] = json.loads(m.group(2))
    return vals


def kv(layout):
    return {k: v for k, v in layout}


# ---------------------------------------------------------------- geometry
def can(c, rot, half=NEMA_HALF):
    sq = Polygon([(-half, -half), (half, -half), (half, half), (-half, half)])
    return affinity.translate(affinity.rotate(sq, rot, origin=(0, 0)), c[0], c[1])


def key_mismatch(P):
    """Hausdorff distance between the joint pattern and itself turned +/-120deg."""
    def rot(Q, a):
        a = math.radians(a); R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]); return Q @ R.T
    return min(max(min(np.linalg.norm(q - p) for p in P) for q in rot(P, 120 * k)) for k in (1, 2))


def clearances(H, M, rot, bolts, J, D, rg, rp, front_r=75.0):
    cans = [can(M[i], rot[i]) for i in range(3)]
    allb = [np.array(b) for bs in bolts for b in bs]
    c = {}
    c['can to can (>= 6mm)'] = min(cans[i].distance(cans[j]) for i, j in itertools.combinations(range(3), 2)) - 6
    c['pinion tip to OTHER dials\' gear tips (>= 3mm)'] = min(
        np.linalg.norm(M[i] - H[j]) - rp - rg for i in range(3) for j in range(3) if i != j) - 3
    c['gear tip to gear tip (>= 2mm)'] = min(np.linalg.norm(H[i] - H[j]) - 2 * rg for i, j in itertools.combinations(range(3), 2)) - 2
    c['motor-screw countersink to spring pocket (>= 2mm)'] = min(np.linalg.norm(b - h) - CB_R - SPRING_R for b in allb for h in H) - 2
    c['spring pocket to motor boss recess (>= 1mm)'] = min(np.linalg.norm(H[j] - M[i]) - SPRING_R - BOSS_REC_R for i in range(3) for j in range(3)) - 1
    c['can corners inside r=70 (front plate is 75)'] = 70 - max(np.linalg.norm(np.array(s.exterior.coords), axis=1).max() for s in cans)
    jt = []
    for P in J:
        jt += [min(np.linalg.norm(P - h) for h in H) - LEG_R - rg - 1.5,                # leg vs gears (cavity)
               min(np.linalg.norm(P - m) for m in M) - LEG_R - rp - 1.5,                # leg vs pinions
               min(np.linalg.norm(P - b) for b in allb) - LEG_R - CB_R - 1.0,           # leg vs motor screw heads
               min(s.distance(Point(P)) for s in cans) - CSK_R - 3.0,                   # countersink + 3mm driver access vs cans
               front_r - 9 - np.linalg.norm(P)]                                         # leg + 3mm inside the front plate
    c['front joints (gears+1.5, pinions+1.5, screw heads+1, cans: csk+3)'] = min(jt)
    c['front joints spread (>= 70mm apart)'] = min(np.linalg.norm(a - b) for a, b in itertools.combinations(J, 2)) - 70
    c['front joints keying (+/-120deg mismatch >= 10mm)'] = key_mismatch(J) - 10
    dt = []
    for Q in D:
        dt += [min(s.distance(Point(Q)) for s in cans) - LEG_R - 3.0,
               min(np.linalg.norm(Q - P) for P in J) - LEG_R - CSK_R - 2.0,
               70 - np.linalg.norm(Q)]
    c['deck legs (cans+3, front countersinks+2, r<=70)'] = min(dt)
    c['deck legs spread (>= 60mm apart)'] = min(np.linalg.norm(a - b) for a, b in itertools.combinations(D, 2)) - 60
    return c


# ---------------------------------------------------------------- gears
def mesh_check(gear_pts, pinion_pts, Ng, Np, cd, n=90):
    G0, P0 = Polygon(gear_pts), Polygon(pinion_pts)
    assert G0.is_valid and P0.is_valid, 'gear profile polygon is self-intersecting'
    ov, gmin, gmax = 0.0, 1e9, 0.0
    for k in range(n):
        tp = k / n * 360 / Np
        P = affinity.rotate(P0, tp, origin=(0, 0))
        G = affinity.translate(affinity.rotate(G0, 180 + 180 / Ng - tp * Np / Ng, origin=(0, 0)), cd, 0)
        ov = max(ov, P.intersection(G).area)
        d = P.distance(G); gmin = min(gmin, d); gmax = max(gmax, d)
    return ov, gmin, gmax


def contact_ratio(m, Ng, Np, xg, xp, pa):
    a = math.radians(pa)
    rbp, rbg = m * Np / 2 * math.cos(a), m * Ng / 2 * math.cos(a)
    rap, rag = m * (Np / 2 + 1 + xp), m * (Ng / 2 + 1 + xg)
    cd = m * (Ng + Np) / 2
    return (math.sqrt(rap**2 - rbp**2) + math.sqrt(rag**2 - rbg**2) - cd * math.sin(a)) / (math.pi * m * math.cos(a))


# ---------------------------------------------------------------- optimiser
def optimise(ab, ac, bc, seed=1, trials=30, N=6000, rg=14.8, rp=8.2, cd=21.0):
    sys.path.insert(0, HERE)
    def holes(ab, ac, bc):
        cx = (ac**2 - bc**2) / (2 * ab); cy = -math.sqrt(ac**2 - (cx + ab / 2)**2)
        P = np.array([[-ab / 2, 0], [ab / 2, 0], [cx, cy]])
        (ax, ay), (bx, by), (qx, qy) = P
        d = 2 * (ax * (by - qy) + bx * (qy - ay) + qx * (ay - by))
        ux = ((ax*ax+ay*ay)*(by-qy) + (bx*bx+by*by)*(qy-ay) + (qx*qx+qy*qy)*(ay-by)) / d
        uy = ((ax*ax+ay*ay)*(qx-bx) + (bx*bx+by*by)*(ax-qx) + (qx*qx+qy*qy)*(bx-ax)) / d
        return P - [ux, uy]
    H = holes(ab, ac, bc)
    def unpack(v):
        M = [H[i] + cd * np.array([math.cos(math.radians(v[i])), math.sin(math.radians(v[i]))]) for i in range(3)]
        bolts = [[M[i] + BOLT_R * np.array([math.cos(math.radians(v[3+i] + 45 + 90*k)), math.sin(math.radians(v[3+i] + 45 + 90*k))])
                  for k in range(4)] for i in range(3)]
        return M, v[3:6], bolts, np.array(v[6:12]).reshape(3, 2), np.array(v[12:18]).reshape(3, 2)
    def f(v):
        M, rot, bolts, J, D = unpack(v)
        return min(clearances(H, M, rot, bolts, J, D, rg, rp).values())
    random.seed(seed); best = None
    rad = [math.degrees(math.atan2(h[1], h[0])) for h in H]
    for _ in range(trials):
        v = [rad[i] + random.uniform(-90, 90) for i in range(3)] + [random.uniform(0, 90) for _ in range(3)]
        for _ in range(6):
            a = random.uniform(0, 360); r = random.uniform(40, 66); v += [r * math.cos(math.radians(a)), r * math.sin(math.radians(a))]
        s = f(v)
        for it in range(N):
            w = v[:]; k = random.randrange(18)
            w[k] += random.gauss(0, (40 if k < 3 else 30 if k < 6 else 15) * (1 - it / N) + 0.2)
            sw = f(w)
            if sw >= s: v, s = w, sw
        if best is None or s > best[0]: best = (s, v)
    s, v = best
    r1 = lambda x: round(x, 1)
    print(f'best worst-margin {s:.2f}mm. Paste into dial_unit_housing.scad:')
    print(f'motor_dir = [{", ".join(str(r1(a % 360)) for a in v[0:3])}];')
    print(f'motor_rot = [{", ".join(str(r1(a % 90)) for a in v[3:6])}];')
    print(f'joint_pts    = [{", ".join(f"[{r1(v[6+2*i])}, {r1(v[7+2*i])}]" for i in range(3))}];')
    print(f'deck_leg_pts = [{", ".join(f"[{r1(v[12+2*i])}, {r1(v[13+2*i])}]" for i in range(3))}];')


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--optimise', nargs=3, type=float, metavar=('AB', 'AC', 'BC'))
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('-D', action='append', default=[], metavar='VAR=VALUE',
                    help='override a SCAD variable for a what-if check, e.g. -D dial_ab=33.8')
    a = ap.parse_args()
    if a.optimise:
        optimise(*a.optimise, seed=a.seed); return

    e = openscad_echo(defines=[('show_print_layout', 'false')] + [tuple(d.split('=', 1)) for d in a.D])
    L = kv(e['LAYOUT'])
    H = np.array(L['hole_pts']); M = np.array(L['motor_pts']); rot = L['motor_rot']
    bolts = L['motor_bolt_pts']; J = np.array(L['joint_pts']); D = np.array(L['deck_leg_pts'])
    m, Ng, Np, xg, xp, pa, bl, cd = L['gear']
    rg, rp = L['gear_tip_r'], L['pinion_tip_r']
    fails = 0
    print(f"dial holes AB/AC/BC = {L['dial_abc']}  (A,B,C at {np.round(H, 2).tolist()})")
    print('\n2D clearances (margin left after each requirement; >= 0 passes):')
    for k, v in clearances(H, M, rot, bolts, J, D, rg, rp, L['front_plate_r']).items():
        ok = v >= -1e-6; fails += not ok
        print(f'  {"ok  " if ok else "FAIL"} {v:7.2f}  {k}')
    # motor-to-dial distances must be exactly the gear centre distance
    cdev = max(abs(np.linalg.norm(M[i] - H[i]) - cd) for i in range(3))
    print(f'  {"ok  " if cdev < 1e-3 else "FAIL"} {cdev:7.4f}  motor shaft to own dial = centre distance {cd}mm (deviation)')
    fails += cdev >= 1e-3

    print('\ngear mesh (SCAD-generated tooth outlines, one full pinion tooth pitch):')
    ov0, g0, G0 = mesh_check(e['GEAR_PROFILE_NOBL'], e['PINION_PROFILE_NOBL'], Ng, Np, cd)
    ov, g, G = mesh_check(e['GEAR_PROFILE'], e['PINION_PROFILE'], Ng, Np, cd)
    ovm, gm, _ = mesh_check(e['GEAR_PROFILE'], e['PINION_PROFILE'], Ng, Np, cd - 0.15)
    cr = contact_ratio(m, Ng, Np, xg, xp, pa)
    rows = [(ov0 < 1e-3 and g0 < 1e-3, f'zero backlash: overlap {ov0:.4f}mm2, flank gap {g0:.4f}-{G0:.4f}mm (conjugate: both ~0)'),
            (ov < 1e-6 and g > 0.05, f'as printed ({bl}mm backlash): overlap {ov:.4f}mm2, flank gap {g:.3f}-{G:.3f}mm'),
            (ovm < 1e-6, f'centre distance 0.15mm SHORT (print/position tolerance): overlap {ovm:.4f}mm2, gap {gm:.3f}mm'),
            (cr >= 1.2, f'contact ratio {cr:.2f} (>= 1.2)')]
    for ok, txt in rows:
        fails += not ok; print(f'  {"ok  " if ok else "FAIL"} {txt}')

    bh, gz0, gz1, pz0, pz1, ctop, mface, tip, deckz, travel, plug0, plug1 = L['z']
    sp_fwd, sp_back, _ = L['spring']
    print('\naxial stack (z from the door face):')
    rows = [(gz0 - 1.5 >= bh, f'gear front face {gz0} clear of the bearing bosses (top {bh}) — spacer only touches the bearing'),
            (pz0 > bh, f'pinion front {pz0} clear of the boss tops {bh} by {pz0 - bh:.1f}mm'),
            (pz0 <= gz0 and gz1 + travel <= pz1, f'gear ({gz0}-{gz1}) stays on the pinion ({pz0}-{pz1}) over the full {travel}mm travel'),
            (pz0 - 0.5 <= tip <= pz1 - 10, f'motor shaft tip at {tip} (+/-0.5) lands inside the pinion ({pz0}-{pz1})'),
            (gz1 + travel < ctop - 0.21 - 0.5, f'gear rear at full travel ({gz1 + travel}) clear of the sled face {ctop} (countersunk motor-screw heads within 0.21mm of it)'),
            (plug1 + travel >= -0.01, f'plug tip at full travel {plug1 + travel:.1f} (>= 0: plate can sit flush on the door)'),
            (sp_back >= 9, f'spring length {sp_fwd} forward / {sp_back} pushed back (needs solid length < {sp_back})')]
    # the pinion is located by the end of the shaft's flat, and can float between the
    # bearing-boss tops (forward) and the sled face (back): check mesh at both extremes
    hub_h = L['pinion_hub_h']
    s_fwd, s_back = bh - pz0, ctop - (pz1 + hub_h)
    for sft, name in ((s_fwd, 'pinion pushed fully FORWARD onto the boss tops'), (s_back, 'pinion pushed fully BACK onto the sled')):
        lo, hi = pz0 + sft, pz1 + sft
        worst = min(max(0, min(hi, b + gz1 - gz0) - max(lo, b)) for b in (gz0, gz0 + travel)) / (gz1 - gz0)
        rows.append((worst >= 0.8, f'{name} ({sft:+.1f}mm): gear face engaged >= {worst*100:.0f}% over the full travel (>= 80%)'))
    for ok, txt in rows:
        fails += not ok; print(f'  {"ok  " if ok else "FAIL"} {txt}')

    print('\nelectronics deck:')
    mb = np.array(L['mega_base_hole_pts_rot'])
    dm = min(np.linalg.norm(p - q) for p in mb for q in D) - CSK_R - 1.3
    ok = dm >= 2; fails += not ok
    print(f'  {"ok  " if ok else "FAIL"} {dm:7.2f}  Mega base screw pilots vs deck-leg countersinks (margin, need >= 2)')
    print('\ndoor magnets (22mm rubber pot magnets, seat ring OD 29):')
    E = openscad_echo()
    M = np.array(E['MAGNET_PTS']); RING_R = 29 / 2
    J = np.array(L['joint_pts']); Hh = np.array(L['hole_pts'])
    rows = [(min(np.linalg.norm(m - j) for m in M for j in J) - RING_R - LEG_R, 1.5, 'seat ring vs front legs'),
            (min(np.linalg.norm(m - h) for m in M for h in Hh) - RING_R - L['boss_d'] / 2, 1.5, 'seat ring vs bearing bosses'),
            (L['front_plate_r'] - max(np.linalg.norm(m) for m in M) - RING_R, 2.0, 'seat ring inside the plate rim'),
            (min(np.linalg.norm(a - b) for a, b in itertools.combinations(M, 2)) - 2 * RING_R, 2.0, 'seat ring to seat ring')]
    for v, need, txt in rows:
        ok = v - need >= 0; fails += not ok
        print(f'  {"ok  " if ok else "FAIL"} {v - need:7.2f}  {txt} (>= {need}mm)')
    print(f"  {L['magnet_count']} magnets")
    print('\nRESULT:', 'ALL PASS' if fails == 0 else f'{fails} FAIL(S)')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
