#!/usr/bin/env python3
"""Convierte el HTML único de make4ht (main.html) en la web de los apuntes: una sola página continua.

Todo queda en index.html. Donde la versión anterior cortaba en páginas (por sección, y por subsección
dentro de las partes largas) se deja un ancla (#tema3), y cada página antigua (tema3.html) queda como
redirección a ese ancla para no romper enlaces. También escribe ids.tsv (id -> página) para el mapa.

Uso: partir_html.py carpeta   (lee carpeta/main.html y escribe index.html y las redirecciones, tema1.html, ...)
"""
import re
import sys
from pathlib import Path

SECCION = re.compile(r'<h3 class=["\']sectionHead["\'][^>]*>')
SUBSECCION = re.compile(r'<h4 class=["\']subsectionHead["\'][^>]*>')
FECHA = re.compile(r'<p[^>]*>(?:(?!</p>).)*\d\d/\d\d/\d{4}(?:(?!</p>).)*</p>\s*$', re.S)


def texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html)).strip()


def nombre_pagina(titulo, ejercicios):
    t = titulo.lower()
    if ejercicios:
        m = re.search(r"tema (\d)", t)
        return f"ejercicios-tema{m.group(1)}.html" if m else "ejercicios.html"
    if "resumen" in t:
        return "resumen.html"
    if "ejercicios" in t:
        return "ejercicios.html"
    if "exámenes" in t or "examenes" in t:
        return "examenes.html"
    m = re.match(r"(\d+)", t)
    return f"tema{m.group(1)}.html" if m else "otra.html"


def inicio_de_bloque(contenido, pos):
    """Retrocede hasta el principio de la línea y, si justo antes hay un párrafo con la fecha
    de la clase (p. ej. 09/09/2026), lo incluye en la página nueva."""
    pos = contenido.rfind("\n", 0, pos) + 1
    previo = contenido[max(0, pos - 600):pos]
    m = FECHA.search(previo)
    if m:
        pos -= len(previo) - m.start()
    return pos


def main(carpeta):
    carpeta = Path(carpeta)
    html = (carpeta / "main.html").read_text(encoding="utf-8")
    fin_nav = html.index("</nav>") + len("</nav>")
    fin_body = html.rindex("</body>")
    cabecera, contenido, pie = html[:fin_nav], html[fin_nav:fin_body], html[fin_body:]

    # Puntos de corte: cada sección y, dentro de la de ejercicios, cada subsección.
    cortes = []  # (posición, título, es_ejercicio_de_tema)
    secciones = [m.start() for m in SECCION.finditer(contenido)]
    for i, s in enumerate(secciones):
        fin_h = contenido.index("</h3>", s)
        titulo = texto(contenido[s:fin_h])
        cortes.append((s, titulo, False))
        if "ejercicios de los boletines" in titulo.lower():
            limite = secciones[i + 1] if i + 1 < len(secciones) else len(contenido)
            for m in SUBSECCION.finditer(contenido, s, limite):
                fin_h4 = contenido.index("</h4>", m.start())
                cortes.append((m.start(), texto(contenido[m.start():fin_h4]), True))

    posiciones = [0] + [inicio_de_bloque(contenido, c[0]) for c in cortes] + [len(contenido)]
    paginas = [("index.html", "Apuntes de Topología Algebraica")]
    for _, titulo, ej in cortes:
        nombre = nombre_pagina(titulo, ej)  # con el número de sección delante
        titulo = re.sub(r"^[\d.]+\s*", "", titulo)
        titulo = re.sub(r"\\\((.*?)\\\)", lambda m: m.group(1).replace("\\", ""), titulo)  # quita \( \) de MathJax
        titulo = titulo.replace("^n", "ⁿ").replace("^1", "¹")
        paginas.append((nombre, titulo))
    # Una sola página continua: en cada punto donde antes se cortaba se pone un ancla (#tema3) y
    # las páginas antiguas (tema3.html#...) quedan como redirecciones, para no romper enlaces.
    anclas = [nombre[:-len(".html")] for nombre, _ in paginas[1:]]
    trozos = [contenido[posiciones[i]:posiciones[i + 1]] for i in range(len(paginas))]
    cuerpo = trozos[0] + "".join(f'<span class="ancla-apartado" id="{a}"></span>{t}' for a, t in zip(anclas, trozos[1:]))
    cuerpo = re.sub(r'href=(["\'])(?:main\.html)?#', r'href=\1#', cuerpo)
    cab = re.sub(r"<title>.*?</title>", lambda _: f"<title>{paginas[0][1]}</title>", cabecera, count=1, flags=re.S)
    cab = cab.replace("</head>", '<script src="vista_previa.js" defer></script>\n</head>', 1)
    (carpeta / "index.html").write_text(cab + cuerpo + pie, encoding="utf-8")
    (carpeta / "main.html").unlink()
    for a in anclas:
        (carpeta / f"{a}.html").write_text(
            f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><title>{paginas[0][1]}</title>'
            f'<meta http-equiv="refresh" content="0; url=index.html#{a}">'
            f'<script>location.replace("index.html" + (location.hash || "#{a}"))</script></head>'
            f'<body><a href="index.html#{a}">Ir a los apuntes</a></body></html>', encoding="utf-8")

    # Para el mapa: todo está en index.html.
    ids = re.findall(r'id=["\']([^"\']+)["\']', cuerpo)
    (carpeta / "ids.tsv").write_text("".join(f"{k}\tindex.html\n" for k in dict.fromkeys(ids)), encoding="utf-8")
    print("Una página continua con", len(anclas), "apartados:", ", ".join(anclas))


if __name__ == "__main__":
    main(sys.argv[1])
