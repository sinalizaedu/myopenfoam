#!/usr/bin/env python3
"""
analyze_sP_nobuckle.py
======================
Analisa on-caso-2sP (PIC via *DSLOAD na parede) e on-caso-2sP-temp (inchaco
no SAS) para responder:

  (1) Por que NAO flambam?
      - curva F-d (reacao axial no engaste vs Dz do globo): monotonica, sem
        queda de forca (snap) -> nao ha instabilidade de flambagem;
      - decomposicao deslocamento AXIAL vs LATERAL: axial >> lateral -> a
        estrutura so encurta (achata), nao kinka.

  (2) A pressao no SAS esta funcionando?
      - campo de pressao hidrostatica p = -(Sxx+Syy+Szz)/3 nos elementos do
        SAS, perfil ao longo de z e estatistica (mediana ~ PIC ~1333 Pa).

Roda com /tmp/ccx2pv/bin/python3 (vtk+matplotlib+numpy).
"""
from __future__ import annotations
import re
from pathlib import Path
import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent
CASES = [
    ("sP: PIC DSLOAD parede", REPO/"cases/on-caso-2sP/ccx/on-caso-2sP", "#27ae60"),
    ("sP-temp: inchaco SAS",  REPO/"cases/on-caso-2sP-temp/ccx/on-caso-2sP-temp", "#8e44ad"),
]

def parse_dat(dat: Path):
    """F_z total nos POSTERIOR_* e U_z medio em ANTERIOR_GLOBO por tempo."""
    txt = dat.read_text()
    force = re.compile(r"total\s+force.*?for\s+set\s+(\w+)\s+and\s+time\s+([-\d.E+]+)\s+([-\d.E+]+)\s+([-\d.E+]+)\s+([-\d.E+]+)", re.I|re.S)
    F = {}
    for m in force.finditer(txt):
        nm,t,fx,fy,fz = m.groups()
        F.setdefault(nm.upper(),{})[float(t)] = float(fz)
    disp = re.compile(r"displacements.*?for\s+set\s+(\w+)\s+and\s+time\s+([-\d.E+]+)\n([^*]*?)(?=\n\s*\n|\Z)", re.I|re.S)
    Uz = {}
    for m in disp.finditer(txt):
        nm,t,body = m.groups()
        vz=[float(l.split()[3]) for l in body.splitlines() if len(l.split())>=4 and re.match(r"\s*\d",l)]
        if vz: Uz.setdefault(nm.upper(),{})[float(t)] = np.mean(vz)
    return F, Uz

def load_vtu(f):
    r=vtk.vtkXMLUnstructuredGridReader(); r.SetFileName(str(f)); r.Update(); g=r.GetOutput()
    pd=g.GetPointData()
    return (vtk_to_numpy(g.GetPoints().GetData()),
            vtk_to_numpy(pd.GetArray("U")),
            vtk_to_numpy(pd.GetArray("S")) if pd.GetArray("S") else None)

def last_vtu(stem: Path):
    vtus=sorted(stem.parent.glob(stem.name+".*.vtu"), key=lambda p:int(p.stem.split(".")[-1]))
    return vtus[-1]

fig,axes=plt.subplots(1,3,figsize=(16,5))
print(f"{'caso':26s} {'F_eng max(mN)':>13s} {'Dz(mm)':>8s} {'|Uz|max':>9s} {'|Ulat|max':>10s} {'p_SAS med(Pa)':>13s}")
for tag,stem,c in CASES:
    F,Uz = parse_dat(Path(str(stem)+".dat"))
    times=sorted(Uz.get("ANTERIOR_GLOBO",{}).keys())
    Dz=np.array([Uz["ANTERIOR_GLOBO"][t] for t in times])
    Feng=np.array([F.get("POSTERIOR_DURA",{}).get(t,0)+F.get("POSTERIOR_PIA",{}).get(t,0)
                   +F.get("POSTERIOR_ON",{}).get(t,0)+F.get("POSTERIOR_SAS",{}).get(t,0) for t in times])
    # painel A: F-d
    axes[0].plot(Dz*1e3, np.abs(Feng)*1e3,"-o",color=c,lw=2,ms=4,label=tag)
    # campo final
    pts,U,S=load_vtu(last_vtu(Path(stem)))
    x0,y0,z0=pts[:,0],pts[:,1],pts[:,2]; r0=np.hypot(x0,y0)
    uz_max=np.abs(U[:,2]).max()*1e3; ulat_max=np.hypot(U[:,0],U[:,1]).max()*1e3
    sas=(r0>1.55e-3)&(r0<2.35e-3)&(z0<30e-3)
    p=-(S[:,0]+S[:,1]+S[:,2])/3.0
    p_sas=p[sas]; pmed=np.median(p_sas)
    # painel B: perfil p_SAS(z)
    edges=np.linspace(0,30e-3,13); zm=[];pm=[]
    zc=z0[sas]
    for i in range(12):
        m=(zc>=edges[i])&(zc<edges[i+1])
        if m.sum()==0: continue
        zm.append(0.5*(edges[i]+edges[i+1])*1e3); pm.append(np.median(p_sas[m]))
    axes[1].plot(pm,zm,"-o",color=c,lw=2,ms=4,label=tag)
    # painel C: barras axial vs lateral
    print(f"{tag:26s} {abs(Feng).max()*1e3:13.1f} {Dz.min()*1e3:8.3f} {uz_max:9.3f} {ulat_max:10.3f} {pmed:13.0f}")
    axes[2].bar([tag.split(':')[0]+"\naxial",tag.split(':')[0]+"\nlateral"],[uz_max,ulat_max],color=[c,c],alpha=[1.0,0.45] if False else None)

axes[0].set_xlabel(r"$\Delta z$ globo (mm)"); axes[0].set_ylabel("|F_z| engaste (mN)")
axes[0].set_title("Curva F-d (monotonica = SEM flambagem)"); axes[0].grid(alpha=0.3); axes[0].legend(fontsize=8); axes[0].invert_xaxis()
axes[1].axvline(1333,color="k",ls="--",lw=0.8,alpha=0.6); axes[1].text(1333,1,"PIC 1333 Pa",rotation=90,fontsize=7,va="bottom")
axes[1].set_xlabel("pressao hidrostatica no SAS (Pa)"); axes[1].set_ylabel("z (mm)")
axes[1].set_title("Pressao no SAS funcionando?\n(mediana por fatia de z)"); axes[1].grid(alpha=0.3); axes[1].legend(fontsize=8)
axes[2].set_ylabel("deslocamento max (mm)"); axes[2].set_title("Axial >> Lateral = so achata"); axes[2].grid(alpha=0.3,axis="y")
fig.suptitle("on-caso-2sP normal vs temp: por que nao flambam + verificacao da pressao no SAS",fontsize=11)
fig.tight_layout(); fig.savefig(REPO/"brunaStuff/on-caso-2sP_analise_nobuckle.png",dpi=130)
print("\nsalvo brunaStuff/on-caso-2sP_analise_nobuckle.png")
