"""Comparacion cuantitativa: dias con hueco de UNA sola persona, manana y tarde.

Fuente A: plantillas REALES de la tienda (PlantillasHorarios.xlsx).
Fuente B: calendario generado 2026 (calendario-2026.xlsx).
Separa manana (antes de las 15:00) de tarde, que es lo relevante.
"""
import re
import sys
from collections import defaultdict
from datetime import date
from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")
DIR_REAL = r"C:\Users\Usuario\Desktop\APP Malato Documentación\PlantillasHorarios.xlsx"
GEN = r"docs\calendario-2026\calendario-2026.xlsx"
DIAS = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
MESES = {m: i + 1 for i, m in enumerate(
    ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO",
     "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"])}
FESTIVOS = {(1, 1), (1, 6), (3, 19), (4, 2), (4, 3), (4, 6), (5, 1),
            (7, 25), (8, 15), (10, 12), (12, 8), (12, 25), (4, 28), (7, 22)}
RX = re.compile(r"(\d{1,2})(?:[:.,](\d{2}))?\s*-\s*(\d{1,2})(?:[:.,](\d{2}))?")


def tramos(t):
    out = []
    for a, b, c, d in RX.findall(t):
        ini = int(a) + (int(b) / 60 if b else 0)
        fin = int(c) + (int(d) / 60 if d else 0)
        if fin > ini:
            out.append((ini, fin))
    return out


def apertura(d):
    """Franjas de apertura segun tipo de dia y temporada."""
    inv = date(2026, 6, 1) <= d <= date(2026, 9, 15)
    finde = d.weekday() == 6 or (d.month, d.day) in FESTIVOS
    sab = d.weekday() == 5
    if finde:
        return [(10, 14.5), (17, 21)]
    if sab:
        return [(9, 14.5), (17.5, 21)] if inv else [(9, 14.5), (17, 21)]
    return [(9, 14.5), (17.5, 21)] if inv else [(8, 14.5), (17, 21)]


def huecos(gente, franjas):
    """Devuelve (hueco_por_la_manana, hueco_por_la_tarde) para un dia."""
    sm = st = False
    for ini, fin in franjas:
        h = ini
        while h < fin:
            n = sum(1 for tr in gente.values() if any(a <= h < b for a, b in tr))
            if n <= 1:
                if h < 15:
                    sm = True
                else:
                    st = True
            h += 0.5
    return sm, st


# Apertura de TEMPORADA NORMAL por indice de dia (0=lunes .. 6=domingo),
# que es la temporada de las plantillas reales.
APERTURA_IDX = {0: [(8, 14.5), (17, 21)], 1: [(8, 14.5), (17, 21)],
                2: [(8, 14.5), (17, 21)], 3: [(8, 14.5), (17, 21)],
                4: [(8, 14.5), (17, 21)], 5: [(9, 14.5), (17, 21)],
                6: [(10, 14.5), (17, 21)]}


# ---------------------------------------------------------------- REAL
wb = load_workbook(DIR_REAL, data_only=True)
real = defaultdict(lambda: defaultdict(list))
for hoja in ["Turnos Gerencia", "Turnos EncargadasIndividualSinC", "Turnos Tienda"]:
    ws = wb[hoja]
    semana = persona = None
    vistos = set()
    for fila in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=8):
        et, b1 = fila[0].value, str(fila[1].value or "").strip().upper()
        if b1 in DIAS:
            if et is not None:
                m = re.search(r"\d", str(et))
                if m:
                    semana = int(m.group())
            persona = None
            continue
        if et is not None:
            e = str(et).strip().upper()
            if re.match(r"^\d", e) or "SEMANA" in e:
                m = re.search(r"\d", e)
                if m:
                    semana = int(m.group())
                persona = None
                continue
            if re.match(r"^(GER|COORD ?1|COORD2|OP ?[123])$", e):
                persona = e
            else:
                persona = None
                continue
        if persona is None or semana is None:
            continue
        for idx, c in enumerate(fila[1:8]):
            t = str(c.value or "").strip()
            if not t or t.upper() in ("VAC", "LIBRE", "$$$"):
                continue
            # la plantilla se repite en bloques: se cuenta una sola vez
            if (semana, idx, persona) in vistos:
                continue
            tr = tramos(t)
            if tr:
                real[semana][idx if idx < 7 else idx].append((persona, tr))
                vistos.add((semana, idx, persona))

# ---------------------------------------------------------------- GENERADO
wb2 = load_workbook(GEN)
gen = defaultdict(lambda: defaultdict(list))
for hoja in wb2.sheetnames:
    partes = hoja.split("-")
    if len(partes) != 2 or partes[1] not in MESES:
        continue
    ws = wb2[hoja]
    dias = []
    for fila in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=9):
        a = fila[0].value
        if isinstance(a, str) and a.strip().upper().startswith("PERSONA"):
            dias = []
            for c in fila[1:8]:
                m = re.search(r"(\d{1,2})\s*$", str(c.value or ""))
                dias.append(int(m.group(1)) if m else None)
            continue
        if not isinstance(a, str) or a.strip() not in (
                "Gerencia", "COORD 1", "COORD 2", "OP 1", "OP 2", "OP 3"):
            continue
        for idx, celda in enumerate(fila[1:8]):
            if idx >= len(dias) or dias[idx] is None:
                continue
            t = str(celda.value or "").strip()
            if not t or t.upper() in ("VAC", "LIBRE"):
                continue
            tr = tramos(t)
            if tr:
                gen[date(2026, MESES[partes[1]], dias[idx])][a.strip()].extend(tr)

print("=" * 78)
print("HUECOS DE UNA SOLA PERSONA · real frente a generado")
print("=" * 78)

# Real: convertir a estructura comparable
real_map = {}
for sem, dias_ in real.items():
    for idx, lista in dias_.items():
        real_map[(sem, idx)] = {}
        for p, tr in lista:
            real_map[(sem, idx)].setdefault(p, []).extend(tr)
n_r = len(real_map)
hm_r = ht_r = 0
for (sem, idx), gente in real_map.items():
    sm, st = huecos(gente, APERTURA_IDX[idx])
    hm_r += sm
    ht_r += st

gen_map = {d: dict(v) for d, v in gen.items()}
n_g = 0
hm_g = ht_g = 0
for d, gente in gen_map.items():
    if date(2026, 6, 1) <= d <= date(2026, 9, 15):
        continue
    n_g += 1
    sm, st = huecos(gente, apertura(d))
    hm_g += sm
    ht_g += st

print(f"REAL (4 semanas = {n_r} dias)")
print(f"  dias con hueco de 1 persona por la MANANA: {hm_r}  ({100*hm_r/n_r:.0f} %)")
print(f"  dias con hueco de 1 persona por la TARDE:  {ht_r}  ({100*ht_r/n_r:.0f} %)")
print(f"\nGENERADO (365 dias)")
print(f"  dias con hueco de 1 persona por la MANANA: {hm_g}  ({100*hm_g/n_g:.0f} %)")
print(f"  dias con hueco de 1 persona por la TARDE:  {ht_g}  ({100*ht_g/n_g:.0f} %)")
print("\nConclusion: si el porcentaje del generado es similar al real, reproduce")
print("la practica de la tienda; si es mucho mayor, esta mas justo de gente.")


