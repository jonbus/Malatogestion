"""Comprueba el desplegable de sugerencias en la app publicada."""
import json
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"}
BASE = "https://app.supermalato.workers.dev"

h = urllib.request.urlopen(urllib.request.Request(BASE + "/", headers=UA), timeout=25).read().decode("utf-8")
js = h.split("<script>")[-1].split("</script>")[0]

print("  version:", (re.search(r"v-\d{4}-\d{2}-\d{2}-\d+", h) or ["?"])[0])
print("  el desplegable existe:", 'id="tarea-sug"' in h)
print("  escribe y pide sugerencias:", "alEscribirTarea(this.value)" in h)
print("  al elegir, rellena el campo:", "elegirSugerencia" in js)
print("  el estilo está:", ".sug-linea" in h)

i = js.find("function alEscribirTarea")
trozo = js[i:i + 420]
print("  NO repinta la pantalla:", "pinta()" not in trozo)
print("  espera a que dejes de escribir:", "setTimeout" in trozo)

cuerpo = json.dumps({"q": "cortar"}).encode()
r = json.loads(urllib.request.urlopen(urllib.request.Request(
    BASE + "/api/sugerencias", data=cuerpo, method="POST",
    headers={**UA, "Content-Type": "application/json"}), timeout=20).read())
print("\n  al escribir «cortar» ofrecería:")
for s in r["sugerencias"][:8]:
    print("    ·", s)
