# wp1.1 — Diagnóstico: scatter de u_r vs K correto

Investigação pedida antes de reaproveitar o pipeline de extração de u_r nos
passos 1.4/1.5. **A verificação 1.1 (K_FEA vs analítico) não foi refeita** —
permanece válida (−0,06% humano, −0,10% coelho).

Script: `scripts/diagnose_ur_extraction.py`

---

## Pergunta 1: normais de casca invertidas por elemento?

**Não confirmado. Evidência forte contra.**

| métrica | humano (ne=12) |
|---|---|
| elementos com n·r̂ > 0 (para fora) | **864 / 864** |
| elementos com n·r̂ < 0 | **0** |
| min(n·r̂) | 0,999 |

A malha cubic-sphere aplica `_orient_nodes()` em `gen_sphere_shell_mesh.py`
(inverte conectividade se n·r̂ < 0). Nenhum elemento ficou com normal para
dentro. **Não é bug de *SHELL SECTION* / orientação NORMAL no CalculiX** no
sentido de metade da malha invertida.

---

## Pergunta 2: mapeamento FRD → malha média (nós expandidos S8)?

**Contribui pouco para o scatter.**

CalculiX expande 3458 nós de entrada → 6054 nós no `.frd`. Coordenadas FRD
ficam deslocadas **~t/2** da superfície média (mediana 0,25 mm humano =
t/2).

Porém, nós FRD no **mesmo direction angular** têm u_r quase idênticos:

| métrica | valor |
|---|---|
| desvio-padrão intra-bucket (mesmo ângulo) | **~0,00013 mm** |
| std/mean u_r após deduplicar por ângulo | **~101%** (inalterado) |

Conclusão: duplicação de nós S8 **não explica** std/mean ≈ 100%.

---

## Pergunta 3: o que causa std/mean ≈ 100% então?

Três fatores combinados — **artefato de pós-processamento**, não falha da FEA
para K:

### 3a. u_r nodal ≠ grandeza correta para casca pressurizada

| método | std/mean u | fração u_r < 0 |
|---|---:|---:|
| u·r̂ nodal (mapeado) | ~100% | ~20% |
| u·r̂ direto no FRD | ~101% | ~21% |
| u·n no centróide (normal de malha) | ~102% | ~21% |
| **∫ u·n dA (Gauss, usado em K)** | — | **K erro −0,06%** |

~**20% dos elementos** (179/864) têm u·n local negativo no centróide, mas a
**soma Gauss por face** dá ΔV = 6,141 µL (correto).

O padrão segue as **faces +X, +Y, +Z do cubic-sphere** (60+60+59 elementos
negativos), não bordas aleatórias de malha. Isso reflete **campo de
deslocamento não puramente radial** quando decomposto nó-a-nó, não inversão
de normal.

### 3b. componente tangencial grande

| métrica | humano |
|---|---|
| mediana \|u_t\| / \|u_r\| | **1,72** |
| p95 | **17,5** |

Para membrana esférica ideal, u deveria ser radial. Aqui \|u_t\| > \|u_r\| na
mediana — **u·r̂ subestima/sobreestima localmente** mesmo com normais corretas.

Causas físicas/numéricas plausíveis (não exigem malha invertida):

- condições de contorno mínimas nos polos **+X, +Y, +Z** (`PIN1`–`PIN3`);
- parametrização cubic-sphere (6 patches) com orientação u,v assimétrica entre
  faces + e −;
- casca S8 de 3 DOF/nó: deslocamento reportado é translacional global, mas o
  campo no patch não é uniformemente radial sob CB assimétricas.

### 3c. métrica `radial_stats()` usa u·r̂ nodal

O aviso ⚠ em `RESULTS.md` vem de `std/mean` de u·r̂. Essa métrica **não bate**
com ΔV = 4πR² u_r,med se u_r,med for tirado de nós — mas bate com
**u_r,from_dV = ΔV/(4πR²)** a **<0,6%** (consistente com K).

---

## O que é seguro herdar para 1.4 / 1.5

| herdar | evitar |
|---|---|
| `cavity_dV_mm3()` — ∫ u·n dA com Gauss 2×2 | `radial_stats()` como gate de QA (<5%) |
| K = ΔP / ΔV | u_r,médio nodal para volume |
| malha com `_orient_nodes()` + checagem n·r̂ | assumir u_r uniforme sem integral |
| mapeamento FRD por direção angular se precisar de nós | mapeamento por coordenada cartesiana (offset t/2) |

### Se 1.4/1.5 precisarem de u_r nodal

1. deduplicar nós FRD por direção angular (média de **u**, não de u_r);
2. usar **r̂ da malha média**, não coordenadas FRD;
3. preferir **u·n** com normal do elemento, não u·r̂;
4. ainda assim, validar sempre contra ∫ u·n dA.

### Checagem rápida de orientação (recomendada em malhas novas)

```bash
python3 scripts/diagnose_ur_extraction.py
```

Verificar `mesh_normals.n_inward == 0`. Isso detecta inversão de conectividade;
**não** substitui validação de ΔV.

---

## Veredicto

| hipótese | status |
|---|---|
| Normal de casca invertida por elemento | **refutada** (864/864 para fora) |
| Bug silencioso no K por orientação | **refutada** (erro <0,1%) |
| Bug silencioso se reutilizar u_r nodal | **confirmada** — métrica enganosa |
| Causa raiz do ⚠ u_r | pós-processamento nodal + CB/patch cubic-sphere, **não** orientação *SHELL SECTION* |

**Não refazer 1.1. Corrigir/adaptar pipeline de u_r antes de 1.4/1.5.**
