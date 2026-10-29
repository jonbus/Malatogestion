"""El worker usa el mismo núcleo, sin copia."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"docs/nube/cloudflare/worker.js"
t = open(p, encoding="utf-8").read()
viejo = "import nucleo from './nucleo.js';"
nuevo = ("/* el MISMO nucleo que usan Netlify y el servidor local:\n"
         "   una sola copia, para que no se queden despistadas */\n"
         "import nucleo from '../netlify/functions/nucleo.js';")
if viejo not in t:
    print("  NO ENCONTRADO (¿ya está cambiado?)")
    print("  primera línea:", t.splitlines()[5] if len(t.splitlines()) > 5 else "")
    sys.exit(0)
open(p, "w", encoding="utf-8").write(t.replace(viejo, nuevo, 1))
print("  ok  el worker importa el núcleo de verdad")
