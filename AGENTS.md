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

## Pasar una práctica (LaTeX + cuaderno)

**Disparador**: «pasa la práctica N», «organiza la práctica N» o «pasa las prácticas». Sin número, usa la carpeta más reciente de `practicas/Apuntes papel/` que aún no tenga sección en `practicas/main.tex`. Una práctica por vez. Las prácticas 1–3 son el modelo de estilo.

1. **Fuentes**: fotos de `practicas/Apuntes papel/aaaa-mm-dd_practicaN/` en orden de numeración, su entrada en `practicas/Apuntes papel/INDICE.md` (ignorado por git) y el cuaderno `practicas/practN.ipynb` (código y resultados reales). Si el cuaderno y las fotos discrepan en un número, manda el cuaderno (salida de Singular) y se avisa. Fotos nuevas: derechas, 1800×2400 como máximo, nombre descriptivo (`00_tema_tema`), entrada en `INDICE.md`; originales en `Apuntes_papel_originales/` (ignorada).
2. **`practicas/main.tex`**: añade al final una `\section{Práctica TOPAL N: Título}` con `\label{sec:pN}` (la 1 se titula «Práctica 1: …»). Dentro:
   - La teoría en `\subsection*{...}` por apartado, con las cajas del preámbulo (`definicion`, `teorema`, `proposicion`, `observacion`, `nota`) y etiqueta única (`\begin{teorema}{Título}{etiqueta}`). Sin marcas `[Cn.m]` ni `\marca*`: eso es solo de `teoria/`. `\cref{tipo:etiqueta}` para citar, también resultados de `teoria/` y de prácticas anteriores si existen en el documento.
   - Ejemplos numéricos como `observacion` (con tablas si hay series de datos); lo que el profesor dice «en clase, sin demostrar» va en `nota` o se deja sin `proof`. Demostración solo si está en las fotos; si la completas, indícalo.
   - Un último `\subsection*{Cálculo con Singular}` con la teoría ya expuesta antes y bloques `\begin{singular}...\end{singular}` agrupados por `\paragraph{Tema.}` con una frase de explicación. Comentarios `//` con el resultado (`// 47`), sin tildes dentro del bloque, exponentes sin `^` (`z2`) salvo en el texto.
   - Cierra con `\subsection*{Resumen de comandos}` (la tabla de la práctica 3): añade solo comandos nuevos y no repitas los ya listados.
3. **Cuaderno `practN.ipynb`** (kernel Singular): primera celda markdown `# Práctica N: título`; después `## k. Apartado` en el mismo orden que los `\subsection*` del LaTeX; entre código, una celda markdown corta que diga qué se calcula y por qué (con $\LaTeX$ inline). Una instrucción o resultado por celda de código; sin celdas vacías ni con errores; salidas guardadas (se ven en GitHub); misma notación que el LaTeX (los mismos `I`, `J`, `f`). No cambies el código ni los resultados al ordenar, solo la estructura y los textos. Si hace falta tocar celdas, valida que el JSON sigue siendo válido.
4. **Fidelidad**: no inventes pasos ni resultados. Lo dudoso va como `% REVISAR: <duda>` y se lista al final; lo completado, indicado.
5. **Comprobar**: `cd practicas && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` (el preámbulo es propio); el PDF no se sube.
6. **Git**: rama nueva, commit `Prácticas: práctica N (<tema>)`, sin push a `main`. Cuenta qué has añadido, las dudas `REVISAR` y las suposiciones.

## Git

- Trabaja en una rama y abre una pull request a `main`; no subas archivos generados ni `material/`.
- Mensajes de commit en español, breves y con prefijo del área (`Teoría:`, `Ejercicios:`, `Web:`, `Prácticas:`).

## La web (`web/`)

- `construir.sh` convierte los apuntes a HTML con make4ht y genera el mapa; la salida es una sola página (`index.html`) con anclas por apartado (`#tema3`), y las URLs antiguas (`tema3.html`) quedan como redirecciones (`partir_html.py`).
- `vista_previa.js`: al pasar el ratón por una referencia, el resultado aparece en un panel a la derecha.
- `apuntes.cfg` y `estilo.css`: configuración de make4ht y estilos (modo claro y oscuro).
- `mapa/generar.py` lee las cajas de `teoria/` y escribe `datos.json`: nodos, aristas (dependencias) y color de cada tema/bloque. `mapa/index.html` dibuja el grafo.
- Al añadir un archivo de teoría, regístralo en `ARCHIVOS` de `mapa/generar.py`.
