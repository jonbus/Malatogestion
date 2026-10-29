"""Por qué no sugiere: mira lo que hay en la memoria."""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"}
BASE = "https://app.supermalato.workers.dev"

est = json.loads(urllib.request.urlopen(urllib.request.Request(
    BASE + "/api/estado", headers=UA), timeout=20).read())
nombres = est.get("nombres") or []
print("  nombres guardados:", len(nombres))
print("  los últimos cinco:")
for n in nombres[-5:]:
    print("   ", n)
print("  ¿hay alguno con 'chorizo'?:",
      [n for n in nombres if "chorizo" in n.lower()])

cuerpo = json.dumps({"q": "chorizo"}).encode()
r = json.loads(urllib.request.urlopen(urllib.request.Request(
    BASE + "/api/sugerencias", data=cuerpo, method="POST",
    headers={**UA, "Content-Type": "application/json"}), timeout=20).read())
print("  sugerencias para 'chorizo':", r.get("sugerencias"))
