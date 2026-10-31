#!/usr/bin/env python3
"""Genera datos.json para el mapa interactivo de resultados a partir de los .tex de los apuntes.

Cada teorema, proposición, definición, observación y nota es un nodo, con su número (del .aux),
enunciado y demostración. Hay una arista A -> B cuando el enunciado o la demostración de B cita
a A, con \\cref o con su referencia de clase ([C6.7]). Cada nodo enlaza a su caja en los apuntes HTML.

Uso: generar.py raiz_del_repo carpeta_con_los_aux carpeta_apuntes_html salida.json
"""
import html
import json
import re
import sys
from pathlib import Path

ARCHIVOS = [
    ("ResultadosPreliminares", 1, "Topología general"),
    ("EquivalenciaHomotopica", 2, "Equivalencia homotópica"),
    ("ElGrupoFundamental", 3, "El grupo fundamental"),
    ("EspaciosSimplementeConexosyGrupoFundamental", 4, "Simplemente conexos y π₁(S¹)"),
    ("AplicacionesTeoriaHomotopia", 5, "Aplicaciones"),
]
# Archivos que no son nodos del mapa pero cuyas cajas se citan desde los apuntes (para resolver \\cref).
ARCHIVOS_SOLO_REFS = [("ResumenHomotopias", 6, "Resumen")]
TIPOS = {  # entorno -> (nombre, prefijo de etiqueta)
    "teorema": ("Teorema", "thm"),
    "proposicion": ("Proposición", "prop"),
    "definicion": ("Definición", "def"),
    "observacion": ("Observación", "obs"),
    "nota": ("Nota", "not"),
}
PREFIJO_A_TIPO = {p: t for t, (_, p) in TIPOS.items()}
MARCAS = {"marcaT": "T", "marcaC": "C", "marcaP": "P", "marcaL": "L", "marcaE": "E"}
# Dependencias que no se citan con \\cref en el texto (vienen del mapa de mapa_teoremas/ y de la
# estructura de los apuntes: cada definición apunta a lo que la usa, cada lema a su teorema).
EXTRA = """
thm:teo_lema_continuidad thm:teo_rel_eq thm:teo_rbe_relativa thm:poincare
thm:teo_cont_conex prop:prop_unicidad_elev prop:lema_dos_elevaciones thm:teo_paridad prop:Theta_invariante
thm:imagen_compacta thm:lema_lebesgue prop:lema_unif_continua
prop:proy_estereografica prop:corolario_sn
thm:teo_rel_eq thm:teo_rbe_relativa thm:teo_contractil prop:prop_pi0_invariante
thm:teo_comp_homo thm:teo_contractil
thm:teo_contractil thm:teo_contractil_arcoconexo prop:cor_s1_no_contractil
thm:teo_estrellado_contractil prop:estrellado prop:corolario_sn thm:teo_convexo_contractil
thm:teo_rbe_relativa thm:poincare
thm:poincare thm:teo_cambio_base thm:funtorialidad_pi1 prop:estrellado def:def_simp_conexo
thm:funtorialidad_pi1 prop:ej_pi1_producto prop:homeomorfismo_pi1 thm:aplicaciones_homotopicas prop:equiv_homotopica thm:teo_no_retracto
thm:teo_cambio_base thm:aplicaciones_homotopicas prop:equiv_homotopica thm:teo_cambio_base_grado prop:cor_arco prop:ej_pw_homotopicos
prop:estrellado thm:aplicaciones_homotopicas thm:teo_no_retracto
thm:aplicaciones_homotopicas prop:equiv_homotopica
prop:equiv_homotopica prop:cor_s1_no_contractil
prop:homeomorfismo_pi1 prop:cor_s2_t2
def:def_simp_conexo thm:cond_simp_conexo
prop:prop_reparametrizacion thm:teo_cambio_base
thm:lema_lebesgue prop:cor_lebesgue_I
prop:cor_lebesgue_I thm:cond_simp_conexo
thm:cond_simp_conexo prop:corolario_sn
prop:corolario_sn prop:cor_s2_t2 prop:cor_no_impar
prop:prop_unicidad_elev thm:teo_existencia_elevaciones thm:teo_pi1_s1 prop:lema_dos_elevaciones
prop:lema_unif_continua thm:teo_existencia_elevaciones
prop:lema_restriccion_p thm:teo_existencia_elevaciones
thm:teo_existencia_elevaciones prop:cor_elev_arcos prop:cor_elev_homotopias
prop:cor_elev_arcos thm:teo_pi1_s1 thm:teo_cambio_base_grado def:def_grado
prop:cor_elev_homotopias thm:teo_pi1_s1
def:def_grado thm:teo_pi1_s1
prop:ej_pi1_producto prop:cor_s2_t2
thm:teo_pi1_s1 prop:cor_s1_no_contractil thm:teo_no_retracto thm:teo_fund_algebra prop:cor_s2_t2
thm:teo_no_retracto thm:teo_brouwer
def:def_retracto thm:teo_no_retracto
prop:lema_cota_raices thm:teo_fund_algebra
prop:lema_dos_elevaciones def:def_grado_x0 thm:teo_cambio_base_grado thm:teo_paridad
def:def_grado_x0 thm:teo_cambio_base_grado
thm:teo_cambio_base_grado obs:obs_grado_clase prop:cor_no_impar
def:def_par_impar thm:teo_paridad
thm:teo_paridad prop:cor_no_impar
prop:cor_no_impar prop:cor_cero_impar thm:teo_borsuk
thm:teo_borsuk prop:cor_no_inyectiva thm:teo_lyusternik
prop:lema_dist_continua thm:teo_lyusternik
def:def_pi0 prop:prop_pi0_invariante
def:def_homotopia thm:teo_rel_eq
def:def_contractil thm:teo_contractil
def:def_eq_homotopica thm:teo_contractil prop:equiv_homotopica
def:def_convexo thm:teo_convexo_contractil
def:def_estrellado thm:teo_estrellado_contractil
def:def_homotopia_relativa thm:teo_rbe_relativa
def:def_grupo_fundamental thm:poincare
def:def_cambio_base thm:teo_cambio_base
def:def_hom_ind thm:teo_hom_ind
thm:teo_hom_ind thm:funtorialidad_pi1
prop:ej_poincare_arcos thm:teo_cambio_base
prop:inverso_homotopico thm:teo_cambio_base
def:concat_conjunta prop:ej_concat_conjunta
def:def_elevacion prop:prop_unicidad_elev
def:def_compacidad thm:imagen_compacta
def:def_desconexion thm:teo_cont_conex
prop:prop_lema_previo thm:teo_lema_continuidad
"""  # cada línea: un resultado y después los que lo usan

INICIO = re.compile(r"\\begin\{(" + "|".join(TIPOS) + r")\}")


# ---------------------------------------------------------------- lectura de LaTeX
def sin_comentarios(s):
    return re.sub(r"(?<!\\)%.*", "", s)


def grupo(s, i):
    """Lee el grupo {…} que empieza en s[i] (saltando espacios). Devuelve (contenido, fin)."""
    while s[i].isspace():
        i += 1
    assert s[i] == "{", s[i:i + 30]
    nivel, j = 0, i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            nivel += 1
        elif c == "}":
            nivel -= 1
            if nivel == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("llave sin cerrar")


def entorno(s, nombre, desde):
    """Posiciones (inicio_cuerpo, fin_cuerpo, fin_total) del entorno `nombre` que empieza en `desde`."""
    abre, cierra = "\\begin{%s}" % nombre, "\\end{%s}" % nombre
    nivel, j = 0, desde
    while True:
        a, c = s.find(abre, j), s.find(cierra, j)
        if a != -1 and a < c:
            nivel, j = nivel + 1, a + len(abre)
        else:
            nivel -= 1
            if nivel == 0:
                return c, c + len(cierra)
            j = c + len(cierra)


def refs_clase(texto):
    """'[C5.14–5.15]' -> ['C5.14', 'C5.15']; '[C2.7, C3.1]' -> ['C2.7', 'C3.1']; '[C11]' -> ['C11']."""
    salida = []
    for bloque in re.findall(r"\[(C[^\]]*)\]", texto):
        for parte in re.split(r",\s*", bloque):
            m = re.match(r"C?(\d+)(?:\.(\d+))?(?:\s*(?:–|--|-)\s*(?:(\d+)\.)?(\d+))?", parte.strip())
            if not m:
                continue
            clase, punto, clase2, punto2 = m.groups()
            if punto is None:
                salida.append(f"C{clase}")
                continue
            salida.append(f"C{clase}.{punto}")
            if punto2:
                fin = int(punto2)
                for k in range(int(punto) + 1, fin + 1):
                    salida.append(f"C{clase2 or clase}.{k}")
    return salida


# ---------------------------------------------------------------- LaTeX -> HTML (para el panel)
MATES = re.compile(r"\$\$.*?\$\$|\$(?:\\.|[^$])+\$|\\\[.*?\\\]|\\\(.*?\\\)"
                   r"|\\begin\{(align\*?|equation\*?|gather\*?|multline\*?)\}.*?\\end\{\1\}", re.S)
SIMPLES = {"textbf": "b", "emph": "i", "textit": "i", "texttt": "code", "underline": "u", "textsc": "span"}


def reemplazar_comando(s, cmd, f, nargs=1):
    patron = re.compile(r"\\" + cmd + r"(?![a-zA-Z])")
    while True:
        m = patron.search(s)
        if not m:
            return s
        j, args = m.end(), []
        try:
            while j < len(s) and s[j] == "[":  # argumento opcional
                j = s.index("]", j) + 1
            for _ in range(nargs):
                a, j = grupo(s, j)
                args.append(a)
        except (AssertionError, ValueError, IndexError):
            s = s[:m.start()] + s[m.end():]
            continue
        s = s[:m.start()] + f(*args) + s[j:]


def a_html(tex, nombre_ref):
    tex = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}",
                 "\n\n[[FIG]]\n\n", tex, flags=re.S)
    tex = re.sub(r"\\begin\{tabular\}.*?\\end\{tabular\}", "\n\n[[TABLA]]\n\n", tex, flags=re.S)
    mates = []

    def guardar(m):
        mates.append(m.group(0))
        return f"\x00{len(mates) - 1}\x00"

    tex = MATES.sub(guardar, tex)
    tex = html.escape(tex, quote=False)
    tex = reemplazar_comando(tex, "captionof", lambda _t, c: f"<i>{c}</i>", 2)
    tex = reemplazar_comando(tex, "texorpdfstring", lambda a, _b: a, 2)
    tex = reemplazar_comando(tex, "href", lambda u, t: f'<a href="{u}">{t}</a>', 2)
    for cmd in ("cref", "Cref"):
        tex = reemplazar_comando(tex, cmd, lambda ls: ", ".join(
            f'<a class="ref" data-id="{l.strip()}">{nombre_ref(l.strip())}</a>' for l in ls.split(",")))
    for cmd, etiqueta in SIMPLES.items():
        tex = reemplazar_comando(tex, cmd, lambda x, e=etiqueta: f"<{e}>{x}</{e}>")
    tex = reemplazar_comando(tex, "textcircled", lambda x: f"({x})")
    tex = reemplazar_comando(tex, "footnote", lambda x: f" ({x})")
    for cmd in ("label", "vspace", "hspace", "captionsetup", "phantom"):
        tex = reemplazar_comando(tex, cmd, lambda *_: "")
    tex = re.sub(r"\\marca[TCPLE]\b|\\marca(?:destacada|suave)\{.\}", "", tex)
    tex = re.sub(r"\\begin\{(itemize|description)\}", "<ul>", tex)
    tex = re.sub(r"\\end\{(itemize|description)\}", "</li></ul>", tex)
    tex = tex.replace("\\begin{enumerate}", "<ol>").replace("\\end{enumerate}", "</li></ol>")
    tex = re.sub(r"\\item\s*\[([^\]]*)\]", r"</li><li class='etq'><b>\1</b> ", tex)
    tex = re.sub(r"\\item\b", "</li><li>", tex)
    tex = re.sub(r"<(ul|ol)>\s*</li>", r"<\1>", tex)
    tex = re.sub(r"\\(begin|end)\{(center|flushleft|flushright|minipage|quote)\}(\{[^}]*\})?", "", tex)
    for a, b in (("\\\\", "<br>"), ("~", "&nbsp;"), ("``", "“"), ("''", "”"), ("---", "—"),
                 ("--", "–"), ("\\ldots", "…"), ("\\dots", "…"), ("\\quad", " "), ("\\qquad", "  "),
                 ("\\textperiodcentered", "·"), ("\\%", "%"), ("\\&amp;", "&amp;"), ("\\,", " ")):
        tex = tex.replace(a, b)
    tex = re.sub(r"\\(noindent|medskip|bigskip|smallskip|hfill|centering|par|newline|clearpage)\b", "", tex)
    tex = re.sub(r"\n\s*\n", "<br class='par'>", tex.strip())
    tex = tex.replace("[[FIG]]", "<span class='fig'>[figura: véase en los apuntes]</span>")
    tex = tex.replace("[[TABLA]]", "<span class='fig'>[tabla: véase en los apuntes]</span>")
    tex = re.sub(r"\x00(\d+)\x00", lambda m: html.escape(mates[int(m.group(1))], quote=False), tex)
    return tex


SIMBOLOS = {
    r"\pi": "π", r"\simeq": "≃", r"\cong": "≅", r"\Theta": "Θ", r"\Rightarrow": "⇒", r"\implies": "⇒",
    r"\to": "→", r"\colon": ":", r"\mathbb{R}": "ℝ", r"\mathbb{Z}": "ℤ", r"\mathbb{C}": "ℂ", r"\times": "×",
    r"\setminus": "∖", r"\circ": "∘", r"\in": "∈", r"\geq": "≥", r"\leq": "≤", r"\neq": "≠", r"\alpha": "α",
    r"\beta": "β", r"\omega": "ω", r"\sigma": "σ", r"\#": "#", r"\{": "{", r"\}": "}", r"\deg": "deg",
    r"\not\cong": "≇", r"\simeq_A": "≃_A", r"\odot": "⊙", r"\mathbb{T}": "T",
}
SUPER = str.maketrans("0123456789n*", "⁰¹²³⁴⁵⁶⁷⁸⁹ⁿ*")
SUB = str.maketrans("0123456789A", "₀₁₂₃₄₅₆₇₈₉A")


def a_texto(tex):
    """Versión en texto plano (para la etiqueta del nodo, que no puede llevar MathJax)."""
    s = re.sub(r"\\marca[TCPLE]\b", "", tex)
    s = re.sub(r"\s*\[C[^\]]*\]", "", s)
    s = s.replace(r"\not\cong", "≇")
    for a, b in sorted(SIMBOLOS.items(), key=lambda x: -len(x[0])):
        s = s.replace(a, b)
    s = re.sub(r"\^\{?([0-9n*])\}?", lambda m: m.group(1).translate(SUPER), s)
    s = re.sub(r"_\{?([0-9A])\}?", lambda m: m.group(1).translate(SUB), s)
    s = re.sub(r"\\[a-zA-Z]+\*?", "", s)
    s = s.replace("$", "").replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip(" .")


# ---------------------------------------------------------------- extracción
def numeros(carpeta_aux):
    """Números de los resultados, leídos de las entradas @cref del .aux (mismo formato en LaTeX y make4ht)."""
    nums = {}
    patron = re.compile(r"\\newlabel\{([^}@]*)@cref\}\{\{\[[^\]]*\]\[[^\]]*\]\[[^\]]*\]([^}]*)\}")
    for aux in Path(carpeta_aux).rglob("*.aux"):
        for clave, num in patron.findall(aux.read_text(errors="ignore")):
            nums[clave] = num
    return nums


def urls(carpeta_html):
    """(entorno, número) -> 'pagina.html#id' buscando las cajas en las páginas HTML."""
    destino = {}
    patron = re.compile(r'<div class=["\']tcolorbox (\w+)["\'] id=["\']([^"\']+)["\']>\s*<div class=["\']tcolorbox-title["\']>'
                        r'\s*(?:<!--[^>]*-->)?\s*<p[^>]*>\s*[^\s<]+\s+([\d.]+):')
    for pagina in sorted(Path(carpeta_html).glob("*.html")):
        for env, ident, num in patron.findall(pagina.read_text(encoding="utf-8")):
            destino.setdefault((env, num), f"{pagina.name}#{ident}")
    return destino


def extraer(raiz, nums, destinos, archivos=ARCHIVOS):
    nodos, por_clase = {}, {}
    for archivo, tema, _ in archivos:
        s = sin_comentarios((Path(raiz) / f"{archivo}.tex").read_text(encoding="utf-8"))
        contador = {}  # cada tipo de caja se numera aparte dentro de su sección (= tema)
        for m in INICIO.finditer(s):
            env = m.group(1)
            contador[env] = contador.get(env, 0) + 1
            titulo, j = grupo(s, m.end())
            etiqueta, j = grupo(s, j)
            clave = f"{TIPOS[env][1]}:{etiqueta.strip()}"
            nums.setdefault(clave, f"{tema}.{contador[env]}")
            if not etiqueta.strip():
                continue
            fin_cuerpo, fin = entorno(s, env, m.start())
            cuerpo = s[j:fin_cuerpo]
            demo = ""
            if "\\begin{proof}" in cuerpo:  # demostración dentro de la caja
                k = cuerpo.index("\\begin{proof}")
                c_fin, c_total = entorno(cuerpo, "proof", k)
                demo, cuerpo = cuerpo[k:c_fin], cuerpo[:k] + cuerpo[c_total:]
            else:  # demostración justo después de la caja
                sig = INICIO.search(s, fin)
                candidatos = [len(s)] + ([sig.start()] if sig else [])
                candidatos += [p for p in (s.find("\\section", fin), s.find("\\subsection", fin)) if p != -1]
                limite = min(candidatos)
                k = s.find("\\begin{proof}", fin, limite)
                if k != -1:
                    p_fin, _ = entorno(s, "proof", k)
                    demo = s[k:p_fin]
            if demo:
                demo = re.sub(r"^\\begin\{proof\}(\[[^\]]*\])?", "", demo)
            marcas = [MARCAS[x] for x in re.findall(r"\\(marca[TCPLE])\b", titulo)]
            clases = refs_clase(titulo)
            nodos[clave] = {
                "id": clave, "tipo": env, "nombreTipo": TIPOS[env][0], "numero": nums.get(clave, "?"),
                "tema": tema, "marcas": marcas, "clase": clases, "tituloTex": titulo,
                "titulo": a_texto(titulo), "cuerpo": cuerpo, "demo": demo,
                "url": destinos.get((env, nums.get(clave, "?")), ""),
            }
            for c in clases:
                por_clase.setdefault(c, []).append(clave)
    return nodos, por_clase


def resolver_referencias(carpeta_html, todos, nums):
    """Cambia las marcas [[REF:a,b]] que deja \\cref en el HTML por enlaces "teorema 3.5 y proposición 4.1"."""
    def enlace(clave, mayuscula):
        n = todos.get(clave)
        tipo = PREFIJO_A_TIPO.get(clave.split(":")[0])
        nombre = TIPOS[tipo][0] if tipo else ""
        nombre = nombre if mayuscula else nombre.lower()
        num = n["numero"] if n else nums.get(clave, "??")
        texto = f"{nombre} {num}".strip()
        return f'<a href="{n["url"]}">{texto}</a>' if n and n["url"] else texto

    def cambio(m):
        claves = [c.strip() for c in m.group(2).split(",")]
        partes = [enlace(c, m.group(1) == "M" and i == 0) for i, c in enumerate(claves)]
        return partes[0] if len(partes) == 1 else ", ".join(partes[:-1]) + " y " + partes[-1]

    for pagina in Path(carpeta_html).glob("*.html"):
        t = pagina.read_text(encoding="utf-8")
        nuevo = re.sub(r"\[\[REF(M?):([^\]]+)\]\]", cambio, t)
        if nuevo != t:
            pagina.write_text(nuevo, encoding="utf-8")


def main(raiz, carpeta_aux, carpeta_html, salida):
    nums = {}  # se rellena al recorrer las cajas; numeros(carpeta_aux) solo completa los que falten
    destinos = urls(carpeta_html)
    nodos, por_clase = extraer(raiz, nums, destinos)
    solo_refs, _ = extraer(raiz, nums, destinos, ARCHIVOS_SOLO_REFS)
    for k, v in numeros(carpeta_aux).items():
        nums.setdefault(k, v)

    def nombre_ref(clave):
        n = nodos.get(clave)
        if n:
            return f"{n['nombreTipo']} {n['numero']}"
        tipo = PREFIJO_A_TIPO.get(clave.split(":")[0])
        return f"{TIPOS[tipo][0] if tipo else ''} {nums.get(clave, '?')}".strip()

    aristas = set()
    for clave, n in nodos.items():
        texto = n["cuerpo"] + "\n" + n["demo"]
        citados = set()
        for grupo_refs in re.findall(r"\\[cC]ref\{([^}]*)\}", texto):
            citados.update(x.strip() for x in grupo_refs.split(","))
        for c in refs_clase(re.sub(r"\\begin\{[a-z]+\}\{[^}]*\[C[^\]]*\][^}]*\}", "", texto)):
            if len(por_clase.get(c, [])) == 1:
                citados.add(por_clase[c][0])
        for otro in citados:
            if otro in nodos and otro != clave:
                aristas.add((otro, clave))  # otro -> clave: "otro se usa en clave"
    for linea in EXTRA.strip().splitlines():
        origen, *usuarios = linea.split()
        for u in usuarios:
            if origen in nodos and u in nodos:
                aristas.add((origen, u))
            else:
                print(f"aviso: arista desconocida {origen} -> {u}")

    datos = {
        "temas": [{"n": t, "nombre": nombre} for _, t, nombre in ARCHIVOS],
        "nodos": [],
        "aristas": [{"de": a, "a": b} for a, b in sorted(aristas)],
    }
    for n in nodos.values():
        datos["nodos"].append({
            "id": n["id"], "tipo": n["tipo"], "nombreTipo": n["nombreTipo"], "numero": n["numero"],
            "tema": n["tema"], "marcas": n["marcas"], "clase": n["clase"], "titulo": n["titulo"],
            "tituloHtml": a_html(re.sub(r"\s*\[C[^\]]*\]", "", n["tituloTex"]), nombre_ref),
            "enunciado": a_html(n["cuerpo"], nombre_ref),
            "demostracion": a_html(n["demo"], nombre_ref) if n["demo"].strip() else "",
            "url": n["url"],
        })
    resolver_referencias(carpeta_html, {**solo_refs, **nodos}, nums)
    Path(salida).write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    sin_url = sum(1 for n in datos["nodos"] if not n["url"])
    print(f"{len(datos['nodos'])} resultados, {len(aristas)} dependencias ({sin_url} sin enlace a los apuntes)")


if __name__ == "__main__":
    main(*sys.argv[1:5])
