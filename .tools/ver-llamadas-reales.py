"""Qué hay de las llamadas ahora mismo en la aplicación."""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"}
d = json.loads(urllib.request.urlopen(urllib.request.Request(
    "https://app.supermalato.workers.dev/api/estado", headers=UA), timeout=20).read())

print("  dia:", d["dia"])
lista = d.get("encargos") or []
print("  tareas extra:", len(lista))
for x in lista:
    print(f"    {x.get('f')} · puesto={x.get('p')} · turno={x.get('turno')} "
          f"· tipo={x.get('tipo')} · hecho={x.get('hecho')}")
    print(f"      «{x.get('t')}»")
    print(f"      tel={x.get('tel')} · motivo={x.get('motivo')} · antes={x.get('antesDe')}")
