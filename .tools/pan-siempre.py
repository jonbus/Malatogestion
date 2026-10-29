"""El informe del pan aparece siempre en la pantalla de la Jefa."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

viejo = """  if(diaMes > 5) return "";
  let a = Number(hoy.slice(0, 4)), m = Number(hoy.slice(5, 7)) - 1;
  if(m < 1){ m = 12; a--; }"""
nuevo = """  /* Del 1 al 5 se mira el mes anterior, para cotejar la factura.
     El resto del mes se mira el que se esta usando. Asi el informe del pan
     esta SIEMPRE en la pantalla de la Jefa. */
  let a = Number(hoy.slice(0, 4)), m = Number(hoy.slice(5, 7));
  if(diaMes <= 5){
    m = m - 1;
    if(m < 1){ m = 12; a--; }
  }"""

if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
open(p, "w", encoding="utf-8").write(t.replace(viejo, nuevo, 1))
print("  ok  el informe del pan aparece siempre")
