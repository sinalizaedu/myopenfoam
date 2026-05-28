"""Localiza o pico de epsilon_vM no campo do solido em t=0.16 s.

Le os campos epsilonEq, sigmaEq, Cx/Cy/Cz no diretorio 0.16 (snapshot do
pico de strain detectado no log) e identifica:
  - cell index do max ε_vM
  - coordenada (x, y, z) dessa cell
  - se eh proximo das caps (z=z_min ou z=z_max) ou no interior
  - qual fracao das cells acima de threshold (ex: ε > 10%) esta em z<5% L ou z>95% L
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np

CASE = Path("/tmp/_diag_export/strain_peak")
DIAG_OUT = Path(__file__).parent / "_diag_strain_peak.txt"


def _read_internal_field_scalar(path: Path) -> np.ndarray:
    """Le internalField nonuniform List<scalar> ... ( ... ) de um campo OpenFOAM."""
    text = path.read_text()
    m = re.search(
        r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\(\s*([^)]+)\)",
        text,
    )
    if not m:
        m2 = re.search(r"internalField\s+uniform\s+([\-\d.eE+]+)", text)
        if m2:
            return np.array([float(m2.group(1))])
        raise ValueError(f"Could not parse {path}")
    n = int(m.group(1))
    body = m.group(2).strip()
    vals = np.fromstring(body, sep="\n", dtype=float)
    if vals.size != n:
        vals = np.fromstring(body.replace("\n", " "), sep=" ", dtype=float)
    if vals.size != n:
        raise ValueError(f"Expected {n} scalars in {path}, got {vals.size}")
    return vals


def main() -> None:
    eps = _read_internal_field_scalar(CASE / "epsilonEq")
    sig = _read_internal_field_scalar(CASE / "sigmaEq")
    cx = _read_internal_field_scalar(CASE / "Cx")
    cy = _read_internal_field_scalar(CASE / "Cy")
    cz = _read_internal_field_scalar(CASE / "Cz")

    n = eps.size
    assert sig.size == cx.size == cy.size == cz.size == n, "size mismatch"

    z_min, z_max = cz.min(), cz.max()
    L_z = z_max - z_min
    cap_thr = 0.10  # 10% da extensao axial perto de cada cap

    is_cap_back = cz < z_min + cap_thr * L_z
    is_cap_front = cz > z_max - cap_thr * L_z
    is_interior = (~is_cap_back) & (~is_cap_front)

    idx_peak = int(eps.argmax())
    peak_z = cz[idx_peak]
    peak_x = cx[idx_peak]
    peak_y = cy[idx_peak]
    r_xy = np.sqrt(peak_x**2 + peak_y**2)
    eps_peak = eps[idx_peak]
    sig_peak = sig[idx_peak]

    if is_cap_back[idx_peak]:
        loc_label = f"CAP_BACK (z={peak_z*1e3:.2f} mm <= {(z_min + cap_thr*L_z)*1e3:.2f} mm)"
    elif is_cap_front[idx_peak]:
        loc_label = f"CAP_FRONT (z={peak_z*1e3:.2f} mm >= {(z_max - cap_thr*L_z)*1e3:.2f} mm)"
    else:
        loc_label = f"INTERIOR (z={peak_z*1e3:.2f} mm)"

    eps_thr = 0.10
    high_strain = eps > eps_thr
    n_high = int(high_strain.sum())
    n_high_cap = int((high_strain & (is_cap_back | is_cap_front)).sum())
    n_high_int = int((high_strain & is_interior).sum())

    p95 = float(np.percentile(eps, 95))
    p99 = float(np.percentile(eps, 99))
    p999 = float(np.percentile(eps, 99.9))

    eps_int_p95 = float(np.percentile(eps[is_interior], 95))
    eps_int_p99 = float(np.percentile(eps[is_interior], 99))

    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("DIAGNOSTICO: localizacao do pico de strain (eps_vM) em t=0.16 s")
    lines.append("=" * 70)
    lines.append(f"  Total cells:           {n}")
    lines.append(f"  z range solido:        [{z_min*1e3:.2f}, {z_max*1e3:.2f}] mm  (L={L_z*1e3:.2f} mm)")
    lines.append(f"  Cap threshold:         {cap_thr*100:.0f}% L = {cap_thr*L_z*1e3:.2f} mm de cada extremidade")
    lines.append("")
    lines.append("--- Pico absoluto ---")
    lines.append(f"  cell idx = {idx_peak}")
    lines.append(f"  (x,y,z) = ({peak_x*1e3:.3f}, {peak_y*1e3:.3f}, {peak_z*1e3:.3f}) mm")
    lines.append(f"  r_xy    = {r_xy*1e3:.3f} mm")
    lines.append(f"  eps_vM  = {eps_peak*100:.2f} %")
    lines.append(f"  sig_vM  = {sig_peak/1000:.2f} kPa")
    lines.append(f"  LOCAL:  {loc_label}")
    lines.append("")
    lines.append("--- Distribuicao de strain alta (eps > 10%) ---")
    lines.append(f"  total cells eps>10%:        {n_high} / {n}  ({n_high/n*100:.2f}%)")
    lines.append(f"     ... nas caps:            {n_high_cap}  ({n_high_cap/max(n_high,1)*100:.1f}% das altas)")
    lines.append(f"     ... no interior:         {n_high_int}  ({n_high_int/max(n_high,1)*100:.1f}% das altas)")
    lines.append("")
    lines.append("--- Percentis no campo COMPLETO ---")
    lines.append(f"  p95(eps_vM) = {p95*100:.2f} %")
    lines.append(f"  p99(eps_vM) = {p99*100:.2f} %")
    lines.append(f"  p99.9       = {p999*100:.2f} %")
    lines.append(f"  max         = {eps.max()*100:.2f} %")
    lines.append("")
    lines.append("--- Percentis SO no INTERIOR (excluindo caps) ---")
    lines.append(f"  p95(eps_vM, interior) = {eps_int_p95*100:.2f} %")
    lines.append(f"  p99(eps_vM, interior) = {eps_int_p99*100:.2f} %")
    lines.append(f"  max(eps_vM, interior) = {eps[is_interior].max()*100:.2f} %")
    lines.append("")
    lines.append("--- Veredicto ---")
    if is_cap_back[idx_peak] or is_cap_front[idx_peak]:
        if eps_int_p99 < 0.10:
            lines.append("  >>> PICO NA CAP. Interior fica abaixo de 10% no p99.")
            lines.append("  >>> ARTEFATO de fixedDisplacement(0). Sem locking aparente.")
            lines.append("  >>> Acao: ignorar dados das caps na pos-analise (Saint-Venant).")
        else:
            lines.append("  >>> Pico na cap, MAS interior tambem tem eps>10% no p99.")
            lines.append("  >>> Possivel locking volumetrico co-existindo com artefato de cap.")
    else:
        lines.append("  >>> PICO NO INTERIOR. Suspeita de VOLUMETRIC LOCKING (nu=0.49).")
        lines.append("  >>> Acao: considerar formulacao mista ou reduzir nu para ~0.45.")

    out_text = "\n".join(lines)
    print(out_text)
    DIAG_OUT.write_text(out_text + "\n")


if __name__ == "__main__":
    main()
