#!/usr/bin/env python3
"""
analyze_on-caso-2F.py
=====================
Compara o caso 2F (achatamento CLINICAMENTE REALISTA, Dz=-0.6 mm, ARCMAX=1.0)
com o caso 2 / V14b (Dz=-1.5 mm, caso extremo) e responde:

    "O nervo+pia ainda flamba (modo S) dentro do tubo dural a deslocamentos
     fisiologicos (~0.6 mm) tipicos da SANS?"

Le, para cada caso:
  - .dat  -> curva F-d (RF no engaste posterior z=0)
  - ultimo .vtu -> kink lateral max por camada radial (on/pia/sas/dura)

Saidas:
  brunaStuff/on-caso-2F_comparacao.png
  brunaStuff/on-caso-2F_summary.txt

Rodar com o python que tem vtk:
  /tmp/ccx2pv/bin/python3 brunaStuff/analyze_on-caso-2F.py
"""
import re
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "brunaStuff"

# (label, dir, tag/prefixo do .dat/.vtu, Dz prescrito mm, cor)
CASES = [
    ("Caso 2 / V14b (Dz=-1.5 mm, extremo)", REPO / "cases/on-caso-2/ccx",  "on-caso-2",  -1.5, "tab:red"),
    ("Caso 2F (Dz=-0.6 mm, clinico real)",  REPO / "cases/on-caso-2F/ccx", "on-caso-2F", -0.6, "tab:blue"),
]

LAYERS = [
    ("on",  0.5e-3,  0.1e-3,  "nervo (r=0.5)"),
    ("pia", 1.55e-3, 0.06e-3, "pia (r=1.55)"),
    ("sas", 2.0e-3,  0.06e-3, "SAS (r=2.0)"),
    ("dura", 2.5e-3, 0.06e-3, "dura (r=2.5)"),
]


def parse_dat(path: Path):
    """Le os blocos do .dat do CCX:
        ' total force (fx,fy,fz) for set NAME and time T' + linha totais
        ' displacements (vx,vy,vz) for set NAME and time T' + N linhas nodais
    Retorna times, Dz (medio vz do ANTERIOR_GLOBO), e RF_z por camada posterior.
    """
    txt = path.read_text(errors="ignore")
    fnum = r"[-+]?\d+\.\d+E[+\-]\d+"
    rec = {}

    # 1) forcas totais (1 linha de 3 numeros)
    for m in re.finditer(
            r"total\s+force[^\n]*for\s+set\s+(\S+)\s+and\s+time\s+(" + fnum + r")\s*\n+\s*"
            r"(" + fnum + r")\s+(" + fnum + r")\s+(" + fnum + r")",
            txt, re.IGNORECASE):
        nset, t, fx, fy, fz = m.groups()
        rec.setdefault(float(t), {})[f"RF_{nset.upper()}"] = float(fz)

    # 2) deslocamentos nodais -> media de vz por set
    for m in re.finditer(
            r"displacements[^\n]*for\s+set\s+(\S+)\s+and\s+time\s+(" + fnum + r")\s*\n([\s\S]*?)(?=\n\s*\n|\Z)",
            txt, re.IGNORECASE):
        nset, t, body = m.groups()
        vzs = []
        for line in body.splitlines():
            p = line.split()
            if len(p) >= 4:
                try:
                    vzs.append(float(p[3]))
                except ValueError:
                    pass
        if vzs:
            rec.setdefault(float(t), {})[f"U_{nset.upper()}"] = float(np.mean(vzs))

    times = sorted(rec.keys())
    Dz = []; F_dura = []; F_pia = []; F_on = []
    for t in times:
        d = rec[t]
        Dz.append(d.get("U_ANTERIOR_GLOBO", np.nan))
        F_dura.append(d.get("RF_POSTERIOR_DURA", 0.0))
        F_pia.append(d.get("RF_POSTERIOR_PIA",  0.0))
        F_on.append(d.get("RF_POSTERIOR_ON",   0.0))
    return (np.array(times), np.array(Dz), np.array(F_dura),
            np.array(F_pia), np.array(F_on))


def parse_vtu_kink(case_dir: Path, tag: str):
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy
    vtus = sorted(case_dir.glob(f"{tag}.*.vtu"),
                  key=lambda p: int(p.stem.split('.')[-1]))
    if not vtus:
        return None
    rdr = vtk.vtkXMLUnstructuredGridReader()
    rdr.SetFileName(str(vtus[-1]))
    rdr.Update()
    g = rdr.GetOutput()
    P = vtk_to_numpy(g.GetPoints().GetData())
    U = vtk_to_numpy(g.GetPointData().GetArray("U"))
    r = np.sqrt(P[:, 0]**2 + P[:, 1]**2)
    res = {"_vtu": vtus[-1].name, "_z": P[:, 2], "_Ulat_field": np.sqrt(U[:, 0]**2 + U[:, 1]**2)}
    for name, r_t, dr, _ in LAYERS:
        m = np.abs(r - r_t) < dr
        if m.sum() == 0:
            res[name] = (0.0, None)
        else:
            U_lat = np.sqrt(U[m, 0]**2 + U[m, 1]**2)
            j = int(np.argmax(U_lat))
            res[name] = (float(U_lat.max()), float(P[m][j, 2]))
    res["Dz_max"] = float(np.abs(U[:, 2]).max())
    res["U_lat_global"] = float(res["_Ulat_field"].max())
    return res


def main():
    data = []
    for label, cdir, tag, dz_presc, color in CASES:
        dat = cdir / f"{tag}.dat"
        if not dat.exists():
            print(f"[SKIP] {dat} nao existe")
            continue
        t, Dz, Fd, Fp, Fo = parse_dat(dat)
        F_eng = -(Fd + Fp + Fo)
        kink = parse_vtu_kink(cdir, tag)
        data.append(dict(label=label, color=color, dz_presc=dz_presc,
                         t=t, Dz=Dz, Fd=Fd, Fp=Fp, Fo=Fo, F_eng=F_eng,
                         kink=kink))
        print(f"{label}: {len(t)} incs, Dz_final={Dz[-1]*1e3:+.3f} mm, "
              f"F_eng_max={np.nanmax(np.abs(F_eng))*1e3:.1f} mN")

    # ------ summary text + tabela de kink ------
    lines = []
    P = lines.append
    P("=" * 78)
    P("on-caso-2F  vs  on-caso-2 (V14b) - efeito da magnitude do achatamento")
    P("Pergunta: o complexo nervo+pia flamba (modo S) a Dz clinicamente realista?")
    P("=" * 78)
    for d in data:
        k = d["kink"]
        P(f"\n### {d['label']}")
        P(f"  Dz prescrito (BC)     : {d['dz_presc']:+.2f} mm")
        if k:
            P(f"  Dz real atingido      : {-k['Dz_max']*1e3:+.3f} mm  (|U_z| max)")
            P(f"  F_eng max (engaste)   : {np.nanmax(np.abs(d['F_eng']))*1e3:7.1f} mN")
            P(f"  Kink lateral por camada (|U_lat| max, mm) [z do pico]:")
            for nm, _, _, lab in LAYERS:
                val, zpk = k[nm]
                zs = f"@ z={zpk*1e3:5.1f} mm" if zpk is not None else ""
                P(f"     {lab:16s}: {val*1e3:6.3f} mm  {zs}")
            ratio = k["pia"][0] / k["dura"][0] if k["dura"][0] > 0 else float("inf")
            P(f"  Razao kink_pia/kink_dura = {ratio:5.2f}  "
              f"(>1 => pia kinka mais que dura = modo S confinado)")
        else:
            P("  (sem .vtu -- rode ccx2paraview)")

    # comparacao direta
    if len(data) == 2:
        ext, rea = data[0], data[1]
        ke, kr = ext["kink"], rea["kink"]
        if ke and kr:
            P("\n" + "-" * 78)
            P("COMPARACAO DIRETA (realista 2F / extremo V14b):")
            for nm, _, _, lab in LAYERS:
                fe, fr = ke[nm][0], kr[nm][0]
                frac = fr / fe if fe > 0 else float("nan")
                P(f"  {lab:16s}: 2F={fr*1e3:6.3f} mm  vs  V14b={fe*1e3:6.3f} mm  "
                  f"-> {frac*100:5.1f}% do kink extremo")
            P("\nVEREDITO:")
            pia_r = kr["pia"][0]
            ratio_r = kr["pia"][0] / kr["dura"][0] if kr["dura"][0] > 0 else 0
            flamba = (pia_r * 1e3 > 0.05) and (ratio_r > 1.3)
            if flamba:
                P(f"  >>> SIM: a 2F (Dz=-0.6 mm) o nervo+pia AINDA flamba em modo S")
                P(f"      (kink_pia={pia_r*1e3:.3f} mm, razao pia/dura={ratio_r:.2f}>1).")
                P(f"      O mecanismo SANS persiste em deslocamento fisiologico, so")
                P(f"      que com amplitude proporcionalmente menor.")
            else:
                P(f"  >>> NAO claramente: a 2F o kink lateral cai para {pia_r*1e3:.3f} mm")
                P(f"      (razao pia/dura={ratio_r:.2f}). O modo S so e' nitido no caso")
                P(f"      extremo (-1.5 mm); a -0.6 mm a resposta e' quase so compressao.")

    txt = "\n".join(lines) + "\n"
    print(txt)
    (OUT / "on-caso-2F_summary.txt").write_text(txt)

    # ------ plot ------
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

    # A: F-d
    ax = axes[0]
    for d in data:
        ax.plot(np.abs(d["Dz"]) * 1e3, np.abs(d["F_eng"]) * 1e3, "o-",
                color=d["color"], lw=2, ms=4, label=d["label"])
    ax.set_xlabel(r"$|\Delta z|$ globo (mm)")
    ax.set_ylabel(r"$|F_z|$ engaste posterior (mN)")
    ax.set_title("(A) Curva F-d")
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(alpha=0.3)

    # B: kink por camada (barras agrupadas)
    ax = axes[1]
    names = [lab for _, _, _, lab in LAYERS]
    x = np.arange(len(names))
    w = 0.38
    for i, d in enumerate(data):
        if not d["kink"]:
            continue
        ys = [d["kink"][nm][0] * 1e3 for nm, _, _, _ in LAYERS]
        ax.bar(x + (i - 0.5) * w, ys, w, color=d["color"], label=d["label"])
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=15, fontsize=8)
    ax.set_ylabel(r"$|U_{lat}|$ max (mm)")
    ax.set_title("(B) Kink lateral por camada radial")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, axis="y")

    # C: perfil U_lat(z) na pia (modo S = inflexao)
    ax = axes[2]
    for d in data:
        k = d["kink"]
        if not k:
            continue
        # reconstroi U_lat na faixa da pia ao longo de z
        # usa o campo completo filtrado por raio ~1.55mm
        # (recarrega para ter z e Ulat alinhados)
        pass
    # perfil pia: relê vtu por caso
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy
    for label, cdir, tag, dz_presc, color in CASES:
        vtus = sorted(cdir.glob(f"{tag}.*.vtu"),
                      key=lambda p: int(p.stem.split('.')[-1]))
        if not vtus:
            continue
        rdr = vtk.vtkXMLUnstructuredGridReader()
        rdr.SetFileName(str(vtus[-1])); rdr.Update()
        g = rdr.GetOutput()
        Pp = vtk_to_numpy(g.GetPoints().GetData())
        Uu = vtk_to_numpy(g.GetPointData().GetArray("U"))
        r = np.sqrt(Pp[:, 0]**2 + Pp[:, 1]**2)
        m = (np.abs(r - 1.55e-3) < 0.06e-3)
        z = Pp[m, 2] * 1e3
        # Ux assinado (mostra a inflexao do modo S melhor que |U_lat|)
        ux = Uu[m, 0] * 1e3
        order = np.argsort(z)
        # envelope: media de Ux por bin de z
        zb = np.linspace(0, 30, 31)
        idx = np.digitize(z, zb)
        zc, uc = [], []
        for b in range(1, len(zb)):
            sel = idx == b
            if sel.sum():
                zc.append(z[sel].mean()); uc.append(ux[sel].mean())
        ax.plot(uc, zc, "o-", color=color, lw=2, ms=4, label=label)
    ax.axvline(0, color="k", lw=0.6, ls="--")
    ax.set_xlabel(r"$U_x$ medio na pia (mm)")
    ax.set_ylabel("z (mm)")
    ax.set_title("(C) Perfil lateral da pia (inflexao = modo S)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    fig.suptitle("on-caso-2F (Dz=-0.6 mm, clinico) vs Caso 2 V14b (Dz=-1.5 mm, extremo)\n"
                 "Reilly et al. 2023: achatamento real ~0.2-0.6 mm",
                 fontsize=12)
    fig.tight_layout()
    png = OUT / "on-caso-2F_comparacao.png"
    fig.savefig(png, dpi=130)
    print(f"Plot salvo em {png}")
    print(f"Sumario salvo em {OUT / 'on-caso-2F_summary.txt'}")


if __name__ == "__main__":
    main()
