"""Que coordinación pueda modificar también la devolución de la tahona.

Antes veía solo la entrada. Ahora tiene un selector Entrada / Devolución.
La tienda sigue igual: ve la devolución, y nada más.
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


# la variable de qué bloque se está viendo
rep("let tahona = {};      // el pan del panadero, por fecha",
    'let tahona = {};      // el pan del panadero, por fecha\nlet panCual = "entrada";   // qué bloque del pan se está viendo: entrada o devolución',
    "la variable del bloque")

# el selector y el bloque
rep("""function pintaPanes(){
  const cual = quien.puesto === "tienda" ? "devolucion" : "entrada";
  const c = document.getElementById("cuerpo");
  c.innerHTML = bloqueTahona(cual);""",
    """function pintaPanes(){
  /* la tienda apunta la devolución; coordinación y la Jefa pueden con las dos */
  const esTienda = quien.puesto === "tienda";
  const cual = esTienda ? "devolucion" : (panCual === "devolucion" ? "devolucion" : "entrada");
  const c = document.getElementById("cuerpo");

  let html = "";
  if(!esTienda){
    const activo = (q)=> cual === q
      ? "font-weight:800;text-decoration:underline"
      : "opacity:.65";
    html += `<div style="display:flex;gap:8px;margin:10px 0;flex-wrap:wrap">` +
      `<button class="btn-add-2" type="button" style="${activo("entrada")}" ` +
      `onclick="verPan('entrada')">Entrada del pan</button>` +
      `<button class="btn-add-2" type="button" style="${activo("devolucion")}" ` +
      `onclick="verPan('devolucion')">Devolución</button></div>`;
  }
  c.innerHTML = html + bloqueTahona(cual);""",
    "el selector y el bloque")

# la función que cambia de bloque
rep("async function guardarTahona(cual){",
    """function verPan(c){
  panCual = (c === "devolucion") ? "devolucion" : "entrada";
  pinta();
}

async function guardarTahona(cual){""",
    "verPan")

rep("v-2026-10-26-78", "v-2026-10-26-79", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
