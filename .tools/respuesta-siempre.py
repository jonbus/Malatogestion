"""La respuesta de la llamada sale siempre, no solo después de llamar."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

viejo = "          (e.llamadoEn || e.respuesta\n"
nuevo = "          (true\n"

if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
t = t.replace(viejo, nuevo, 1)
t = t.replace("v-2026-10-26-53", "v-2026-10-26-54")
open(p, "w", encoding="utf-8").write(t)
print("  ok  la respuesta sale siempre")
