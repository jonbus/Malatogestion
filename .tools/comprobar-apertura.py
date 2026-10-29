"""Comprueba los dos patrones embebidos en la pantalla de la apertura."""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
h = open("docs/momentos/apertura.html", encoding="utf-8").read()
d = json.loads(re.search(r"const P = (\{.*?\});\n", h, re.S).group(1))
for k, p in d.items():
    pasos = sum(len(b["pasos"]) for b in p["bloques"])
    print(f"  Patrón {k} · {p['nombre']}")
    print(f"    abre a las {p['abre']}")
    print(f"    bloques: {len(p['bloques'])}   pasos: {pasos}   hornadas: {len(p['hornadas'])}")
    for b in p["bloques"]:
        horno = f"  [al horno: {b['horno'][:52]}…]" if b.get("horno") else ""
        print(f"      {b['titulo']:<28} {len(b['pasos']):>2} pasos  ({b['ancla']}){horno}")
    for x in p["hornadas"]:
        print(f"        {x['n']}.ª {x['ini']}-{x['fin']}  {x['que'][:46]}"
              f"  detalle={len(x.get('detalle', []))} aclar={len(x.get('aclaraciones', []))}")
    print()
