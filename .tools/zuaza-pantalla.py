"""La pantalla de Zuaza: devolución y entrada del día, en la misma hoja."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if v in t:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    else:
        print("  NO ENCONTRADO: " + e)


FUNCION = r'''/* ------------------------------------------------ ZUAZA
   El pan de Zuaza. PRIMERO la devolución —lo que vuelve al proveedor—,
   y después la entrada —lo que llega—. Las dos en la misma pantalla. */
let zuaza = {};

const PANES_ZUAZA = [
  ["casero", "Casero", "3,65"],
  ["barra_casera", "Barra Casera", "2,15"],
  ["molde", "Molde", "3,65"],
  ["integral", "Integral", "3,15"],
  ["cereales", "Cereales", "3,85"],
  ["maiz", "Maíz", "3,85"],
  ["pasas_nueces", "Pasas/Nueces", "4,65"],
  ["txoripan", "Txoripan", "1,85"]
];

function moverFechaZuaza(n){
  const d = new Date(fechaSel + "T12:00:00");
  d.setDate(d.getDate() + n);
  fechaSel = d.toISOString().slice(0, 10);
  pinta();
}

function hoyZuaza(){
  fechaSel = DIA;
  pinta();
}

function pintaZuaza(){
  const c = document.getElementById("cuerpo");
  const f = fechaSel;
  const dia = (zuaza || {})[f] || {};
  const dev = dia.devolucion || {};
  const ent = dia.entrada || {};
  const v = (x)=> (x === null || x === undefined) ? "" : x;

  let html = `<h2 class="bloque">Zuaza<small>${bonito(f)}</small></h2>`;

  html += `<div style="display:flex;gap:8px;margin:10px 0;flex-wrap:wrap">
      <button class="btn-add-2" type="button" onclick="moverFechaZuaza(-1)">◀ día anterior</button>
      <button class="btn-add-2" type="button" onclick="hoyZuaza()">hoy</button>
      <button class="btn-add-2" type="button" onclick="moverFechaZuaza(1)">día siguiente ▶</button>
    </div>`;

  html += `<div class="lista"><div class="item">
      <div class="cab-item"><span class="txt">
        <b>Primero la devolución. Después la entrada.</b>
        <span class="n">Lo que vuelve al proveedor y lo que llega hoy.</span>
      </span></div>
      <table style="width:100%;border-collapse:collapse;font-size:13px;margin-top:8px">
        <tr>
          <th style="text-align:left;padding:6px 4px">Pan</th>
          <th style="padding:6px 4px">Devolución</th>
          <th style="padding:6px 4px">Entrada</th>
        </tr>`;

  PANES_ZUAZA.forEach(([k, n, precio])=>{
    html += `<tr>
        <td style="padding:6px 4px">${n} <small style="color:#8a938f">${precio} €</small></td>
        <td style="padding:6px 4px;text-align:center">
          <input type="number" min="0" inputmode="decimal" id="z-d-${k}"
                 value="${v(dev[k])}" style="width:78px;text-align:center"></td>
        <td style="padding:6px 4px;text-align:center">
          <input type="number" min="0" inputmode="decimal" id="z-e-${k}"
                 value="${v(ent[k])}" style="width:78px;text-align:center"></td>
      </tr>`;
  });

  html += `</table>
      <div class="nueva-nota">
        <button class="btn-add" type="button" onclick="guardarZuaza()">Guardar el pan de este día</button>
        <span class="pista" style="margin-left:8px">${dia.h ? "apuntado a las " + dia.h : ""}</span>
      </div>
    </div></div>`;

  c.innerHTML = html;
}

async function guardarZuaza(){
  const f = fechaSel;
  const recoge = (pre)=>{
    const x = {};
    for(const [k] of PANES_ZUAZA){
      const val = valorDe("z-" + pre + k, "");
      x[k] = (val === "" || val === null) ? "" : val;
    }
    return x;
  };
  ponerSync("trabajando", "Guardando el pan de Zuaza…");
  try{
    for(const par of [["devolucion", "d-"], ["entrada", "e-"]]){
      const r = await fetch("/api/zuaza", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fecha: f, cual: par[0], quien: quien.id, valores: recoge(par[1]) })
      });
      if(!r.ok) throw new Error("HTTP " + r.status);
      const d = await r.json();
      if(!d.ok) throw new Error(d.error || "no se guardó");
      zuaza = d.zuaza || {};
    }
    ponerSync("ok", "Pan de Zuaza guardado");
  }catch(e){
    ponerSync("error", "No se pudo guardar el pan de Zuaza");
  }
  pinta();
}

'''

# 1 · las funciones
rep("function pintaCalendario(){", FUNCION + "function pintaCalendario(){", "las funciones de Zuaza")

# 2 · el botón en el menú de coordinación y de la Jefa
rep('''  coordinacion: [
    ["calendario", "Calendario", "📅"],
    ["panes", "Registro de panes", "🍞"],''',
    '''  coordinacion: [
    ["calendario", "Calendario", "📅"],
    ["panes", "Registro de panes", "🍞"],
    ["zuaza", "Zuaza", "🥖"],''',
    "el botón de Zuaza en coordinación")

rep('''  gerencia: [
    ["general", "El día", "📋"],
    ["turno", "Turno", "📅"],''',
    '''  gerencia: [
    ["general", "El día", "📋"],
    ["turno", "Turno", "📅"],
    ["zuaza", "Zuaza", "🥖"],''',
    "el botón de Zuaza en la Jefa")

# 3 · la ruta
rep('  if(tab === "panes"){ pintaPanes(); return; }',
    '  if(tab === "panes"){ pintaPanes(); return; }\n  if(tab === "zuaza"){ pintaZuaza(); return; }',
    "la ruta a la pantalla")

# 4 · los datos, al arrancar
rep("      cascadas = d.cascadas || {};",
    "      cascadas = d.cascadas || {};\n      zuaza = d.zuaza || {};",
    "cargar el pan de Zuaza")

# 5 · el día que se mira, al principio
rep('v-2026-10-26-77', 'v-2026-10-26-78', "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
