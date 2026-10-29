"""Informe del pan: entre dos fechas, corregir un día, y un texto que se lea en WhatsApp."""
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


NUEVO = r'''/* ---------------------------------------------------- sacar el informe fuera
   El texto de WhatsApp NO lleva columnas: WhatsApp usa una letra de ancho
   distinto para cada carácter, así que alinear con espacios es imposible.
   Va una línea por pan con el neto, que se lee bien en cualquier móvil. */
const MESES_LARGOS = ["enero","febrero","marzo","abril","mayo","junio","julio",
                      "agosto","septiembre","octubre","noviembre","diciembre"];

let panDesde = "", panHasta = "";     /* el rango del informe */
let panCorrige = "";                  /* el día que se está corrigiendo */

function mesPan(){
  const hoy = fechaBuena(DIA);
  const diaMes = Number(hoy.slice(8, 10));
  let a = Number(hoy.slice(0, 4)), m = Number(hoy.slice(5, 7));
  if(diaMes <= 5){ m = m - 1; if(m < 1){ m = 12; a--; } }
  const pref = a + "-" + String(m).padStart(2, "0");
  return { a: a, m: m, prefijo: pref,
           nombre: MESES_LARGOS[m - 1] + " de " + a,
           desde: pref + "-01",
           hasta: pref + "-" + String(new Date(a, m, 0).getDate()).padStart(2, "0") };
}

/* el rango que se está mirando (por defecto, el mes) */
function rangoPan(){
  const mes = mesPan();
  const d = /^\d{4}-\d{2}-\d{2}$/.test(panDesde) ? panDesde : mes.desde;
  const h = /^\d{4}-\d{2}-\d{2}$/.test(panHasta) ? panHasta : mes.hasta;
  return d <= h ? { desde: d, hasta: h } : { desde: h, hasta: d };
}

function diasPan(){
  const r = rangoPan();
  return Object.keys(tahona || {}).filter(f => f >= r.desde && f <= r.hasta).sort();
}

function filasPan(){
  const dias = diasPan();
  return PANES_TAHONA.map(([k, nombre])=>{
    let e = 0, d = 0;
    dias.forEach(f=>{
      const dia = tahona[f] || {};
      if(dia.entrada && dia.entrada[k]) e += Number(dia.entrada[k]);
      if(dia.devolucion && dia.devolucion[k]) d += Number(dia.devolucion[k]);
    });
    return { nombre: nombre, entra: e, sale: d, queda: e - d };
  });
}

function nombreRango(){
  const r = rangoPan();
  const dd = (f) => f.slice(8) + "/" + f.slice(5, 7);
  return "del " + dd(r.desde) + " al " + dd(r.hasta);
}

function textoPan(){
  const filas = filasPan();
  let te = 0, td = 0;
  let t = "MALATO · LA TAHONA\n" + nombreRango() + "\n\n";
  filas.forEach(f=>{
    te += f.entra; td += f.sale;
    t += f.nombre + ": " + f.queda +
         (f.entra || f.sale ? "   (" + f.entra + " − " + f.sale + ")" : "") + "\n";
  });
  t += "\nTOTAL: " + (te - td) + "   (" + te + " − " + td + ")\n";
  t += "\nEntradas menos devoluciones. Unidades.";
  return t;
}

function csvPan(){
  const filas = filasPan();
  const r = rangoPan();
  let te = 0, td = 0;
  let c = "Malato · La tahona;" + nombreRango() + "\n\n";
  c += "Pan;Entra;Sale;Queda\n";
  filas.forEach(f=>{
    te += f.entra; td += f.sale;
    c += f.nombre + ";" + f.entra + ";" + f.sale + ";" + f.queda + "\n";
  });
  c += "TOTAL;" + te + ";" + td + ";" + (te - td) + "\n";
  /* el detalle día a día, para poder cuadrar la factura */
  c += "\nDía;Pan;Entra;Sale\n";
  Object.keys(tahona || {}).filter(f => f >= r.desde && f <= r.hasta).sort()
    .forEach(f=>{
      const dia = tahona[f] || {};
      PANES_TAHONA.forEach(([k, nombre])=>{
        const e = (dia.entrada && dia.entrada[k]) || 0;
        const d = (dia.devolucion && dia.devolucion[k]) || 0;
        if(e || d) c += f + ";" + nombre + ";" + e + ";" + d + "\n";
      });
    });
  return c;
}

async function compartirPan(){
  const texto = textoPan();
  try{
    if(navigator.share){
      await navigator.share({ title: "La tahona", text: texto });
      ponerSync("ok", "Compartido");
    }else{
      await navigator.clipboard.writeText(texto);
      ponerSync("ok", "Copiado · pégalo en WhatsApp");
    }
  }catch(e){
    if(String(e && e.name) === "AbortError") return;
    ponerSync("error", "No se pudo compartir");
  }
}

function descargarPan(){
  const csv = csvPan();
  const blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  const r = rangoPan();
  a.download = "tahona-" + r.desde + "-a-" + r.hasta + ".csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(()=> URL.revokeObjectURL(a.href), 2000);
  ponerSync("ok", "Descargado para Excel");
}

/* corregir un día: se abre con sus diez casillas y se guarda tal cual */
async function guardarPanDia(dia){
  const ent = {}, dev = {};
  document.querySelectorAll("[data-pane]").forEach(i=>{ ent[i.dataset.pane] = i.value; });
  document.querySelectorAll("[data-pand]").forEach(i=>{ dev[i.dataset.pand] = i.value; });
  ponerSync("trabajando", "Corrigiendo el " + dia + "…");
  try{
    for(const cual of ["entrada", "devolucion"]){
      const r = await fetch("/api/tahona", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quien: quien.id, fecha: dia, cual: cual,
                               valores: cual === "entrada" ? ent : dev })
      });
      if(!r.ok) throw new Error("HTTP " + r.status);
      const d = await r.json();
      tahona = d.tahona || {};
    }
    panCorrige = "";
    ponerSync("ok", "Corregido el " + dia);
  }catch(e){
    ponerSync("error", "No se pudo corregir");
  }
  pinta();
}

'''

i = t.find("/* ---------------------------------------------------- sacar el informe fuera")
j = t.find("function bloqueTahonaResumen(){")
if i < 0 or j < 0:
    print("   NO ENCONTRADO el bloque de informes")
    sys.exit(1)
t = t[:i] + NUEVO + t[j:]
print("   ok  las funciones del informe, reescritas")

# ---------------------------------------------------------------- el bloque
BLOQUE = r'''function bloqueTahonaResumen(){
  const mes = mesPan();
  const r = rangoPan();
  const filas = filasPan();
  const dias = diasPan();
  let html = `<h2 class="bloque bloque-viene">Tahona · el pan` +
    `<small>${nombreRango()} · entradas menos devoluciones</small></h2>`;

  /* el rango: de qué día a qué día */
  html += `<div class="lista lista-viene"><div class="nueva-nota">` +
    `<span class="pista">Desde</span>` +
    `<input type="date" id="pan-desde" value="${r.desde}" onchange="panDesde=this.value; pinta()">` +
    `<span class="pista">hasta</span>` +
    `<input type="date" id="pan-hasta" value="${r.hasta}" onchange="panHasta=this.value; pinta()">` +
    `<button class="btn-add-2" type="button" onclick="panDesde='${mes.desde}';` +
    `panHasta='${mes.hasta}'; pinta()">Este mes</button></div>`;

  html += `<div class="rec-tabla">` +
    `<div class="rec-fila rec-cab"><span>Pan</span><span>Entra</span>` +
    `<span>Sale</span><span>Queda</span><span></span></div>`;
  let totE = 0, totD = 0;
  filas.forEach(f=>{
    totE += f.entra; totD += f.sale;
    html += `<div class="rec-fila"><span>${f.nombre}</span><span>${f.entra}</span>` +
      `<span>${f.sale}</span><span><b>${f.queda}</b></span><span></span></div>`;
  });
  html += `<div class="rec-fila rec-hoy"><span>Total</span><span>${totE}</span>` +
    `<span>${totD}</span><span><b>${totE - totD}</b></span><span></span></div>`;
  html += `</div>`;

  /* los botones para sacarlo */
  html += `<div class="nueva-nota" style="border:none; margin-top:10px">` +
    `<button class="btn-add" type="button" onclick="compartirPan()">Compartir</button>` +
    ` <button class="btn-add" type="button" onclick="descargarPan()" ` +
    `style="background:#fff; color:var(--tinta); border:1px solid var(--borde)">` +
    `Descargar para Excel</button></div>`;

  /* corregir: los días del rango, uno a uno */
  html += `</div><h2 class="bloque bloque-viene">Corregir un día` +
    `<small>si algún dato no cuadra con la factura</small></h2>` +
    `<div class="lista lista-viene"><div class="nueva-nota">` +
    `<span class="pista">Día</span>` +
    `<input type="date" id="pan-dia" value="${panCorrige || r.desde}" ` +
    `onchange="panCorrige=this.value; pinta()">` +
    `<button class="btn-add-2" type="button" onclick="panCorrige=document.getElementById('pan-dia').value; pinta()">Abrir</button>` +
    `</div>`;

  const f = panCorrige || "";
  if(f){
    const dia = (tahona || {})[f] || {};
    html += `<div class="rec-tabla"><div class="rec-fila rec-cab">` +
      `<span>Pan</span><span>Entrada</span><span></span>` +
      `<span>Devolución</span><span></span></div>`;
    PANES_TAHONA.forEach(([k, nombre])=>{
      const e = dia.entrada && dia.entrada[k] !== null && dia.entrada[k] !== undefined
        ? dia.entrada[k] : "";
      const d = dia.devolucion && dia.devolucion[k] !== null && dia.devolucion[k] !== undefined
        ? dia.devolucion[k] : "";
      html += `<div class="rec-fila"><span>${nombre}</span>` +
        `<span><input type="number" min="0" step="1" inputmode="numeric" ` +
        `data-pane="${k}" value="${e}" style="width:64px"></span><span></span>` +
        `<span><input type="number" min="0" step="1" inputmode="numeric" ` +
        `data-pand="${k}" value="${d}" style="width:64px"></span><span></span></div>`;
    });
    html += `</div><div class="nueva-nota" style="border:none">` +
      `<button class="btn-add" type="button" ` +
      `onclick="guardarPanDia('${f}')">Guardar ese día</button></div>`;
  }
  html += `</div>`;
  return html;
}
'''

i = t.find("function bloqueTahonaResumen(){")
j = t.find("async function guardarTahona(cual){")
if i < 0 or j < 0:
    print("   NO ENCONTRADO el bloque del resumen")
    sys.exit(1)
t = t[:i] + BLOQUE + "\n" + t[j:]
print("   ok  el bloque del informe, con rango y corrección")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
