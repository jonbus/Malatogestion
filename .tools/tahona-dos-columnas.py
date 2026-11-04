"""La Tahona con dos columnas, igual que Zuaza pero al revés.

Casillas con nombre propio: tahE-<pan> para la entrada y tahD-<pan> para la
devolución. Así se pueden pintar las dos a la vez sin que se confundan.
"""
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


FUNCION = r'''/* ------------------------------------------------ LA TAHONA, A DOS COLUMNAS
   Entrada y devolución en la misma hoja, como Zuaza pero al revés:
   primero la entrada, después la devolución.
   Las casillas llevan nombre propio (tahE / tahD) para no confundirse. */
const PANES_TAHONA_DOS = [
  ["txapata", "Txapata", "1,85"],
  ["txapatita", "Txapatita", "1,10"],
  ["barra", "Barra de Pan", "1,50"],
  ["cuarto", "Cuarto de Pan", "1,20"],
  ["txoripan", "Txoripan Tahona", "1,80"]
];

function pintaTahona(){
  const c = document.getElementById("cuerpo");
  const f = fechaSel;
  const dia = (tahona || {})[f] || {};
  const ent = dia.entrada || {};
  const dev = dia.devolucion || {};
  const v = (x)=> (x === null || x === undefined) ? "" : x;

  let html = botonesPan() + botonesDia() +
    `<h2 class="bloque">Tahona<small>${bonito(f)}</small></h2>` +
    `<div class="lista"><div class="item">
      <div class="cab-item"><span class="txt">
        <b>Primero la entrada. Después la devolución.</b>
        <span class="n">Lo que llega hoy y lo que vuelve al panadero.</span>
      </span></div>
      <table style="width:100%;border-collapse:collapse;font-size:13px;margin-top:8px">
        <tr>
          <th style="text-align:left;padding:6px 4px">Pan</th>
          <th style="padding:6px 4px">Entrada</th>
          <th style="padding:6px 4px">Devolución</th>
        </tr>`;

  PANES_TAHONA_DOS.forEach(([k, n, precio])=>{
    html += `<tr>
        <td style="padding:6px 4px">${n} <small style="color:#8a938f">${precio} €</small></td>
        <td style="padding:6px 4px;text-align:center">
          <input type="number" min="0" inputmode="decimal" id="tahE-${k}"
                 value="${v(ent[k])}" style="width:78px;text-align:center"></td>
        <td style="padding:6px 4px;text-align:center">
          <input type="number" min="0" inputmode="decimal" id="tahD-${k}"
                 value="${v(dev[k])}" style="width:78px;text-align:center"></td>
      </tr>`;
  });

  html += `</table>
      <div class="nueva-nota">
        <button class="btn-add" type="button" onclick="guardarTahonaDos()">Guardar el pan de este día</button>
      </div>
    </div></div>`;

  c.innerHTML = html;
}

async function guardarTahonaDos(){
  const f = fechaSel;
  const recoge = (pre)=>{
    const x = {};
    for(const p of PANES_TAHONA_DOS){
      const val = valorDe("tah" + pre + "-" + p[0], "");
      x[p[0]] = (val === "" || val === null) ? "" : val;
    }
    return x;
  };
  ponerSync("trabajando", "Guardando el pan de la tahona…");
  try{
    for(const par of [["entrada", "E"], ["devolucion", "D"]]){
      const r = await fetch("/api/tahona", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fecha: f, cual: par[0], quien: quien.id, valores: recoge(par[1]) })
      });
      if(!r.ok) throw new Error("HTTP " + r.status);
      const d = await r.json();
      if(!d.ok) throw new Error(d.error || "no se guardó");
      tahona = d.tahona || {};
    }
    ponerSync("ok", "Pan de la tahona guardado");
  }catch(e){
    ponerSync("error", "No se pudo guardar el pan de la tahona");
  }
  pinta();
}

'''

rep("function pintaCalendario(){", FUNCION + "function pintaCalendario(){", "las funciones de la Tahona")

# la ruta: si es tahona, a la pantalla nueva
rep('  if(panVista === "zuaza"){ pintaZuaza(); return; }',
    '  if(panVista === "zuaza"){ pintaZuaza(); return; }\n  if(panVista === "tahona"){ pintaTahona(); return; }',
    "la ruta a la Tahona")

rep("v-2026-10-26-86", "v-2026-10-26-87", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
