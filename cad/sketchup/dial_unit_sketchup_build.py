# ============================================================
# SketchUp review model of the v2 dial unit — build script for the
# Trimble SketchUp connector (its build_model tool runs Python against a
# cloud SketchUp model; no imports allowed, `math` is pre-loaded).
#
# Not the print source: cad/dial_unit_housing.scad is. This rebuilds the
# same parts as native SketchUp geometry from the same numbers, so they
# can be looked at in SketchUp. Keep P and the constants below in sync with
# the SCAD; cad/tools/dial_layout_check.py does not read this file.
# Checked when written (2026-10-05): every derived position matches the
# SCAD's echo output within 5e-5mm, every part is closed with outward
# faces, and the per-part volumes match the SCAD STLs within 1%.
#
# Use: paste PART 1 into build_model (clean: true), then PART 2, then
# PART 3, then save_model. Units are set to mm in PART 1.
# Rebuilt 2026-10-06 (countersunk motor-screw holes in the sled, scene 6 added;
# then 6 rubber pot magnets + retainers replacing the 147 disc pockets).
# ============================================================

# ======================= PART 1: geometry + definitions =======================
up = model.get_options_manager().get_options_provider_by_name("UnitsOptions")
_k = {str(k).split('.')[-1]: k for k in list(up.keys())}
for _n, _v in [("LENGTH_FORMAT", 0), ("LENGTH_UNIT", 2), ("LENGTH_PRECISION", 1), ("AREA_UNIT", 2), ("VOLUME_UNIT", 2)]:
    up[_k[_n]] = TypedValue(int_value=_v)
# Pure-python geometry for the v2 dial unit, mirroring cad/dial_unit_housing.scad.
# Uses only `math` so the same text runs inside the SketchUp connector (no imports there:
# the SketchUp wrapper strips the import line below). All units mm, our frame:
# x right, y up on the door, z out of the door. Faces are (outer_loop, [inner_loops]),
# loops are lists of (x, y, z); windings are chosen so normals point OUT of the material.

P = dict(
    dial_ab=33.0, dial_ac=42.5, dial_bc=42.5,
    motor_dir=[216.4, 114.1, 337.1], motor_rot=[36.3, 36.3, 56.2],
    joint_pts=[[59.5, -8.3], [-25.8, -50.5], [-18.7, 60.6]],
    deck_leg_pts=[[-4.5, -59.4], [29.7, 8.2], [-50.5, 43.5]],
    mega_rotation=244.0, mega_offset=[-2.5, -5.0],
)

# ---------------- derived constants (same formulas as the SCAD) ----------------
M_GEAR, NG, NP, XG, XP, PA, BL = 1.0, 28, 14, -0.2, 0.2, 20.0, 0.25
CD = M_GEAR * (NG + NP) / 2.0
PLATE_T, LIP_H, BW, NB = 5.0, 2.0, 7.0, 2
POCKET_R = 22.15 / 2; LIP_R = 19.5 / 2; BOSS_R = POCKET_R + 2.5
BOSS_H = LIP_H + NB * BW                      # 16
JOURNAL_R, SPACER_R, SPACER_H, GEAR_FACE, TRAVEL = 7.85 / 2, 5.5, 1.5, 6.0, 7.0
GEAR_Z0 = BOSS_H + SPACER_H; GEAR_Z1 = GEAR_Z0 + GEAR_FACE
PLUG_Z0, PLUG_LEN = -2.0, 5.0
PIN_Z0 = GEAR_Z0 - 0.5; PIN_FACE = GEAR_FACE + TRAVEL + 1; PIN_Z1 = PIN_Z0 + PIN_FACE
PIN_HUB_H = 4.0; PIN_HUB_R_VISUAL = 5.9        # (real hub is 6.0; 5.9 keeps it inside the tooth roots for a clean face)
CAVITY_TOP = PIN_Z1 + PIN_HUB_H + 0.5          # 35.5
SLED_T = 6.0; MOTOR_FACE = CAVITY_TOP + SLED_T # 41.5
SHAFT_LEN = 24.0; SHAFT_TIP = MOTOR_FACE - SHAFT_LEN
SPRING_R = 8.6 / 2; GEAR_SPRING_D = 2.0; SLED_SPRING_D = 3.0
DECK_H = 48.0 + 6.0; DECK_Z = MOTOR_FACE + DECK_H; DECK_T = 5.0
LEG_R = 6.0; PILOT_R = 5.4 / 2; PILOT_D = 12.0
M6_CLR_R = 6.4 / 2; CSK_R = 14.0 / 2; CSK_D = (14.0 - 6.4) / 2
BOSS_REC_R = 23.0 / 2; BOSS_REC_H = 2.5; SHAFT_HOLE_R = 7.0 / 2
BOLT_SQ = 31.0; BOLT_R = 3.4 / 2; CB_R = 6.3 / 2; CB_D = (6.3 - 3.4) / 2   # M3 90deg countersink (2026-10-06)
NEMA = 42.3; CAN_CLR = 1.5
RMAG_R, RMAG_H, RMAG_HOLE_R, RMAG_RING_R, RMAG_SEAT = 11.0, 6.0, 22.4 / 2, 29.0 / 2, 6.0 - 0.2   # 22mm rubber pot magnets (2026-10-06)
RMAG_RET_R, RMAG_RET_T, RMAG_SCREW_R = 27.0 / 2, 3.0, 4.5 / 2
RMAG_POS_R, RMAG_ROT = 53.5, 26.75
FRONT_R = 75.0; PTR_LEN, PTR_W = 10.0, 16.0
MEGA_PILOT_R = 2.6 / 2
MEGA_HOLES = [[-35.52, -24.11], [-35.52, 24.15], [39.41, 24.15], [45.76, -24.11]]
MEGA_BASE_HOLES = [[5.6, -19.3], [5.4, 18.7], [-56.3, -25.0], [-56.1, 24.0]]
STAR_TIP_D = 7.73 - 0.35; STAR_ROOT_D = (7.73 - 2 * 2.00) - 0.35; STAR_W = 1.04


def rot2(p, a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a)
    return [p[0] * c - p[1] * s, p[0] * s + p[1] * c]


def holes():
    ab, ac, bc = P['dial_ab'], P['dial_ac'], P['dial_bc']
    cx = (ac * ac - bc * bc) / (2 * ab); cy = -math.sqrt(ac * ac - (cx + ab / 2) ** 2)
    pts = [[-ab / 2, 0.0], [ab / 2, 0.0], [cx, cy]]
    (ax, ay), (bx, by), (qx, qy) = pts
    d = 2 * (ax * (by - qy) + bx * (qy - ay) + qx * (ay - by))
    ux = ((ax*ax+ay*ay)*(by-qy) + (bx*bx+by*by)*(qy-ay) + (qx*qx+qy*qy)*(ay-by)) / d
    uy = ((ax*ax+ay*ay)*(qx-bx) + (bx*bx+by*by)*(ax-qx) + (qx*qx+qy*qy)*(bx-ax)) / d
    return [[p[0] - ux, p[1] - uy] for p in pts]


H = holes()
MOT = [[H[i][0] + CD * math.cos(math.radians(P['motor_dir'][i])),
        H[i][1] + CD * math.sin(math.radians(P['motor_dir'][i]))] for i in range(3)]
BOLTS = [[[MOT[i][0] + q[0], MOT[i][1] + q[1]] for q in
          [rot2([BOLT_SQ / 2 * (1 if k < 2 else -1), BOLT_SQ / 2 * (1 if k % 2 == 0 else -1)], P['motor_rot'][i]) for k in range(4)]]
         for i in range(3)]
MEGA_BASE_ROT = [[rot2(p, P['mega_rotation'])[0] + P['mega_offset'][0], rot2(p, P['mega_rotation'])[1] + P['mega_offset'][1]] for p in MEGA_BASE_HOLES]
MEGA_HOLES_ROT = [[rot2(p, P['mega_rotation'])[0] + P['mega_offset'][0], rot2(p, P['mega_rotation'])[1] + P['mega_offset'][1]] for p in MEGA_HOLES]


# ---------------- 2D helpers ----------------
def circle(cx, cy, r, n, a0=0.0):
    return [[cx + r * math.cos(a0 + 2 * math.pi * i / n), cy + r * math.sin(a0 + 2 * math.pi * i / n)] for i in range(n)]


def area2(loop):
    a = 0.0
    for i in range(len(loop)):
        x0, y0 = loop[i][0], loop[i][1]; x1, y1 = loop[(i + 1) % len(loop)][0], loop[(i + 1) % len(loop)][1]
        a += x0 * y1 - x1 * y0
    return a / 2


def ccw(loop):
    return loop if area2(loop) > 0 else loop[::-1]


def hull(points):
    pts = sorted(set((round(p[0], 6), round(p[1], 6)) for p in points))
    def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 1e-9: lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 1e-9: upper.pop()
        upper.append(p)
    return [list(p) for p in lower[:-1] + upper[:-1]]


def inv_deg(a):
    return (math.tan(math.radians(a)) - math.radians(a)) * 180 / math.pi


def gear_profile(m, N, x, pa, bl, steps=10):
    r = m * N / 2; rb = r * math.cos(math.radians(pa)); ra = r + m * (1 + x); rf = r - m * (1.25 - x)
    s = m * (math.pi / 2 + 2 * x * math.tan(math.radians(pa))) - bl / 2
    th = s / (2 * r) * 180 / math.pi
    r0 = max(rb, rf)
    fl = []
    for k in range(steps + 1):
        R = r0 + (ra - r0) * k / steps
        fl.append([R, th + inv_deg(pa) - inv_deg(math.degrees(math.acos(min(1.0, rb / R))))])
    if rf < rb:
        fl = [[rf, fl[0][1]]] + fl
    p = 360.0 / N; h0 = fl[0][1]; out = []
    for i in range(N):
        c = i * p
        for R, h in fl:
            out.append([R * math.cos(math.radians(c - h)), R * math.sin(math.radians(c - h))])
        for R, h in reversed(fl):
            out.append([R * math.cos(math.radians(c + h)), R * math.sin(math.radians(c + h))])
        for j in range(1, 5):
            t = c + h0 + (p - 2 * h0) * j / 5
            out.append([rf * math.cos(math.radians(t)), rf * math.sin(math.radians(t))])
    return out


def tooth_profile(r_tip, r_root, teeth, width):
    pitch = 360.0 / teeth
    hwt = math.degrees(math.asin(min(1.0, (width / 2) / r_tip))); hwr = math.degrees(math.asin(min(1.0, (width / 2) / r_root)))
    out = []
    for i in range(teeth):
        for R, a in ((r_root, i * pitch - hwr), (r_tip, i * pitch - hwt), (r_tip, i * pitch + hwt), (r_root, i * pitch + hwr)):
            out.append([R * math.cos(math.radians(a)), R * math.sin(math.radians(a))])
    return out


def front_outline(n=96):
    # circle r75 unioned with the pointer triangle (-8,70),(8,70),(0,85)
    a = 289.0; b = 1972.0; c = -661.0   # (8-8t)^2+(70+15t)^2 = 75^2  ->  a t^2 + b t + c = 0
    t = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
    xi, yi = 8 - 8 * t, 70 + 15 * t
    ai = math.atan2(yi, xi)        # right intersection angle (just under 90deg)
    pts = []
    for p in circle(0, 0, FRONT_R, n):
        ang = math.atan2(p[1], p[0])
        if not (ai < ang < math.pi - ai):
            pts.append(p)
    # rotate list so it starts just after the left intersection, then insert pointer
    pts = sorted(pts, key=lambda p: (math.atan2(p[1], p[0]) - (math.pi - ai)) % (2 * math.pi))
    return ccw(pts + [[xi, yi], [0.0, FRONT_R + PTR_LEN], [-xi, yi]])


def magnet_pts():
    return [[RMAG_POS_R * math.cos(math.radians(RMAG_ROT + 60 * k)), RMAG_POS_R * math.sin(math.radians(RMAG_ROT + 60 * k))] for k in range(6)]


def sled_outline():
    pts = []
    for i in range(3):
        hs = (NEMA + CAN_CLR + 6) / 2
        pts += [[MOT[i][0] + q[0], MOT[i][1] + q[1]] for q in [rot2(v, P['motor_rot'][i]) for v in ([-hs, -hs], [hs, -hs], [hs, hs], [-hs, hs])]]
    for p in P['joint_pts']: pts += circle(p[0], p[1], CSK_R + 4, 48)
    for p in P['deck_leg_pts']: pts += circle(p[0], p[1], LEG_R + 1, 48)
    for p in H: pts += circle(p[0], p[1], SPRING_R + 3, 32)
    return ccw(hull(pts))


def deck_outline():
    pts = []
    for p in MEGA_HOLES_ROT: pts += circle(p[0], p[1], 11, 32)
    for p in MEGA_BASE_ROT: pts += circle(p[0], p[1], 7.5, 32)
    for p in P['deck_leg_pts']: pts += circle(p[0], p[1], 14, 48)
    return ccw(hull(pts))


# ---------------- 3D face builders ----------------
def L3(loop, z): return [(p[0], p[1], z) for p in loop]


def hface(loop2, z, up, holes2=()):
    """horizontal face at z. up=True -> normal +z (outer CCW), else -z (outer CW). holes opposite."""
    o = ccw(loop2)
    if not up: o = o[::-1]
    hs = []
    for h in holes2:
        hh = ccw(h)
        hs.append(L3(hh[::-1] if up else hh, z))
    return (L3(o, z), hs)


def wall(loop2, z0, z1, outward=True, loop2_top=None):
    """vertical (or conical when loop2_top given, same point count) band. outward=True: the
    loop bounds material on its inside (outer skin); False: hole wall (material outside)."""
    a = ccw(loop2); b = ccw(loop2_top) if loop2_top else a
    faces = []
    n = len(a)
    for i in range(n):
        j = (i + 1) % n
        q = [(a[i][0], a[i][1], z0), (a[j][0], a[j][1], z0), (b[j][0], b[j][1], z1), (b[i][0], b[i][1], z1)]
        if z1 < z0: q = q[::-1]
        faces.append((q if outward else q[::-1], []))
    return faces


def blind_hole_from_top(c, r, n, ztop, depth):
    """walls + bottom of a blind round hole opening at ztop going down"""
    lp = circle(c[0], c[1], r, n)
    return wall(lp, ztop - depth, ztop, outward=False) + [hface(lp, ztop - depth, True)]


def blind_hole_from_bottom(c, r, n, zbot, depth):
    lp = circle(c[0], c[1], r, n)
    return wall(lp, zbot, zbot + depth, outward=False) + [hface(lp, zbot + depth, False)]


# ---------------- parts ----------------
def front_assembly():
    out = front_outline(); mags = magnet_pts()
    lip = [circle(h[0], h[1], LIP_R, 48) for h in H]
    pocket = [circle(h[0], h[1], POCKET_R, 48) for h in H]
    boss = [circle(h[0], h[1], BOSS_R, 48) for h in H]
    legs = [circle(p[0], p[1], LEG_R, 24) for p in P['joint_pts']]
    mh = [circle(m[0], m[1], RMAG_HOLE_R, 48) for m in mags]
    mr = [circle(m[0], m[1], RMAG_RING_R, 48) for m in mags]
    F = []
    F.append(hface(out, 0.0, False, lip + mh))
    for i in range(len(mags)):                          # magnet through hole + seat ring
        F += wall(mh[i], 0.0, RMAG_SEAT, outward=False)
        F += wall(mr[i], PLATE_T, RMAG_SEAT, outward=True)
        F.append(hface(mr[i], RMAG_SEAT, True, [mh[i]]))
    for i in range(3):
        F += wall(lip[i], 0.0, LIP_H, outward=False)
        F.append(hface(pocket[i], LIP_H, True, [lip[i]]))
        F += wall(pocket[i], LIP_H, BOSS_H, outward=False)
        F.append(hface(boss[i], BOSS_H, True, [pocket[i]]))
        F += wall(boss[i], PLATE_T, BOSS_H, outward=True)
    F.append(hface(out, PLATE_T, True, boss + legs + mr))
    F += wall(out, 0.0, PLATE_T, outward=True)
    for i, p in enumerate(P['joint_pts']):
        F += wall(legs[i], PLATE_T, CAVITY_TOP, outward=True)
        F.append(hface(legs[i], CAVITY_TOP, True, [circle(p[0], p[1], PILOT_R, 16)]))
        F += blind_hole_from_top(p, PILOT_R, 16, CAVITY_TOP, PILOT_D)
    return F


def rmag_magnet():
    c = circle(0, 0, RMAG_R, 48)
    return [hface(c, 0.0, False), hface(c, RMAG_H, True)] + wall(c, 0.0, RMAG_H, True)


def rmag_retainer():
    o = circle(0, 0, RMAG_RET_R, 48); i = circle(0, 0, RMAG_SCREW_R, 16)
    return [hface(o, 0.0, False, [i]), hface(o, RMAG_RET_T, True, [i])] + wall(o, 0, RMAG_RET_T, True) + wall(i, 0, RMAG_RET_T, False)


def motor_sled():
    z0, z1 = CAVITY_TOP, MOTOR_FACE
    out = sled_outline()
    shaft = [circle(m[0], m[1], SHAFT_HOLE_R, 24) for m in MOT]
    rec = [circle(m[0], m[1], BOSS_REC_R, 48) for m in MOT]
    cb = [circle(b[0], b[1], CB_R, 16) for bs in BOLTS for b in bs]
    bh = [circle(b[0], b[1], BOLT_R, 16) for bs in BOLTS for b in bs]
    spr = [circle(h[0], h[1], SPRING_R, 24) for h in H]
    jc = [circle(p[0], p[1], M6_CLR_R, 24) for p in P['joint_pts']]
    jk = [circle(p[0], p[1], CSK_R, 24) for p in P['joint_pts']]
    dl = [circle(p[0], p[1], LEG_R, 24) for p in P['deck_leg_pts']]
    F = [hface(out, z0, False, shaft + cb + spr + jc), hface(out, z1, True, rec + bh + jk + dl)]
    F += wall(out, z0, z1, outward=True)
    zr = z1 - BOSS_REC_H
    for i in range(3):
        F += wall(shaft[i], z0, zr, outward=False)
        F.append(hface(rec[i], zr, True, [shaft[i]]))
        F += wall(rec[i], zr, z1, outward=False)
    for k in range(len(cb)):
        F += wall(cb[k], z0, z0 + CB_D, outward=False, loop2_top=bh[k])   # countersink cone
        F += wall(bh[k], z0 + CB_D, z1, outward=False)
    for h in H: F += blind_hole_from_bottom(h, SPRING_R, 24, z0, SLED_SPRING_D)
    zc = z1 - CSK_D
    for i in range(3):
        F += wall(jc[i], z0, zc, outward=False)
        F += wall(jc[i], zc, z1, outward=False, loop2_top=jk[i])
    for i, p in enumerate(P['deck_leg_pts']):
        F += wall(dl[i], z1, DECK_Z, outward=True)
        F.append(hface(dl[i], DECK_Z, True, [circle(p[0], p[1], PILOT_R, 16)]))
        F += blind_hole_from_top(p, PILOT_R, 16, DECK_Z, PILOT_D)
    return F


def deck():
    z0, z1 = DECK_Z, DECK_Z + DECK_T
    out = deck_outline()
    jc = [circle(p[0], p[1], M6_CLR_R, 24) for p in P['deck_leg_pts']]
    jk = [circle(p[0], p[1], CSK_R, 24) for p in P['deck_leg_pts']]
    mp = [circle(p[0], p[1], MEGA_PILOT_R, 12) for p in MEGA_BASE_ROT]
    F = [hface(out, z0, False, jc + mp), hface(out, z1, True, jk + mp)]
    F += wall(out, z0, z1, outward=True)
    zc = z1 - CSK_D
    for i in range(3):
        F += wall(jc[i], z0, zc, outward=False)
        F += wall(jc[i], zc, z1, outward=False, loop2_top=jk[i])
    for c in mp: F += wall(c, z0, z1, outward=False)
    return F


def gear_shaft():
    """local print frame: z=0 gear rear (spring) face, plug on top"""
    g = gear_profile(M_GEAR, NG, XG, PA, BL)
    spr = circle(0, 0, SPRING_R, 24); sp = circle(0, 0, SPACER_R, 32); jr = circle(0, 0, JOURNAL_R, 32)
    star = tooth_profile(STAR_TIP_D / 2, STAR_ROOT_D / 2, 8, STAR_W)
    zj = GEAR_FACE + SPACER_H; zp = zj + (GEAR_Z0 - SPACER_H - PLUG_Z0); zt = zp + PLUG_LEN
    F = [hface(g, 0.0, False, [spr])]
    F += blind_hole_from_bottom([0, 0], SPRING_R, 24, 0.0, GEAR_SPRING_D)
    F += wall(g, 0.0, GEAR_FACE, outward=True)
    F.append(hface(g, GEAR_FACE, True, [sp]))
    F += wall(sp, GEAR_FACE, zj, outward=True)
    F.append(hface(sp, zj, True, [jr]))
    F += wall(jr, zj, zp, outward=True)
    F.append(hface(jr, zp, True, [star]))
    F += wall(star, zp, zt, outward=True)
    F.append(hface(star, zt, True))
    return F


def _dbore_loops(r=5.0 / 2 + 0.15, flat_y=2.0 + 0.15, n=32):
    """round bore loop with the two chord points inserted, the D loop, and the cap segment"""
    a1 = math.asin(flat_y / r); a2 = math.pi - a1     # chord endpoints (right, left)
    ang = sorted(set([2 * math.pi * i / n for i in range(n)] + [a1, a2]))
    full = [[r * math.cos(a), r * math.sin(a)] for a in ang]
    dl = [p for a, p in zip(ang, full) if not (a1 < a < a2)]
    seg = [p for a, p in zip(ang, full) if a1 <= a <= a2]
    return full, dl, seg


def pinion():
    """local print frame: z=0 hub end (motor side), teeth on top"""
    pr = gear_profile(M_GEAR, NP, XP, PA, BL)
    hub = circle(0, 0, PIN_HUB_R_VISUAL, 48)
    full, dl, seg = _dbore_loops()
    zr = 2.5; zt = PIN_HUB_H + PIN_FACE
    F = [hface(hub, 0.0, False, [full])]
    F += wall(hub, 0.0, PIN_HUB_H, outward=True)
    F.append(hface(pr, PIN_HUB_H, False, [hub]))
    F += wall(pr, PIN_HUB_H, zt, outward=True)
    F.append(hface(pr, zt, True, [dl]))
    F += wall(full, 0.0, zr, outward=False)
    F.append(hface(seg, zr, False))                       # where the D starts: material above the flat
    F += wall(dl, zr, zt, outward=False)
    return F


def motor_dummy():
    """local: origin on the shaft axis at the mounting face, can along +z, boss+shaft along -z"""
    h = NEMA / 2; sq = [[-h, -h], [h, -h], [h, h], [-h, h]]
    boss = circle(0, 0, 11.0, 48); sh = circle(0, 0, 2.5, 24)
    F = [hface(sq, 0.0, False, [boss]), hface(sq, 48.0, True)] + wall(sq, 0.0, 48.0, True)
    F += wall(boss, -2.0, 0.0, True) + [hface(boss, -2.0, False, [sh])]
    F += wall(sh, -SHAFT_LEN, -2.0, True) + [hface(sh, -SHAFT_LEN, False)]
    return F


def bearing_608():
    o = circle(0, 0, 11.0, 48); i = circle(0, 0, 4.0, 32)
    return [hface(o, 0.0, False, [i]), hface(o, BW, True, [i])] + wall(o, 0, BW, True) + wall(i, 0, BW, False)


def spring_placeholder(length):
    o = circle(0, 0, 3.6, 16); i = circle(0, 0, 3.1, 16)
    return [hface(o, 0.0, False, [i]), hface(o, length, True, [i])] + wall(o, 0, length, True) + wall(i, 0, length, False)


def door_reference(size=170.0, thick=8.0):
    s = size / 2; sq = [[-s, -s * 0.9], [s, -s * 0.9], [s, s * 1.1], [-s, s * 1.1]]
    hl = [circle(h[0], h[1], 13.0 / 2, 32) for h in H]
    F = [hface(sq, -thick, False, hl), hface(sq, 0.0, True, hl)] + wall(sq, -thick, 0.0, True)
    for c in hl: F += wall(c, -thick, 0.0, False)
    return F


def mega_envelope():
    hx, hy = 101.52 / 2, 53.3 / 2; sq = [[-hx, -hy], [hx, -hy], [hx, hy], [-hx, hy]]
    return [hface(sq, 0.0, False), hface(sq, 30.0, True)] + wall(sq, 0.0, 30.0, True)


PARTS = dict(front=front_assembly, sled=motor_sled, deck=deck, gearshaft=gear_shaft, pinion=pinion,
             motor=motor_dummy, bearing=bearing_608, door=door_reference, mega=mega_envelope,
             rmag=rmag_magnet, retainer=rmag_retainer)

# ================= SketchUp adapter (runs inside build_model) =================
S = 1.0 / 25.4   # mm -> inch

def to_gi(F):
    gi = GeometryInput(); verts = []; vid = {}
    def idx(p):
        k = (round(p[0], 5), round(p[1], 5), round(p[2], 5))
        if k not in vid:
            vid[k] = len(verts); verts.append(SUPoint3D(p[0] * S, p[1] * S, p[2] * S))
        return vid[k]
    fl = [([idx(p) for p in o], [[idx(p) for p in h] for h in hs]) for o, hs in F]
    gi.set_vertices(verts)
    for o, hs in fl:
        lp = LoopInput()
        for i in o: lp.add_vertex_index(i)
        fi, gi = gi.add_face(lp)
        for h in hs:
            il = LoopInput()
            for i in h: il.add_vertex_index(i)
            gi = gi.face_add_inner_loop(fi, il)
    return gi

def get_mat(name, r, g, b, a=255):
    ex = {m.get_name(): m for m in model.get_materials()}
    if name in ex: return ex[name]
    m = Material(); m.set_name(name); m.set_color(SUColor(r, g, b, a)); model.add_materials([m])
    return m

def soften(ents, max_deg=35.0):
    c = math.cos(math.radians(max_deg)); n_soft = 0
    for e in ents.get_edges():
        fs = e.get_faces()
        if len(fs) == 2:
            a, b = fs[0].get_normal(), fs[1].get_normal()
            dot = a.x * b.x + a.y * b.y + a.z * b.z
            if dot > c and not (abs(a.z) > 0.999 and abs(b.z) > 0.999):
                e.set_soft(True); e.set_smooth(True); n_soft += 1
    return n_soft

def make_def(name, F, mat):
    for d in model.get_component_definitions():
        if d.get_name() == name:
            return d, 'existing'
    cd = ComponentDefinition(); cd.set_name(name); model.add_component_definitions([cd])
    cd.get_entities().fill(to_gi(F), weld_vertices=True)
    ns = soften(cd.get_entities())
    for f in cd.get_entities().get_faces():
        f.set_front_material(mat); f.set_back_material(mat)
    return cd, ns

mats = {
    'front': get_mat('Front plate PETG', 74, 88, 104),
    'sled': get_mat('Motor sled PETG', 120, 136, 152),
    'deck': get_mat('Electronics deck PETG', 160, 172, 184),
    'gearshaft': get_mat('Gear-shaft PETG-CF', 230, 145, 56),
    'pinion': get_mat('Pinion PETG-CF', 106, 168, 79),
    'motor': get_mat('NEMA17 dummy', 40, 40, 44, 150),
    'bearing': get_mat('608 bearing steel', 190, 192, 196),
    'door': get_mat('Safe door reference', 120, 110, 95, 90),
    'mega': get_mat('Mega envelope', 40, 150, 160, 70),
    'spring': get_mat('Spring placeholder', 200, 40, 40),
    'rmag': get_mat('Rubber magnet (black)', 30, 30, 32),
    'retainer': get_mat('Magnet retainer PETG', 160, 172, 184),
}
names = {
    'front': 'Front plate (base) + bosses + legs', 'sled': 'Motor sled + deck legs', 'deck': 'Electronics deck',
    'gearshaft': 'Dial gear-shaft (28T)', 'pinion': 'Motor pinion (14T)', 'motor': 'NEMA17 17HE19-2004S (dummy)',
    'bearing': '608 bearing', 'rmag': 'Rubber pot magnet 22x6 (Wukong)', 'retainer': 'Magnet retainer', 'door': 'Safe door (reference, dial holes)', 'mega': 'Arduino Mega + RAMPS envelope (placeholder)',
}
report = {}
for key, fn in PARTS.items():
    cd, ns = make_def(names[key], fn(), mats[key])
    report[key] = {'faces': len(cd.get_entities().get_faces()), 'softened': ns, 'manifold': cd.is_manifold()}
spr_len = (CAVITY_TOP + SLED_SPRING_D) - (GEAR_Z1 - GEAR_SPRING_D)
cd, ns = make_def('Spring (placeholder, 17mm installed)', spring_placeholder(spr_len), mats['spring'])
report['spring'] = {'faces': len(cd.get_entities().get_faces()), 'manifold': cd.is_manifold()}
session_state['layout'] = {'H': H, 'MOT': MOT, 'MAGS': magnet_pts(), 'motor_dir': P['motor_dir'], 'motor_rot': P['motor_rot'],
                           'mega_rotation': P['mega_rotation'], 'mega_offset': P['mega_offset']}
session_state['z'] = {'GEAR_Z1': GEAR_Z1, 'CAVITY_TOP': CAVITY_TOP, 'MOTOR_FACE': MOTOR_FACE, 'DECK_Z': DECK_Z,
                      'DECK_T': DECK_T, 'LIP_H': LIP_H, 'BW': BW, 'NB': NB, 'NG': NG, 'NP': NP,
                      'spring_z0': GEAR_Z1 - GEAR_SPRING_D}
result = report

# ======================= PART 2: place the parts (assembled + exploded) =======================
IN = 1.0 / 25.4
L = session_state['layout']; Z = session_state['z']
H, MOT = L['H'], L['MOT']
defs = {d.get_name(): d for d in model.get_component_definitions()}
def D(prefix):
    for n, d in defs.items():
        if n.startswith(prefix): return d
    raise Exception('no def ' + prefix)
def T(rotz=0.0, flipx=False, t=(0, 0, 0)):
    c, s = math.cos(math.radians(rotz)), math.sin(math.radians(rotz))
    m = [c, s, 0, 0,  s, -c, 0, 0,  0, 0, -1, 0] if flipx else [c, s, 0, 0,  -s, c, 0, 0,  0, 0, 1, 0]
    return SUTransformation(m + [t[0] * IN, t[1] * IN, t[2] * IN, 1])
existing = {l.get_name(): l for l in model.get_layers()}
tag_names = ['Front plate', 'Motor sled', 'Electronics deck', 'Gear-shafts', 'Pinions', '608 bearings',
             'Motors (dummy)', 'Springs (placeholder)', 'Mega envelope (placeholder)', 'Safe door (reference)', 'Door magnets',
             'Assembled view', 'Exploded view']
new = []
for n in tag_names:
    if n not in existing:
        l = Layer(); l.set_name(n); new.append(l)
if new: model.add_layers(new)
tags = {l.get_name(): l for l in model.get_layers()}
def place(parent, d, name, tr, tag):
    inst = d.create_instance(); inst.set_name(name); inst.set_transform(tr)
    parent.get_entities().add_instance(inst); inst.set_layer(tags[tag])
    return inst
def build(wrapper_name, offset_su, explode):
    g = Group(); model.get_entities().add_group(g); g.set_name(wrapper_name)
    # our frame (x right, y up the door, z out of the door) -> SketchUp (X, Z up, -Y toward the viewer)
    g.set_transform(SUTransformation([1, 0, 0, 0,  0, 0, 1, 0,  0, -1, 0, 0,
                                      offset_su[0] * IN, offset_su[1] * IN, offset_su[2] * IN, 1]))
    e = (lambda k: explode.get(k, 0.0))
    place(g, D('Front plate'), 'Front plate', T(t=(0, 0, e('front'))), 'Front plate')
    place(g, D('Motor sled'), 'Motor sled', T(t=(0, 0, e('sled'))), 'Motor sled')
    place(g, D('Electronics deck'), 'Electronics deck', T(t=(0, 0, e('deck'))), 'Electronics deck')
    for i in range(3):
        beta = L['motor_dir'][i] + 180.0
        nm = 'ABC'[i]
        place(g, D('Dial gear-shaft'), 'Gear-shaft dial ' + nm, T(beta + 180 + 180.0 / Z['NG'], True, (H[i][0], H[i][1], Z['GEAR_Z1'] + e('gear'))), 'Gear-shafts')
        place(g, D('Motor pinion'), 'Pinion motor ' + str(i + 1), T(beta, True, (MOT[i][0], MOT[i][1], Z['CAVITY_TOP'] - 0.5 + e('pinion'))), 'Pinions')
        place(g, D('NEMA17'), 'Motor ' + str(i + 1) + ' (drives dial ' + nm + ')', T(L['motor_rot'][i], False, (MOT[i][0], MOT[i][1], Z['MOTOR_FACE'] + e('motor'))), 'Motors (dummy)')
        for k in range(Z['NB']):
            place(g, D('608 bearing'), '608 bearing dial ' + nm + ' #' + str(k + 1), T(t=(H[i][0], H[i][1], Z['LIP_H'] + k * Z['BW'] + e('bearing') + k * e('bearing_step'))), '608 bearings')
        place(g, D('Spring'), 'Spring dial ' + nm, T(t=(H[i][0], H[i][1], Z['spring_z0'] + e('spring'))), 'Springs (placeholder)')
    for k, m in enumerate(L['MAGS']):
        place(g, D('Rubber pot magnet'), 'Door magnet ' + str(k + 1), T(t=(m[0], m[1], -0.2 - e('rmag'))), 'Door magnets')
        place(g, D('Magnet retainer'), 'Magnet retainer ' + str(k + 1), T(t=(m[0], m[1], 5.8 + e('retainer'))), 'Door magnets')
    mo = L['mega_offset']
    place(g, D('Arduino Mega'), 'Mega + RAMPS envelope', T(L['mega_rotation'], False, (mo[0], mo[1], Z['DECK_Z'] + Z['DECK_T'] + 3 + e('mega'))), 'Mega envelope (placeholder)')
    return g
ga = build('Dial unit - assembled', (0, 0, 130), {})
place(ga, D('Safe door'), 'Safe door (reference)', T(), 'Safe door (reference)')
ga.set_layer(tags['Assembled view'])
ge = build('Dial unit - exploded', (260, 0, 130),
           {'bearing': 40, 'bearing_step': 12, 'gear': 95, 'spring': 150, 'pinion': 190, 'sled': 235, 'motor': 300, 'deck': 400, 'mega': 440, 'rmag': 30, 'retainer': 20})
ge.set_layer(tags['Exploded view'])

# ======================= PART 3: style, scenes, camera =======================
# Product-studio look (connector's sketchup-styles skill, AO off). Scene tabs
# hide tags; camera eye/target are inches in the SketchUp frame.
DEFAULTS = {
    "rendering_options": {
        "EDGE_DISPLAY_MODE": TypedValue(int_value=1), "EDGE_COLOR_MODE": TypedValue(int_value=0),
        "RENDER_MODE": TypedValue(int_value=2), "MODEL_TRANSPARENCY": TypedValue(bool_value=False),
        "MATERIAL_TRANSPARENCY": TypedValue(bool_value=True), "DRAW_DEPTH_QUE": TypedValue(bool_value=False),
        "DEPTH_QUE_WIDTH": TypedValue(int_value=2), "DRAW_SILHOUETTES": TypedValue(bool_value=True),
        "SILHOUETTE_WIDTH": TypedValue(int_value=2), "DRAW_HORIZON": TypedValue(bool_value=False),
        "DRAW_GROUND": TypedValue(bool_value=False), "DISPLAY_SKETCH_AXES": TypedValue(bool_value=False),
        "HIGHLIGHT_COLOR": TypedValue(color_value=SUColor(0, 1, 255, 255)),
        "LOCKED_COLOR": TypedValue(color_value=SUColor(255, 0, 0, 255)),
    },
    "shadow_info": {},
}
FURNITURE_STUDIO = {
    "rendering_options": {
        "BACKGROUND_COLOR": TypedValue(color_value=SUColor(214, 216, 218, 255)),
        "FACE_FRONT_COLOR": TypedValue(color_value=SUColor(245, 240, 230, 255)),
        "FACE_BACK_COLOR": TypedValue(color_value=SUColor(180, 178, 170, 255)),
        "FOREGROUND_COLOR": TypedValue(color_value=SUColor(50, 48, 45, 255)),
        "DEPTH_QUE_WIDTH": TypedValue(int_value=1),
        "AMBIENT_OCCLUSION": TypedValue(bool_value=False),
    },
    "shadow_info": {
        "DISPLAY_SHADOWS": TypedValue(bool_value=True),
        "LIGHT": TypedValue(int_value=80), "DARK": TypedValue(int_value=60),
    },
}
apply_preset(model, {
    "rendering_options": {**DEFAULTS["rendering_options"], **FURNITURE_STUDIO["rendering_options"]},
    "shadow_info": {**DEFAULTS["shadow_info"], **FURNITURE_STUDIO["shadow_info"]},
})
tags = {l.get_name(): l for l in model.get_layers()}
EXP = 'Exploded view'
scene_defs = [
    ("1 Assembled on the door", [EXP], (-8.4, -13.7, 11.2), (0, -2.2, 5.3), 35.0),
    ("2 Gear train", [EXP, 'Motor sled', 'Motors (dummy)', 'Electronics deck', 'Mega envelope (placeholder)'],
     (4.6, -7.8, 10.4), (0, -0.6, 5.1), 35.0),
    ("3 Exploded", ['Assembled view'], (37.4, -3.5, 20.0), (10.2, -11.3, 5.3), 35.0),
    ("4 Seen from in front of the safe", [EXP], (0, -40.0, 5.12), (0, 0, 5.12), 12.0),
    ("5 Motor sled side", [EXP, 'Electronics deck', 'Mega envelope (placeholder)'], (9.5, -13.0, 9.5), (0, -2.2, 5.1), 35.0),
    # 2026-10-06: the sled's door-side face, to show the countersunk motor-screw holes
    ("6 Sled inner face (countersunk motor screws)",
     [EXP, 'Safe door (reference)', 'Front plate', 'Gear-shafts', '608 bearings', 'Springs (placeholder)', 'Pinions'],
     (3.5, 9.5, 8.0), (0, -1.5, 5.12), 35.0),
    ("7 Door side: rubber magnets", [EXP, 'Safe door (reference)'], (3.0, 13.0, 8.5), (0, 0, 5.12), 35.0),
]
scenes = []
for name, _, _, _, _ in scene_defs:
    sc = Scene(); sc.set_name(name); scenes.append(sc)
model.add_scenes(scenes)                       # must be in the model before configuring
for sc, (name, hide, eye, tgt, fov) in zip(scenes, scene_defs):
    cam = Camera()
    cam.set_orientation(SUPoint3D(*eye), SUPoint3D(*tgt), SUVector3D(0, 0, 1))
    cam.enable_perspective(); cam.set_perspective_frustum_fov(fov)
    sc.set_use_camera(True); sc.set_camera(cam)
    sc.set_use_hidden_layers(True)
    for h in hide: sc.add_layer(tags[h])       # add_layer = HIDE in that scene
model.set_active_scene(scenes[0])
tags[EXP].set_visibility(False)                # opening view matches scene 1
mc = Camera()
mc.set_orientation(SUPoint3D(-8.4, -13.7, 11.2), SUPoint3D(0, -2.2, 5.3), SUVector3D(0, 0, 1))
mc.enable_perspective(); mc.set_perspective_frustum_fov(35.0)
model.set_camera(mc)
# then save_model. (Its thumbnail ignores the camera/scenes; open the file to check.)
