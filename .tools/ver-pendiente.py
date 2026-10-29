"""Mira qué hay pendiente y de qué fechas, antes de borrar nada."""
import json
import sys
import urllib.request
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"
req = urllib.request.Request("https://app.supermalato.workers.dev/api/estado",
                             headers={"User-Agent": UA})
d = json.loads(urllib.request.urlopen(req, timeout=25).read())

print("  hoy:", d["dia"])
print()

print("  === marcas por día ===")
dias = Counter(k.split("|")[0] for k in d["marcas"])
for f in sorted(dias):
    print(f"    {f}  {dias[f]} marcas" + ("   (hoy)" if f == d["dia"] else "   (anterior)"))

print("\n  === notas ===")
for f in sorted(d.get("notas") or {}):
    print(f"    {f}: {len(d['notas'][f])}")

print("\n  === tareas extra ===")
for x in d.get("encargos") or []:
    print(f"    {x.get('f')}  {x.get('p'):<13} {str(x.get('t'))[:50]}  "
          f"{'hecha' if x.get('hecho') else 'PENDIENTE'}")

print("\n  === recuentos ===")
for f, v in sorted((d.get("recuentos") or {}).items()):
    print(f"    {f}: {json.dumps(v)}")

print("\n  === traslados ===")
print("   ", json.dumps(d.get("traslados") or {}))
