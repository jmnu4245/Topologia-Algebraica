#!/usr/bin/env bash
# Construye la web (apuntes en HTML + mapa interactivo de resultados) en .web/sitio/.
# GitHub Actions la publica en GitHub Pages; en local se puede abrir .web/sitio/index.html.
#   web/construir.sh [carpeta de salida]
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
SALIDA="$(realpath -m "${1:-$RAIZ/.web/sitio}")"
SRC="$RAIZ/.web/src"

# make4ht escribe sus auxiliares junto al .tex, así que se compila sobre una copia de las fuentes.
rm -rf "$SRC" "$SALIDA"
mkdir -p "$SRC/ejercicios" "$SALIDA/apuntes" "$SALIDA/mapa"
cp "$RAIZ"/*.tex "$SRC/"
cp "$RAIZ"/ejercicios/*.tex "$SRC/ejercicios/"
cp "$RAIZ/web/apuntes.cfg" "$RAIZ/web/estilo.css" "$RAIZ/web/main.mk4" "$SRC/"

# Rutas relativas: TeX no admite la ruta absoluta del proyecto (lleva espacio y tilde).
echo "Convirtiendo los apuntes a HTML..."
(cd "$SRC" && make4ht -c apuntes.cfg -d html main.tex > "$RAIZ/.web/make4ht.log" 2>&1) || {
  tail -30 "$RAIZ/.web/make4ht.log"; echo "Error en make4ht; log en .web/make4ht.log" >&2; exit 1; }
cp -r "$SRC/html/." "$SALIDA/apuntes/"
cp "$RAIZ/web/estilo.css" "$SALIDA/apuntes/"
# make4ht fija colores por id para cada caja; se quitan para que mande estilo.css.
sed -i '/^#tcolobox-[0-9]* /d' "$SALIDA/apuntes/main.css"
python3 "$RAIZ/web/partir_html.py" "$SALIDA/apuntes"

echo "Generando el mapa de resultados..."
python3 "$RAIZ/web/mapa/generar.py" "$RAIZ" "$SRC" "$SALIDA/apuntes" "$SALIDA/mapa/datos.json"
cp "$RAIZ/web/mapa/index.html" "$SALIDA/mapa/"
cp "$RAIZ/web/index.html" "$SALIDA/"
touch "$SALIDA/.nojekyll"
echo "Web lista en $SALIDA"
