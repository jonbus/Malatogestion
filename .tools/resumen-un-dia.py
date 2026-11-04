"""El resumen enseña UN día, el que se elija. Al entrar, el de hoy."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

INICIO = "function pintaResumenEncargos(){"
FIN = "/* ------------------------------------------------ MANDAR EL PEDIDO DE MAÑANA"

i = t.find(INICIO)
j = t.find(FIN)
if i < 0 or j < 0 or j <= i:
    print("  NO ENCONTRADO el resumen")
    sys.exit(1)

NUEVO = '''let diaResumen = "";   /* el día que se está mirando en el resumen */

function pintaResumenEncargos(){
  const f = diaResumen || DIA;
  const lista = (encargosFecha || []).filter(e => e.desde === f);

  /* se agrupa por proveedor */
  const grupos = {};
  for(const e of lista){
    const g = e.producto ? (e.que || "Proveedor") : "Varios";
    if(!grupos[g]) grupos[g] = [];
    grupos[g].push(e);
  }

  const manana = diaDeManana();

  let html = `<h2 class="bloque">Resumen por días<small>${bonito(f)}</small></h2>`;

  html += `<div style="display:flex;gap:8px;margin:10px 0;flex-wrap:wrap">
      <button class="btn-add-2" type="button" onclick="resumenEncargos=false; pinta();">◀ Volver a encargos</button>
      <button class="btn-add-2" type="button" onclick="diaResumen='${DIA}'; pinta();">hoy</button>
      <button class="btn-add-2" type="button" onclick="diaResumen='${manana}'; pinta();">mañana</button>
      <input type="date" value="${f}" onchange="diaResumen=this.value; pinta();" style="flex:0 1 160px">
    </div>`;

  html += `<div style="display:flex;gap:8px;margin:10px 0;flex-wrap:wrap">
      <button class="btn-add-2" type="button" onclick="mandarPedidoProveedor('Zuaza')"
        style="${lista.some(e => e.que === 'Zuaza') ? '' : 'opacity:.45'}">📲 Pedido a Zuaza (Patxi)</button>
      <button class="btn-add-2" type="button" onclick="mandarPedidoProveedor('Tahona')"
        style="${lista.some(e => e.que === 'Tahona') ? '' : 'opacity:.45'}">📲 Pedido a la Tahona (Jon)</button>
    </div>`;

  if(!lista.length){
    return html + `<div class="lista"><div class="item">
      <div class="cab-item"><span class="txt"><b>${bonito(f)}</b>
        <span class="n">sin encargos</span></span></div>
    </div></div>`;
  }

  html += `<div class="lista"><div class="item">
    <div class="cab-item"><span class="txt"><b>${bonito(f)}</b>
      <span class="n">${lista.length} ${lista.length === 1 ? "encargo" : "encargos"}</span>
    </span></div>`;

  for(const g of Object.keys(grupos).sort()){
    html += `<div style="padding:6px 0"><b style="font-size:12px">${g}</b>`;
    for(const e of grupos[g]){
      html += `<div style="padding:4px 0 4px 12px;font-size:13px">
        ${e.producto ? `<b>${e.cantidad || "?"}</b> ${e.producto}` : `${e.que}`}
        ${e.nota ? `<span class="n" style="display:block">${e.nota}</span>` : ""}
      </div>`;
    }
    html += `</div>`;
  }

  html += `</div></div>`;
  return html;
}

'''

t = t[:i] + NUEVO + t[j:]

# al entrar en encargos, el resumen vuelve a hoy
t = t.replace('if(calBloque === "encargos"){ formEncargo = false; encProveedor = ""; resumenEncargos = false; }',
              'if(calBloque === "encargos"){ formEncargo = false; encProveedor = ""; resumenEncargos = false; diaResumen = ""; }',
              1)
t = t.replace("  formEncargo = false; encProveedor = \"\"; resumenEncargos = false;\n  calBloque",
              "  formEncargo = false; encProveedor = \"\"; resumenEncargos = false; diaResumen = \"\";\n  calBloque",
              1)
t = t.replace('  formEncargo = false; encProveedor = ""; resumenEncargos = false;\n  /* cada vez',
              '  formEncargo = false; encProveedor = ""; resumenEncargos = false; diaResumen = "";\n  /* cada vez',
              1)

t = t.replace("v-2026-10-26-95", "v-2026-10-26-96", 1)

open(p, "w", encoding="utf-8").write(t)
print("  ok  el resumen, de un día")
