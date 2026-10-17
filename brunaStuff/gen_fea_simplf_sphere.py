#!/usr/bin/env python3
"""90° spherical sclera+cornea shell for fea-simplf.

Radii locked to B2 equatorial inner/outer (metres). 5° polar holes, C3D8I.
Writes fea-simplf_mesh.inp (nodes/elements/nsets/surfaces).

    python3 brunaStuff/gen_fea_simplf_sphere.py --out cases/fea-simplf/ccx/fea-simplf_mesh.inp
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np

# B2 walls (m)
R_SCLERA_IN = 8.67e-3
R_SCLERA_OUT = 9.00e-3
R_CORNEA_IN = 8.16e-3
R_CORNEA_OUT = 8.52e-3
LIMBUS_DEG = 54.7          # from anterior pole
HOLE_DEG = 5.0
N_RAD = 5
N_PHI = 12                 # 90° wedge
N_THETA_SCLERA = 20
N_THETA_CORNEA = 12


def _nset(fh, name, ids, per_line=8):
    ids = sorted(set(int(i) for i in ids))
    fh.write(f"*NSET, NSET={name}\n")
    for i in range(0, len(ids), per_line):
        chunk = ids[i:i + per_line]
        fh.write(", ".join(f"{n:7d}" for n in chunk) + "\n")


def _surf(fh, name, pairs):
    fh.write(f"*SURFACE, NAME={name}, TYPE=ELEMENT\n")
    for eid, loc in pairs:
        fh.write(f"{eid:8d}, S{loc}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    theta_post = math.radians(HOLE_DEG)                 # from +y
    theta_ant = math.radians(180.0 - HOLE_DEG)
    theta_lim = math.radians(180.0 - LIMBUS_DEG)        # 125.3° from +y

    th_s = np.linspace(theta_post, theta_lim, N_THETA_SCLERA + 1)
    th_c = np.linspace(theta_lim, theta_ant, N_THETA_CORNEA + 1)
    # drop duplicated limbus from cornea side for node uniqueness along theta
    theta = np.concatenate([th_s, th_c[1:]])
    n_th = len(theta)  # nodes in theta
    phi = np.linspace(0.0, 0.5 * math.pi, N_PHI + 1)  # 0 = +x (z=0), pi/2 = -z (x=0)
    n_ph = len(phi)
    n_r = N_RAD + 1

    n_th_s_nodes = N_THETA_SCLERA + 1
    limbus_it = N_THETA_SCLERA  # index of limbus in concatenated theta

    def radius(it: int, ir: int) -> float:
        xi = ir / N_RAD
        if it < limbus_it:
            return (1.0 - xi) * R_SCLERA_IN + xi * R_SCLERA_OUT
        if it > limbus_it:
            return (1.0 - xi) * R_CORNEA_IN + xi * R_CORNEA_OUT
        # limbus shared nodes: average so hexes on both sides stay conformal
        rin = 0.5 * (R_SCLERA_IN + R_CORNEA_IN)
        rout = 0.5 * (R_SCLERA_OUT + R_CORNEA_OUT)
        return (1.0 - xi) * rin + xi * rout

    def nid(ir, it, ip) -> int:
        return 1 + ir + n_r * (it + n_th * ip)

    # y = +R cos(theta)  (theta=0 posterior +y)
    # x =  R sin(theta) cos(phi)
    # z = -R sin(theta) sin(phi)   so phi=0 → z=0, phi=90° → x=0, z<0
    coords = {}
    for ip in range(n_ph):
        for it in range(n_th):
            for ir in range(n_r):
                r = radius(it, ir)
                th = theta[it]
                ph = phi[ip]
                x = r * math.sin(th) * math.cos(ph)
                y = r * math.cos(th)
                z = -r * math.sin(th) * math.sin(ph)
                coords[nid(ir, it, ip)] = (x, y, z)

    # elements: ir, it, ip cell indices
    # C3D8: bottom (ir) then top (ir+1); CCW in (it, ip)
    # Face mapping CCX: S1 bottom ir, S2 top ir+1
    elems = []  # (eid, elset, nodes[8])
    eid = 0
    for ip in range(N_PHI):
        for it in range(n_th - 1):
            zone = "SCLERA" if it < limbus_it else "CORNEA"
            for ir in range(N_RAD):
                n000 = nid(ir, it, ip)
                n100 = nid(ir + 1, it, ip)
                n010 = nid(ir, it + 1, ip)
                n110 = nid(ir + 1, it + 1, ip)
                n001 = nid(ir, it, ip + 1)
                n101 = nid(ir + 1, it, ip + 1)
                n011 = nid(ir, it + 1, ip + 1)
                n111 = nid(ir + 1, it + 1, ip + 1)
                # C3D8: 1-4 = low-r face CCW viewed from high-r
                # (it,ip) -> (it+1,ip) -> (it+1,ip+1) -> (it,ip+1)
                nodes8 = (n000, n010, n011, n001, n100, n110, n111, n101)
                eid += 1
                elems.append((eid, zone, nodes8, ir, it, ip))

    # surfaces: inner ir=0 is S1 of the inner-layer elements
    inner_pairs = []
    outer_pairs = []
    polar_post = []
    polar_ant = []
    for eid, zone, nodes8, ir, it, ip in elems:
        if ir == 0:
            inner_pairs.append((eid, 1))  # S1 bottom = inner
        if ir == N_RAD - 1:
            inner_r = False
            outer_pairs.append((eid, 2))  # S2 top = outer
        if it == 0:
            polar_post.append((eid, 3))  # S3 = it face (nodes 1-2-6-5 = n000,n010,... wait)
            # S3 is 1-2-6-5 = n000, n010, n110, n100  that's the it=constant+1? 
            # Our 1=n000 (it,ip), 2=n010 (it+1,ip) — S3 is the (ip) side?
            # We need the it=0 face: nodes with it (not it+1): n000, n001, n101, n100
            # That's S6: 4-1-5-8 = n001, n000, n100, n101. Yes S6.
        if it == n_th - 2:
            # anterior hole: it+1 = last theta. Face with it+1: n010, n011, n111, n110
            # S4: 2-3-7-6 = n010, n011, n111, n110. Yes S4.
            pass

    # Recompute polar faces with the correct local side
    polar_post = []
    polar_ant = []
    for eid, zone, nodes8, ir, it, ip in elems:
        if it == 0:
            polar_post.append((eid, 6))  # S6: it = first
        if it == n_th - 2:
            polar_ant.append((eid, 4))   # S4: it+1 = last

    n_inner = [nid(0, it, ip) for it in range(n_th) for ip in range(n_ph)]
    n_outer = [nid(N_RAD, it, ip) for it in range(n_th) for ip in range(n_ph)]
    n_sym0 = [nid(ir, it, 0) for ir in range(n_r) for it in range(n_th)]       # phi=0, z=0
    n_sym90 = [nid(ir, it, n_ph - 1) for ir in range(n_r) for it in range(n_th)]  # phi=90, x=0
    n_post_ring = [nid(ir, 0, ip) for ir in range(n_r) for ip in range(n_ph)]
    n_ant_ring = [nid(ir, n_th - 1, ip) for ir in range(n_r) for ip in range(n_ph)]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as fh:
        fh.write("** fea-simplf spherical shell (B2 inner/outer, 90 deg wedge)\n")
        fh.write(f"** R_sclera={R_SCLERA_IN}/{R_SCLERA_OUT}  R_cornea={R_CORNEA_IN}/{R_CORNEA_OUT}\n")
        fh.write("*NODE, NSET=NALL\n")
        for i in sorted(coords):
            x, y, z = coords[i]
            fh.write(f"{i:8d}, {x: .8e}, {y: .8e}, {z: .8e}\n")

        by_zone = {"SCLERA": [], "CORNEA": []}
        for eid, zone, nodes8, ir, it, ip in elems:
            by_zone[zone].append((eid, nodes8))
        for zone, elist in by_zone.items():
            fh.write(f"*ELEMENT, TYPE=C3D8I, ELSET={zone}\n")
            for eid, n8 in elist:
                fh.write(
                    f"{eid:8d}, {n8[0]:8d}, {n8[1]:8d}, {n8[2]:8d}, {n8[3]:8d}, "
                    f"{n8[4]:8d}, {n8[5]:8d}, {n8[6]:8d}, {n8[7]:8d}\n"
                )

        _nset(fh, "FSI_ACTIVE", n_inner)
        _nset(fh, "OUTER", n_outer)
        _nset(fh, "SYMMETRY_0", n_sym0)
        _nset(fh, "SYMMETRY_90", n_sym90)
        _nset(fh, "POSTERIOR_RING", n_post_ring)
        _nset(fh, "ANTERIOR_RING", n_ant_ring)
        _nset(fh, "POSTERIOR_POLE", [nid(0, 0, 0)])  # unused for Uy; ring is the pin

        _surf(fh, "FSI_ACTIVE_SURF", inner_pairs)
        _surf(fh, "OUTER_SURF", outer_pairs)
        _surf(fh, "POLAR_POST_SURF", polar_post)
        _surf(fh, "POLAR_ANT_SURF", polar_ant)

        # symmetry plane faces for completeness (volume integral r·n = 0)
        sym0_pairs = []
        sym90_pairs = []
        for eid, zone, nodes8, ir, it, ip in elems:
            if ip == 0:
                sym0_pairs.append((eid, 3))   # S3: ip face (1-2-6-5 = n000,n010,n110,n100) that's it direction
                # phi=0 face: nodes with ip: n000, n010, n110, n100 = S3 yes
            if ip == N_PHI - 1:
                # phi=last face: n001, n011, n111, n101 = S5: 3-4-8-7 = n011, n001, n101, n111
                sym90_pairs.append((eid, 5))
        _surf(fh, "SYMMETRY_0_SURF", sym0_pairs)
        _surf(fh, "SYMMETRY_90_SURF", sym90_pairs)

    n_hex = len(elems)
    v_in = 0.25 * (4.0 / 3.0) * math.pi * R_SCLERA_IN ** 3
    print(f"wrote {args.out}")
    print(f"  nodes={len(coords)}  hex={n_hex}  "
          f"sclera={len(by_zone['SCLERA'])} cornea={len(by_zone['CORNEA'])}")
    print(f"  analytic quarter inner-sphere (R=R_SCLERA_IN) V={v_in:.6e} m3")


if __name__ == "__main__":
    main()
