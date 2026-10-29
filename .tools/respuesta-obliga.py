"""Una llamada no se tacha sin respuesta: primero lo que dijeron."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

VIEJO = """async function encargoHecho(id, deshacer){
  ponerSync("trabajando", deshacer ? "Deshaciendo…" : "Marcando…");"""
NUEVO = """async function encargoHecho(id, deshacer){
  /* una llamada no se tacha sin apuntar lo que dijeron */
  if(!deshacer){
    const e = (encargos || []).find(x => String(x.id) === String(id));
    if(e && e.tipo === "llamada" && !String(e.respuesta || "").trim()){
      ponerSync("error", "Apunta primero la respuesta de la llamada");
      return;
    }
  }
  ponerSync("trabajando", deshacer ? "Deshaciendo…" : "Marcando…");"""

if VIEJO not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
t = t.replace(VIEJO, NUEVO, 1)
t = t.replace("v-2026-10-26-54", "v-2026-10-26-55")
open(p, "w", encoding="utf-8").write(t)
print("  ok  la llamada pide la respuesta antes de tacharse")
