# claude-wp1.1 — varredura de theta_min (borda da calota)

Caso independente (Sonnet/Claude), em paralelo ao `cases/wp1.1/` oficial.
Não edita nada lá — só importa `write_mesh` (`gen_sphere_shell_mesh.py`) e
`extract` (`extract_K.py`) dos scripts já validados.

## Pergunta

Quanto a **borda livre da calota** (nós em θ < θ_min do polo) está
distorcendo K perto do polo? É a *pergunta 1* do
`cases/HANDOFF_WP1_octant_geometry.md`, e ainda não foi respondida
quantitativamente.

## Método

Roda WP1.1 (verificação linear vs fórmula analítica de casca fina) na
malha de octante (θ,φ) já validada, com **ne=6 fixo** (malha de referência)
e **três valores de θ_min: 1,0°, 3,0°, 5,0°**. Para humano e coelho.

Se a variação de K com θ_min for pequena (|ΔK| < 0,1% entre extremos), a
borda livre não é artefato relevante e o default de 3,0° usado no restante
do projeto está seguro. Se for grande, o WP1.5 (modelo anatômico) e o
WP1.4 (varredura) vão herdar esse erro sistemático.

## Rodar (dentro do container)

```bash
docker compose run --rm fsi bash -lc 'cd /simulation/claude-wp1.1 && python3 scripts/verify_theta_min_sweep_claude.py'
```

Ou:

```bash
cd cases/claude-wp1.1 && ./Allrun
```

## Saída

- `output/RESULTS.md` — tabela por espécie: `K_FEA`, erro vs analítico, ΔK relativa a θ_min=3°.
- `output/results.json` — mesmos dados em JSON.
- `output/ccx/` — decks + logs + `.frd` de cada corrida.

Total: 6 corridas (2 espécies × 3 θ_min), ~1 min cada.
