# Guía para contribuir (personas y agentes)

Apuntes de Topología Algebraica (curso 2026/27) en LaTeX, con versión web. Idioma: **español**.

## Estructura

| Ruta | Qué va ahí |
|---|---|
| `main.tex` | Documento principal: orden de partes y `\include`s. |
| `preambulo.tex` | Paquetes, cajas (`teorema`, `definicion`, `proposicion`, `observacion`, `nota`, `ejercicio`) y macros. |
| `teoria/` | Contenido: un `.tex` por tema, `ResumenHomotopias.tex`, `intro.tex`, `presentacion.tex`. |
| `ejercicios/` | `temaN.tex` (boletín N), `ejercicios.tex` (reúne los boletines), `examenes.tex`. |
| `papel/` | Fotos de apuntes manuscritos: `aaaa-mm-dd_claseN/`. |
| `practicas/` | Prácticas con Singular: `main.tex` (apuntes), `practN.ipynb`, fotos en `practicas/Apuntes papel/`. Es un documento aparte con su propio `preambulo.tex`. |
| `web/` | Web (HTML + mapa de resultados). No tocar salvo que cambies la web. |
| `scripts/` | `exportar.sh` (PDF por tema en `exportados/`), `installsingular.sh`. |
| `mapa_teoremas/` | Mapa antiguo en TikZ; el vigente es el de `web/mapa/`. |
| `material/` | Local, **ignorado por git** (PDFs del profesor, exámenes, notas de estudio). No subir. |

Los archivos generados (`*.aux`, `*.pdf`, `.web/`, `exportados/`, `.exportar/`) están en `.gitignore`: no se suben.

## Dónde meter cada cosa

- **Apuntes de una clase nueva**: en el `.tex` del tema correspondiente, dentro de `teoria/`. Empieza con un encabezado `dd/mm/aaaa (Clase n)`. Las fotos del manuscrito van en `papel/aaaa-mm-dd_claseN/`.
- **Tema nuevo**: crea `teoria/NombreTema.tex` y añade en `main.tex` un `\inicioparte{tN}{Tema N}{Título}{subsection}` seguido de `\include{teoria/NombreTema}`. Después:
  1. `scripts/exportar.sh`: añade `[tN]`/`[eN]` al array `NOMBRE`.
  2. `web/mapa/generar.py`: añade el archivo (sin ruta ni `.tex`) a `ARCHIVOS` (y colores/nombres si procede).
  3. `ejercicios/ejercicios.tex`: añade su `\inicioparte{eN}...` y `\input{ejercicios/temaN}`; crea `ejercicios/temaN.tex`.
  4. `teoria/presentacion.tex`: lista de archivos del repositorio.
- **Boletín de ejercicios**: `ejercicios/temaN.tex`, con el entorno `ejercicio` (`\begin{ejercicio}{TN.k (título)}`). La solución, por orden de prioridad: `\enapuntes{\cref{...}}`, `\fuenteclase{fecha}`, `\fuenteexamen{...}`, `\fuentepropia`.
- **Examen resuelto**: la tabla de `ejercicios/examenes.tex` (qué cayó y dónde está la solución).
- **Práctica**: cuaderno `practicas/practN.ipynb` y su resumen en `practicas/main.tex`; fotos en `practicas/Apuntes papel/`.
- **Colaboradores**: `teoria/presentacion.tex`, sección «Coautores» (quien abre un issue útil, con su número).

## Convenciones de los apuntes

- Resultados en cajas con etiqueta única, **`\begin{teorema}{Título [C3.9] \marcaT}{etiqueta}`**: la etiqueta lleva prefijo según el tipo (`thm:`, `def:`, `prop:`, `obs:`, `not:`, que pone el entorno) y el título termina con la referencia de clase `[Cn.m]` (clase *n*, resultado *m*).
- Marcas de importancia: `\marcaT` (teorema), `\marcaC` (clave), `\marcaP`, `\marcaL` (más suaves), `\marcaE` (ejercicio propuesto en clase y demostrado en su sitio).
- Referencias con `\cref{tipo:etiqueta}`. La web y el mapa de dependencias se construyen a partir de esas citas: una cita `\cref` en un enunciado o demostración crea una arista.
- Rutas en `\include`/`\input` relativas a la raíz (`teoria/...`, `ejercicios/...`), no al archivo.
- Nombres de archivo en `teoria/`: sin espacios ni tildes.

## Comprobar antes de subir

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -usepretex='\def\versionfinal{}' main.tex   # PDF completo
web/construir.sh        # web en .web/sitio/ (necesita make4ht); debe acabar con "0 sin enlace a los apuntes"
scripts/exportar.sh     # opcional: PDFs por tema (necesita qpdf)
```

Mientras editas un tema, descomenta `\includeonly{teoria/...}` en `main.tex` (vuelve a comentarlo antes de subir). La CI (`.github/workflows/`) compila el PDF y publica un *release* y la web en cada push a `main`.

## Pasar apuntes a LaTeX (flujo automático)

**Disparador**: cuando alguien diga algo como «pasa los apuntes», «pasa la clase N a LaTeX» o «transcribe la clase del dd/mm», hazlo directamente, sin pedir más instrucciones. Si no dice qué clase, usa la carpeta más reciente de `papel/` que aún no esté en `teoria/` (busca su encabezado `dd/mm/aaaa (Clase n)`).

1. **Fuentes**: lee todas las fotos de `papel/aaaa-mm-dd_claseN/` en orden de numeración, `papel/INDICE.md` (qué hay en cada foto; está ignorado por git) y la entrada `(N)` del PDF de contenidos de clase de la raíz (`Clases_*.pdf`; sácalo con `pdftotext`). El PDF manda para la estructura y los nombres de los resultados, y ayuda con la letra dudosa.
2. **Destino**: añade al final del `.tex` del tema en `teoria/`, con el encabezado `dd/mm/aaaa (Clase n)`. Si el tema no existe, sigue «Tema nuevo». Una clase por vez; si una foto pertenece a otra clase según el PDF, avísalo.
3. **Formato**: cajas con `[Cn.m]` y marcas, `\cref` solo donde el resultado se use de verdad, diagramas con `tikz-cd` y no con imágenes (ver «Convenciones»). Ejercicios propuestos: añádelos a `ejercicios/temaN.tex` con `\enapuntes{\cref{...}}`.
4. **Fidelidad**: no inventes pasos ni resultados. Lo ilegible o dudoso va como `% REVISAR: <duda>` y se lista al final; lo que completes para que la demostración sea coherente, indícalo.
5. **Comprobar** (ver «Comprobar antes de subir»): compila con `\includeonly{teoria/...}` y deja `main.tex` como estaba; `web/construir.sh` debe acabar con «0 sin enlace a los apuntes».
6. **Git**: rama nueva, commit `Teoría: clase N (<tema>)`, sin push a `main`. Cuenta al final qué has añadido, las dudas `REVISAR` y cualquier suposición.

Si el usuario manda fotos nuevas, primero colócalas en `papel/aaaa-mm-dd_claseN/` con nombre descriptivo (derechas, 1800×2400 como máximo) y añade su entrada a `papel/INDICE.md`; la fecha y el número de clase salen del PDF de contenidos, no de la foto.

## Git

- Trabaja en una rama y abre una pull request a `main`; no subas archivos generados ni `material/`.
- Mensajes de commit en español, breves y con prefijo del área (`Teoría:`, `Ejercicios:`, `Web:`, `Prácticas:`).

## La web (`web/`)

- `construir.sh` convierte los apuntes a HTML con make4ht y genera el mapa; la salida es una sola página (`index.html`) con anclas por apartado (`#tema3`), y las URLs antiguas (`tema3.html`) quedan como redirecciones (`partir_html.py`).
- `vista_previa.js`: al pasar el ratón por una referencia, el resultado aparece en un panel a la derecha.
- `apuntes.cfg` y `estilo.css`: configuración de make4ht y estilos (modo claro y oscuro).
- `mapa/generar.py` lee las cajas de `teoria/` y escribe `datos.json`: nodos, aristas (dependencias) y color de cada tema/bloque. `mapa/index.html` dibuja el grafo.
- Al añadir un archivo de teoría, regístralo en `ARCHIVOS` de `mapa/generar.py`.
