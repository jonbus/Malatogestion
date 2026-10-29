"""Quien esta presente a cada hora, dia a dia, los primeros dias de enero."""
import re
import sys
from collections import defaultdict
from datetime import date, time
from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")
wb = load_workbook(r"docs\calendario-2026\calendario-2026.xlsx")
PERSONAS = ["Gerencia", "COORD 1", "COORD 2", "OP 1", "OP 2", "OP 3"]


def rangos(t):
    out = []
    for h1, m1, h2, m2 in re.findall(r"(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})", t):
        out.append((int(h1) + int(m1) / 60, int(h2) + int(m2) / 60))
    return out


ws = wb["01-ENERO"]
print("ENERO · turnos y ocupacion por hora (primeras dos semanas)\n")
dia_actual = []
for fila in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=9):
    a = fila[0].value
    if isinstance(a, str) and a.strip().upper().startswith("PERSONA"):
        dia_actual = []
        for c in fila[1:8]:
            m = re.search(r"(\d{1,2})\s*$", str(c.value or ""))
            dia_actual.append(int(m.group(1)) if m else None)
        continue
    if not isinstance(a, str) or a.strip() not in PERSONAS:
        continue
    for idx, celda in enumerate(fila[1:8]):
        if idx >= len(dia_actual) or dia_actual[idx] is None:
            continue
        d = dia_actual[idx]
        if d > 14:
            continue
        t = str(celda.value or "").strip()
        if not t or t.upper() in ("VAC", "LIBRE"):
            continue
        rs = rangos(t)
        if not rs:
            continue
        ocupacion = defaultdict(int)
        for a_, b_ in rs:
            h = int(a_)
            while h < b_:
                ocupacion[h] += 1
                h += 1
        horas = " ".join(f"{h:02d}h:{ocupacion[h]}" for h in range(6, 22) if ocupacion[h])
        print(f"  {d:>2} ene · {a.strip():<9} {t:<28} | {horas}")

print("\nResumen del 2 de enero (viernes):")
ws = wb["01-ENERO"]
for r in range(5, 12):
    v = ws.cell(row=r, column=3).value      # columna 'V 2'
    p = ws.cell(row=r, column=1).value
    if p:
        print(f"  {p:<9} {v}")
