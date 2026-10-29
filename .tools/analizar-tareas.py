"""Analiza el libro de tareas: estructura, duplicados y tamano del problema."""
import sys
from collections import defaultdict, Counter
from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")
wb = load_workbook(r".tools\tareas.xlsx", data_only=True)

# --- 1) comparar las dos hojas de personas de tienda
a, b = wb["1TareasDiariasMañanaTardeOperar"], wb["2TareasDiariasMañanaTardeOperar"]
dif = 0
for r in range(1, max(a.max_row, b.max_row) + 1):
    for c in range(1, 4):
        va, vb = a.cell(row=r, column=c).value, b.cell(row=r, column=c).value
        if (va or "") != (vb or ""):
            dif += 1
            if dif <= 8:
                print(f"  r{r}c{c}: hoja1={va!r}  hoja2={vb!r}")
print(f"\nCeldas distintas entre las dos hojas de personas de tienda: {dif}")
print(f"(filas: {a.max_row} y {b.max_row})\n")


def parsear(hoja, col_tarea=2, col_obs=3):
    """Devuelve {dia: [(tarea, obs)]} leyendo los bloques 'TAREAS ORDINARIAS <DIA>'."""
    ws = wb[hoja]
    dia = None
    salida = defaultdict(list)
    for r in range(1, ws.max_row + 1):
        v1 = ws.cell(row=r, column=1).value
        v2 = ws.cell(row=r, column=col_tarea).value
        v3 = ws.cell(row=r, column=col_obs).value if col_obs else None
        # La cabecera de dia puede estar en cualquier columna con 'TAREAS ORDINARIAS'
        for v in (v1, v2):
            if isinstance(v, str) and "ORDINARIAS" in v.upper():
                dia = v.strip().upper().replace("TAREAS ORDINARIAS", "").strip()
        if dia and isinstance(v2, str) and v2.strip() and "ORDINARIAS" not in v2.upper():
            t = v2.strip()
            if t.upper() in ("TAREAS", "√"):
                continue
            salida[dia].append((t, (str(v3).strip() if v3 else "")))
    return salida


print("=" * 76)
print("TAMANO DEL PROBLEMA")
print("=" * 76)
for hoja in ["1TareasDiariasMañanaTardeOperar", "Tareas Coordinadoras", "Tareas CocinaMañana"]:
    d = parsear(hoja, 2, 3 if hoja != "Tareas Coordinadoras" else None)
    total = sum(len(v) for v in d.values())
    distintas = len({t for v in d.values() for t, _ in v})
    print(f"\n{hoja}")
    print(f"   dias con tareas: {len(d)}  ·  lineas de tarea: {total}  ·  tareas distintas: {distintas}")
    for dia, lista in d.items():
        print(f"     {dia:<12} {len(lista):>3} tareas")

# --- tareas que mas se repiten
print("\n" + "=" * 76)
print("TAREAS QUE MAS SE REPITEN (hoja de personas de tienda)")
print("=" * 76)
d = parsear("1TareasDiariasMañanaTardeOperar", 2, 3)
c = Counter(t for v in d.values() for t, _ in v)
for tarea, n in c.most_common(12):
    print(f"  {n:>2} dias | {tarea[:88]}")
