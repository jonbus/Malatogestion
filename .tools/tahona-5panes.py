"""Tahona con los cinco panes: entrada y devolución por tipo."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
fallos = 0

# ============================================================ 1 · el servidor
p = r"docs/nube/netlify/functions/nucleo.js"
t = open(p, encoding="utf-8").read()

viejo = """      const num = (x) => {
        if (x === '' || x === null || x === undefined) return null;
        const n = Number(x);
        return Number.isFinite(n) && n >= 0 ? Math.round(n * 100) / 100 : null;
      };
      const estado = await leer();
      if (!estado.tahona) estado.tahona = {};
      const dia = estado.tahona[fecha] || {};
      if (cuerpo.entrada !== undefined) dia.entrada = num(cuerpo.entrada);
      if (cuerpo.devolucion !== undefined) dia.devolucion = num(cuerpo.devolucion);
      dia.q = marca; dia.h = hora;
      estado.tahona[fecha] = dia;"""

nuevo = """      const cual = cuerpo.cual === 'devolucion' ? 'devolucion' : 'entrada';
      const PANES = ['txapata', 'txapatita', 'barra', 'cuarto', 'txoripan'];
      const v = cuerpo.valores || {};
      const num = (x) => {
        if (x === '' || x === null || x === undefined) return null;
        const n = Number(x);
        return Number.isFinite(n) && n >= 0 ? Math.round(n * 100) / 100 : null;
      };
      const limpio = {};
      for (const pan of PANES) limpio[pan] = num(v[pan]);
      const estado = await leer();
      if (!estado.tahona) estado.tahona = {};
      const dia = estado.tahona[fecha] || {};
      dia[cual] = limpio;
      dia.q = marca; dia.h = hora;
      estado.tahona[fecha] = dia;"""

if viejo in t:
    t = t.replace(viejo, nuevo, 1)
    open(p, "w", encoding="utf-8").write(t)
    print("   ok  el servidor guarda los cinco panes")
else:
    print("   NO ENCONTRADO en el servidor")
    fallos += 1

# ============================================================ 2 · la app
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

# --- el bloque, reescrito
i = t.find("function bloqueTahona(cual){")
j = t.find("async function guardarTahona(cual){")
if i < 0 or j < 0:
    print("   NO ENCONTRADO el bloque de la tahona")
    sys.exit(1)
fin = t.find("\n}\n", j)
bloque_nuevo = r'''const PANES_TAHONA = [
  ["txapata", "Txapata"], ["txapatita", "Txapatita"], ["barra", "Barra"],
  ["cuarto", "Cuarto"], ["txoripan", "Txoripan"]
];

function bloqueTahona(cual){
  /* cual: "entrada" (coordinación, por la mañana) o "devolucion" (tienda, por la tarde) */
  const esEntrada = cual === "entrada";
  const dia = (tahona || {})[fechaSel] || {};
  const valores = dia[cual] || {};
  const apuntado = PANES_TAHONA.some(([k]) => valores[k] !== null && valores[k] !== undefined);
  const titulo = esEntrada ? "Tahona · entrada del pan" : "Tahona · devolución";
  const pista = esEntrada
    ? "Lo que trae el panadero por la mañana."
    : "Lo que se le devuelve por la noche.";
  let html = `<h2 class="bloque">${titulo}<small>${
    apuntado ? "apuntado" : "sin apuntar"}</small></h2>`;
  html += `<div class="lista"><div class="recuento tahona">`;
  PANES_TAHONA.forEach(([k, nombre])=>{
    const v = valores[k];
    html += `<label class="rec-campo"><span>${nombre}</span>` +
      `<input type="number" min="0" step="1" inputmode="numeric" ` +
      `data-tah="${k}" value="${v !== null && v !== undefined ? v : ""}"></label>`;
  });
  html += `</div>`;
  html += `<p class="pista" style="padding:0 14px">${pista}</p>`;
  html += `<div class="nueva-nota" style="border:none; margin-top:0">` +
    `<button id="tah-guardar" class="btn-add" type="button" ` +
    `data-cual="${cual}">Guardar el pan</button></div></div>`;
  return html;
}

/* el resumen del mes anterior: solo para la Jefa, del 1 al 5 */
function bloqueTahonaResumen(){
  const hoy = fechaBuena(DIA);
  const diaMes = Number(hoy.slice(8, 10));
  if(diaMes > 5) return "";
  let a = Number(hoy.slice(0, 4)), m = Number(hoy.slice(5, 7)) - 1;
  if(m < 1){ m = 12; a--; }
  const prefijo = a + "-" + String(m).padStart(2, "0");
  const filas = Object.keys(tahona || {}).filter(f => f.startsWith(prefijo)).sort();
  if(!filas.length) return "";
  const MESES = ["enero","febrero","marzo","abril","mayo","junio","julio",
                 "agosto","septiembre","octubre","noviembre","diciembre"];
  let html = `<h2 class="bloque bloque-viene">Tahona · resumen de ${MESES[m - 1]}` +
    `<small>entradas menos devoluciones · para cotejar la factura</small></h2>` +
    `<div class="lista lista-viene"><div class="rec-tabla">` +
    `<div class="rec-fila rec-cab"><span>Pan</span><span>Entra</span>` +
    `<span>Sale</span><span>Queda</span><span></span></div>`;
  let totE = 0, totD = 0;
  PANES_TAHONA.forEach(([k, nombre])=>{
    let e = 0, d = 0;
    filas.forEach(f=>{
      const dia = tahona[f] || {};
      if(dia.entrada && dia.entrada[k]) e += Number(dia.entrada[k]);
      if(dia.devolucion && dia.devolucion[k]) d += Number(dia.devolucion[k]);
    });
    totE += e; totD += d;
    html += `<div class="rec-fila"><span>${nombre}</span><span>${e}</span>` +
      `<span>${d}</span><span><b>${e - d}</b></span><span></span></div>`;
  });
  html += `<div class="rec-fila rec-hoy"><span>Total</span><span>${totE}</span>` +
    `<span>${totD}</span><span><b>${totE - totD}</b></span><span></span></div>`;
  html += `</div></div>`;
  return html;
}

async function guardarTahona(cual){
  const valores = {};
  document.querySelectorAll("[data-tah]").forEach(i=>{ valores[i.dataset.tah] = i.value; });
  ponerSync("trabajando", "Guardando el pan…");
  try{
    const r = await fetch("/api/tahona", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, fecha: fechaSel, cual: cual, valores: valores })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    tahona = d.tahona || {};
    if(typeof d.version === "number") versionVista = d.version;
    ponerSync("ok", "Pan guardado");
  }catch(e){
    ponerSync("error", "No se pudo guardar el pan");
  }
  pinta();
}
'''
t = t[:i] + bloque_nuevo + t[fin + 3:]
print("   ok  el bloque de la tahona, con los cinco panes")

# --- el botón (ahora lleva el tipo en el propio botón)
viejo_boton = '''  const tg = document.getElementById("tah-guardar");
  if(tg) tg.addEventListener("click", ()=> guardarTahona(
    document.getElementById("tah-entrada") ? "entrada" : "devolucion"));'''
nuevo_boton = '''  const tg = document.getElementById("tah-guardar");
  if(tg) tg.addEventListener("click", ()=> guardarTahona(tg.dataset.cual || "entrada"));'''
if viejo_boton in t:
    t = t.replace(viejo_boton, nuevo_boton, 1)
    print("   ok  el botón dice de qué es")
else:
    print("   NO ENCONTRADO el botón")
    fallos += 1

# --- la etiqueta del bloque
t = t.replace(".rec-campo input{", ".tahona{grid-template-columns:repeat(2, 1fr)}\n  .rec-campo input{", 1)

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
