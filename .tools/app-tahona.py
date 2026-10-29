"""La app: las dos tareas de Tahona y el resumen de gerencia."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def cambia(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


BLOQUE = r'''/* ---------------------------------------------------------- la tahona
   El pan del panadero: entra por la mañana y se devuelve lo que no se vende.
   A fin de mes se suma entradas y se restan devoluciones, para cotejar con su factura. */
function euros(n){
  if(n === null || n === undefined || n === "") return "—";
  return Number(n).toFixed(2).replace(".", ",") + " €";
}

function bloqueTahona(cual){
  /* cual: "entrada" (coordinación, por la mañana) o "devolucion" (tienda, por la tarde) */
  const esEntrada = cual === "entrada";
  const dia = (tahona || {})[fechaSel] || {};
  const valor = dia[cual];
  const titulo = esEntrada ? "Tahona · entrada del pan" : "Tahona · devolución";
  const pista = esEntrada
    ? "Lo que trae el panadero por la mañana."
    : "Lo que se le devuelve por la noche.";
  let html = `<h2 class="bloque">${titulo}<small>${
    valor !== undefined && valor !== null ? euros(valor) : "sin apuntar"}</small></h2>`;
  html += `<div class="lista"><div class="nueva-nota">
      <label class="pista" style="flex:0 0 auto">${esEntrada ? "Entrada" : "Devolución"}</label>
      <input type="number" min="0" step="0.01" inputmode="decimal"
             id="tah-${cual}" value="${valor !== undefined && valor !== null ? valor : ""}"
             placeholder="0,00" style="flex:0 0 120px">
      <span class="pista">€</span>
      <button id="tah-guardar" class="btn-add" type="button">Guardar</button>
    </div><p class="pista">${pista}</p></div>`;
  return html;
}

/* el resumen del mes anterior: solo para la Jefa, del 1 al 5 */
function bloqueTahonaResumen(){
  const hoy = fechaBuena(DIA);
  const diaMes = Number(hoy.slice(8, 10));
  if(diaMes > 5) return "";
  /* el mes anterior */
  let a = Number(hoy.slice(0, 4)), m = Number(hoy.slice(5, 7)) - 1;
  if(m < 1){ m = 12; a--; }
  const prefijo = a + "-" + String(m).padStart(2, "0");
  const filas = Object.keys(tahona || {}).filter(f => f.startsWith(prefijo)).sort();
  if(!filas.length) return "";
  let ent = 0, dev = 0;
  filas.forEach(f=>{
    if(tahona[f].entrada) ent += Number(tahona[f].entrada);
    if(tahona[f].devolucion) dev += Number(tahona[f].devolucion);
  });
  const MESES = ["enero","febrero","marzo","abril","mayo","junio","julio",
                 "agosto","septiembre","octubre","noviembre","diciembre"];
  const neto = ent - dev;
  let html = `<h2 class="bloque bloque-viene">Tahona · resumen de ${MESES[m - 1]}` +
    `<small>para cotejar con la factura del panadero</small></h2>` +
    `<div class="lista lista-viene"><div class="rec-tabla">`;
  html += `<div class="rec-fila"><span>Entradas</span><span style="text-align:right"></span>` +
    `<span></span><span style="text-align:right"></span><span>${euros(ent)}</span></div>`;
  html += `<div class="rec-fila"><span>Devoluciones</span><span></span><span></span>` +
    `<span></span><span>${euros(dev)}</span></div>`;
  html += `<div class="rec-fila rec-hoy"><span>Al panadero</span><span></span><span></span>` +
    `<span></span><span>${euros(neto)}</span></div>`;
  html += `</div></div>`;
  return html;
}

async function guardarTahona(cual){
  const inp = document.getElementById("tah-" + cual);
  if(!inp) return;
  const cuerpo = { quien: quien.id, fecha: fechaSel };
  cuerpo[cual] = inp.value === "" ? null : inp.value;
  ponerSync("trabajando", "Guardando el pan…");
  try{
    const r = await fetch("/api/tahona", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cuerpo)
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

cambia("function bloqueSinDia(pre){", BLOQUE + "function bloqueSinDia(pre){",
       "los bloques de la tahona")

# 1 · la variable
cambia('let recuentos = {};   // el recuento del lunes, por fecha del lunes',
       'let recuentos = {};   // el recuento del lunes, por fecha del lunes\n'
       'let tahona = {};      // el pan del panadero, por fecha',
       "la variable de la tahona")

# 2 · se carga con el estado
cambia("      recuentos = d.recuentos || {};",
       "      recuentos = d.recuentos || {};\n      tahona = d.tahona || {};",
       "la tahona se carga al arrancar")

# 3 · el botón de guardar
cambia('  const rg = document.getElementById("rec-guardar");',
       '  const tg = document.getElementById("tah-guardar");\n'
       '  if(tg) tg.addEventListener("click", ()=> guardarTahona(\n'
       '    document.getElementById("tah-entrada") ? "entrada" : "devolucion"));\n'
       '  const rg = document.getElementById("rec-guardar");',
       "el botón de guardar el pan")

# 4 · coordinación: la entrada, todos los días
cambia('      if(W === "LUN") html += bloqueRecuento(true, true);',
       '      html += bloqueTahona("entrada");\n'
       '      if(W === "LUN") html += bloqueRecuento(true, true);',
       "coordinación tiene la entrada del pan")

# 5 · tienda, por la tarde: la devolución
cambia('      if(W === "LUN" && tab === "manana") html += bloqueRecuento(true, false);',
       '      if(tab === "tarde") html += bloqueTahona("devolucion");\n'
       '      if(W === "LUN" && tab === "manana") html += bloqueRecuento(true, false);',
       "tienda por la tarde tiene la devolución")

# 6 · la Jefa: el resumen, del 1 al 5
cambia("  html += bloqueRecuento(false, true);   /* la Jefa lo mira, no lo apunta */",
       "  html += bloqueTahonaResumen();   /* del 1 al 5, el mes anterior */\n"
       "  html += bloqueRecuento(false, true);   /* la Jefa lo mira, no lo apunta */",
       "la Jefa tiene el resumen del pan")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
