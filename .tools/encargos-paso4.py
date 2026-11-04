"""Paso 4: el resumen de los encargos, por días.

Enseña TODO —también los días pasados— agrupado por día y, dentro de cada día,
por proveedor. Es lo que después se mandará al proveedor.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if t.count(v) == 1:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    elif t.count(v) == 0:
        print("  NO ENCONTRADO: " + e)
    else:
        print(f"  OJO, aparece {t.count(v)} veces: " + e)


# 1 · el estado
rep('let encCantidad = "", encNota = "";',
    'let encCantidad = "", encNota = "";\nlet resumenEncargos = false;   // ¿se está mirando el resumen por días?',
    "el estado del resumen")

# 2 · la pantalla del resumen
FUNCION = r'''/* ------------------------------------------------ EL RESUMEN POR DÍAS
   Todo lo encargado, agrupado por día y, dentro de cada día, por proveedor.
   Enseña también los días pasados: sirve para comprobar cualquier cosa. */
function pintaResumenEncargos(){
  const c = document.getElementById("cuerpo");

  /* se agrupa por el día para el que es cada encargo */
  const porDia = {};
  for(const e of (encargosFecha || [])){
    const f = e.desde || "";
    if(!f) continue;
    if(!porDia[f]) porDia[f] = [];
    porDia[f].push(e);
  }
  const dias = Object.keys(porDia).sort();

  let html = `<h2 class="bloque">Resumen por días<small>${dias.length} ${
    dias.length === 1 ? "día" : "días"}</small></h2>`;

  html += `<div style="display:flex;gap:8px;margin:10px 0;flex-wrap:wrap">
      <button class="btn-add-2" type="button" onclick="resumenEncargos=false; pinta();">◀ Volver a encargos</button>
    </div>`;

  if(!dias.length){
    return html + `<div class="lista"><p class="pista" style="padding:14px">
      Todavía no hay encargos.</p></div>`;
  }

  dias.forEach(f=>{
    const lista = porDia[f];
    /* dentro del día, por proveedor: Zuaza, Tahona y lo demás aparte */
    const grupos = {};
    for(const e of lista){
      const g = e.producto ? (e.que && e.que.toLowerCase().includes("zuaza") ? "Zuaza" : "Proveedor") : "Varios";
      if(!grupos[g]) grupos[g] = [];
      grupos[g].push(e);
    }
    html += `<div class="lista"><div class="item">
      <div class="cab-item"><span class="txt"><b>${bonito(f)}</b>
        <span class="n">${lista.length} ${lista.length === 1 ? "encargo" : "encargos"}</span>
      </span></div>`;
    for(const g of Object.keys(grupos).sort()){
      html += `<div style="padding:6px 0"><b style="font-size:12px">${g}</b>`;
      for(const e of grupos[g]){
        html += `<div style="padding:4px 0 4px 12px;font-size:13px">
          ${e.producto
            ? `<b>${e.cantidad || "?"}</b> ${e.producto}`
            : `${e.que}`}
          ${e.nota ? `<span class="n" style="display:block">${e.nota}</span>` : ""}
        </div>`;
      }
      html += `</div>`;
    }
    html += `</div></div>`;
  });

  c.innerHTML = html;
}

'''

rep("function bloqueFormEncargo(){", FUNCION + "function bloqueFormEncargo(){", "la pantalla del resumen")

# 3 · si está abierto el resumen, se enseña eso
rep("""function bloqueFormEncargo(){
  const lunes = proximoLunes();""",
    """function bloqueFormEncargo(){
  if(resumenEncargos) return pintaResumenEncargos() || "";
  const lunes = proximoLunes();""",
    "la entrada al resumen")

# 4 · el botón, junto a los tres
rep('''        <button class="btn-add-2" type="button" onclick="abrirEncargoProveedor('')">Varios</button>
      </div>''',
    '''        <button class="btn-add-2" type="button" onclick="abrirEncargoProveedor('')">Varios</button>
        <button class="btn-add-2" type="button" onclick="resumenEncargos=true; pinta();">📋 Resumen por días</button>
      </div>''',
    "el botón del resumen")

# 5 · al salir de encargos, también se cierra el resumen
rep('  if(k !== "calendario"){ formEncargo = false; encProveedor = ""; }',
    '  if(k !== "calendario"){ formEncargo = false; encProveedor = ""; resumenEncargos = false; }',
    "el resumen se cierra al salir")

rep("v-2026-10-26-90", "v-2026-10-26-91", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
