# claude-wp1.2 — multi-start do ajuste Ogden vs Pallikaris

Caso independente (Sonnet/Claude), em paralelo ao `cases/wp1.2/`. Não edita
nada lá — só importa `write_mesh`, `write_deck`, `extract_pv`, `ccx_utils`,
`fit_hyperelastic` dos scripts já validados.

## Pergunta

Quantos mínimos locais existem no espaço (μ₁, α₁, D₁) para o ajuste
Ogden N=1 contra a curva de Pallikaris, e qual é o global?

### Contexto

**STALE (Sep 2026):** nenhum ajuste Ogden abaixo é resultado fechado — pontos reportados
pelo otimizador falham em reteste isolado. Multi-start continua útil para diagnóstico, mas
números não entram no relatório. Direção atual: E1/E2 → Yeoh (ver `../wp1.2/output_exploration/`).

Histórico (referência apenas): três mínimos locais distintos foram encontrados
(R² 0,93–0,97), nenhum reprodutível de forma robusta entre ambientes.

## Método

Least-squares (mesma implementação da `fit_pallikaris_claude.py`, D₁ livre
em log₁₀, `diff_step=0.005`, `max_nfev=40`), partindo de **6 x₀ deliberados**:

1. `(2,14; 1,77; log₁₀0,238)` — mínimo A conhecido do PDF
2. `(5,44; 0,49; log₁₀2,26e-4)` — mínimo B (Sonnet)
3. `(7,16; 0,50; log₁₀0,0713)` — mínimo B (Cursor)
4. `(1,0; 2,5; -2)` — cobertura: μ₁ baixo, α₁ alto
5. `(4,0; 1,0; -3)` — cobertura: meio-caminho
6. `(9,0; 0,6; -6)` — cobertura: μ₁ alto, quase-incompressível

Bounds unificados: μ₁∈[0,3–12], α₁∈[0,3–3,5], log₁₀D₁∈[-8, 0].

O script agrupa os 6 resultados finais em clusters (tolerância ~0,5 em μ₁,
0,1 em α₁, 1 em log₁₀D₁) e reporta o global.

## Rodar (dentro do container)

```bash
docker compose run --rm fsi bash -lc 'cd /simulation/claude-wp1.2 && python3 scripts/fit_pallikaris_multistart_claude.py'
```

Ou:

```bash
cd cases/claude-wp1.2 && ./Allrun
```

**Custo estimado:** 6 x₀ × ~30 nfev × ~12 s/CCX ≈ **35–45 min**.

## Saída

- `output_multistart/RESULTS.md` — tabela ordenada por custo, lista de
  clusters, global.
- `output_multistart/multistart_results.json` — todos os fits, atribuição
  de cluster, índice do melhor.
- `output_multistart/ccx_runs/` — todos os decks + logs.
