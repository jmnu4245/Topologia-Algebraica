#!/usr/bin/env python3
"""Genera mapa.tex (grafo de dependencias entre teoremas) a partir de las listas
NODOS y ARISTAS de este fichero.

Distribución en "carriles": una columna por tema (de izquierda a derecha) y
las filas siguen el orden de dependencia (de arriba abajo, una flecha siempre
baja). Las flechas son ortogonales y viajan por los pasillos entre columnas y
entre filas, de modo que nunca atraviesan una caja.
Uso:  python3 generar.py && pdflatex mapa.tex
"""
import json, math, re, subprocess, sys
from pathlib import Path

# --- colores por tema (nombre TikZ, descripción) ---------------------------
TEMAS = {
    1: ("tUno",    "Tema 1: topología general"),
    2: ("tDos",    "Tema 2: equivalencia homotópica"),
    3: ("tTres",   "Tema 3: el grupo fundamental"),
    4: ("tCuatro", "Tema 4: simplemente conexos y $\\pi_1(S^1)$"),
    5: ("tCinco",  "Tema 5: aplicaciones"),
}

# --- nodos: id -> (tema, título, enunciado) --------------------------------
NODOS = {
 # Tema 1
 "peg":   (1, "Lema de pegamiento",
           r"$X=B_1\cup B_2$ con $B_i$ cerrados y $f|_{B_i}$ continuas $\Rightarrow f$ continua."),
 "conexo":(1, "Conexión",
           r"$f$ continua y $X$ conexo $\Rightarrow f(X)$ conexo. Si $f\colon X\to\mathbb Z$ es continua y $X$ conexo, $f$ es constante."),
 "compacto":(1, "Compacidad",
           r"Imagen continua de compacto es compacta. Heine--Borel: en $\mathbb R^n$, compacto $\iff$ cerrado y acotado."),
 "estereo":(1, "Proyección estereográfica",
           r"$S^n\setminus\{N\}\cong\mathbb R^n$."),
 # Tema 2
 "equiv": (2, r"$\simeq$ es relación de equivalencia",
           r"Reflexiva, simétrica ($F(x,1-t)$) y transitiva (se concatenan las homotopías)."),
 "comphomo":(2, "Composición de homotopías",
           r"$f_1\simeq f_2$ y $g_1\simeq g_2\Rightarrow g_1f_1\simeq g_2f_2$, con $H(x,t)=G(F(x,t),t)$."),
 "contractil":(2, "Caracterización de contráctil",
           r"Equivalen: (a) $1_X\simeq c_{x_0}$ para algún $x_0$; (b) para todo $x$; (c) dos aplicaciones cualesquiera $T\to X$ son homotópicas; (d) $X\simeq$ punto."),
 "estrellado":(2, r"Convexo $\Rightarrow$ estrellado $\Rightarrow$ contráctil",
           r"$F(x,t)=tx+(1-t)x_0$ contrae un $X\subseteq\mathbb R^n$ estrellado."),
 "ejemplos":(2, "Ejemplos de equivalencia homotópica",
           r"$S^1\times[-1,1]\simeq S^1$, $\mathbb R^2\setminus\{0\}\simeq S^1$, el cono es contráctil, $S^2\setminus\{N\}\simeq$ punto."),
 # Tema 3
 "relA":  (3, r"$\simeq_A$ es relación de equivalencia",
           r"Igual que $\simeq$, comprobando además que $A$ queda fijo."),
 "contr_arco":(3, r"Contráctil $\Rightarrow$ arco-conexo",
           r"$\alpha(t)=F(x,t)$ une $x$ con $x_0$; se concatenan dos."),
 "poincare":(3, "Teorema de Poincaré",
           r"$\pi_1(X,x_0)=C_{x_0}(X)/\!\simeq_{\{0,1\}}$ es un grupo: producto bien definido, asociativo, neutro $c_{x_0}$ e inverso $[\alpha^{-1}]$."),
 "cambiobase":(3, "Cambio de punto base",
           r"$P_\omega[\alpha]=[\omega^{-1}*\alpha*\omega]$ es un isomorfismo $\pi_1(X,x_0)\to\pi_1(X,x_1)$, con inverso $P_{\omega^{-1}}$."),
 "funtor":(3, "Homomorfismo inducido y funtorialidad",
           r"$f_*[\alpha]=[f\circ\alpha]$ es homomorfismo; $(g f)_*=g_*f_*$ y $(1_X)_*=1$."),
 "homeo": (3, r"Homeomorfismo $\Rightarrow$ $\pi_1$ isomorfo",
           r"Si $f$ es homeomorfismo, $f_*g_*=1$ y $g_*f_*=1$."),
 "estr_pi1":(3, r"Estrellado $\Rightarrow\pi_1=1$",
           r"$F(s,t)=t\alpha(s)+(1-t)x_0$ contrae todo lazo dejando fijos los extremos."),
 "gstar": (3, "Aplicaciones homotópicas",
           r"$f\simeq g$ con $\sigma(t)=F(x_0,t)\Rightarrow g_*=P_\sigma\circ f_*$ (se recorre el borde del cuadrado)."),
 "invhom":(3, "Invariancia homotópica",
           r"$X\simeq Y$ arco-conexos $\Rightarrow\pi_1(X)\cong\pi_1(Y)$."),
 "contr_pi1":(3, r"Contráctil $\Rightarrow\pi_1=1$",
           r"Un contráctil tiene el tipo de homotopía de un punto."),
 # Tema 4
 "simpconexo":(4, "Simplemente conexo",
           r"En un arco-conexo, $\pi_1=1\iff$ dos arcos con los mismos extremos son siempre $\simeq_{\{0,1\}}$."),
 "reparam":(4, "Reparametrización",
           r"$g\colon I\to I$ continua con $g(0)=0$, $g(1)=1\Rightarrow\alpha\simeq_{\{0,1\}}\alpha\circ g$."),
 "lebesgue":(4, "Lema de Lebesgue",
           r"$X$ métrico compacto y $\{U_i\}$ recubrimiento abierto $\Rightarrow\exists\delta$: cada $B(x,\delta)$ está en algún $U_i$. En $[0,1]$: partición regular $t_j=j/n$."),
 "condsuf":(4, "Condición suficiente",
           r"$X=\bigcup V_i$ abiertos con $V_i$ simplemente conexos, $V_i\cap V_j$ arco-conexo y $\bigcap V_i\neq\emptyset\Rightarrow X$ simplemente conexo."),
 "sn":    (4, r"$S^n$ ($n\geq2$) es simplemente conexa",
           r"$V_1=S^n\setminus\{N\}$, $V_2=S^n\setminus\{S\}$; $V_1\cap V_2\cong S^{n-1}\times]-1,1[$ es arco-conexo."),
 "recubr":(4, "Exponencial y unicidad de elevaciones",
           r"$p(t)=e^{2\pi it}$ es homomorfismo con $\ker p=\mathbb Z$. Si $X$ es conexo, dos elevaciones de $f$ que coinciden en un punto son iguales."),
 "unifcont":(4, r"Compacto $\Rightarrow$ uniformemente continua",
           r"Una $f$ continua definida en un compacto de $\mathbb R^n$ es uniformemente continua."),
 "existelev":(4, "Existencia de elevaciones",
           r"$X\subseteq\mathbb R^n$ convexo y compacto, $f\colon X\to S^1$, $p(t_0)=f(x_0)\Rightarrow\exists!\,\tilde f$ con $\tilde f(x_0)=t_0$."),
 "elevarcos":(4, "Elevación de arcos y homotopías",
           r"Para $I$ e $I\times I$: existe una única elevación que empieza en $0$."),
 "pi1s1": (4, r"$\pi_1(S^1)\cong\mathbb Z$",
           r"$\deg[\alpha]=\tilde\alpha(1)$ es un isomorfismo $\pi_1(S^1)\to\mathbb Z$ (bien definido, homomorfismo, inyectivo, sobreyectivo)."),
 "prodpi1":(4, "Grupo fundamental de un producto",
           r"$\pi_1(X\times Y,(x_0,y_0))\cong\pi_1(X,x_0)\times\pi_1(Y,y_0)$."),
 "nocontr":(4, "Consecuencias",
           r"$S^1$ no es contráctil. $S^2\not\cong T^2$, pues $\pi_1(S^2)=1$ y $\pi_1(T^2)=\mathbb Z^2$."),
 # Tema 5
 "noretr":(5, r"No retracción $D^2\to S^1$",
           r"No existe $r\colon D^2\to S^1$ continua con $r|_{S^1}=1$: $r_*i_*=1_{\mathbb Z}$ factorizaría por $\pi_1(D^2)=1$."),
 "brouwer":(5, "Punto fijo de Brouwer",
           r"Toda $f\colon D^2\to D^2$ continua tiene un punto fijo."),
 "dosel": (5, r"Dos elevaciones y $\deg_{x_0}$",
           r"Dos elevaciones de un arco difieren en una constante entera; $\deg_{x_0}(\alpha)=\tilde\alpha(1)-\tilde\alpha(0)$ está bien definido."),
 "degbase":(5, "Cambio de base y grado",
           r"$\deg_{(1,0)}\circ P_\omega=\deg_{x_0}$; en particular $\deg_{x_0}$ solo depende de la clase de homotopía."),
 "tfa":   (5, "Teorema fundamental del álgebra",
           r"Todo polinomio no constante de $\mathbb C[z]$ tiene una raíz: si no la tuviera, el grado de $\sigma$ valdría $0$ y $k\geq1$."),
 "paridad":(5, "Paridad de Borsuk--Hirsch",
           r"$f\colon S^1\to S^1$ par $\Rightarrow\deg(f\circ\sigma)$ par; $f$ impar $\Rightarrow\deg(f\circ\sigma)$ impar."),
 "noimpar":(5, r"No hay impares $S^2\to S^1$",
           r"Si $g$ fuese impar, $f=g\circ j$ tendría $\deg(f\sigma)$ impar y, por ser $S^2$ simplemente conexo, también $0$."),
 "borsuk":(5, "Teorema de Borsuk",
           r"$f\colon S^2\to\mathbb R^2$ continua $\Rightarrow\exists x$ con $f(x)=f(-x)$. Consecuencias: una impar se anula; no hay inyectivas $S^2\to\mathbb R^2$."),
 "lyus":  (5, "Lyusternik--Schnirelmann",
           r"Si tres cerrados recubren $S^2$, alguno contiene dos puntos antipodales."),
 "pi0":   (5, r"$\#\pi_0$ es invariante homotópico",
           r"$\pi_0(X)$ es el conjunto de arco-componentes; $X\simeq Y\Rightarrow\#\pi_0(X)=\#\pi_0(Y)$."),
 "seno":  (5, "Curva seno topológica",
           r"Es conexa pero tiene $2$ arco-componentes, luego no es contráctil."),
}

# --- aristas: (origen, destino, cómo se usa, discontinua?) -----------------
ARISTAS = [
 # Tema 1 -> otros
 ("peg","equiv",r"pegar $F^{(1)}$ y $F^{(2)}$"),
 ("peg","relA",r"pegar, con $A$ fijo"),
 ("peg","poincare",r"pegar homotopías a trozos"),
 ("conexo","recubr",r"$f_1-f_2$ es constante"),
 ("conexo","dosel",r"$k(t)$ es constante"),
 ("conexo","paridad",r"$h$ y $g$ son constantes"),
 ("compacto","lebesgue",r"subrecubrimiento finito"),
 ("compacto","unifcont",r"recubrir con bolas"),
 ("estereo","ejemplos",r"$S^2\setminus\{N\}\cong\mathbb R^2$"),
 ("estereo","sn",r"$V_i\cong\mathbb R^n$"),
 # Tema 2
 ("equiv","relA",r"misma prueba"),
 ("equiv","contractil",r"simetría y transitividad"),
 ("comphomo","contractil",r"$1_X f\simeq c_x f$"),
 ("contractil","contr_arco",r"$F(x,t)$ une $x$ con $x_0$"),
 ("contractil","contr_pi1",r"$X\simeq$ punto"),
 ("estrellado","ejemplos",r"$D^2$, $\mathbb R^2$ contráctiles"),
 ("estrellado","estr_pi1",r"misma homotopía, extremos fijos"),
 ("estrellado","sn",r"$\mathbb R^n$ es contráctil"),
 ("equiv","pi0",r"homotopía entre aplicaciones"),
 # Tema 3
 ("relA","poincare",r"$\simeq_{\{0,1\}}$ define $\pi_1$"),
 ("poincare","cambiobase",r"concatenar arcos"),
 ("poincare","funtor",r"$\pi_1$ es grupo"),
 ("poincare","estr_pi1",r"$[\alpha]=[c_{x_0}]$"),
 ("poincare","simpconexo",r"inversos: $\alpha*\beta^{-1}$"),
 ("funtor","prodpi1",r"proyecciones inducen"),
 ("funtor","homeo",r"$f_*g_*=1$"),
 ("funtor","gstar",r"componer con $G$"),
 ("funtor","invhom",r"$(gf)_*=g_*f_*$"),
 ("funtor","noretr",r"$r_*i_*=1$"),
 ("cambiobase","gstar",r"$P_\sigma$ transporta lazos"),
 ("cambiobase","invhom",r"$P_\sigma$ es biyectiva"),
 ("cambiobase","degbase",r"$P_\omega[\alpha]=[\omega^{-1}\alpha\omega]$"),
 ("estr_pi1","gstar",r"$\pi_1(I\times I)=1$"),
 ("estr_pi1","noretr",r"$\pi_1(D^2)=1$"),
 ("gstar","invhom",r"$g_*f_*$ es $P_\sigma$"),
 ("invhom","contr_pi1",r"$X\simeq$ punto"),
 ("contr_arco","contr_pi1",r"$X$ es arco-conexo"),
 ("contr_pi1","nocontr",r"contráctil $\Rightarrow\pi_1=1$"),
 ("homeo","nocontr",r"$\pi_1$ invariante topológico"),
 # Tema 4
 ("simpconexo","condsuf",r"lazos triviales en cada $V_j$"),
 ("reparam","cambiobase",r"$[\alpha*\beta*\gamma]$ sin paréntesis",True),
 ("lebesgue","condsuf",r"partición regular de $I$"),
 ("condsuf","sn",r"$V_1=S^n\setminus N$, $V_2=S^n\setminus S$"),
 ("sn","nocontr",r"$\pi_1(S^2)=1$"),
 ("recubr","existelev",r"unicidad"),
 ("unifcont","existelev",r"$\|x-x'\|<\delta$"),
 ("existelev","elevarcos",r"$I$ e $I\times I$ convexos compactos"),
 ("elevarcos","pi1s1",r"elevar lazos y homotopías"),
 ("recubr","pi1s1",r"$p^{-1}(1,0)=\mathbb Z$"),
 ("prodpi1","nocontr",r"$\pi_1(T^2)=\mathbb Z^2$"),
 ("pi1s1","nocontr",r"$\pi_1(S^1)=\mathbb Z\neq1$"),
 # Tema 5
 ("pi1s1","noretr",r"$\pi_1(S^1)=\mathbb Z$"),
 ("noretr","brouwer",r"se construiría una retracción"),
 ("pi1s1","tfa",r"grado y homotopías relativas"),
 ("recubr","dosel",r"$p$ es homomorfismo"),
 ("dosel","degbase",r"$\tilde\omega_1-\tilde\omega_2$ constante"),
 ("elevarcos","degbase",r"elevar $\omega^{-1}$, $\alpha$, $\omega$"),
 ("dosel","paridad",r"grado con cualquier elevación"),
 ("degbase","noimpar",r"$\deg_{x_0}$ solo depende de la clase"),
 ("paridad","noimpar",r"$\deg(f\sigma)$ impar"),
 ("sn","noimpar",r"$j\circ\sigma\simeq c$ en $S^2$"),
 ("noimpar","borsuk",r"$\frac{f(x)-f(-x)}{\|f(x)-f(-x)\|}$ sería impar"),
 ("borsuk","lyus",r"$g=(d(x,A_1),d(x,A_2))$"),
 ("pi0","seno",r"$\#\pi_0=2\neq1$"),
 ("contractil","seno",r"contráctil $\simeq$ punto"),
]

# ---------------------------------------------------------------------------
W = 6.8            # ancho de las cajas (cm)
PITCH = 10.2       # distancia entre columnas
LANE_H = 0.27      # separación entre líneas horizontales (llevan etiqueta)
LANE_V = 0.14      # separación entre líneas verticales en los pasillos

def aprox_lineas(texto, chars=44):
    t = re.sub(r"\\[a-zA-Z]+", "x", texto)
    t = re.sub(r"[$\\{}_^]", "", t)
    return max(1, math.ceil(len(t) / chars))

def altura_cm(titulo, enun):
    return 0.46 * aprox_lineas(titulo, 41) + 0.34 * aprox_lineas(enun, 45) + 0.35

def main():
    aqui = Path(__file__).parent
    ids = list(NODOS)
    col = {k: NODOS[k][0] - 1 for k in ids}
    preds = {k: [] for k in ids}
    for a in ARISTAS:
        preds[a[1]].append(a[0])

    # profundidad (camino más largo desde una fuente)
    prof = {}
    def depth(k):
        if k not in prof:
            prof[k] = 0 if not preds[k] else 1 + max(depth(p) for p in preds[k])
        return prof[k]
    for k in ids: depth(k)

    # nivel: debajo de todos sus predecesores y debajo de lo ya colocado en su columna
    nivel, ultimo = {}, {c: -1 for c in range(5)}
    for k in sorted(ids, key=lambda k: (prof[k], ids.index(k))):
        n = max([nivel[p] + 1 for p in preds[k]] + [ultimo[col[k]] + 1])
        nivel[k] = n; ultimo[col[k]] = n
    NL = max(nivel.values()) + 1
    alto = {k: altura_cm(NODOS[k][1], NODOS[k][2]) for k in ids}
    H = [max([alto[k] for k in ids if nivel[k] == l] + [0.5]) for l in range(NL)]
    cx = {k: col[k] * PITCH for k in ids}

    # canal (columna de pasillo) por el que baja cada flecha
    def canal(a, b):
        ca, cb = col[a], col[b]
        c = cb if ca < cb else (cb + 1 if ca > cb else ca + 1)
        return (c - 0.5) * PITCH

    # puntos de salida / entrada repartidos a lo ancho de la caja
    sal = {k: sorted([e for e in ARISTAS if e[0] == k],
                     key=lambda e: (col[e[1]], nivel[e[1]])) for k in ids}
    ent = {k: sorted([e for e in ARISTAS if e[1] == k],
                     key=lambda e: (col[e[0]], nivel[e[0]])) for k in ids}
    def reparto(lista, e, k):
        n = len(lista); i = lista.index(e)
        ancho = W - 1.6
        return cx[k] + (0 if n == 1 else -ancho / 2 + ancho * i / (n - 1))

    # --- 1.ª pasada: reparto de "carriles" (independiente de las alturas) ---
    ocupado_h, ocupado_v = {}, {}
    def lane(dic, clave, a, b):
        a, b = min(a, b) - 0.25, max(a, b) + 0.25
        usados = dic.setdefault(clave, [])
        n = 0
        while any(l == n and not (b < x1 or a > x2) for l, x1, x2 in usados):
            n += 1
        usados.append((n, a, b))
        return n

    plan = []
    for e in sorted(ARISTAS, key=lambda e: -abs(nivel[e[1]] - nivel[e[0]])):
        a, b = e[0], e[1]
        xs, xt = reparto(sal[a], e, a), reparto(ent[b], e, b)
        la, lb = nivel[a], nivel[b]
        if col[a] == col[b] and lb == la + 1 and abs(xs - xt) < 0.05:
            plan.append((e, "recta", xs, xt, None, None, None, None))
        elif lb == la + 1:
            n1 = lane(ocupado_h, la, xs, xt)
            plan.append((e, "corta", xs, xt, n1, None, None, None))
        else:
            xc0 = canal(a, b)
            n1 = lane(ocupado_h, la, xs, xc0)
            n2 = lane(ocupado_h, lb - 1, xc0, xt)
            nv = lane(ocupado_v, round(xc0, 2), la, lb - 1)
            plan.append((e, "larga", xs, xt, n1, n2, nv, xc0))

    # --- 2.ª pasada: alturas de los pasillos según los carriles usados ---
    lanes_gap = {}
    for p in plan:
        e, tipo, xs, xt, n1, n2, nv, xc0 = p
        la, lb = nivel[e[0]], nivel[e[1]]
        if n1 is not None: lanes_gap[la] = max(lanes_gap.get(la, 0), n1 + 1)
        if n2 is not None: lanes_gap[lb - 1] = max(lanes_gap.get(lb - 1, 0), n2 + 1)
    top, bottom, y = [], [], 0.0
    for l in range(NL):
        top.append(y); bottom.append(y - H[l])
        y -= H[l] + 0.8 + LANE_H * lanes_gap.get(l, 1)
    cy = {k: top[nivel[k]] - alto[k] / 2 for k in ids}
    ytop = lambda k: cy[k] + alto[k] / 2
    ybot = lambda k: cy[k] - alto[k] / 2
    gy = lambda l, n: bottom[l] - 0.4 - n * LANE_H

    trazos = []
    for e, tipo, xs, xt, n1, n2, nv, xc0 in plan:
        a, b = e[0], e[1]
        ys, yt = ybot(a), ytop(b)
        la, lb = nivel[a], nivel[b]
        if tipo == "recta":
            pts = [(xs, ys), (xt, yt)]
            etiq = (xs + 0.12, (ys + yt) / 2, "west")
        elif tipo == "corta":
            g = gy(la, n1)
            pts = [(xs, ys), (xs, g), (xt, g), (xt, yt)]
            etiq = ((xs + xt) / 2, g, "center")
        else:
            xc = xc0 + (nv - 8) * LANE_V
            g1, g2 = gy(la, n1), gy(lb - 1, n2)
            pts = [(xs, ys), (xs, g1), (xc, g1), (xc, g2), (xt, g2), (xt, yt)]
            etiq = ((xc + xt) / 2 if abs(xc - xt) > 1.8 else xt - 0.9 if xc < xt else xt + 0.9, g2, "center")
        trazos.append((e, pts, etiq))

    L = []
    L.append(r"""% Mapa de dependencias entre teoremas. Generado por generar.py
% Compilar con pdflatex mapa.tex  (las coordenadas son fijas: se puede editar a mano)
\documentclass[tikz,border=14pt]{standalone}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish]{babel}
\usepackage{amsmath,amssymb}
\usepackage{lmodern}
\renewcommand{\familydefault}{\sfdefault}
\usetikzlibrary{arrows.meta,calc,backgrounds}
""")
    cols = {"tUno": "orange!90!black", "tDos": "green!50!black", "tTres": "blue!75!black",
            "tCuatro": "violet!80!black", "tCinco": "red!75!black"}
    for n, c in cols.items():
        L.append(rf"\colorlet{{{n}}}{{{c}}}")
    L.append(r"""
\tikzset{
  nodo/.style={draw=#1, fill=#1!6, rounded corners=3pt, line width=0.7pt,
     align=left, inner sep=3.5pt, anchor=center},
  flecha/.style={-{Stealth[length=4.5pt,width=4pt]}, line width=0.55pt, rounded corners=3pt},
  etiqueta/.style={font=\fontsize{6}{6.5}\selectfont, fill=white, fill opacity=0.9, text opacity=1,
     inner sep=1pt, rounded corners=1pt, align=center},
}
\begin{document}
\begin{tikzpicture}[x=1cm,y=1cm]
""")
    # carriles
    y_alto, y_bajo = 2.4, bottom[-1] - 1.0
    L.append(r"\begin{scope}[on background layer]")
    for c in range(5):
        cl = list(TEMAS.values())[c][0]
        L.append(rf"\fill[{cl}!5,rounded corners=6pt] ({c*PITCH-PITCH/2+0.15:.2f},{y_bajo:.2f}) rectangle ({c*PITCH+PITCH/2-0.15:.2f},{y_alto:.2f});")
        L.append(rf"\draw[{cl}!40,rounded corners=6pt,line width=0.6pt] ({c*PITCH-PITCH/2+0.15:.2f},{y_bajo:.2f}) rectangle ({c*PITCH+PITCH/2-0.15:.2f},{y_alto:.2f});")
    L.append(r"\end{scope}")
    for c, (t, (cl, desc)) in enumerate(TEMAS.items()):
        L.append(rf"\node[font=\large\bfseries,text={cl}] at ({c*PITCH:.2f},{y_alto-0.7:.2f}) {{T{t}\ \ {desc}}};")
    # nodos
    for k, (tema, tit, enun) in NODOS.items():
        cl = TEMAS[tema][0]
        L.append(rf"\node[nodo={cl}, minimum width={W}cm, minimum height={alto[k]:.2f}cm, text width={W-0.5}cm] "
                 rf"(n{k}) at ({cx[k]:.2f},{cy[k]:.2f}) "
                 rf"{{{{\bfseries\footnotesize\color{{{cl}}}{tit}}}\hfill{{\tiny\color{{{cl}}}T{tema}}}\\[-1pt]"
                 rf"{{\scriptsize {enun}}}}};")
    L.append("")
    for e, pts, etiq in trazos:
        cl = TEMAS[NODOS[e[0]][0]][0]
        estilo = f"flecha,draw={cl}" + (",dashed" if len(e) > 3 and e[3] else "")
        ruta = " -- ".join(f"({x:.2f},{y:.2f})" for x, y in pts)
        L.append(rf"\draw[{estilo}] {ruta};")
    for e, pts, etiq in trazos:
        cl = TEMAS[NODOS[e[0]][0]][0]
        x, y, anc = etiq
        pos = "" if anc == "center" else f",anchor={anc}"
        L.append(rf"\node[etiqueta,text={cl}{pos}] at ({x:.2f},{y:.2f}) {{{e[2]}}};")
    # título y leyenda
    L.append(rf"\node[anchor=west,font=\huge\bfseries] at ({-PITCH/2:.2f},{y_alto+2.2:.2f}) "
             r"{Mapa de dependencias entre teoremas (Topología Algebraica)};")
    L.append(rf"\node[anchor=west,font=\small,align=left] at ({-PITCH/2:.2f},{y_alto+1.0:.2f}) "
             r"{Una columna por tema; se lee de arriba abajo. Una flecha $A\to B$ significa que $A$ se usa para demostrar $B$ y la etiqueta dice cómo.\\"
             r"El color de la flecha es el del tema de origen. Línea discontinua: referencia hacia atrás (la reparametrización está en el Tema 4 pero se usa antes).};")
    L.append(r"""\end{tikzpicture}
\end{document}
""")
    (aqui / "mapa.tex").write_text("\n".join(L), encoding="utf-8")
    print("escrito", aqui / "mapa.tex", f"({len(NODOS)} nodos, {len(ARISTAS)} aristas, {NL} filas)")

main()
