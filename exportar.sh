#!/usr/bin/env bash
# Exporta cada tema (teoría y ejercicios) y los exámenes en PDF separados, con portadilla e índice.
# Compila main.tex en modo exportación (\def\exportar{}) en .exportar/ y corta el PDF por las páginas
# que anota \inicioparte en main.partes. La compilación normal de main.tex no cambia.
#   ./exportar.sh      deja los PDF en exportados/
set -euo pipefail
cd "$(dirname "$0")"

BUILD=.exportar
SALIDA=exportados
PREFIJO=TopologiaAlgebraica

declare -A NOMBRE=(
  [t1]=Tema1_Teoria      [e1]=Tema1_Ejercicios
  [t2]=Tema2_Teoria      [e2]=Tema2_Ejercicios
  [t3]=Tema3_Teoria      [e3]=Tema3_Ejercicios
  [t4]=Tema4_Teoria      [e4]=Tema4_Ejercicios
  [t5]=Tema5_Teoria      [e5]=Tema5_Ejercicios
  [ex]=Examenes_2025-26
)

mkdir -p "$BUILD/ejercicios" "$SALIDA"
echo "Compilando en modo exportación (puede tardar unos minutos)..."
if ! latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir="$BUILD" \
    -usepretex='\def\versionfinal{}\def\exportar{}' main.tex > "$BUILD/compilacion.log" 2>&1; then
  tail -20 "$BUILD/compilacion.log"
  echo "Error al compilar; el log completo está en $BUILD/compilacion.log" >&2
  exit 1
fi

PDF="$BUILD/main.pdf"
total=$(qpdf --show-npages "$PDF")
mapfile -t partes < "$BUILD/main.partes"

# Cada parte va desde su página inicial hasta la anterior a la siguiente marca (o hasta el final).
for i in "${!partes[@]}"; do
  read -r id inicio <<< "${partes[$i]}"
  if (( i + 1 < ${#partes[@]} )); then
    read -r _ siguiente <<< "${partes[$((i + 1))]}"
    fin=$((siguiente - 1))
  else
    fin=$total
  fi
  [[ -n "${NOMBRE[$id]:-}" ]] || continue
  destino="$SALIDA/${PREFIJO}_${NOMBRE[$id]}.pdf"
  qpdf --empty --pages "$PDF" "$inicio-$fin" -- "$destino"
  printf '%-45s páginas %3d-%3d\n' "$destino" "$inicio" "$fin"
done
