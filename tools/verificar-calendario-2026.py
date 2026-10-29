"""Verifica el calendario 2026 LEYENDO EL EXCEL entregado.

No se fia de los datos intermedios: reconstruye la asignacion desde las celdas
del libro y comprueba las reglas duras una a una.

Uso:  python tools/verificar-calendario-2026.py
"""
import datetime as dt
import re
import sys
from collections import defaultdict

from openpyxl import load_workbook

LIBRO = 'docs/calendario-2026/calendario-2026.xlsx'
DIAS = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
FESTIVOS = {(1, 1), (1, 6), (3, 19), (4, 2), (4, 3), (4, 6), (5, 1),
            (7, 25), (8, 15), (10, 12), (12, 8), (12, 25),
            (4, 28), (7, 22)}          # los 2 ultimos son SUPUESTOS
LOCALES_SUPUESTOS = {(4, 28), (7, 22)}
OBJETIVO = {'COORD 1': 1396.8, 'COORD 2': 938.5, 'OP 1': 938.5, 'OP 2': 938.5, 'OP 3': 938.5}
MARGEN5 = {'COORD 1': 69.8, 'COORD 2': 46.9, 'OP 1': 46.9, 'OP 2': 46.9, 'OP 3': 46.9}
PERSONAS = ['Gerencia', 'COORD 1', 'COORD 2', 'OP 1', 'OP 2', 'OP 3']
COORDS = ['COORD 1', 'COORD 2']

fallos = []
avisos = []


def fallo(msg):
    fallos.append(msg)


def aviso(msg):
    avisos.append(msg)


# ---------------------------------------------------------------- lectura
wb = load_workbook(LIBRO, data_only=True)
if 'CALENDARIO' not in wb.sheetnames:
    print('FALLO: no existe la hoja CALENDARIO'); sys.exit(1)

ws = wb['CALENDARIO']
filas = list(ws.iter_rows(values_only=True))

agenda = defaultdict(dict)        # persona -> fecha -> [(ini, fin, horas, cocina)]
fechas_vistas = set()
cursor = dt.date(2026, 1, 1)

i = 0
while i < len(filas):
    fila = filas[i]
    if fila and str(fila[0]).strip() == 'PERSONA':
        cabs = [c for c in fila[1:8]]
        # reconstruir fechas a partir de "L 5"
        dias = []
        for c in cabs:
            if c is None or str(c).strip() == '':
                dias.append(None); continue
            m = re.match(r'^([LMXJVSD])\s+(\d{1,2})$', str(c).strip())
            dias.append((m.group(1), int(m.group(2))) if m else None)
        fechas = []
        cur = cursor
        for d in dias:
            if d is None:
                fechas.append(None); continue
            letra, num = d
            f = cur
            for _ in range(20):
                if f.day == num and DIAS[f.weekday()] == letra and f >= cursor:
                    break
                f += dt.timedelta(days=1)
            fechas.append(f)
            cur = f + dt.timedelta(days=1)
        validas = [f for f in fechas if f]
        if validas:
            cursor = max(validas) + dt.timedelta(days=1)
        # filas de personas
        for k in range(1, len(PERSONAS) + 1):
            pf = filas[i + k]
            if not pf or pf[0] not in PERSONAS:
                continue
            quien = pf[0]
            for j, f in enumerate(fechas):
                if f is None:
                    continue
                v = pf[1 + j] if 1 + j < len(pf) else None
                if v is None or str(v).strip() == '':
                    continue
                txt = str(v).strip()
                fechas_vistas.add(f)
                if txt == 'VAC':
                    agenda[quien].setdefault(f, [])
                    continue
                es_cocina = 'COCINA' in txt
                txt2 = txt.split('·')[0].strip()
                for tramo in txt2.split('+'):
                    m = re.match(r'^(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})$', tramo.strip())
                    if not m:
                        fallo(f'Celda ilegible en {quien} {f}: {v!r}')
                        continue
                    hi = int(m.group(1)) + int(m.group(2)) / 60
                    hf = int(m.group(3)) + int(m.group(4)) / 60
                    agenda[quien].setdefault(f, []).append((hi, hf, round(hf - hi, 2), es_cocina))
        i += len(PERSONAS) + 1
        continue
    i += 1

print(f'Celdas de turno reconstruidas: {sum(len(v) for v in agenda.values())}')
print(f'Dias con actividad: {len(fechas_vistas)}')

# ---------------------------------------------------------------- 1 COBERTURA
req_incumplidos = []
for f in sorted(fechas_vistas):
    wd = f.weekday()
    fest = (f.month, f.day) in FESTIVOS
    es_dom = wd == 6
    req_m = 3 if (fest or es_dom or wd == 3) else 2
    manana = [p for p in PERSONAS if any(t[0] < 15 for t in agenda[p].get(f, []))]
    tarde = [p for p in PERSONAS if any(t[0] >= 15 for t in agenda[p].get(f, []))]
    if len(manana) < req_m:
        req_incumplidos.append((f, 'manana', req_m, len(manana)))
    if len(tarde) < 1:
        req_incumplidos.append((f, 'tarde', 1, len(tarde)))

print(f'\n[1] COBERTURA')
print(f'  dias revisados: {len(fechas_vistas)}')
print(f'  incumplimientos de minimo: {len(req_incumplidos)}')
for f, fr, req, hay in req_incumplidos[:10]:
    print(f'    {f} ({DIAS[f.weekday()]}) {fr}: requeridos {req}, presentes {hay}')

# ---------------------------------------------------------------- 2 HORAS
horas = {p: round(sum(t[2] for d in agenda[p].values() for t in d), 2) for p in PERSONAS}
print(f'\n[2] HORAS ANUALES vs CONTRATO')
for p in PERSONAS:
    if p in OBJETIVO:
        o, dv = OBJETIVO[p], horas[p] - OBJETIVO[p]
        ok = abs(dv) <= MARGEN5[p]
        print(f'  {p:<9} {horas[p]:8.2f} h | contrato {o:7.1f} | desvio {dv:+8.2f} '
              f'({100*dv/o:+6.2f}%) | margen 5% {MARGEN5[p]:5.1f} | {"OK" if ok else "FUERA"}')
        if not ok:
            fallo(f'{p} fuera del 5%: desvio {dv:+.2f} h')
    else:
        print(f'  {p:<9} {horas[p]:8.2f} h | autonoma, sin tope')

# ---------------------------------------------------------------- 3 FESTIVOS
print(f'\n[3] FESTIVOS TRABAJADOS')
fest_p = {p: 0 for p in PERSONAS}
fest_dias = []
for f in sorted(fechas_vistas):
    if (f.month, f.day) not in FESTIVOS:
        continue
    quienes = [p for p in PERSONAS if agenda[p].get(f)]
    for p in quienes:
        fest_p[p] += 1
    fest_dias.append((f, quienes))
print(f'  festivos en el calendario: {len(fest_dias)} (14 esperados)')
for p in PERSONAS:
    print(f'    {p:<9} {fest_p[p]}')
# Composicion obligatoria de cada festivo y cada domingo:
# 3 personas y EXACTAMENTE una persona de tienda (las otras dos libran el dia entero).
comp_mal = []
ops_dias = 0
for f in sorted(fechas_vistas):
    wd, fest = f.weekday(), (f.month, f.day) in FESTIVOS
    if not (fest or wd == 6):
        continue
    manana = [p for p in PERSONAS if any(t[0] < 15 for t in agenda[p].get(f, []))]
    n_ops = len([p for p in manana if p.startswith('OP')])
    n_co = len([p for p in manana if p in COORDS])
    if n_ops != 1 or n_co < 1 or len(manana) != 3:
        comp_mal.append((f, manana, n_ops, n_co))
    ops_dias += n_ops
print(f'  dias de domingo+festivo revisados: {len(fechas_vistas) and sum(1 for f in fechas_vistas if f.weekday()==6 or (f.month,f.day) in FESTIVOS)}')
print(f'  dias con exactamente una persona de tienda (deben ser TODOS): '
      f'{sum(1 for f in fechas_vistas if (f.weekday()==6 or (f.month,f.day) in FESTIVOS) and len([p for p in PERSONAS if any(t[0]<15 for t in agenda[p].get(f,[])) and p.startswith("OP")])==1)}')
for f, m, no, nc in comp_mal[:12]:
    print(f'    COMPOSICION INCORRECTA {f} ({DIAS[f.weekday()]}): {m} '
          f'-> {no} tienda(s), {nc} coordinadora(s)')
if comp_mal:
    for f, m, no, nc in comp_mal:
        fallo(f'composicion de festivo/domingo {f}: {m} ({no} personas de tienda, {nc} coordinadoras)')
ops = [fest_p[o] for o in ['OP 1', 'OP 2', 'OP 3']]
if max(ops) - min(ops) > 1:
    aviso(f'reparto de festivos entre las personas de tienda desigual: {ops} (objetivo 4-5 cada una)')
for c in COORDS:
    if fest_p[c] < 5:
        aviso(f'{c} trabaja pocos festivos: {fest_p[c]}')

# ---------------------------------------------------------------- 4 COCINA
print(f'\n[4] COCINA')
cocinas = {p: 0 for p in PERSONAS}
dias_cocina = 0
mal_cocina = []
for f in sorted(fechas_vistas):
    wd, fest = f.weekday(), (f.month, f.day) in FESTIVOS
    debe = (wd == 5 or wd == 6 or fest)
    quienes = [p for p in PERSONAS if any(t[3] for t in agenda[p].get(f, []))]
    if debe:
        dias_cocina += 1
        if len(quienes) != 1:
            mal_cocina.append((f, f'esperada 1 cocinera, hay {len(quienes)}: {quienes}'))
        elif quienes[0] not in COORDS:
            mal_cocina.append((f, f'cocina {quienes[0]}: NO es coordinadora'))
        else:
            cocinas[quienes[0]] += 1
    elif quienes:
        mal_cocina.append((f, f'cocina en dia que no toca: {quienes}'))
print(f'  dias de asador esperados: {dias_cocina}')
for p in PERSONAS:
    if cocinas[p] or p in COORDS:
        print(f'    {p:<9} {cocinas[p]} cocinas')
print(f'  incidencias: {len(mal_cocina)}')
for f, m in mal_cocina[:10]:
    print(f'    {f}: {m}')
if mal_cocina:
    for f, m in mal_cocina:
        fallo(f'cocina {f}: {m}')
if abs(cocinas['COORD 1'] - cocinas['COORD 2']) > 4:
    aviso(f'rotacion de cocina desequilibrada: {cocinas["COORD 1"]} vs {cocinas["COORD 2"]}')

# ---------------------------------------------------------------- 5 SOLAPES Y DESCANSO
print(f'\n[5] SOLAPES Y DESCANSO (>= 12 h entre tarde y manana siguiente)')
solapes, descansos = [], []
for p in PERSONAS:
    for f, tramos in agenda[p].items():
        ts = sorted(tramos, key=lambda t: t[0])
        for a, b in zip(ts, ts[1:]):
            if b[0] < a[1] - 1e-9:
                solapes.append((p, f, a, b))
    for f in sorted(agenda[p]):
        tarde = [t for t in agenda[p][f] if t[0] >= 15]
        if not tarde:
            continue
        fin = max(t[1] for t in tarde)
        sig = f + dt.timedelta(days=1)
        for t in agenda[p].get(sig, []):
            if t[0] >= 15:
                continue
            descanso = (24 - fin) + t[0]
            if descanso < 12 - 1e-9:
                descansos.append((p, f, fin, sig, t[0], round(descanso, 2)))
print(f'  solapes: {len(solapes)}')
for s in solapes[:5]:
    print(f'    {s}')
print(f'  descansos < 12 h: {len(descansos)}')
for d in descansos[:10]:
    print(f'    {d[0]}: sale {d[2]:.2f} el {d[1]} y entra {d[4]:.2f} el {d[3]} -> {d[5]} h')
if solapes:
    fallo(f'{len(solapes)} solapes')
if descansos:
    fallo(f'{len(descansos)} descansos por debajo de 12 h')

# ---------------------------------------------------------------- 6 VACACIONES
print(f'\n[6] VACACIONES')
ws_v = wb['VACACIONES']
periodos = []
for fila in ws_v.iter_rows(values_only=True):
    if fila and fila[0] in PERSONAS and fila[1] and fila[2]:
        try:
            a = dt.datetime.strptime(str(fila[1]), '%d/%m/%Y').date()
            b = dt.datetime.strptime(str(fila[2]), '%d/%m/%Y').date()
            periodos.append((fila[0], a, b))
        except ValueError:
            continue
print(f'  periodos registrados: {len(periodos)}')
for p, a, b in periodos:
    print(f'    {p:<9} {a} -> {b} ({(b-a).days+1} dias)')
    # comprobar que el Excel marca VAC esos dias
    ws_mes = None
    for mes in range(1, 13):
        nom = f'{mes:02d}-'
        for s in wb.sheetnames:
            if s.startswith(nom):
                ws_mes = s
    faltan = [d for d in [(a + dt.timedelta(days=k)) for k in range((b - a).days + 1)]
              if d in agenda[p] and any(t for t in agenda[p][d])]
    if faltan:
        fallo(f'{p} con turnos asignados en dias de vacaciones: {faltan[:5]}')
concurrencia = {}
for p, a, b in periodos:
    d = a
    while d <= b:
        concurrencia.setdefault(d, []).append(p)
        d += dt.timedelta(days=1)
max_conc = max((len(v) for v in concurrencia.values()), default=0)
print(f'  maxima coincidencia simultanea: {max_conc}')
soles = [(d, v) for d, v in sorted(concurrencia.items()) if len(v) > 1]
if soles:
    ini = soles[0][0]; fin = ini; bloques = []
    for d, _ in soles[1:]:
        if (d - fin).days == 1:
            fin = d
        else:
            bloques.append((ini, fin)); ini = fin = d
    bloques.append((ini, fin))
    for a, b in bloques:
        dias = (b - a).days + 1
        quien = concurrencia[a]
        etiqueta = 'EXCEPCION PEDIDA' if dias > 7 else 'dentro del limite'
        print(f'  solape {a}->{b}: {dias} dias, {quien} [{etiqueta}]')
        if dias > 7:
            aviso(f'solape de {dias} dias entre {quien}: supera la regla de 1 semana '
                  f'(la propiedad lo pidio expresamente para ver el caso duro)')
if max_conc > 2:
    fallo(f'{max_conc} personas de vacaciones a la vez (maximo 2)')

# ---------------------------------------------------------------- 7 PLUS
print(f'\n[7] PLUS (trabajar de 2 cuando tocaban 3)')
plus = 0
for f in sorted(fechas_vistas):
    wd, fest = f.weekday(), (f.month, f.day) in FESTIVOS
    req = 3 if (fest or wd == 6 or wd == 3) else 2
    manana = [p for p in PERSONAS if any(t[0] < 15 for t in agenda[p].get(f, []))]
    if len(manana) < req:
        plus += 1
        print(f'  {f} ({DIAS[wd]}): requeridos {req}, presentes {len(manana)}')
print(f'  dias con plus: {plus}')

# ---------------------------------------------------------------- 8 DIA CRITICO
print(f'\n[8] DIA CRITICO 25/07/2026')
fc = dt.date(2026, 7, 25)
quienes = [p for p in PERSONAS if agenda[p].get(fc)]
coc = [p for p in PERSONAS if any(t[3] for t in agenda[p].get(fc, []))]
print(f'  trabajan: {quienes}')
print(f'  cocina: {coc}')
print(f'  COORD 2 de vacaciones ese dia: {"si" if any(p=="COORD 2" for p,a,b in periodos if a<=fc<=b) else "no"}')
if coc != ['COORD 1']:
    fallo(f'25/07: se esperaba que cocinara COORD 1 por obligacion, y cocina {coc}')
else:
    print('  correcto: cocina COORD 1 por obligacion (unica coordinadora disponible)')

# ---------------------------------------------------------------- RESUMEN
print('\n' + '=' * 74)
print(f'RESULTADO: {len(fallos)} fallo(s) duro(s), {len(avisos)} aviso(s)')
for f in fallos:
    print(f'  FALLO  {f}')
for a in avisos:
    print(f'  aviso  {a}')
print('=' * 74)
sys.exit(1 if fallos else 0)
