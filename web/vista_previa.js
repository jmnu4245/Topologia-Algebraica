// Vista previa de las referencias a resultados (cajas tcolorbox) al pasar el ratón por el enlace.
// - Caja en la misma página: se clona. En otra página: se descarga una vez (fetch), se guarda en
//   caché y se extrae la caja por su id. Solo se muestra la caja (título y enunciado): la
//   demostración va fuera de ella en el HTML y no se copia.
// - Pantallas anchas: nota al margen derecho. Resto: recuadro flotante junto al enlace.
// - Táctil (sin hover): el primer toque muestra la vista previa y el segundo sigue el enlace.
// - Se cierra al sacar el ratón, con Escape o al pulsar fuera.
(function () {
  "use strict";

  var SELECTOR = 'a[href*="#tcolobox-"]';
  var RETRASO_ABRIR = 250;   // ms con el ratón encima antes de abrir
  var RETRASO_CERRAR = 300;  // ms para poder pasar del enlace al recuadro sin que se cierre
  var MARGEN = 8;            // separación mínima con los bordes de la ventana
  var ANCHO_MARGEN = 1300;   // a partir de aquí, nota al margen (si cabe)
  var MIN_NOTA = 280;        // ancho mínimo de la nota al margen para usarla

  var paginas = new Map();   // url sin # -> Promise<Document>
  var recuadro = null;       // el elemento flotante
  var enlaceActual = null;   // enlace cuya vista previa se muestra
  var turno = 0;             // invalida cargas que terminan tarde
  var temporizadorAbrir = 0, temporizadorCerrar = 0;
  var ultimoPuntero = "mouse";

  function destino(enlace) {
    var url;
    try { url = new URL(enlace.getAttribute("href"), location.href); } catch (e) { return null; }
    var id = decodeURIComponent(url.hash.slice(1));
    if (!/^tcolobox-/.test(id)) return null;
    var mismaPagina = url.origin === location.origin && url.pathname === location.pathname;
    url.hash = "";
    return { id: id, mismaPagina: mismaPagina, pagina: url.href };
  }

  function documentoDe(pagina) {
    if (!paginas.has(pagina)) {
      var promesa = fetch(pagina, { credentials: "same-origin" })
        .then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status);
          return r.text();
        })
        .then(function (html) { return new DOMParser().parseFromString(html, "text/html"); });
      promesa.catch(function () { paginas.delete(pagina); });  // reintenta la próxima vez
      paginas.set(pagina, promesa);
    }
    return paginas.get(pagina);
  }

  // Copia de la caja sin ids (no duplicarlos en la página) y sin demostraciones, por si alguna
  // estuviera dentro de la caja.
  function copiaLimpia(caja) {
    var copia = document.importNode(caja, true);
    copia.querySelectorAll(".proof").forEach(function (el) { el.remove(); });
    copia.removeAttribute("id");
    copia.querySelectorAll("[id]").forEach(function (el) { el.removeAttribute("id"); });
    copia.querySelectorAll("a[id]:empty").forEach(function (el) { el.remove(); });
    return copia;
  }

  function cajaPara(d) {
    if (d.mismaPagina) {
      var caja = document.getElementById(d.id);
      return Promise.resolve(caja ? copiaLimpia(caja) : null);
    }
    return documentoDe(d.pagina).then(function (doc) {
      var caja = doc.getElementById(d.id);
      return caja ? copiaLimpia(caja) : null;
    });
  }

  function componerFormulas(el) {
    var mj = window.MathJax;
    if (!mj) return Promise.resolve();
    var listo = mj.startup && mj.startup.promise ? mj.startup.promise : Promise.resolve();
    return listo.then(function () {
      if (typeof mj.typesetPromise === "function") return mj.typesetPromise([el]);
    }).catch(function () {});
  }

  function crearRecuadro() {
    if (recuadro) return recuadro;
    recuadro = document.createElement("div");
    recuadro.className = "vista-previa";
    recuadro.id = "vista-previa";
    recuadro.setAttribute("role", "tooltip");
    recuadro.hidden = true;
    recuadro.addEventListener("pointerenter", cancelarCierre);
    recuadro.addEventListener("pointerleave", function (e) {
      if (e.pointerType !== "touch") programarCierre();
    });
    document.body.appendChild(recuadro);
    return recuadro;
  }

  function usarMargen() {
    if (window.innerWidth <= ANCHO_MARGEN) return null;
    var cuerpo = document.body.getBoundingClientRect();
    var izquierda = cuerpo.right + 16;
    var ancho = Math.min(448, window.innerWidth - izquierda - MARGEN - 8);
    return ancho >= MIN_NOTA ? { izquierda: izquierda, ancho: ancho } : null;
  }

  // Coloca el recuadro (coordenadas del documento) sin que se salga de la ventana.
  function colocar() {
    if (!recuadro || !enlaceActual || recuadro.hidden) return;
    var r = enlaceActual.getBoundingClientRect();
    var vw = document.documentElement.clientWidth, vh = window.innerHeight;
    var margen = usarMargen();
    var arriba, izquierda;
    recuadro.classList.toggle("vista-previa--margen", !!margen);
    recuadro.style.maxHeight = "";
    if (margen) {
      recuadro.style.width = margen.ancho + "px";
      recuadro.style.maxHeight = (vh - 2 * MARGEN) + "px";
      var alto = recuadro.offsetHeight;
      izquierda = margen.izquierda;
      arriba = Math.max(MARGEN, Math.min(r.top - 12, vh - alto - MARGEN));
    } else {
      recuadro.style.width = Math.min(576, vw - 2 * MARGEN) + "px";
      var abajo = vh - r.bottom - MARGEN - 6, encima = r.top - MARGEN - 6;
      var haciaAbajo = abajo >= Math.min(recuadro.scrollHeight, 320) || abajo >= encima;
      recuadro.style.maxHeight = Math.max(120, haciaAbajo ? abajo : encima) + "px";
      var altoF = recuadro.offsetHeight;
      arriba = haciaAbajo ? r.bottom + 6 : r.top - 6 - altoF;
      izquierda = Math.max(MARGEN, Math.min(r.left, vw - recuadro.offsetWidth - MARGEN));
    }
    recuadro.style.left = (izquierda + window.scrollX) + "px";
    recuadro.style.top = (arriba + window.scrollY) + "px";
  }

  function mostrar(enlace) {
    var d = destino(enlace);
    if (!d) return;
    cancelarCierre();
    if (enlace === enlaceActual && recuadro && !recuadro.hidden) return;
    var mio = ++turno;
    crearRecuadro();
    if (enlaceActual) enlaceActual.removeAttribute("aria-describedby");
    enlaceActual = enlace;
    enlace.setAttribute("aria-describedby", "vista-previa");
    recuadro.innerHTML = '<p class="vista-previa-aviso">Cargando…</p>';
    recuadro.hidden = false;
    colocar();
    cajaPara(d).then(function (caja) {
      if (mio !== turno) return;
      recuadro.innerHTML = "";
      if (!caja) {
        recuadro.innerHTML = '<p class="vista-previa-aviso">No se encontró el resultado.</p>';
        colocar();
        return;
      }
      recuadro.appendChild(caja);
      recuadro.scrollTop = 0;
      colocar();
      return componerFormulas(caja).then(function () { if (mio === turno) colocar(); });
    }, function () {
      if (mio !== turno) return;
      recuadro.innerHTML = '<p class="vista-previa-aviso">No se pudo cargar la vista previa.</p>';
      colocar();
    });
  }

  function cerrar() {
    clearTimeout(temporizadorAbrir);
    cancelarCierre();
    turno++;
    if (enlaceActual) enlaceActual.removeAttribute("aria-describedby");
    enlaceActual = null;
    if (recuadro) { recuadro.hidden = true; recuadro.innerHTML = ""; }
  }

  function programarCierre() {
    cancelarCierre();
    temporizadorCerrar = setTimeout(cerrar, RETRASO_CERRAR);
  }
  function cancelarCierre() { clearTimeout(temporizadorCerrar); }

  function enlaceDe(el) {
    var a = el && el.closest ? el.closest(SELECTOR) : null;
    return a && !(recuadro && recuadro.contains(a)) ? a : null;
  }

  // Ratón: abrir con un pequeño retraso, cerrar al salir del enlace y del recuadro.
  document.addEventListener("pointerover", function (e) {
    if (e.pointerType === "touch") return;
    var a = enlaceDe(e.target);
    if (!a) return;
    cancelarCierre();
    if (a === enlaceActual) return;
    clearTimeout(temporizadorAbrir);
    temporizadorAbrir = setTimeout(function () { mostrar(a); }, RETRASO_ABRIR);
  });
  document.addEventListener("pointerout", function (e) {
    if (e.pointerType === "touch") return;
    var a = enlaceDe(e.target);
    if (!a || a.contains(e.relatedTarget)) return;
    clearTimeout(temporizadorAbrir);
    if (a === enlaceActual) programarCierre();
  });

  // Táctil: primer toque muestra, segundo sigue el enlace. Pulsar fuera cierra.
  document.addEventListener("pointerdown", function (e) {
    ultimoPuntero = e.pointerType || "mouse";
    if (!recuadro || recuadro.hidden) return;
    if (recuadro.contains(e.target) || (enlaceActual && enlaceActual.contains(e.target))) return;
    cerrar();
  }, true);
  document.addEventListener("click", function (e) {
    var a = enlaceDe(e.target);
    if (!a || ultimoPuntero !== "touch" || e.ctrlKey || e.metaKey || e.shiftKey) return;
    if (a === enlaceActual && recuadro && !recuadro.hidden) { cerrar(); return; }  // 2.º toque: navega
    e.preventDefault();
    mostrar(a);
  });

  // Teclado: al enfocar el enlace se muestra; Escape cierra.
  document.addEventListener("focusin", function (e) {
    var a = enlaceDe(e.target);
    if (a && ultimoPuntero !== "touch" && a.matches(":focus-visible")) mostrar(a);
  });
  document.addEventListener("focusout", function (e) {
    if (enlaceDe(e.target) === enlaceActual) programarCierre();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && recuadro && !recuadro.hidden) cerrar();
  });

  window.addEventListener("resize", function () { if (recuadro && !recuadro.hidden) colocar(); });
})();
