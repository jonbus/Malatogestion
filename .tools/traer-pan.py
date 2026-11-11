"""Trae el pan de la nube al estado del Pi, sin tocar nada más."""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

BASE = r".tools"
pi = json.load(open(BASE + r"\estado-pi.json", encoding="utf-8"))
nube = json.load(open(BASE + r"\pan-nube.json", encoding="utf-8"))

estado = pi["estado"]
print("  claves del estado del Pi:", ", ".join(sorted(estado.keys())))

for campo in ("tahona", "zuaza"):
    antes = len(estado.get(campo) or {})
    estado.setdefault(campo, {})
    origen = nube.get(campo) or {}
    puestos = 0
    for dia, datos in origen.items():
        if dia not in estado[campo]:
            puestos += 1
        estado[campo][dia] = datos      # manda la nube, que es la que tiene lo nuevo
    print(f"  {campo}: {antes} dias en el Pi -> {len(estado[campo])} ahora ({puestos} nuevos)")

# sube la versión, para que se note que ha cambiado
try:
    estado["version"] = int(estado.get("version") or 0) + 1
except Exception:
    estado["version"] = 1
print("  version nueva:", estado["version"])

json.dump(pi, open(BASE + r"\estado-nuevo.json", "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))
print("  escrito estado-nuevo.json")
