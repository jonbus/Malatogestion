"""Mira las tareas extra guardadas y dónde deberían aparecer."""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"
req = urllib.request.Request("https://app.supermalato.workers.dev/api/estado",
                             headers={"User-Agent": UA})
d = json.loads(urllib.request.urlopen(req, timeout=25).read())

print("  hoy:", d["dia"])
enc = d.get("encargos") or []
print("  tareas extra guardadas:", len(enc))
for x in enc:
    print(f"    fecha={x.get('f')}  puesto={x.get('p')}  turno={x.get('turno')}  "
          f"{'HECHA' if x.get('hecho') else 'pendiente'}")
    print(f"      texto: {x.get('t')}")
    print(f"      la puso: {x.get('q')}   id={x.get('id')}")

print("\n  === dónde se vería cada una ===")
for x in enc:
    if x.get("hecho"):
        print(f"    «{x.get('t')[:40]}»: ya está hecha, no se muestra")
        continue
    donde = []
    if x.get("f") == d["dia"]:
        donde.append("hoy")
    elif x.get("f"):
        donde.append(f"el {x.get('f')} (hay que ir a ese día)")
    else:
        donde.append("sin día")
    p = x.get("p")
    t = x.get("turno")
    if p == "tienda":
        donde.append("pestaña " + ("Tarde" if t == "tarde" else "Mañana" if t == "manana" else "Mañana y Tarde"))
    elif p == "coordinacion":
        donde.append("pestaña El día")
    else:
        donde.append("pestaña General (la Jefa)")
    print(f"    «{str(x.get('t'))[:40]}» -> " + " · ".join(donde))
