#!/usr/bin/env python3
"""Parte el HTML único que genera make4ht (main.html) en una página por tema.

make4ht puede partir por secciones él solo, pero con hyperref no lo hace en algunas versiones
de TeX Live, así que se parte aquí: una página por \\section y, dentro de "Ejercicios de los
boletines", una por \\subsection (los ejercicios de cada tema). Se reescriben los enlaces
internos para que apunten a la página donde está cada id.

Uso: partir_html.py carpeta   (lee carpeta/main.html y escribe index.html, tema1.html, ...)
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
    trozos = [contenido[posiciones[i]:posiciones[i + 1]] for i in range(len(paginas))]

    # Qué ids hay en cada página, para reescribir los enlaces internos.
    donde = {}
    for (nombre, _), trozo in zip(paginas, trozos):
        for ident in re.findall(r'id=["\']([^"\']+)["\']', trozo):
            donde.setdefault(ident, nombre)

    def reescribir(trozo, nombre):
        def cambio(m):
            ident = m.group(2)
            destino = donde.get(ident)
            if destino is None or destino == nombre:
                return f'href="#{ident}"'
            return f'href="{destino}#{ident}"'
        return re.sub(r'href=["\'](main\.html)?#([^"\']+)["\']', cambio, trozo)

    for i, ((nombre, titulo), trozo) in enumerate(zip(paginas, trozos)):
        nuevo = f"<title>{titulo} · Topología Algebraica</title>" if i else "<title>Apuntes de Topología Algebraica</title>"
        cab = re.sub(r"<title>.*?</title>", lambda _: nuevo, cabecera, count=1, flags=re.S)
        enlaces = []
        if i > 0:
            enlaces.append(f'<a href="{paginas[i - 1][0]}">← {paginas[i - 1][1]}</a>')
        enlaces.append('<a href="index.html">Índice</a>')
        if i + 1 < len(paginas):
            enlaces.append(f'<a href="{paginas[i + 1][0]}">{paginas[i + 1][1]} →</a>')
        navegacion = f'<nav class="paginas">{" ".join(enlaces)}</nav>'
        cuerpo = reescribir(trozo, nombre)
        (carpeta / nombre).write_text(cab + navegacion + cuerpo + navegacion + pie, encoding="utf-8")
    (carpeta / "main.html").unlink()

    # Para el mapa: en qué página está cada id.
    (carpeta / "ids.tsv").write_text("".join(f"{k}\t{v}\n" for k, v in donde.items()), encoding="utf-8")
    print(f"{len(paginas)} páginas:", ", ".join(p for p, _ in paginas))


if __name__ == "__main__":
    main(sys.argv[1])
