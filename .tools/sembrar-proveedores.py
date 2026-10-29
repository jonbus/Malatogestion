"""Los proveedores de la propiedad, con sus contactos y teléfonos.

Los teléfonos se guardan en dígitos, para que el móvil pueda marcar directamente.
"""
import json
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")
TOKEN = __import__("os").environ.get("CLOUDFLARE_API_TOKEN", "")
CUENTA = __import__("os").environ.get("CLOUDFLARE_ACCOUNT_ID", "")
KV = "544a4e67fd9c4acaab5a0e7d2dcfbd35"
API = "https://api.cloudflare.com/client/v4"
CLAVE = "estado"


def tel(x):
    return "".join(c for c in x if c.isdigit())


def p(nombre, contactos, antes=None, cod=None):
    return {
        "n": nombre,
        "cod": cod,
        "antes": antes,
        "cs": [{"p": persona, "t": tel(numero)} for persona, numero in contactos],
    }


PROVEEDORES = [
    p("Cadagua", [("Oficina", "94 679 82 29"), ("Central", "91 484 20 79"),
                  ("Almudena (comercial)", "600 59 98 40")], antes="15:00", cod="231949"),
    p("Matutano / Arbixe", [("César (comercial)", "616 80 06 60")]),
    p("Nestlé (Ariza)", [("David (comercial)", "653 83 16 46")]),
    p("Dulcesol", [("Oficina", "94 671 31 52"), ("Alex (comercial)", "666 08 06 91")]),
    p("Campofrío", [("Central", "91 484 29 19"), ("Ane (comercial)", "677 40 67 95")]),
    p("Lantzarez", [("Oficina", "94 640 06 59"), ("Enrique (comercial)", "633 84 15 65")]),
    p("Tosfrit", [("Oficina", "94 452 06 06"), ("Benji (comercial)", "627 25 78 54")]),
    p("Danone", [("Central", "93 122 27 28")]),
    p("Caravan (colonias)", [("Juan (comercial)", "651 87 97 10")]),
    p("Compas", [("Oficina", "94 457 02 33")]),
    p("Hielos", [("Oficina", "659 82 56 54"), ("Oficina 2", "94 600 90 34")]),
    p("El Pozo", [("Manu (comercial)", "656 75 20 03")]),
    p("Digasa / Coaliment", [("Mikel (comercial)", "670 48 01 83"),
                             ("Jon (jefe de ventas)", "663 74 79 07"),
                             ("Luis (comercial)", "673 95 79 17")], antes="13:00"),
    p("Cofresa", [("Roser (comercial)", "663 46 92 17")]),
    p("Panamar", [("Oficina", "944 86 26 34"), ("Begoña", "620 74 67 80")],
      antes="16:00", cod="1200698"),
    p("Bikain", [("Aitor (comercial)", "617 88 97 55")]),
    p("Gonvador", [("Oficina", "94 452 25 99"), ("Juan (comercial)", "639 12 71 96")]),
    p("Rocarsa", [("Oficina", "941 54 64 74"), ("Comercial", "678 56 64 13")]),
    p("Uvesa", [("Oficina", "94 426 31 34"), ("Imanol (pedidos)", "628 54 89 67"),
                ("David (pedidos 2)", "646 21 14 56")]),
    p("Frutas Tito", [("Oficina", "944 48 54 20"), ("Oficina 2", "689 03 43 07")]),
    p("Vrizzo (Merkapack)", [("Oficina", "945 28 87 87"), ("Josu (comercial)", "689 44 65 46"),
                             ("Javier (jefe)", "659 17 26 50")]),
    p("Urki", [("Oficina", "94 648 08 66")]),
    p("Herci", [("Oficina", "944 12 09 43"), ("Oficina 2", "944 12 01 99"),
                ("Marta (comercial)", "646 62 95 54"),
                ("Tablet vacaciones", "687 08 58 27")]),
    p("Oilasko", [("Oficina", "94 452 11 85"), ("Sergio (repartidor)", "651 70 75 53")]),
    p("Etxeko Nafarroa", [("Sergio (repartidor)", "679 69 75 87")]),
    p("Argal", [("Aitor (comercial)", "629 52 64 72")]),
    p("Vizcaína Alimentación", [("Oficina", "94 471 01 77"),
                                ("Mikel (comercial)", "678 28 10 49")]),
    p("Serrano", [("Oficina", "94 672 97 90"), ("Rubi (comercial)", "646 96 83 64"),
                  ("Félix (comercial)", "699 48 90 31")]),
    p("Arrate Gestoría", [("Oficina (Marta)", "945 89 02 06"),
                          ("Jon (seguros)", "615 75 19 45"),
                          ("Ane (fiscal)", "615 75 19 43"),
                          ("Iñaki (laboral)", "635 74 33 88")]),
    p("Vascolac", [("Oficina", "94 452 33 00")]),
    p("Gozoki Etxea", [("Oficina", "94 471 12 04"), ("Oscar (comercial)", "688 66 20 14")]),
]


def cf(metodo, ruta, datos=None):
    h = {"Authorization": "Bearer " + TOKEN}
    if datos is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(API + ruta, data=datos, method=metodo, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            bruto = r.read()
            try:
                return r.status, json.loads(bruto)
            except Exception:
                return r.status, {"_bruto": bruto}
    except urllib.error.HTTPError as e:
        return e.code, {"_error": e.read().decode("utf-8", "replace")[:300]}


c, estado = cf("GET", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}")
if c != 200:
    print("  no se pudo leer:", estado)
    sys.exit(1)

estado["proveedores"] = PROVEEDORES

c, d = cf("PUT", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}",
          json.dumps(estado).encode())
print(f"  escribir -> HTTP {c}")
if c != 200:
    print("  ", d)
    sys.exit(1)

c, d = cf("GET", f"/accounts/{CUENTA}/storage/kv/namespaces/{KV}/values/{CLAVE}")
prov = d.get("proveedores") or []
print(f"\n  proveedores guardados: {len(prov)}")
print(f"  teléfonos en total: {sum(len(x['cs']) for x in prov)}")
print(f"  con hora límite: {sum(1 for x in prov if x['antes'])}")
print(f"  con código de cliente: {sum(1 for x in prov if x['cod'])}")
print("\n  los cinco primeros:")
for x in prov[:5]:
    cs = " · ".join(f"{c['p']}: {c['t']}" for c in x["cs"])
    print(f"    {x['n']}{' (antes de las ' + x['antes'] + ')' if x['antes'] else ''}")
    print(f"      {cs}")
print("\n  y lo vuestro intacto:")
print(f"    marcas {len(d.get('marcas') or {})} · encargos {len(d.get('encargos') or [])} · "
      f"cascadas {len(d.get('cascadas') or {})} · nombres {len(d.get('nombres') or [])}")
