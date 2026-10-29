"""Ocupacion SIMULTANEA minima por dia: cuanta gente hay a la vez en cada hora.

Es la comprobacion que faltaba: no cuantos turnos de manana hay, sino cuanta
gente hay presente al mismo tiempo mientras la tienda esta abierta.
"""
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")
wb = load_workbook(r"docs\calendario-2026\calendario-2026.xlsx")
PERSONAS = ["Gerencia", "COORD 1", "COORD 2", "OP 1", "OP 2", "OP 3"]
MESES = {m: i + 1 for i, m in enumerate(
    ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO",
     "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"])}
FESTIVOS = {(1, 1), (1, 6), (3, 19), (4, 2), (4, 3), (4, 6), (5, 1),
            (7, 25), (8, 15), (10, 12), (12, 8), (12, 25), (4, 28), (7, 22)}


def tramos(t):
    return [(int(a) + int(b) / 60, int(c) + int(d) / 60)
            for a, b, c, d in re.findall(r"(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})", t)]


agenda = defaultdict(dict)      # fecha -> {persona: [tramos]}
for hoja in wb.sheetnames:
    partes = hoja.split("-")
    if len(partes) != 2 or partes[1] not in MESES:
        continue
    mes = MESES[partes[1]]
    ws = wb[hoja]
    dias = []
    for fila in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=9):
        a = fila[0].value
        if isinstance(a, str) and a.strip().upper().startswith("PERSONA"):
            dias = [int(re.search(r"(\d{1,2})\s*$", str(c.value or "")).group(1))
                    if re.search(r"(\d{1,2})\s*$", str(c.value or "")) else None
                    for c in fila[1:8]]
            continue
        if not isinstance(a, str) or a.strip() not in PERSONAS:
            continue
        for idx, celda in enumerate(fila[1:8]):
            if idx >= len(dias) or dias[idx] is None:
                continue
            t = str(celda.value or "").strip()
            if not t or t.upper() in ("VAC", "LIBRE"):
                continue
            tr = tramos(t)
            if tr:
                agenda[date(2026, mes, dias[idx])][a.strip()] = tr

print("=" * 76)
print("OCUPACION SIMULTANEA · cuanta gente hay a la vez, hora a hora")
print("=" * 76)

dias_una_persona = []
por_franja = defaultdict(int)
for f in sorted(agenda):
    inv = date(2026, 6, 1) <= f <= date(2026, 9, 15)
    finde = f.weekday() == 6 or (f.month, f.day) in FESTIVOS
    sab = f.weekday() == 5 and (f.month, f.day) not in FESTIVOS
    if finde:
        abierto = [(10, 14.5), (17, 21)]
    elif sab:
        abierto = [(9, 14.5), (17.5 if inv else 17, 21)] if not inv else [(9, 14.5), (17.5, 21)]
    else:
        abierto = [(9, 14.5), (17.5, 21)] if inv else [(8, 14.5), (17, 21)]
    ocupacion = []
    for ini, fin in abierto:
        h = ini
        while h < fin:
            n = sum(1 for tr in agenda[f].values() if any(a <= h < b for a, b in tr))
            ocupacion.append((h, n))
            h += 0.5
    minimo = min(n for _, n in ocupacion)
    horas_solas = [h for h, n in ocupacion if n <= 1]
    if minimo <= 1:
        dias_una_persona.append((f, horas_solas))
        franja = f"{int(min(horas_solas)):02d}:00-{int(max(horas_solas)) + 1:02d}:00"
        por_franja[franja] += 1

print(f"dias con turno asignado: {len(agenda)}")
print(f"dias en que la tienda esta abierta con UNA sola persona en algun momento: "
      f"{len(dias_una_persona)}")
print(f"  ({100 * len(dias_una_persona) / len(agenda):.0f} % de los dias del ano)")
print("\nFranjas horarias afectadas (cuantas veces):")
for fr, n in sorted(por_franja.items(), key=lambda x: -x[1]):
    print(f"  {fr}  ->  {n} dias")

print("\nPrimeros 12 casos:")
for f, hs in dias_una_persona[:12]:
    quien = ", ".join(sorted(agenda[f]))
    print(f"  {f} ({'LMXJVSD'[f.weekday()]})  solo en "
          f"{int(min(hs)):02d}:00-{int(max(hs)) + 1:02d}:00  |  ese dia trabajan: {quien}")

# Cuantos dias cumplen de verdad el minimo de 2 simultaneas en manana
cumple2 = sum(1 for f in agenda if min(
    n for h, n in [(h, sum(1 for tr in agenda[f].values() if any(a <= h < b for a, b in tr)))
                   for h in [x / 2 for x in range(14, 29)]]) >= 2)
print(f"\ndias con al menos 2 personas simultaneas toda la manana: {cumple2} de {len(agenda)}")
