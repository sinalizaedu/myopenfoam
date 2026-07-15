"""Verifica o balanco de forcas axial no 'cul-de-sac' do SAS.

Conceito anatomico (Berdahl/Killer/Hayreh):
  P_CSF entra em z=0 pela coluna do LCR (cisterna quiasmatica) e e forcada
  a parar contra a tampa peripapilar da esclera em z=30.

Balanco de forcas axial esperado:
  F_in (em z=0, posterior_sas)  =  P_CSF * Area_anel_SAS
  F_out (em z=30, tampa)        =  Integral de sigma_zz * dA  na regiao
                                   anular da sclera_peri+sclera_ring que
                                   esta sob a SAS (r=1.55 a r=2.35).

Em equilibrio estatico: F_in == F_out (a esclera segura a coluna do LCR).

Geometria:
  Area_anel_SAS = pi * (R_sas^2 - R_pia^2)
                = pi * (2.35e-3^2 - 1.55e-3^2)
                = pi * (5.5225 - 2.4025) * 1e-6
                = 9.802e-6 m^2

  F_esperada = 1333 Pa * 9.802e-6 m^2 = 1.3068e-2 N = 13.07 mN
"""

from __future__ import annotations

import math

R_PIA  = 1.55e-3
R_SAS  = 2.35e-3
P_CSF  = 1333.0

A_ring = math.pi * (R_SAS**2 - R_PIA**2)
F_in   = P_CSF * A_ring

print(f"========== Cul-de-sac do SAS - balanco de forcas axial ==========")
print()
print(f"Geometria do anel da SAS (r=1.55 a 2.35 mm):")
print(f"  Area anular = pi*(R_sas^2 - R_pia^2)")
print(f"              = pi*({R_SAS*1e3:.2f}e-3^2 - {R_PIA*1e3:.2f}e-3^2)")
print(f"              = {A_ring:.4e} m^2")
print(f"              = {A_ring*1e6:.3f} mm^2")
print()
print(f"Pressao do LCR aplicada em posterior_sas (z=0): P_CSF = {P_CSF:.0f} Pa")
print(f"  (= 10 mmHg, PIC normal supino)")
print()
print(f"Forca axial entrando na coluna do SAS:")
print(f"  F_in = P_CSF * A_ring")
print(f"       = {P_CSF:.0f} * {A_ring:.4e}")
print(f"       = {F_in*1000:.4f} mN")
print()
print(f"Pelo principio de equilibrio estatico, em z=30 a tampa peripapilar")
print(f"da esclera (anel r=1.55-2.35 mm em sclera_peri+sclera_ring) deve")
print(f"absorver e reverter exatamente F_out = F_in = {F_in*1000:.3f} mN.")
print()
print(f"Stress axial medio esperado na tampa (assumindo distribuicao uniforme):")
print(f"  sigma_zz_medio = F_in / A_ring = P_CSF = {P_CSF:.0f} Pa")
print()
print(f"Pelo efeito de Poisson (SAS soft solid, nu=0.30):")
nu_sas = 0.30
sigma_lat = nu_sas/(1-nu_sas) * P_CSF
print(f"  sigma_radial = nu/(1-nu) * P_CSF")
print(f"              = {nu_sas}/{1-nu_sas:.2f} * {P_CSF:.0f}")
print(f"              = {sigma_lat:.0f} Pa")
print(f"  (push lateral da pia interna + pull da dura externa - subestimado")
print(f"   vs fluido real onde sigma_radial == sigma_axial == P_CSF.)")
print()
print(f"=================================================================")
print(f"Magnitude relativa contact_local vs P_CSF:")
P_contact = 9034.0
print(f"  P_contact = {P_contact:.0f} Pa  (arteria oftalmica)")
print(f"  P_CSF     = {P_CSF:.0f} Pa")
print(f"  P_contact / P_CSF = {P_contact/P_CSF:.2f}x")
print(f"  -> O contato e ~7x maior em pressao, mas atua em area pontual")
print(f"     (~1 mm^2 vs 9.8 mm^2 da tampa).")
A_contact = 1.0e-6
F_contact = P_contact * A_contact
print(f"  F_contact = P_contact * A_contact ~= {P_contact:.0f} * {A_contact*1e6:.1f}e-6")
print(f"           ~= {F_contact*1000:.3f} mN")
print(f"  Razao das forcas: F_contact / F_CSF = {F_contact/F_in:.3f}")
print(f"  -> Forcas comparaveis em magnitude integral. As deformacoes sao")
print(f"     dominadas pela direcao: contact gera bending lateral (cantilever)")
print(f"     enquanto P_CSF gera compressao axial pura.")
