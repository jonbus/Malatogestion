"""Junta las DOS hojas de personas de tienda: la lista completa de tareas.

Las dos estan vigentes y se alternan, asi que la lista real es la UNION.
Informa de que tareas estan solo en una, solo en la otra, o en las dos.
"""
import sys
from collections import defaultdict
from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")
wb = load_workbook(r".tools\tareas.xlsx", data_only=True)
DIAS = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]


def parsear(hoja):
    """{dia: [(tarea, obs, turno)]} — el primer 'Fichar' abre la manana, el segundo la tarde."""
    ws = wb[hoja]
    dia = None
    turno = "M"
    fichados = 0
    salida = defaultdict(list)
    for r in range(1, ws.max_row + 1):
        v1 = ws.cell(row=r, column=1).value
        v2 = ws.cell(row=r, column=2).value
        v3 = ws.cell(row=r, column=3).value
        # La cabecera del dia viene en la columna A, no en la B.
        for v in (v1, v2):
            if isinstance(v, str) and "ORDINARIAS" in v.upper():
                dia = v.strip().upper().replace("TAREAS ORDINARIAS", "").strip()
                turno, fichados = "M", 0
        if isinstance(v1, str) and "ORDINARIAS" in v1.upper():
            continue
        if not isinstance(v2, str) or not v2.strip():
            continue
        t = v2.strip()
        if t.upper() in ("TAREAS", "\u221a") or t.startswith("*"):
            continue
        if t.upper() == "FICHAR":
            fichados += 1
            if fichados == 1:
                turno = "T"
            continue
        salida[dia].append((t, str(v3).strip() if v3 else "", turno))
    return salida


a = parsear("1TareasDiariasMañanaTardeOperar")
b = parsear("2TareasDiariasMañanaTardeOperar")

ta = {t for v in a.values() for t, _, _ in v}
tb = {t for v in b.values() for t, _, _ in v}
todas = ta | tb

print("=" * 78)
print("LAS DOS HOJAS DE TIENDAS, JUNTAS")
print("=" * 78)
print(f"  hoja 1: {len(ta)} tareas distintas")
print(f"  hoja 2: {len(tb)} tareas distintas")
print(f"  SOLO en la hoja 1: {len(ta - tb)}")
print(f"  SOLO en la hoja 2: {len(tb - ta)}")
print(f"  en las dos:        {len(ta & tb)}")
print(f"  UNION (la lista real): {len(todas)} tareas distintas")

print("\n--- Tareas que SOLO estan en una de las dos hojas ---")
for t in sorted(ta - tb, key=str.lower):
    print(f"  [solo hoja 1] {t}")
for t in sorted(tb - ta, key=str.lower):
    print(f"  [solo hoja 2] {t}")

# inventario de la union, con los dias y turnos en que aparece
print("\n" + "=" * 78)
print("INVENTARIO DE LA UNION")
print("=" * 78)
info = defaultdict(lambda: {"dias": set(), "turnos": set(), "obs": ""})
for fuente in (a, b):
    for dia, lista in fuente.items():
        if not dia:
            continue
        for t, obs, tu in lista:
            info[t]["dias"].add(dia[:3])
            info[t]["turnos"].add(tu)
            if obs and not info[t]["obs"]:
                info[t]["obs"] = obs
for t in sorted(info, key=lambda x: (-len(info[x]["dias"]), x.lower())):
    d = info[t]["dias"]
    turnos = "/".join(sorted(info[t]["turnos"]))
    obs = f"   [{info[t]['obs'][:44]}]" if info[t]["obs"] else ""
    print(f"  {len(d)}d {turnos:<3} | {t}{obs}")
print(f"\nTOTAL: {len(info)} tareas distintas en la lista unida")
