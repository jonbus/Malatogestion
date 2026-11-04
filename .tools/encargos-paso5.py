"""Paso 5: mandar el pedido de mañana por WhatsApp, a cada proveedor.

Zuaza → Patxi · 635 73 99 26
Tahona → Jon  · 650 16 00 78

Solo lo de mañana, y con la cantidad delante.
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


FUNCION = r'''/* ------------------------------------------------ MANDAR EL PEDIDO DE MAÑANA
   Solo lo de mañana, a cada proveedor por su teléfono. */
const TELEFONOS_PROVEEDOR = {
  "Zuaza": "34635739926",
  "Tahona": "34650160078"
};

function diaDeManana(){
  const d = new Date(DIA + "T12:00:00");
  d.setDate(d.getDate() + 1);
  return d.toISOString().slice(0, 10);
}

function textoPedidoProveedor(prov){
  const f = diaDeManana();
  const lista = (encargosFecha || []).filter(e =>
    e.desde === f && e.producto && (e.que || "") === prov);
  if(!lista.length) return "";
  const SALTO = String.fromCharCode(10);
  const partes = ["Kaixo, tenemos encargado para mañana:", ""];
  for(const e of lista){
    let linea = (e.cantidad === "" || e.cantidad === null || e.cantidad === undefined
      ? "?" : e.cantidad) + " " + e.producto;
    if(e.nota) linea += " (" + e.nota + ")";
    partes.push(linea);
  }
  partes.push("", "Mila esker,", "Malato");
  return partes.join(SALTO);
}

function mandarPedidoProveedor(prov){
  const texto = textoPedidoProveedor(prov);
  if(!texto){
    ponerSync("error", "No hay nada de " + prov + " para mañana");
    return;
  }
  const tel = TELEFONOS_PROVEEDOR[prov];
  if(!tel){
    ponerSync("error", "No hay teléfono de " + prov);
    return;
  }
  window.open("https://wa.me/" + tel + "?text=" + encodeURIComponent(texto), "_blank");
}

'''

rep("function bloqueFormEncargo(){", FUNCION + "function bloqueFormEncargo(){", "las funciones del pedido")

# el botón dentro del resumen, uno por proveedor
rep('''  html += `<div style="display:flex;gap:8px;margin:10px 0;flex-wrap:wrap">
      <button class="btn-add-2" type="button" onclick="resumenEncargos=false; pinta();">◀ Volver a encargos</button>
    </div>`;''',
    '''  const manana = diaDeManana();
  const hayManana = (prov)=> (encargosFecha || []).some(e =>
    e.desde === manana && e.producto && (e.que || "") === prov);

  html += `<div style="display:flex;gap:8px;margin:10px 0;flex-wrap:wrap">
      <button class="btn-add-2" type="button" onclick="resumenEncargos=false; pinta();">◀ Volver a encargos</button>
      <button class="btn-add-2" type="button" onclick="mandarPedidoProveedor('Zuaza')"
        style="${hayManana("Zuaza") ? "" : "opacity:.45"}">📲 Pedido a Zuaza (Patxi)</button>
      <button class="btn-add-2" type="button" onclick="mandarPedidoProveedor('Tahona')"
        style="${hayManana("Tahona") ? "" : "opacity:.45"}">📲 Pedido a la Tahona (Jon)</button>
    </div>`;''',
    "los dos botones de mandar")

rep("v-2026-10-26-92", "v-2026-10-26-93", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
