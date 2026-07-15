# Dossiê on-caso-2F — Achatamento do globo CLINICAMENTE REALISTA

**Data:** 2026-05-29
**Origem:** variante do `on-caso-2` (V14b) criada para responder à crítica do item 3
(magnitude do achatamento) baseada em Reilly et al. (2023).
**Arquivo principal:** `cases/on-caso-2F/ccx/on-caso-2F.inp`
**Status:** Convergiu até λ=1.0 (Δz=-0.6 mm), 22 incrementos, ~2m44s (Riks, sem cutbacks)

---

## 1. Motivação (crítica do item 3)

No `on-caso-2` (V14b) o globo anterior recebe uma rampa de **Δz = −1,5 mm** para
induzir o achatamento e engatilhar a compressão. A literatura sugere que isso é
uma **superestimativa biomecânica**:

- **Reilly et al. (2023):** o inchaço da gordura orbital na SANS prevê mudança de
  comprimento axial (achatamento) da ordem de apenas **−7,29 a −32,12 μm**.
- **Clínica de astronautas:** shift hipermetrópico de **+0,50 a +1,75 dioptrias**.
- ~3 D ≈ 1 mm de encurtamento axial → deformação clínica real **~0,2 a 0,6 mm**.

Logo −1,5 mm representa um **caso extremo** (ou a soma do achatamento com o
retrocesso/translação de todo o globo). O `on-caso-2F` usa o **limite superior
clínico (−0,6 mm)** e pergunta: *o complexo nervo+pia ainda flamba (modo S)
dentro do tubo dural a deslocamentos fisiológicos?*

---

## 2. O que muda em relação ao V14b

| Parâmetro | on-caso-2 (V14b) | **on-caso-2F** |
|---|---|---|
| Δz prescrito no globo | −1,50 mm | **−0,60 mm** |
| ARCMAX (Riks) | 2,5 | **1,0** (não escala além do clínico) |
| dl_init (Riks) | 0,025 | 0,02 |
| Mesh, materiais, SAS, dura ortotrópica, Winkler, perturbação, EOM | — | **idênticos** |

O ARCMAX foi reduzido de 2,5 → 1,0 de propósito: assim o load factor λ do Riks
**não escala o BC além do valor clínico**, e Δz_máx fica travado em −0,6 mm
(senão o solver "voltaria" para −1,5 mm e a comparação perderia o sentido).

A malha (`on-caso-2F_mesh.inp` + `on-caso-2F_winkler.inp`) é **cópia** da do
`on-caso-2` — geometria idêntica, só muda a magnitude da carga.

---

## 3. Resultado: SIM, ainda flamba em modo S

Convergência **limpa** (22 incrementos, 2–4 iterações cada, sem nenhum cutback)
— a estrutura segue o mesmo caminho de equilíbrio do V14b, só que parando antes.

### Kink lateral por camada (último incremento)

| Camada (raio) | **2F (−0,6 mm)** | V14b (−1,5 mm) | 2F / V14b |
|---|---|---|---|
| nervo (r=0,5)  | 0,187 mm | 0,203 mm | 92 % |
| **pia (r=1,55)** | **0,240 mm** | **0,275 mm** | 87 % |
| SAS (r=2,0)    | 0,155 mm | 0,161 mm | 96 % |
| dura (r=2,5)   | 0,100 mm | 0,079 mm | 127 % |
| **razão pia/dura** | **2,40** | **3,48** | — |

- A razão **kink_pia / kink_dura = 2,40 > 1** confirma o **modo S confinado**:
  a pia continua kinkando muito mais que a dura mesmo a −0,6 mm.
- O perfil `Ux(z)` na pia mantém a **inflexão S** (positivo em z≈9 mm,
  negativo em z≈21 mm) — praticamente idêntico ao do V14b.

### Curva F-d

- As curvas F-d do 2F e do V14b **se sobrepõem exatamente** no intervalo
  comum [0, −0,6 mm] (mesmo modelo, só para antes).
- F_eng no engaste posterior: **158 mN @ −0,6 mm** (vs 537 mN @ −1,5 mm no V14b).

---

## 4. Ressalva honesta (importante para o relatório)

O kink lateral é **quase independente de Δz** (0,240 mm a −0,6 mm vs 0,275 mm a
−1,5 mm: cresce só ~15 % enquanto Δz cresce 2,5×). Isso indica que o formato
do modo S é **estabelecido cedo** e é fortemente **semeado pela perturbação
antissimétrica constante (±3 mN, sem amplitude)**, e não por uma bifurcação de
flambagem aguda. A convergência sem nenhum snap-through reforça isso.

Interpretação: a −0,6 mm o mecanismo SANS (nervo+pia macio kinkando dentro do
tubo dural rígido) **continua qualitativamente presente e com a mesma forma**,
mas a "flambagem" aqui é mais uma **flexão confinada conduzida pela perturbação**
do que uma instabilidade de Euler clássica que dispara só acima de um P_cr.
Em outras palavras: o modelo **não precisa** dos −1,5 mm para mostrar o modo S —
o achatamento clínico realista (−0,6 mm) já o produz.

---

## 5. Como reproduzir

```bash
# solver (container):
cd /Users/brunaenne/Documents/repos/myopenfoam
docker compose run --rm fsi bash -lc "cd /simulation/on-caso-2F/ccx && ./Allrun"

# converter .frd -> .vtu (host):
cd cases/on-caso-2F/ccx && /tmp/ccx2pv/bin/ccx2paraview on-caso-2F.frd vtu

# análise + comparação com V14b (host, python com vtk):
/tmp/ccx2pv/bin/python3 brunaStuff/analyze_on-caso-2F.py
```

**Saídas:**
- `brunaStuff/on-caso-2F_comparacao.png` — F-d, kink por camada, perfil S da pia
- `brunaStuff/on-caso-2F_summary.txt` — números brutos

---

## 6. Próximos passos sugeridos

- **Sweep de Δz** (−0,2 / −0,4 / −0,6 mm) para ver se o kink é mesmo flat → se for,
  confirma que a perturbação domina (e aí vale rampar a perturbação junto com λ).
- **Rampar a perturbação** (`*CLOAD, AMPLITUDE=DZRAMP` nos PERT_NODES) e refazer o
  2F: aí o kink deve crescer com Δz e poderemos falar em P_cr de verdade.
- Reportar o 2F como o **caso fisiologicamente defensável** e manter o V14b
  (−1,5 mm) como **caso extremo / limite superior** no relatório.
