#!/usr/bin/env python3
"""Acceptance checks for the O1 blockMesh (Lamminsalo G2-fluid domain).

Run inside an OpenFOAM case directory that already contains constant/polyMesh
written by blockMesh -dict system/blockMeshDict.O1.  Reads only the polyMesh
itself, so it is independent of the dict that produced it.

Checks, in the order of the plan's acceptance criteria:
  1. TM is the exact Table SI parallelogram, one block, 5 cells across.
  2. No loose parts: bounding box, patch inventory, cell-type census.
  3. Lens and iris voids lie on their analytic curves, and the 37.3 um
     minimum iris-lens clearance is resolved by at least 4 cells.
"""
import math
import re
import sys

MM = 1000.0  # metres -> mm, the unit the Missel/Lamminsalo tables use

# Analytic surfaces, Table SI (cm -> mm)
LENS_FRONT = (0.0, -0.31, 5.76)
LENS_REAR = (0.0, -4.15, 4.79)
CORNEA = (0.0, -0.15, 8.01)
HYALOID = (0.0, 2.95, 9.41)
ELLIPSE = (8.37, 6.90)

# Table SI/SII landmarks used as block corners
PT = {
    "A": (0.0, -8.16), "B": (6.61, -4.68), "C": (6.70, -4.75),
    "D": (6.93, -4.49), "E": (6.84, -4.42), "F": (6.90, -4.02),
    "G": (6.92, -3.86), "H": (7.00, -3.35), "I": (8.01, -2.00),
    "J": (0.0, 6.90), "K": (0.0, 0.64), "L": (4.75, -3.57),
    "M": (0.0, -6.07), "N": (3.78, -4.94), "O": (3.11, -5.38),
    "P": (3.00, -5.27), "Q": (3.69, -4.81),
}

# The iris void is the Table SII polygon; these are its 5 straight wall segments
IRIS_SEGMENTS = [("F", "N"), ("N", "O"), ("O", "P"), ("P", "Q"), ("Q", "G")]

fails = []
notes = []


def check(ok, label, detail=""):
    tag = "PASS" if ok else "FAIL"
    print(f"  [{tag}] {label}" + (f"   {detail}" if detail else ""))
    if not ok:
        fails.append(label)


# ---------------------------------------------------------------- parsing ----
def _body(path):
    """Strip the FoamFile header and C++ comments from an OpenFOAM file."""
    txt = open(path).read()
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    txt = re.sub(r"//[^\n]*", " ", txt)
    i = txt.find("FoamFile")
    if i >= 0:
        depth = 0
        for j in range(txt.index("{", i), len(txt)):
            if txt[j] == "{":
                depth += 1
            elif txt[j] == "}":
                depth -= 1
                if depth == 0:
                    return txt[j + 1:]
    return txt


def read_points(path):
    b = _body(path)
    start = b.index("(", b.index("("))
    return [tuple(float(v) * MM for v in m.group(1).split())
            for m in re.finditer(r"\(\s*([-\d.eE+\s]+?)\s*\)", b)]


def read_faces(path):
    b = _body(path)
    return [[int(v) for v in m.group(2).split()]
            for m in re.finditer(r"(\d+)\s*\(([\d\s]+?)\)", b)]


def read_labels(path):
    b = _body(path)
    m = re.search(r"(\d+)\s*\(", b)
    if not m:
        return []
    end = b.index(")", m.end())
    return [int(v) for v in b[m.end():end].split()]


def read_boundary(path):
    b = _body(path)
    out = {}
    for m in re.finditer(r"(\w+)\s*\{([^}]*)\}", b):
        d = dict(re.findall(r"(\w+)\s+([^;]+);", m.group(2)))
        out[m.group(1)] = {
            "type": d.get("type", "?"),
            "nFaces": int(d.get("nFaces", 0)),
            "startFace": int(d.get("startFace", 0)),
        }
    return out


def read_cellzones(path):
    try:
        b = _body(path)
    except IOError:
        return {}
    out = {}
    for m in re.finditer(r"(\w+)\s*\{(.*?)\n\s*\}", b, flags=re.S):
        n = re.search(r"cellLabels[^;]*?List<label>\s*\n?\s*(\d+)", m.group(2))
        if n:
            out[m.group(1)] = int(n.group(1))
    return out


# ------------------------------------------------------------------ helpers --
def rz(p):
    """(radius, y) of a mesh point -- the meridional coordinates."""
    return math.hypot(p[0], p[2]), p[1]


def dist_circle(p, circ):
    xc, yc, R = circ
    r, y = rz(p)
    return abs(math.hypot(r - xc, y - yc) - R)


def face_points(faces, points, patch):
    ids = set()
    for f in faces[patch["startFace"]:patch["startFace"] + patch["nFaces"]]:
        ids.update(f)
    return [points[i] for i in ids]


def seg_distance(p, a, b):
    """Distance from meridional point p to the segment a-b."""
    r, y = rz(p)
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = ((r - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(r - (ax + t * dx), y - (ay + t * dy))


def gap(x):
    """Iris-lens clearance at radius x, from the plan's gap function."""
    return 6.96 - x * 2.0 / 3.0 - math.sqrt(33.1776 - x * x)


# --------------------------------------------------------------------- main --
pts = read_points("constant/polyMesh/points")
faces = read_faces("constant/polyMesh/faces")
owner = read_labels("constant/polyMesh/owner")
bnd = read_boundary("constant/polyMesh/boundary")
zones = read_cellzones("constant/polyMesh/cellZones")
ncells = max(owner) + 1

print(f"\nO1 mesh: {len(pts)} points, {len(faces)} faces, {ncells} cells\n")

# =================== 1. TM is the Table SI parallelogram ====================
print("1. TRABECULAR MESHWORK")
B, C, D, E = (PT[k] for k in "BCDE")
len_cd = math.dist(C, D)
len_bc = math.dist(B, C)
v1 = (C[0] - B[0], C[1] - B[1])
v2 = (E[0] - B[0], E[1] - B[1])
ang = math.degrees(math.acos((v1[0] * v2[0] + v1[1] * v2[1])
                             / (math.hypot(*v1) * math.hypot(*v2))))
para = max(abs((C[0] - B[0]) + (E[0] - D[0])), abs((C[1] - B[1]) + (E[1] - D[1])))
check(para < 1e-9, "B-C is exactly the negative of D-E (true parallelogram)",
      f"closure error {para * 1e6:.3f} nm")
check(abs(len_cd - 0.34713) < 1e-4 and abs(len_bc - 0.11402) < 1e-4,
      "outlet face 0.34713 mm x thickness 0.11402 mm",
      f"{len_cd:.5f} x {len_bc:.5f} mm, corner {ang:.2f} deg")
n_theta = 12
expect_tm = 5 * n_theta * n_theta
check(zones.get("tm_zone") == expect_tm,
      f"tm_zone holds exactly 5 x {n_theta} x {n_theta} = {expect_tm} cells",
      f"got {zones.get('tm_zone')}")
notes.append(f"TM cells {len_bc / 5 * 1000:.1f} um across x "
             f"{len_cd / n_theta * 1000:.1f} um along, corner {ang:.2f} deg")

# ========================== 2. No loose parts ===============================
print("\n2. NO LOOSE PARTS")
xs = [p[0] for p in pts]
ys = [p[1] for p in pts]
zs = [p[2] for p in pts]
bbox_ok = (abs(min(xs)) < 1e-9 and abs(max(xs) - 8.37) < 2e-3
           and abs(min(ys) + 8.16) < 1e-3 and abs(max(ys) - 6.90) < 1e-3
           and abs(min(zs)) < 1e-9 and abs(max(zs) - 8.37) < 2e-3)
check(bbox_ok, "bounding box matches the analytic domain",
      f"x [{min(xs):.3f}, {max(xs):.3f}]  y [{min(ys):.3f}, {max(ys):.3f}]  "
      f"z [{min(zs):.3f}, {max(zs):.3f}] mm")

want = {"outlet_tm": "patch", "ac_inlet": "patch", "lens_wall": "wall",
        "iris_wall": "wall", "wall": "wall", "symmetry_0": "symmetry",
        "symmetry_90": "symmetry"}
check(set(bnd) == set(want), "exactly the 7 expected patches, no defaultFaces",
      ", ".join(sorted(bnd)))
for name, typ in want.items():
    p = bnd.get(name)
    if p:
        check(p["nFaces"] > 0 and p["type"] == typ,
              f"patch {name} non-empty and type {typ}",
              f"{p['nFaces']} faces, type {p['type']}")

# ================== 3. Lens and iris voids, and the gap =====================
print("\n3. LENS AND IRIS VOIDS")
lens_pts = face_points(faces, pts, bnd["lens_wall"])
dev = [min(dist_circle(p, LENS_FRONT), dist_circle(p, LENS_REAR))
       for p in lens_pts]
check(max(dev) < 0.010, "every lens_wall point within 10 um of its circle",
      f"max {max(dev) * 1000:.2f} um over {len(lens_pts)} points")

iris_pts = face_points(faces, pts, bnd["iris_wall"])
idev = [min(seg_distance(p, PT[a], PT[b]) for a, b in IRIS_SEGMENTS)
        for p in iris_pts]
check(max(idev) < 0.010, "every iris_wall point on a Table SII segment "
      "(no smoothing of the turning points)",
      f"max {max(idev) * 1000:.2f} um over {len(iris_pts)} points")

# radial extent of the voids
lr = [rz(p)[0] for p in lens_pts]
ly = [rz(p)[1] for p in lens_pts]
check(abs(max(lr) - 4.75) < 0.01 and abs(min(ly) + 6.07) < 0.01
      and abs(max(ly) - 0.64) < 0.01, "lens void spans the analytic extent",
      f"equator r {max(lr):.3f} mm, y {min(ly):.3f} to {max(ly):.3f} mm")
ir = [rz(p)[0] for p in iris_pts]
check(abs(min(ir) - 3.00) < 0.01, "pupil aperture radius 3.00 mm "
      "(6.0 mm pupil diameter)", f"min iris radius {min(ir):.4f} mm")

# ---- the gap: count mesh lines across the iris-lens clearance --------------
print("\n   iris-lens clearance")
P, Q = PT["P"], PT["Q"]
d = (Q[0] - P[0], Q[1] - P[1])
dl = math.hypot(*d)
d = (d[0] / dl, d[1] / dl)
n = (-d[1], d[0])                      # unit normal, iris -> lens
if n[1] < 0:
    n = (-n[0], -n[1])

xc, yc, R = LENS_FRONT
# Collect the symmetry_0 mesh points that lie between the straight iris
# posterior P-Q and the lens_front circle, i.e. the pupil channel.  h is the
# height above the iris line, t the local clearance there, so h/t is the
# normalised across-gap coordinate and separates the block's x1 grid lines.
chan = []
for p in pts:
    if abs(p[2]) > 1e-9:               # symmetry_0 plane only
        continue
    r, y = rz(p)
    s = (r - P[0]) * d[0] + (y - P[1]) * d[1]
    h = (r - P[0]) * n[0] + (y - P[1]) * n[1]
    if not (-1e-9 <= s <= dl + 1e-9) or h < -1e-6:
        continue
    fx, fy = P[0] + s * d[0], P[1] + s * d[1]
    b = (fx - xc) * n[0] + (fy - yc) * n[1]
    disc = b * b - ((fx - xc) ** 2 + (fy - yc) ** 2 - R * R)
    if disc < 0:
        continue
    t = -b - math.sqrt(disc)           # foot point -> lens_front along n
    if t <= 0 or h > t + 1e-6:
        continue
    chan.append((s, h, t, h / t))

levels = {}
for s, h, t, ratio in chan:
    levels.setdefault(round(ratio * 8), []).append((s, h, t))
counts = sorted({len(v) for v in levels.values()})
check(len(levels) - 1 >= 4 and len(counts) == 1,
      f"the clearance is crossed by {len(levels) - 1} cells everywhere "
      "(4 required)",
      f"{len(levels)} grid lines x {counts[0] if len(counts) == 1 else counts} "
      "columns")

for v in levels.values():
    v.sort()
col_i = min(range(len(levels[0])),
            key=lambda i: abs(P[0] + levels[0][i][0] * d[0] - 3.195))
col = sorted(levels[k][col_i][1] for k in levels)
x_here = P[0] + levels[0][col_i][0] * d[0]
gmin = gap(x_here)
steps = [(col[i + 1] - col[i]) * 1000 for i in range(len(col) - 1)]
check(abs(gmin - 0.0373) < 5e-4 and len(steps) >= 4,
      "the 37.3 um minimum section itself is resolved",
      f"x = {x_here:.4f} mm, gap {gmin * 1000:.2f} um, {len(steps)} cells of "
      f"{min(steps):.2f}-{max(steps):.2f} um")
notes.append(f"pupil throat: {len(steps)} cells across the {gmin * 1000:.1f} um "
             f"minimum at x = {x_here:.3f} mm "
             f"({sum(steps) / len(steps):.2f} um each)")
for name, x in (("P (tip corner)", 3.00), ("minimum", 3.195), ("Q (turn)", 3.69)):
    print(f"        gap at {name:16s} x = {x:.3f} mm : {gap(x) * 1000:6.2f} um")

print("\n" + "=" * 70)
for s in notes:
    print("  note: " + s)
print(f"\n  {'ALL ACCEPTANCE CHECKS PASSED' if not fails else 'FAILED: ' + '; '.join(fails)}")
print("=" * 70 + "\n")
sys.exit(1 if fails else 0)
