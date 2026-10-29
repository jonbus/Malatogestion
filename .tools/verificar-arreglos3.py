"""Comprueba en la app publicada los tres arreglos."""
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"}
h = urllib.request.urlopen(urllib.request.Request(
    "https://app.supermalato.workers.dev/", headers=UA), timeout=25).read().decode("utf-8")
js = h.split("<script>")[-1].split("</script>")[0]

print("  version:", (re.search(r"v-\d{4}-\d{2}-\d{2}-\d+", h) or ["?"])[0])
print("  se puede destachar:", "deshacer: !!deshacer" in js)
print("  dice como destacharla:", "toca para destacharla" in js)
print("  el pan dice a que hora:", "guardado a las" in js)
print("  el texto de arreglar:", "como una tarea más" in js)
print("  ya no dice «lo ve coordinación»:", "Lo verá coordinación" not in js)
