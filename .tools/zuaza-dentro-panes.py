"""Zuaza pasa a estar DENTRO de «Registro de panes», con dos botones."""
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


# 1 · los botones que separan Tahona de Zuaza
rep("let panCual = \"entrada\";",
    '''let panCual = "entrada";
let panVista = "tahona";   // dentro de «Registro de panes»: tahona o zuaza

/* los dos botones de arriba: Tahona y Zuaza */
function botonesPan(){
  const chulo = (q)=> panVista === q
    ? "font-weight:800;text-decoration:underline"
    : "opacity:.62";
  return `<div style="display:flex;gap:8px;margin:10px 0;flex-wrap:wrap">` +
    `<button class="btn-add-2" type="button" style="${chulo("tahona")}" ` +
    `onclick="verPanVista('tahona')">Tahona</button>` +
    `<button class="btn-add-2" type="button" style="${chulo("zuaza")}" ` +
    `onclick="verPanVista('zuaza')">Zuaza</button></div>`;
}

function verPanVista(k){
  panVista = (k === "zuaza") ? "zuaza" : "tahona";
  pinta();
  guardaVista();
}''',
    "los dos botones")

# 2 · el registro de panes: si toca Zuaza, va a Zuaza
rep("""function pintaPanes(){
  /* la tienda apunta la devolución; coordinación y la Jefa pueden con las dos */
  const esTienda = quien.puesto === "tienda";""",
    """function pintaPanes(){
  if(panVista === "zuaza"){ pintaZuaza(); return; }
  /* la tienda apunta la devolución; coordinación y la Jefa pueden con las dos */
  const esTienda = quien.puesto === "tienda";""",
    "la entrada a Zuaza")

rep("""  let html = "";
  if(!esTienda){
    const activo = (q)=> cual === q""",
    """  let html = botonesPan();
  if(!esTienda){
    const activo = (q)=> cual === q""",
    "los botones en la tahona")

# 3 · la pantalla de Zuaza, con los botones arriba
rep("""  let html = `<h2 class="bloque">Zuaza<small>${bonito(f)}</small></h2>`;""",
    """  let html = botonesPan() + `<h2 class="bloque">Zuaza<small>${bonito(f)}</small></h2>`;""",
    "los botones en Zuaza")

# 4 · y se quita la sección aparte
rep('    ["zuaza", "Zuaza", "🥖"],\n', '', "el botón suelto de coordinación")
rep('    ["zuaza", "Zuaza", "🥖"],\n', '', "el botón suelto de la Jefa")
rep('  if(tab === "zuaza"){ pintaZuaza(); return; }\n', '', "la ruta suelta")

rep("v-2026-10-26-82", "v-2026-10-26-83", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
