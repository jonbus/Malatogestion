"""Compara la ocupacion simultanea de las plantillas REALES con la del calendario generado.

Pregunta a responder: los huecos de una sola persona por la manana,
¿los tiene tambien el horario real de la tienda o los ha creado el generador?
"""
import re
import sys
from collections import defaultdict
from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")
REAL = r"C:\Users\Usuario\Desktop\APP Malato Documentación\PlantillasHorarios.xlsx"
DIAS = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]


def tramos(t):
    """Admite los DOS formatos: '7-14,30' (plantillas reales) y '7:00-14:30' (generado)."""
    return [(int(a) + (int(b) / 60 if b else 0), int(c) + (int(d) / 60 if d else 0))
            for a, b, c, d in re.findall(
                r"(\d{1,2})(?:[:.,](\d{2}))?\s*-\s*(\d{1,2})(?:[:.,](\d{2}))?", t)]


def semana_idx(s):
    m = re.search(r"\d", str(s))
    return int(m.group()) if m else None


wb = load_workbook(REAL, data_only=True)
agenda = defaultdict(lambda: defaultdict(list))     # semana -> dia -> [(persona, tramos)]

for hoja in ["Turnos Gerencia", "Turnos EncargadasIndividualSinC", "Turnos Tienda"]:
    ws = wb[hoja]
    semana = None
    persona = None
    for fila in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=8):
        et = fila[0].value
        b1 = str(fila[1].value or "").strip().upper()

        if b1 in DIAS:                       # fila de cabecera de semana
            if et is not None:
                si = semana_idx(et)
                if si:
                    semana = si
            persona = None
            continue

        if et is not None:
            e = str(et).strip().upper()
            if re.match(r"^\d", e) or "SEMANA" in e:
                si = semana_idx(e)
                if si:
                    semana = si
                persona = None
                continue
            # OJO: la etiqueta de persona y sus turnos comparten fila.
            # Aqui NO se hace continue: hay que seguir leyendo la fila.
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
            tr = tramos(t)
            if tr:
                agenda[semana][idx].append((persona, tr))

print("=" * 78)
print("PLANTILLAS REALES · gente presente a la vez (temporada normal)")
print("=" * 78)
print("(solo las 4 semanas de la hoja de Gerencia; se marcan los huecos de 1 persona)\n")

for sem in sorted(agenda):
    print(f"SEMANA {sem}")
    for dia in range(7):
        gente = agenda[sem].get(dia, [])
        if not gente:
            continue
        # franjas de apertura de temporada normal
        aperturas = [(8, 14.5), (17, 21)] if dia < 5 else \
                    [(9, 14.5), (17, 21)] if dia == 5 else [(10, 14.5), (17, 21)]
        huecos = []
        for ini, fin in aperturas:
            h = ini
            while h < fin:
                n = sum(1 for _, tr in gente if any(a <= h < b for a, b in tr))
                if n <= 1:
                    huecos.append(int(h))
                h += 0.5
        marca = ""
        if huecos:
            h1, h2 = min(huecos), max(huecos)
            tramos_h = []
            ini = h1
            for x in range(h1, h2 + 2):
                if x not in huecos:
                    if x - 1 >= ini:
                        tramos_h.append(f"{ini:02d}:00-{x:02d}:00")
                    ini = x + 1
            marca = "   <-- SOLO 1 PERSONA en " + ", ".join(tramos_h)
        print(f"   {DIAS[dia]:<10} {len(gente)} personas{marca}")

print("\nDetalle de la semana 2 (la que antes se ha citado):")
for dia in range(7):
    gente = agenda[2].get(dia, [])
    if gente:
        print(f"   {DIAS[dia]:<10} " + " | ".join(f"{p}" for p, _ in gente))
