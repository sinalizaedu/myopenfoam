#!/bin/bash
# Roda apenas o sólido (iris) standalone, sem preCICE.
# Cargas prescritas: P_top=1300 Pa (PC), P_bottom=1000 Pa (AC), ΔP=300 Pa.
# Deflexão esperada ≈ 0.5 mm em forma de D.
set -e

SOLID=/simulation/eye-fsi-tc0/solid

echo "=== Limpando resultados anteriores do sólido ==="
cd "$SOLID"
rm -rf [1-9]* [1-9][0-9]* processor* log.blockMesh log.solids4Foam solid_prescribed.log blockMesh_prescribed.log precice-run/ 2>/dev/null || true

echo "=== Gerando malha (blockMesh) ==="
blockMesh 2>&1 | tee log.blockMesh
echo "  Malha OK"

echo "=== Rodando solids4Foam standalone ==="
solids4Foam 2>&1 | tee log.solids4Foam
echo "  solids4Foam concluído"

echo ""
echo "=== Resultado: deslocamento máximo da íris ==="
LAST_T=$(ls -d "$SOLID"/[0-9]* 2>/dev/null | grep -v '^.*\/0$' | sort -t/ -k1 -g | tail -1)
if [ -n "$LAST_T" ] && [ -f "$LAST_T/D" ]; then
    echo "t = $(basename $LAST_T)"
    grep -A 3 "internalField" "$LAST_T/D" | head -5
    python3 -c "
import re
with open('$LAST_T/D') as f:
    txt = f.read()
vals = re.findall(r'\(([^)]+)\)', txt[txt.find('nonuniform'):])
ys = [float(v.split()[1]) for v in vals if len(v.split())==3]
if ys:
    print(f'D_y min={min(ys)*1000:.3f} mm  max={max(ys)*1000:.3f} mm')
    print(f'Deflexão máxima: {max(abs(v) for v in ys)*1000:.3f} mm')
else:
    print('Sem dados de deslocamento')
" 2>/dev/null || true
else
    echo "Nenhum diretório de tempo encontrado: $LAST_T"
fi
