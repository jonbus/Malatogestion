"""Mira el encargo que se ha creado y por qué no avisa."""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"}
d = json.loads(urllib.request.urlopen(urllib.request.Request(
    "https://app.supermalato.workers.dev/api/estado", headers=UA), timeout=20).read())

print("  hoy:", d["dia"])
lista = d.get("encargosFecha") or []
print("  encargos guardados:", len(lista))
for e in lista:
    print(f"    id: {e.get('id')}")
    print(f"      qué: {e.get('que')}  ·  cliente: {e.get('cliente')}")
    print(f"      tipo: {e.get('tipo')}  desde: {e.get('desde')}  hasta: {e.get('hasta')}"
          f"  días: {e.get('dias')}")
    print(f"      antelación: {e.get('antelacion')}  lo pide: {e.get('quienPide')}")
    print(f"      pedidos: {e.get('pedidos')}   recibidos: {e.get('recibidos')}")
