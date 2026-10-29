"""Diagnostica por qué no vuelven los recuentos y los partes."""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
U = "http://127.0.0.1:8100"


def pide(ruta, cuerpo=None):
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    h = {"Content-Type": "application/json"} if datos else {}
    req = urllib.request.Request(U + ruta, data=datos, headers=h,
                                 method="POST" if datos else "GET")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


print("  1) se guarda un recuento")
r = pide("/api/recuento", {"quien": "co1", "fecha": "2026-10-26",
                           "valores": {"pollos": 7, "codillos": 2, "patatas": 1, "bravas": 0}})
print("     respuesta.recuentos:", json.dumps(r.get("recuentos")))

print("\n  2) qué hay en el fichero")
d = json.load(open(r"docs/nube/.datos/estado.json", encoding="utf-8"))["estado"]
print("     claves:", list(d.keys()))
print("     recuentos en el fichero:", json.dumps(d.get("recuentos")))

print("\n  3) qué devuelve /api/estado")
e = pide("/api/estado")
print("     recuentos:", json.dumps(e.get("recuentos")))

print("\n  4) un encargo con partes")
c = pide("/api/encargo", {"quien": "co1", "t": "PRUEBA PARTES", "p": "gerencia",
                          "f": "2026-10-29", "clave": "prueba:partes",
                          "partes": ["uno", "dos"]})
enc = [x for x in (c.get("encargos") or []) if x.get("clave") == "prueba:partes"]
print("     partes guardados:", json.dumps(enc[0].get("partes") if enc else None))
for x in (c.get("encargos") or []):
    if x.get("clave") == "prueba:partes":
        pide("/api/encargo-borrar", {"id": x["id"]})
        print("     (borrado)")
