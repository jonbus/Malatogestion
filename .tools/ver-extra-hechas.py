"""Comprueba que las tareas extra hechas se quedan a la vista."""
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"}
h = urllib.request.urlopen(urllib.request.Request(
    "https://app.supermalato.workers.dev/", headers=UA), timeout=25).read().decode("utf-8")
js = h.split("<script>")[-1].split("</script>")[0]

print("  version:", (re.search(r"v-\d{4}-\d{2}-\d{2}-\d+", h) or ["?"])[0])
print("  las hechas no se esconden:", "las hechas NO se esconden" in js)
print("  cuenta las hechas:", "todas hechas" in js)
print("  la hecha va marcada:", "hecha" in js)
print("  clase .hecha definida:", ".hecha" in h)

i = js.find("function avisoExtras")
j = js.find("function pintaGerencia")
bloque = js[i:j]
print("\n  === el bloque de las extra ===")
for trozo in bloque.split("\n"):
    if "hecho" in trozo or "caja" in trozo or "pista" in trozo:
        print("   ", trozo.strip()[:110])
