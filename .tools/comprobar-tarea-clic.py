"""Comprueba en la app publicada que la tarea extra se marca y se pasa."""
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"}
h = urllib.request.urlopen(urllib.request.Request(
    "https://app.supermalato.workers.dev/", headers=UA), timeout=25).read().decode("utf-8")

print("  version:", (re.search(r"v-\d{4}-\d{2}-\d{2}-\d+", h) or ["?"])[0])
print("  se marca con su propia orden:", "encargoHecho('" in h and 'onclick="encargoHecho' in h)
print("  el pasar, con su propia orden:", "onchange=\"if(this.value) moverEncargo" in h)
print("  la etiqueta de urgente:", "tag urgente" in h)
print("  la de para arreglar:", "PARA ARREGLAR" in h)
