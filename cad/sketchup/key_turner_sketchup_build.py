# ============================================================
# SketchUp review model of the key-turner unit (v1) — build script for the
# Trimble SketchUp connector's build_model (no imports; `math` pre-loaded).
# Not the print source: cad/key_turner_housing.scad is. Same numbers; checked
# 2026-10-06: every part closed with outward faces, volumes within 1% of the
# SCAD STLs (cap/base omit the cosmetic chamfer, notch and roof marks).
# Use: paste the whole file into build_model (clean: true), then save_model.
# ============================================================
# Key-turner v1 geometry for SketchUp (pure python + math), mirrors cad/key_turner_housing.scad.
# Frame: x right, y up on the door, z out of the door (z=0 door face), key axis = z.
# Faces are (outer_loop, [inner_loops]) of (x, y, z); normals point out of the material.

# ---- numbers (same as the SCAD) ----
KEY_PROT = 31.89; COLLAR_R = 7.97 / 2; BOW_W = 24.60; BOW_T = 2.90; BOW_FULL_Z = 12.6
SWELL_T = 9.48; SWELL_Z = 8.0; RING_R = 10.75 / 2; RING_Z = KEY_PROT - 6.6 - RING_R
CAP_OD = 36.0; CAP_Z0 = 18.5; SLOT_W = 3.3; SLOT_L = 30.0; SLOT_TOP = KEY_PROT + 0.6
MOUTH_W = 6.0; MOUTH_H = 1.5; CAP_TOP = SLOT_TOP + 2.0
TONGUE_W, TONGUE_H, TONGUE_L = 6.0, 4.0, 28.0
HUB_R = 15.0; HUB_Z0 = CAP_TOP + 0.5; GROOVE_W = 6.5; GROOVE_TOP = CAP_TOP + TONGUE_H + 0.5
SHAFT_TIP = GROOVE_TOP + 1.5; MOTOR_FACE = SHAFT_TIP + 24.0; HUB_Z1 = MOTOR_FACE - 10.5
BASE_T = 6.0; BASE_R = 43.0; BASE_HOLE_R = 14.0
MP_T = 6.0; MP_Z0 = MOTOR_FACE - MP_T
LEG_R = 6.0; LEG_POS = 36.0; LEG_ANG = [180.0, 60.0, -60.0]
PILOT_R = 5.4 / 2; PILOT_D = 16.0
M6_CLR_R = 6.4 / 2; CSK_R = 14.0 / 2; CSK_D = (14.0 - 6.4) / 2
BOLT_SQ = 31.0; BOLT_R = 3.4 / 2; CB_R = 6.3 / 2; CB_D = (6.3 - 3.4) / 2
BOSS_REC_R = 23.0 / 2; BOSS_REC_H = 2.5; SHAFT_HOLE_R = 7.0 / 2
NEMA = 42.3; CAN_CLR = 1.5; SHAFT_LEN = 24.0
LEGS = [[LEG_POS * math.cos(math.radians(a)), LEG_POS * math.sin(math.radians(a))] for a in LEG_ANG]


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


def L3(loop, z): return [(p[0], p[1], z) for p in loop]


def hface(loop2, z, up, holes2=()):
    o = ccw(loop2)
    if not up: o = o[::-1]
    hs = [L3(ccw(h)[::-1] if up else ccw(h), z) for h in holes2]
    return (L3(o, z), hs)


def wall(loop2, z0, z1, outward=True, loop2_top=None):
    a = ccw(loop2); b = ccw(loop2_top) if loop2_top else a
    faces = []; n = len(a)
    for i in range(n):
        j = (i + 1) % n
        q = [(a[i][0], a[i][1], z0), (a[j][0], a[j][1], z0), (b[j][0], b[j][1], z1), (b[i][0], b[i][1], z1)]
        faces.append((q if outward else q[::-1], []))
    return faces


def newell(loop):
    n = [0.0, 0.0, 0.0]
    for i in range(len(loop)):
        p, q = loop[i], loop[(i + 1) % len(loop)]
        n[0] += (p[1] - q[1]) * (p[2] + q[2]); n[1] += (p[2] - q[2]) * (p[0] + q[0]); n[2] += (p[0] - q[0]) * (p[1] + q[1])
    return n


def face3(loop, normal, holes=()):
    """planar face in 3D with the given outward normal; holes wound opposite"""
    nn = newell(loop)
    o = loop if sum(a * b for a, b in zip(nn, normal)) > 0 else loop[::-1]
    hs = []
    for h in holes:
        hn = newell(h)
        hs.append(h[::-1] if sum(a * b for a, b in zip(hn, normal)) > 0 else h)
    return (o, hs)


def blind_hole_from_top(c, r, n, ztop, depth):
    lp = circle(c[0], c[1], r, n)
    return wall(lp, ztop - depth, ztop, outward=False) + [hface(lp, ztop - depth, True)]


def dbore_loop(r=5.0 / 2 + 0.15, flat_y=2.0 + 0.15, n=32):
    a1 = math.asin(flat_y / r); a2 = math.pi - a1
    ang = sorted(set([2 * math.pi * i / n for i in range(n)] + [a1, a2]))
    return [[r * math.cos(a), r * math.sin(a)] for a in ang if not (a1 < a < a2)]


# ---------------- parts ----------------
def kt_base():
    out = circle(0, 0, BASE_R, 96); hole = circle(0, 0, BASE_HOLE_R, 48)
    legs = [circle(p[0], p[1], LEG_R, 24) for p in LEGS]
    F = [hface(out, 0.0, False, [hole]), hface(out, BASE_T, True, [hole] + legs)]
    F += wall(out, 0.0, BASE_T, True) + wall(hole, 0.0, BASE_T, False)
    for i, p in enumerate(LEGS):
        F += wall(legs[i], BASE_T, MP_Z0, True)
        F.append(hface(legs[i], MP_Z0, True, [circle(p[0], p[1], PILOT_R, 16)]))
        F += blind_hole_from_top(p, PILOT_R, 16, MP_Z0, PILOT_D)
    return F


def kt_motor_plate():
    z0, z1 = MP_Z0, MOTOR_FACE
    hs = (NEMA + CAN_CLR + 6) / 2
    pts = [[-hs, -hs], [hs, -hs], [hs, hs], [-hs, hs]]
    for p in LEGS: pts += circle(p[0], p[1], CSK_R + 4, 48)
    out = ccw(hull(pts))
    shaft = circle(0, 0, SHAFT_HOLE_R, 24); rec = circle(0, 0, BOSS_REC_R, 48)
    bolts = [[sx * BOLT_SQ / 2, sy * BOLT_SQ / 2] for sx in (-1, 1) for sy in (-1, 1)]
    cb = [circle(b[0], b[1], CB_R, 16) for b in bolts]; bh = [circle(b[0], b[1], BOLT_R, 16) for b in bolts]
    jc = [circle(p[0], p[1], M6_CLR_R, 24) for p in LEGS]; jk = [circle(p[0], p[1], CSK_R, 24) for p in LEGS]
    F = [hface(out, z0, False, [shaft] + cb + jc), hface(out, z1, True, [rec] + bh + jk)]
    F += wall(out, z0, z1, True)
    zr = z1 - BOSS_REC_H
    F += wall(shaft, z0, zr, False) + [hface(rec, zr, True, [shaft])] + wall(rec, zr, z1, False)
    for k in range(4):
        F += wall(cb[k], z0, z0 + CB_D, False, loop2_top=bh[k]) + wall(bh[k], z0 + CB_D, z1, False)
    zc = z1 - CSK_D
    for i in range(3):
        F += wall(jc[i], z0, zc, False) + wall(jc[i], zc, z1, False, loop2_top=jk[i])
    return F


def rect(xh, yh):
    return [[xh, yh], [-xh, yh], [-xh, -yh], [xh, -yh]]   # ccw


def kt_cap():
    out = circle(0, 0, CAP_OD / 2, 96)
    mouth = rect(MOUTH_W / 2, SLOT_L / 2 + 1); slot = rect(SLOT_W / 2, SLOT_L / 2)
    tg = rect(TONGUE_L / 2, TONGUE_W / 2)
    zs = CAP_Z0 + MOUTH_H
    F = [hface(out, CAP_Z0, False, [mouth])]
    F += wall(out, CAP_Z0, CAP_TOP, True)
    F += wall(mouth, CAP_Z0, zs, False, loop2_top=slot)          # lead-in
    F += wall(slot, zs, SLOT_TOP, False) + [hface(slot, SLOT_TOP, False)]
    F.append(hface(out, CAP_TOP, True, [tg]))
    F += wall(tg, CAP_TOP, CAP_TOP + TONGUE_H, True) + [hface(tg, CAP_TOP + TONGUE_H, True)]
    return F


def kt_hub():
    r = HUB_R; g = GROOVE_W / 2; a1 = math.asin(g / r); n = 64
    ang = sorted(set([2 * math.pi * i / n for i in range(n)] + [a1, math.pi - a1, math.pi + a1, 2 * math.pi - a1]))
    P = [[r * math.cos(a), r * math.sin(a)] for a in ang]
    A = [p for a, p in zip(ang, P) if a1 - 1e-9 <= a <= math.pi - a1 + 1e-9]               # y >= g arc
    B = [p for a, p in zip(ang, P) if math.pi + a1 - 1e-9 <= a <= 2 * math.pi - a1 + 1e-9]  # y <= -g arc
    R = [p for a, p in zip(ang, P) if a <= a1 + 1e-9 or a >= 2 * math.pi - a1 - 1e-9]       # right ends, |y|<=g
    Lf = [p for a, p in zip(ang, P) if math.pi - a1 - 1e-9 <= a <= math.pi + a1 + 1e-9]     # left ends
    z0, zg, z1 = HUB_Z0, GROOVE_TOP, HUB_Z1
    F = [face3(L3(A, z0), (0, 0, -1)), face3(L3(B, z0), (0, 0, -1))]
    for arc in (A, B):
        for i in range(len(arc) - 1):
            p, q = arc[i], arc[i + 1]
            F.append(face3([(p[0], p[1], z0), (q[0], q[1], z0), (q[0], q[1], zg), (p[0], p[1], zg)], (p[0] + q[0], p[1] + q[1], 0)))
    xa = r * math.cos(a1)
    F.append(face3([(xa, g, z0), (-xa, g, z0), (-xa, g, zg), (xa, g, zg)], (0, -1, 0)))
    F.append(face3([(xa, -g, z0), (-xa, -g, z0), (-xa, -g, zg), (xa, -g, zg)], (0, 1, 0)))
    # groove ceiling strip: right arc (from -a1 up to a1) then left arc (pi-a1 .. pi+a1)
    Rs = sorted(R, key=lambda p: p[1]); Ls = sorted(Lf, key=lambda p: -p[1])
    F.append(face3(L3(Rs + Ls, zg), (0, 0, -1)))
    full = ccw(P)
    F += wall(full, zg, z1, True)
    dl = dbore_loop()
    F.append(hface(full, z1, True, [dl]))
    F += wall(dl, SHAFT_TIP, z1, False) + [hface(dl, SHAFT_TIP, True)]
    return F


def kt_key_collar():
    c = circle(0, 0, COLLAR_R, 32)
    return [hface(c, -8.0, False), hface(c, 5.6, True)] + wall(c, -8.0, 5.6, True)


def kt_key_head():
    R0 = rect(COLLAR_R, COLLAR_R); R1 = rect(SWELL_T / 2, 5.0); R2 = rect(BOW_T / 2, BOW_W / 2)
    F = [hface(R0, 5.6, False)] + wall(R0, 5.6, SWELL_Z, True, loop2_top=R1) + wall(R1, SWELL_Z, BOW_FULL_Z, True, loop2_top=R2)
    rb = BOW_W / 2; zc = KEY_PROT - rb; t = BOW_T / 2
    arc = [[rb * math.cos(math.pi * i / 32), zc + rb * math.sin(math.pi * i / 32)] for i in range(33)]
    outline = [[rb, BOW_FULL_Z]] + arc + [[-rb, BOW_FULL_Z]]          # (y, z), bottom edge closes it
    ring = [[RING_R * math.cos(2 * math.pi * i / 24), RING_Z + RING_R * math.sin(2 * math.pi * i / 24)] for i in range(24)]
    for sx in (1, -1):
        F.append(face3([(sx * t, p[0], p[1]) for p in outline], (sx, 0, 0), [[(sx * t, p[0], p[1]) for p in ring]]))
    for i in range(len(outline) - 1):
        p, q = outline[i], outline[i + 1]
        my, mz = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        out_n = (0, my - 0.0, mz - (BOW_FULL_Z + zc) / 2)            # away from the bow's middle
        F.append(face3([(t, p[0], p[1]), (t, q[0], q[1]), (-t, q[0], q[1]), (-t, p[0], p[1])], out_n))
    for i in range(len(ring)):
        p, q = ring[i], ring[(i + 1) % len(ring)]
        mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 - RING_Z)
        F.append(face3([(t, p[0], p[1]), (t, q[0], q[1]), (-t, q[0], q[1]), (-t, p[0], p[1])], (0, -mid[0], -mid[1])))
    return F


def kt_motor():
    h = NEMA / 2; sq = rect(h, h)
    boss = circle(0, 0, 11.0, 48); sh = circle(0, 0, 2.5, 24)
    F = [hface(sq, 0.0, False, [boss]), hface(sq, 48.0, True)] + wall(sq, 0.0, 48.0, True)
    F += wall(boss, -2.0, 0.0, True) + [hface(boss, -2.0, False, [sh])]
    F += wall(sh, -SHAFT_LEN, -2.0, True) + [hface(sh, -SHAFT_LEN, False)]
    return F


def kt_door(size=140.0, thick=6.0):
    s = size / 2; sq = rect(s, s); hl = circle(0, 0, 12.05 / 2, 32)
    return [hface(sq, -thick, False, [hl]), hface(sq, 0.0, True, [hl])] + wall(sq, -thick, 0.0, True) + wall(hl, -thick, 0.0, False)


KT_PARTS = dict(base=kt_base, plate=kt_motor_plate, cap=kt_cap, hub=kt_hub, collar=kt_key_collar,
                head=kt_key_head, motor=kt_motor, door=kt_door)

# ================= SketchUp adapter + placement + scenes =================
up = model.get_options_manager().get_options_provider_by_name("UnitsOptions")
_k = {str(k).split('.')[-1]: k for k in list(up.keys())}
for _n, _v in [("LENGTH_FORMAT", 0), ("LENGTH_UNIT", 2), ("LENGTH_PRECISION", 1), ("AREA_UNIT", 2), ("VOLUME_UNIT", 2)]:
    up[_k[_n]] = TypedValue(int_value=_v)
S = 1.0 / 25.4

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
    c = math.cos(math.radians(max_deg))
    for e in ents.get_edges():
        fs = e.get_faces()
        if len(fs) == 2:
            a, b = fs[0].get_normal(), fs[1].get_normal()
            if a.x * b.x + a.y * b.y + a.z * b.z > c and not (abs(a.z) > 0.999 and abs(b.z) > 0.999):
                e.set_soft(True); e.set_smooth(True)

def make_def(name, F, mat):
    cd = ComponentDefinition(); cd.set_name(name); model.add_component_definitions([cd])
    cd.get_entities().fill(to_gi(F), weld_vertices=True)
    soften(cd.get_entities())
    for f in cd.get_entities().get_faces():
        f.set_front_material(mat); f.set_back_material(mat)
    return cd

spec = [  # key, definition name, material, rgba, tag
    ('base', 'Key turner base + legs', 'Key turner base PETG', (74, 88, 104, 255), 'Base + legs'),
    ('plate', 'Key turner motor plate', 'Key turner motor plate PETG', (120, 136, 152, 255), 'Motor plate'),
    ('cap', 'Key cap (slot + tongue)', 'Key cap PETG-CF', (230, 145, 56, 255), 'Key cap'),
    ('hub', 'Motor hub (groove + D-bore)', 'Motor hub PETG-CF', (106, 168, 79, 255), 'Motor hub'),
    ('motor', 'NEMA17 17HE19-2004S (dummy)', 'NEMA17 dummy', (40, 40, 44, 150), 'Motor (dummy)'),
    ('collar', 'Key collar (from measurements)', 'Key steel', (200, 200, 205, 255), 'Key (from measurements)'),
    ('head', 'Key head (from measurements)', 'Key steel', (200, 200, 205, 255), 'Key (from measurements)'),
    ('door', 'Safe door (reference, lock hole)', 'Safe door reference', (120, 110, 95, 90), 'Safe door (reference)'),
]
defs = {}
for key, dname, mname, rgba, tag in spec:
    defs[key] = make_def(dname, KT_PARTS[key](), get_mat(mname, *rgba))
tag_names = sorted(set(s[4] for s in spec)) + ['Assembled view', 'Exploded view']
new = []
for n in tag_names:
    l = Layer(); l.set_name(n); new.append(l)
model.add_layers(new)
tags = {l.get_name(): l for l in model.get_layers()}
IN = S
def T(t=(0, 0, 0)):
    return SUTransformation([1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, t[0] * IN, t[1] * IN, t[2] * IN, 1])
def build(wname, off_su, explode):
    g = Group(); model.get_entities().add_group(g); g.set_name(wname)
    # our frame (x right, y up the door, z out of the door) -> SketchUp (X, Z up, -Y toward the viewer)
    g.set_transform(SUTransformation([1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, off_su[0] * IN, off_su[1] * IN, off_su[2] * IN, 1]))
    for key, dname, mname, rgba, tag in spec:
        if key == 'door' and explode: continue
        inst = defs[key].create_instance(); inst.set_name(dname)
        inst.set_transform(T((0, 0, explode.get(key, 0.0) if explode else (MOTOR_FACE if key == 'motor' else 0.0))))
        if explode and key == 'motor': inst.set_transform(T((0, 0, MOTOR_FACE + explode['motor'])))
        g.get_entities().add_instance(inst); inst.set_layer(tags[tag])
    return g
ga = build('Key turner - assembled', (0, 0, 130), {})
ga.set_layer(tags['Assembled view'])
ge = build('Key turner - exploded', (200, 0, 130), {'cap': 45, 'hub': 85, 'plate': 125, 'motor': 165})
ge.set_layer(tags['Exploded view'])

DEFAULTS = {"rendering_options": {
    "EDGE_DISPLAY_MODE": TypedValue(int_value=1), "EDGE_COLOR_MODE": TypedValue(int_value=0),
    "RENDER_MODE": TypedValue(int_value=2), "MODEL_TRANSPARENCY": TypedValue(bool_value=False),
    "MATERIAL_TRANSPARENCY": TypedValue(bool_value=True), "DRAW_DEPTH_QUE": TypedValue(bool_value=False),
    "DEPTH_QUE_WIDTH": TypedValue(int_value=1), "DRAW_SILHOUETTES": TypedValue(bool_value=True),
    "SILHOUETTE_WIDTH": TypedValue(int_value=2), "DRAW_HORIZON": TypedValue(bool_value=False),
    "DRAW_GROUND": TypedValue(bool_value=False), "DISPLAY_SKETCH_AXES": TypedValue(bool_value=False),
    "HIGHLIGHT_COLOR": TypedValue(color_value=SUColor(0, 1, 255, 255)),
    "LOCKED_COLOR": TypedValue(color_value=SUColor(255, 0, 0, 255)),
    "BACKGROUND_COLOR": TypedValue(color_value=SUColor(214, 216, 218, 255)),
    "FACE_FRONT_COLOR": TypedValue(color_value=SUColor(245, 240, 230, 255)),
    "FACE_BACK_COLOR": TypedValue(color_value=SUColor(180, 178, 170, 255)),
    "FOREGROUND_COLOR": TypedValue(color_value=SUColor(50, 48, 45, 255)),
    "AMBIENT_OCCLUSION": TypedValue(bool_value=False)},
    "shadow_info": {"DISPLAY_SHADOWS": TypedValue(bool_value=True), "LIGHT": TypedValue(int_value=80), "DARK": TypedValue(int_value=60)}}
apply_preset(model, DEFAULTS)
EXP = 'Exploded view'
scene_defs = [
    ("1 Assembled on the door", [EXP], (-7.0, -11.0, 9.0), (0, -2.0, 5.12), 35.0),
    ("2 Cap on the key (frame and motor hidden)", [EXP, 'Base + legs', 'Motor plate', 'Motor (dummy)'], (-3.6, -4.6, 7.0), (0, -1.0, 5.12), 35.0),
    ("3 Exploded", ['Assembled view'], (21.0, -16.0, 12.0), (7.87, -5.0, 5.12), 35.0),
    ("4 Seen from in front of the safe", [EXP], (0, -30.0, 5.12), (0, 0, 5.12), 15.0),
]
scenes = []
for name, _, _, _, _ in scene_defs:
    sc = Scene(); sc.set_name(name); scenes.append(sc)
model.add_scenes(scenes)
for sc, (name, hide, eye, tgt, fov) in zip(scenes, scene_defs):
    cam = Camera(); cam.set_orientation(SUPoint3D(*eye), SUPoint3D(*tgt), SUVector3D(0, 0, 1))
    cam.enable_perspective(); cam.set_perspective_frustum_fov(fov)
    sc.set_use_camera(True); sc.set_camera(cam); sc.set_use_hidden_layers(True)
    for h in hide: sc.add_layer(tags[h])
model.set_active_scene(scenes[0])
tags[EXP].set_visibility(False)
mc = Camera(); mc.set_orientation(SUPoint3D(-7.0, -11.0, 9.0), SUPoint3D(0, -2.0, 5.12), SUVector3D(0, 0, 1))
mc.enable_perspective(); mc.set_perspective_frustum_fov(35.0); model.set_camera(mc)
result = {k: {'faces': len(d.get_entities().get_faces()), 'manifold': d.is_manifold()} for k, d in defs.items()}
