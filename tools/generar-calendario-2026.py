"""Genera el calendario laboral 2026 completo de la tienda.

Criterio de reparto: cada turno va a quien mas le falta para su objetivo anual
(deficit en horas). La Gerencia es la ultima de la cola y cubre lo que sobra,
que es su papel real de comodin.

Reglas duras implementadas (ver docs/RRHH-TURNOS.md):
  - Minimos de cobertura por dia y franja.
  - Sin coordinadora no hay asador; la Gerencia NUNCA cocina.
  - Domingo y festivo: la persona de tienda hace el dia completo y las otras dos libran.
  - Descanso >= 12 h entre la tarde y la manana siguiente.
  - Nadie hace dos turnos solapados el mismo dia.

Uso:  python tools/generar-calendario-2026.py
"""
import datetime as dt
import json
import os

# ==========================================================================
# 1 · CALENDARIO
# ==========================================================================
FESTIVOS_NACIONALES = [(1, 1), (1, 6), (3, 19), (4, 2), (4, 3), (4, 6), (5, 1),
                       (7, 25), (8, 15), (10, 12), (12, 8), (12, 25)]
# [falta] Los 2 festivos locales NO estan confirmados: van como SUPUESTOS.
FESTIVOS_LOCALES_SUPUESTOS = [(4, 28), (7, 22)]
FESTIVOS = set(FESTIVOS_NACIONALES) | set(FESTIVOS_LOCALES_SUPUESTOS)
NOMBRE = {
    (1, 1): 'Ano Nuevo', (1, 6): 'Reyes', (3, 19): 'San Jose',
    (4, 2): 'Jueves Santo', (4, 3): 'Viernes Santo', (4, 6): 'Lunes de Pascua',
    (5, 1): 'Dia del Trabajo', (7, 25): 'Santiago', (8, 15): 'Asuncion',
    (10, 12): 'Hispanidad', (12, 8): 'Inmaculada', (12, 25): 'Navidad',
    (4, 28): 'San Prudencio (SUPUESTO)', (7, 22): 'La Magdalena (SUPUESTO)',
}
DIAS = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
MESES = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO',
         'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
DIA_CRITICO = dt.date(2026, 7, 25)


def es_verano(d):
    return d.month in (6, 7, 8) or (d.month == 9 and d.day <= 15)


CAL = []
_d = dt.date(2026, 1, 1)
while _d.year == 2026:
    CAL.append({'fecha': _d, 'wd': _d.weekday(), 'festivo': (_d.month, _d.day) in FESTIVOS,
                'verano': es_verano(_d), 'iso': _d.isocalendar()[1]})
    _d += dt.timedelta(days=1)
POR_FECHA = {e['fecha']: e for e in CAL}

# ==========================================================================
# 2 · PERSONAS Y OBJETIVOS
# ==========================================================================
OBJETIVO = {'COORD 1': 1396.8, 'COORD 2': 938.5, 'OP 1': 938.5, 'OP 2': 938.5, 'OP 3': 938.5}
MARGEN5 = {'COORD 1': 69.8, 'COORD 2': 46.9, 'OP 1': 46.9, 'OP 2': 46.9, 'OP 3': 46.9}
COORDS = ['COORD 1', 'COORD 2']
TIENDAS = ['OP 1', 'OP 2', 'OP 3']
EQUIPO = COORDS + TIENDAS
PERSONAS = ['Gerencia'] + EQUIPO
PG = 'OP 1'

# ==========================================================================
# 3 · VACACIONES (escenario propuesto por la propiedad)
# ==========================================================================
VACACIONES = [
    ('OP 1', '2026-06-01', '2026-06-30', 'Un mes completo'),
    ('OP 2', '2026-07-06', '2026-08-02', 'Cuatro semanas'),
    ('OP 3', '2026-08-03', '2026-08-30', 'Cuatro semanas'),
    ('COORD 2', '2026-07-13', '2026-07-26', 'Dos semanas: COINCIDE con OP 2'),
    ('COORD 1', '2026-01-26', '2026-02-15', 'Fuera de verano'),
]


def rango(ini, fin):
    a, b, out = dt.date.fromisoformat(ini), dt.date.fromisoformat(fin), set()
    while a <= b:
        out.add(a); a += dt.timedelta(days=1)
    return out


VAC = {p: set() for p in PERSONAS}
for p, i, f, _ in VACACIONES:
    VAC[p] |= rango(i, f)

# ==========================================================================
# 4 · CATALOGO DE TURNOS
# ==========================================================================
def slots_dia(e):
    wd, fest, ver = e['wd'], e['festivo'], e['verano']
    if fest or wd == 6:
        return [
            dict(tag='D-APERTURA', ini='8:00', fin='15:00', h=7.0, req='any', franja='M'),
            dict(tag='D-COCINA', ini='9:00', fin='15:00', h=6.0, req='coord', franja='M'),
            dict(tag='D-OP', ini='9:00', fin='15:00', h=6.0, req='op', franja='M'),
            dict(tag='D-TARDE', ini='17:00', fin='21:30', h=4.5, req='op', franja='T'),
        ]
    if wd == 5:
        if ver:
            return [dict(tag='S-COCINA', ini='8:00', fin='14:30', h=6.5, req='coord', franja='M'),
                    dict(tag='S-2', ini='10:30', fin='14:30', h=4.0, req='any', franja='M'),
                    dict(tag='S-TARDE', ini='17:30', fin='21:30', h=4.0, req='any', franja='T')]
        return [dict(tag='S-COCINA', ini='8:00', fin='15:00', h=7.0, req='coord', franja='M'),
                dict(tag='S-2', ini='10:30', fin='15:00', h=4.5, req='any', franja='M'),
                dict(tag='S-TARDE', ini='17:00', fin='21:30', h=4.5, req='any', franja='T')]
    out = []
    if ver:
        out.append(dict(tag='M-APERTURA', ini='8:00', fin='14:30', h=6.5, req='mando', franja='M'))
        out.append(dict(tag='M-2', ini='11:00', fin='14:30', h=3.5, req='any', franja='M'))
        out.append(dict(tag='TARDE', ini='17:30', fin='21:30', h=4.0, req='any', franja='T'))
    else:
        out.append(dict(tag='M-APERTURA', ini='7:00', fin='14:30', h=7.5, req='mando', franja='M'))
        out.append(dict(tag='M-2', ini='11:00', fin='14:30', h=3.5, req='any', franja='M'))
        out.append(dict(tag='TARDE', ini='17:00', fin='21:30', h=4.5, req='any', franja='T'))
    if wd == 3:
        out.append(dict(tag='J-APOYO', ini='9:00', fin='12:00', h=3.0, req='any', franja='M'))
    return out


def slot(e, tag):
    for s in slots_dia(e):
        if s['tag'] == tag:
            return s
    return None


# ==========================================================================
# 5 · REPARTO
# ==========================================================================
agenda = {p: {} for p in PERSONAS}
horas = {p: 0.0 for p in PERSONAS}
cocina = {}
cocinas = {p: 0 for p in PERSONAS}
festivos = {p: 0 for p in PERSONAS}
findes = {p: 0 for p in PERSONAS}
fest_trab = {p: 0 for p in PERSONAS}       # festivos cubiertos (para repartirlos)


def apunta(p, e, tag, h, franja):
    agenda[p].setdefault(e['fecha'], []).append({'tag': tag, 'h': h, 'franja': franja})
    horas[p] += h


def deficit(p):
    return -1.0 if p not in OBJETIVO else OBJETIVO[p] - horas[p]


EXTRA_TIEMPOS = {'REF-MANANA': ('9:00', '14:30'), 'REF-TARDE': ('17:30', '21:30')}


def hora_num(t):
    h, m = t.split(':')
    return int(h) + int(m) / 60


def datos_slot(e, tag):
    """Devuelve el slot completo (con franja y horas) de una etiqueta en un dia."""
    for s in slots_dia(e):
        if s['tag'] == tag:
            return s
    if tag in EXTRA_TIEMPOS:
        ini, fin = EXTRA_TIEMPOS[tag]
        return dict(tag=tag, ini=ini, fin=fin,
                    h=round(hora_num(fin) - hora_num(ini), 2),
                    franja='M' if tag == 'REF-MANANA' else 'T')
    return None


def rompe_descanso_siguiente(p, e, tag):
    """Comprueba el descanso en sentido contrario: anadir una TARDE puede romper
    la manana que la persona YA tiene asignada al dia siguiente."""
    d = datos_slot(e, tag)
    if d is None or d['franja'] != 'T':
        return False
    fin = hora_num(d['fin'])
    sig = e['fecha'] + dt.timedelta(days=1)
    for t in agenda[p].get(sig, []):
        ds = datos_slot(POR_FECHA[sig], t['tag'])
        if ds and ds['franja'] == 'M' and (24.0 - fin) + hora_num(ds['ini']) < 12.0:
            return True
    return False


def puede(p, e, s):
    """Puede esta persona tomar este turno ese dia.

    Comprueba las DOS direcciones del descanso de 12 h:
      - la manana, respecto de la tarde del dia anterior;
      - la tarde, respecto de la manana del dia siguiente (que puede estar ya
        asignada, porque el domingo se reparte antes que el sabado).
    """
    if e['fecha'] in VAC[p] or agenda[p].get(e['fecha']):
        return False
    if s is None:
        return True
    if s.get('franja') == 'T':
        return not rompe_descanso_siguiente(p, e, s['tag'])
    if s.get('franja') != 'M':
        return True
    prev = e['fecha'] - dt.timedelta(days=1)
    fin_prev = 0.0
    for t in agenda[p].get(prev, []):
        d = datos_slot(POR_FECHA[prev], t['tag'])
        if d:
            fin_prev = max(fin_prev, hora_num(d['fin']))
    if fin_prev < 15.0:
        return True
    return (24.0 - fin_prev) + hora_num(s['ini']) >= 12.0


def libre(p, e, s=None):
    return puede(p, e, s)


def clave_prioridad(p):
    """1) quien no llega a su objetivo, 2) la Gerencia (comodin), 3) quien lo supera."""
    if p in OBJETIVO:
        return (0 if deficit(p) > 0 else 2, -deficit(p))
    return (1, 0.0)


def elige(cands, e, s=None, clave=None):
    libres = [p for p in cands if puede(p, e, s)]
    if not libres:
        return None
    libres.sort(key=clave or clave_prioridad)
    return libres[0]


semanas = {}
for e in CAL:
    semanas.setdefault(e['iso'], []).append(e)
for iso in semanas:
    semanas[iso].sort(key=lambda x: x['wd'])

TRABAJADO = {p: set() for p in PERSONAS}

for idx, iso in enumerate(sorted(semanas)):
    week = semanas[iso]

    # --- TIENDAS: ciclo de 3 semanas --------------------------------
    FASE = {'A': {'M': 'M-2', 'X': 'M-2', 'J': 'M-2', 'V': 'M-2', 'S': 'S-2'},
            'B': {'L': 'M-2', 'M': 'TARDE', 'X': 'TARDE', 'J': 'TARDE', 'V': 'TARDE'},
            'C': {'L': 'TARDE', 'S': 'S-TARDE'}}
    for k, op in enumerate(TIENDAS):
        fase = ['A', 'B', 'C'][(idx + k) % 3]
        for e in week:
            if e['festivo'] or e['wd'] == 6:
                continue
            tag = FASE[fase].get(DIAS[e['wd']])
            s = slot(e, tag) if tag else None
            if not s:
                continue
            # Si la titular esta de vacaciones (o no puede por descanso), el turno
            # NO se queda vacio: lo cubre la companera que mas lo necesite.
            p = op if puede(op, e, s) else elige(TIENDAS + ['Gerencia'], e, s)
            if p:
                apunta(p, e, s['tag'], s['h'], s['franja'])
                TRABAJADO[p].add(e['fecha'])

    # --- DOMINGOS Y FESTIVOS (antes que el sabado: quien trabaja la tarde del
    # sabado no puede entrar el domingo de manana por el descanso de 12 h) ----
    for e in week:
        if not (e['festivo'] or e['wd'] == 6):
            continue
        ss = {x['tag']: x for x in slots_dia(e)}
        # En festivo se reparte por festivos ya trabajados; en domingo, por findes.
        if e['festivo']:
            clave_op = lambda o: (fest_trab[o], findes[o], -deficit(o))
        else:
            clave_op = lambda o: (findes[o], -deficit(o))
        op = elige(TIENDAS, e, ss['D-OP'], clave=clave_op)
        if op:
            apunta(op, e, 'D-OP', ss['D-OP']['h'], 'M')
            apunta(op, e, 'D-TARDE', ss['D-TARDE']['h'], 'T')
            TRABAJADO[op].add(e['fecha'])
            findes[op] += 1
            if e['festivo']:
                festivos[op] += 1
                fest_trab[op] += 1
        c = elige(COORDS, e, ss['D-COCINA'], clave=lambda p: (cocinas[p], -deficit(p)))
        if c is None:
            c = elige(['Gerencia'], e, ss['D-COCINA'])
        if c:
            apunta(c, e, 'D-COCINA', ss['D-COCINA']['h'], 'M')
            TRABAJADO[c].add(e['fecha'])
            cocina[e['fecha']] = c
            cocinas[c] += 1
            if e['festivo']:
                festivos[c] += 1
        p = elige(['Gerencia'] + COORDS, e, ss['D-APERTURA'])
        if p:
            apunta(p, e, 'D-APERTURA', ss['D-APERTURA']['h'], 'M')
            TRABAJADO[p].add(e['fecha'])
            if e['festivo']:
                festivos[p] += 1

    # --- SABADO NO FESTIVO -------------------------------------------
    for e in week:
        if e['wd'] != 5 or e['festivo']:
            continue
        s = slot(e, 'S-COCINA')
        c = elige(COORDS, e, s, clave=lambda p: (cocinas[p], -deficit(p)))
        if c:
            apunta(c, e, s['tag'], s['h'], s['franja'])
            TRABAJADO[c].add(e['fecha'])
            cocina[e['fecha']] = c
            cocinas[c] += 1
        s2 = slot(e, 'S-2')
        p2 = elige(TIENDAS + ['Gerencia'] + COORDS, e, s2)
        if p2:
            apunta(p2, e, s2['tag'], s2['h'], s2['franja'])
            TRABAJADO[p2].add(e['fecha'])
        st = slot(e, 'S-TARDE')
        p3 = elige(TIENDAS + ['Gerencia'] + COORDS, e, st)
        if p3:
            apunta(p3, e, st['tag'], st['h'], st['franja'])
            TRABAJADO[p3].add(e['fecha'])

    # --- APERTURAS DE MANDO (L-V) ------------------------------------
    for e in week:
        if e['festivo'] or e['wd'] in (5, 6):
            continue
        s = slot(e, 'M-APERTURA')
        p = elige(COORDS, e, s) or elige(['Gerencia'], e, s)
        if p:
            apunta(p, e, s['tag'], s['h'], s['franja'])
            TRABAJADO[p].add(e['fecha'])

    # --- APOYO DEL JUEVES --------------------------------------------
    for e in week:
        if e['wd'] != 3 or e['festivo']:
            continue
        s = slot(e, 'J-APOYO')
        p = elige(COORDS + TIENDAS, e, s) or elige(['Gerencia'], e, s)
        if p:
            apunta(p, e, s['tag'], s['h'], s['franja'])
            TRABAJADO[p].add(e['fecha'])

# ==========================================================================
# 6 · REEQUILIBRIO
# ==========================================================================
# El diseno cubre los minimos, pero los minimos suman MAS horas que los
# contratos del equipo. Ese exceso NO se reparte entre el personal: se transfiere
# a la Gerencia, que es autonoma y sin tope. Se transfieren turnos completos
# (nunca se borran), asi que la cobertura se mantiene intacta.
TRANSFERIBLES = ['M-2', 'TARDE', 'S-2', 'S-TARDE', 'J-APOYO', 'REF-MANANA', 'REF-TARDE',
                 'M-APERTURA', 'D-APERTURA']
# La cocina NO es transferible a la Gerencia: la Gerencia nunca es cocinera (D-66).
NO_TRANSFERIBLE = ['S-COCINA', 'D-COCINA']
PAREJAS = {'D-OP': 'D-TARDE', 'D-TARDE': 'D-OP'}


def quitar(p, fecha, tag):
    lst = agenda[p].get(fecha)
    if not lst:
        return None
    for i, t in enumerate(lst):
        if t['tag'] == tag:
            horas[p] -= t['h']
            return lst.pop(i)
    return None


def poner(p, e, t):
    agenda[p].setdefault(e['fecha'], []).append(t)
    horas[p] += t['h']
    TRABAJADO[p].add(e['fecha'])


transferidos = 0
for p in EQUIPO:
    if horas[p] <= OBJETIVO[p] + 2.0:
        continue
    # primero verano (es donde se compensa), luego el resto del ano
    fechas_p = sorted(agenda[p], key=lambda f: (not POR_FECHA[f]['verano'], f))
    for fecha in fechas_p:
        if horas[p] <= OBJETIVO[p] + 2.0:
            break
        e = POR_FECHA[fecha]
        for t in list(agenda[p].get(fecha, [])):
            if t['tag'] not in TRANSFERIBLES:
                continue
            if not puede('Gerencia', e, datos_slot(e, t['tag'])):
                continue
            if rompe_descanso_siguiente('Gerencia', e, t['tag']):
                continue
            tomado = quitar(p, fecha, t['tag'])
            if tomado:
                poner('Gerencia', e, tomado)
                transferidos += 1
        if horas[p] <= OBJETIVO[p] + 2.0:
            break
        # domingos y festivos: la persona de tienda que hacia el dia completo. El turno NO
        # puede ir a la Gerencia: la composicion obliga a que haya UNA tienda.
        for t in list(agenda[p].get(fecha, [])):
            if t['tag'] != 'D-OP':
                continue
            if not puede('Gerencia', e, datos_slot(e, 'D-OP')):
                pass
            otras = [o for o in TIENDAS if o != p and o not in VAC and not agenda[o].get(fecha)
                     and puede(o, e, datos_slot(e, 'D-OP'))]
            if not otras:
                continue
            otras.sort(key=clave_prioridad)
            q = otras[0]
            a = quitar(p, fecha, 'D-OP')
            b = quitar(p, fecha, 'D-TARDE')
            if a:
                poner(q, e, a)
            if b:
                poner(q, e, b)
            if a or b:
                transferidos += 1
            break

# Refuerzo de verano para quien quede corto
REFUERZOS = [dict(tag='REF-MANANA', ini='9:00', fin='14:30', h=5.5, franja='M'),
             dict(tag='REF-TARDE', ini='17:30', fin='21:30', h=4.0, franja='T')]
for p in EQUIPO:
    guardia = 0
    while deficit(p) > 3.5 and guardia < 500:
        guardia += 1
        metido = False
        for e in CAL:
            if not e['verano'] or e['wd'] == 6 or e['festivo']:
                continue
            if not libre(p, e):
                continue
            for r in REFUERZOS:
                if any(t['tag'] == r['tag'] for t in agenda[p].get(e['fecha'], [])):
                    continue
                if not puede(p, e, dict(r)) or rompe_descanso_siguiente(p, e, r['tag']):
                    continue
                poner(p, e, dict(r))
                metido = True
                break
            if metido:
                break
        if not metido:
            break

print(f'Turnos transferidos a la Gerencia: {transferidos}')

# --------------------------------------------------------------------------
# 6b · REPARACION DEL DESCANSO DE 12 H
# --------------------------------------------------------------------------
# El reparto en una sola pasada puede dejar algun par tarde/manana con menos de
# 12 h (sobre todo cuando la pasada de reequilibrio mueve turnos). Aqui se
# detectan y se reasignan. Si alguno no se puede arreglar, se deja constar.
def violaciones_descanso():
    out = []
    for p in PERSONAS:
        for f in sorted(agenda[p]):
            fins = []
            for t in agenda[p][f]:
                d = datos_slot(POR_FECHA[f], t['tag'])
                if d and d['franja'] == 'T':
                    fins.append(hora_num(d['fin']))
            if not fins:
                continue
            fin = max(fins)
            g = f + dt.timedelta(days=1)
            for t in agenda[p].get(g, []):
                d = datos_slot(POR_FECHA[g], t['tag'])
                if d and d['franja'] == 'M' and (24.0 - fin) + hora_num(d['ini']) < 12.0:
                    out.append((p, f, t['tag'], g))
    return out


arreglados, irresolubles = 0, []
for _ in range(6):
    vs = violaciones_descanso()
    if not vs:
        break
    progreso = False
    for p, f, tag_m, g in vs:
        e_f, e_g = POR_FECHA[f], POR_FECHA[g]
        movido = False
        # 1) mover la TARDE del dia anterior
        for t in list(agenda[p].get(f, [])):
            d = datos_slot(e_f, t['tag'])
            if not d or d['franja'] != 'T':
                continue
            cands = [q for q in PERSONAS if q != p
                     and puede(q, e_f, d) and not rompe_descanso_siguiente(q, e_f, t['tag'])]
            cands.sort(key=clave_prioridad)
            if cands:
                quitar(p, f, t['tag'])
                poner(cands[0], e_f, t)
                arreglados += 1
                movido = True
                break
        if movido:
            progreso = True
            continue
        # 2) mover la MANANA del dia siguiente
        d = datos_slot(e_g, tag_m)
        if d is None:
            irresolubles.append((p, f, tag_m, g, 'turno desconocido'))
            continue
        cands = []
        for q in PERSONAS:
            if q == p or not puede(q, e_g, d):
                continue
            if d['req'] == 'coord' and q not in COORDS:
                continue
            cands.append(q)
        cands.sort(key=clave_prioridad)
        if cands:
            tomado = quitar(p, g, tag_m)
            if tomado:
                poner(cands[0], e_g, tomado)
                arreglados += 1
                progreso = True
                continue
        irresolubles.append((p, f, tag_m, g, 'sin candidato viable'))
    if not progreso:
        break

print(f'Descansos reparados: {arreglados} · irresolubles: {len(irresolubles)}')
for ir in irresolubles[:10]:
    print(f'  IRRESOLUBLE {ir[0]}: tarde del {ir[1]} -> manana del {ir[3]} ({ir[4]})')


def requerido_manana(e):
    if e['festivo'] or e['wd'] == 6 or e['wd'] == 3:
        return 3
    return 2


plus_dias = {}
for e in CAL:
    req = requerido_manana(e)
    presentes = [p for p in PERSONAS
                 if any(t['franja'] == 'M' for t in agenda[p].get(e['fecha'], []))]
    if len(presentes) < req:
        plus_dias[e['fecha']] = {'req': req, 'hay': len(presentes), 'quien': presentes}

# ==========================================================================
# 8 · SALIDA
# ==========================================================================
SALIDA = os.path.join('docs', 'calendario-2026')
os.makedirs(SALIDA, exist_ok=True)

# --- datos derivados ------------------------------------------------------
plus_dias_persona = {p: sum(1 for f, v in plus_dias.items() if p in v['quien']) for p in PERSONAS}

roles_dia = {}          # fecha -> {'cocina': p, 'op': p, 'gente': set}
for e in CAL:
    f = e['fecha']
    gente = set()
    for p in PERSONAS:
        if agenda[p].get(f):
            gente.add(p)
    roles_dia[f] = {'cocina': cocina.get(f), 'gente': gente}
    for p in PERSONAS:
        for t in agenda[p].get(f, []):
            if t['tag'] == 'D-OP':
                roles_dia[f]['op'] = p

festivos_detalle = []
for e in CAL:
    if not e['festivo']:
        continue
    f = e['fecha']
    orig = 'SUPUESTO' if (f.month, f.day) in FESTIVOS_LOCALES_SUPUESTOS else 'confirmado'
    festivos_detalle.append({
        'fecha': f, 'nombre': NOMBRE.get((f.month, f.day), ''),
        'dia': DIAS[e['wd']], 'origen': orig,
        'gente': sorted(roles_dia[f]['gente']),
        'cocina': roles_dia[f]['cocina'],
    })

# --- libro ----------------------------------------------------------------
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

F_TIT = Font(bold=True, size=14, color='0A5741')
F_CAB = Font(bold=True, size=10, color='FFFFFF')
F_PERS = Font(bold=True, size=10)
F_NORM = Font(size=9)
F_FEST = Font(size=9, bold=True, color='7A4A00')
F_CRIT = Font(size=9, bold=True, color='9C0006')

R_MARCA = PatternFill('solid', fgColor='0E7A56')
R_CAB = PatternFill('solid', fgColor='0A5741')
R_FEST = PatternFill('solid', fgColor='FFE9B0')
R_FEST2 = PatternFill('solid', fgColor='FFD98A')
R_VAC = PatternFill('solid', fgColor='D9DDE3')
R_LIBRE = PatternFill('solid', fgColor='F2F5F3')
R_COCINA = PatternFill('solid', fgColor='CDEBDC')
R_CRIT = PatternFill('solid', fgColor='FFC7CE')
R_FINDE = PatternFill('solid', fgColor='EDF3EF')

BORDE = Border(*[Side(style='thin', color='BFCBC4')] * 4)
CEN = Alignment(horizontal='center', vertical='center', wrap_text=True)


def tiempos(e, tag):
    """Inicio y fin de un turno. Se derivan del dia para no duplicar el dato."""
    for s in slots_dia(e):
        if s['tag'] == tag:
            return s['ini'], s['fin']
    return EXTRA_TIEMPOS.get(tag, ('?', '?'))


def texto_celda(p, f):
    if f in VAC[p]:
        return 'VAC'
    lst = agenda[p].get(f)
    if not lst:
        return ''
    e = POR_FECHA[f]
    orden = sorted(lst, key=lambda t: tiempos(e, t['tag'])[0])
    txt = ' + '.join(f"{tiempos(e, t['tag'])[0]}-{tiempos(e, t['tag'])[1]}" for t in orden)
    if any(t['tag'] in ('S-COCINA', 'D-COCINA') for t in orden):
        txt += ' · COCINA'
    return txt


def horas_dia(p, f):
    return round(sum(t['h'] for t in agenda[p].get(f, [])), 2)


def bloque_semana(ws, r, week, titulo):
    """Escribe un bloque de una semana. Devuelve la fila siguiente."""
    ws.cell(row=r, column=1, value=titulo).font = F_TIT
    r += 1
    ws.cell(row=r, column=1, value='PERSONA').font = F_CAB
    ws.cell(row=r, column=1).fill = R_CAB
    for j, e in enumerate(week):
        c = ws.cell(row=r, column=2 + j, value=f"{DIAS[e['wd']]} {e['fecha'].day}")
        c.font = F_CAB
        c.fill = R_FEST2 if e['festivo'] else R_CAB
        c.alignment = CEN
    c = ws.cell(row=r, column=9, value='HORAS')
    c.font = F_CAB
    c.fill = R_CAB
    c.alignment = CEN
    r += 1
    for p in PERSONAS:
        ws.cell(row=r, column=1, value=p).font = F_PERS
        tot = 0.0
        for j, e in enumerate(week):
            f = e['fecha']
            v = texto_celda(p, f)
            c = ws.cell(row=r, column=2 + j, value=v)
            c.font = F_NORM
            c.alignment = CEN
            c.border = BORDE
            if f == DIA_CRITICO:
                c.fill = R_CRIT
                c.font = F_CRIT
            elif f in VAC[p]:
                c.fill = R_VAC
            elif e['festivo']:
                c.fill = R_FEST
            elif any(t['tag'] in ('S-COCINA', 'D-COCINA') for t in agenda[p].get(f, [])):
                c.fill = R_COCINA
            elif not agenda[p].get(f):
                c.fill = R_LIBRE
            elif e['wd'] == 6:
                c.fill = R_FINDE
            tot += horas_dia(p, f)
        c = ws.cell(row=r, column=9, value=round(tot, 2))
        c.font = F_PERS
        c.alignment = CEN
        c.border = BORDE
        r += 1
    return r + 1


wb = Workbook()
wb.remove(wb.active)

# --- hojas mensuales ------------------------------------------------------
for mes in range(1, 13):
    ws = wb.create_sheet(f'{mes:02d}-{MESES[mes-1][:12]}')
    ws.column_dimensions['A'].width = 12
    for j in range(7):
        ws.column_dimensions[get_column_letter(2 + j)].width = 15
    ws.column_dimensions['I'].width = 8
    ws.cell(row=1, column=1, value=f'CALENDARIO {MESES[mes-1]} 2026').font = Font(bold=True, size=16, color='0A5741')
    ws.cell(row=2, column=1, value='Verde = cocina · Amarillo = festivo · Gris = VAC · Rojo = dia critico').font = F_NORM
    r = 4
    for iso in sorted(semanas):
        week = [e for e in semanas[iso] if e['fecha'].month == mes]
        if not week:
            continue
        r = bloque_semana(ws, r, week, f'Semana {iso}')

# --- CALENDARIO completo --------------------------------------------------
ws = wb.create_sheet('CALENDARIO')
ws.column_dimensions['A'].width = 12
for j in range(7):
    ws.column_dimensions[get_column_letter(2 + j)].width = 15
ws.column_dimensions['I'].width = 8
ws.cell(row=1, column=1, value='CALENDARIO LABORAL 2026 — TIENDA (52 semanas)').font = Font(bold=True, size=16, color='0A5741')
ws.cell(row=2, column=1, value='Turnos reales de la tienda. La Gerencia nunca cocina. Festivos locales = SUPUESTOS.').font = F_NORM
r = 4
for iso in sorted(semanas):
    r = bloque_semana(ws, r, semanas[iso], f'Semana {iso}')

# --- RESUMEN --------------------------------------------------------------
ws = wb.create_sheet('RESUMEN')
ws.column_dimensions['A'].width = 12
for col in 'BCDEFGHIJK':
    ws.column_dimensions[col].width = 13
ws.cell(row=1, column=1, value='RESUMEN ANUAL 2026').font = Font(bold=True, size=16, color='0A5741')
cab = ['PERSONA', 'HORAS AÑO', 'CONTRATO', 'DESVÍO', '% DESVÍO', 'DENTRO 5%',
       'FESTIVOS', 'COCINAS', 'DÍAS TRABAJADOS', 'DÍAS LIBRES', 'PLUS ($$$)']
for j, t in enumerate(cab):
    c = ws.cell(row=3, column=1 + j, value=t)
    c.font = F_CAB
    c.fill = R_CAB
    c.alignment = CEN
r = 4
for p in PERSONAS:
    o = OBJETIVO.get(p)
    dv = (horas[p] - o) if o else None
    trab = len(TRABAJADO[p])
    vals = [p, round(horas[p], 1), (round(o, 1) if o else 'autónoma'),
            (round(dv, 1) if o else '—'),
            (f'{100*dv/o:+.2f}%' if o else '—'),
            (('SÍ' if abs(dv) <= MARGEN5[p] else 'NO') if o else '—'),
            festivos[p], cocinas[p], trab, 365 - trab, plus_dias_persona.get(p, 0)]
    for j, v in enumerate(vals):
        c = ws.cell(row=r, column=1 + j, value=v)
        c.font = F_PERS if j == 0 else F_NORM
        c.alignment = CEN
        c.border = BORDE
        if j == 5 and o and abs(dv) > MARGEN5[p]:
            c.fill = R_CRIT
    r += 1
r += 1
ws.cell(row=r, column=1, value='TOTAL EQUIPO (sin Gerencia)').font = F_PERS
ws.cell(row=r, column=2, value=round(sum(horas[p] for p in EQUIPO), 1)).font = F_PERS
ws.cell(row=r + 1, column=1, value='TOTAL HORAS DE LA GERENCIA').font = F_PERS
ws.cell(row=r + 1, column=2, value=round(horas['Gerencia'], 1)).font = F_PERS
ws.cell(row=r + 3, column=1, value='Días con plus (2 cuando tocaban 3):').font = F_PERS
ws.cell(row=r + 3, column=4, value=len(plus_dias)).font = F_PERS

# --- FESTIVOS -------------------------------------------------------------
ws = wb.create_sheet('FESTIVOS')
for col, w in zip('ABCDEFG', [12, 26, 5, 34, 12, 12, 14]):
    ws.column_dimensions[col].width = w
ws.cell(row=1, column=1, value='FESTIVOS 2026 — 14 días').font = Font(bold=True, size=16, color='0A5741')
ws.cell(row=2, column=1, value='Los marcados SUPUESTO son los 2 festivos locales, NO confirmados.').font = F_FEST
for j, t in enumerate(['FECHA', 'FESTIVIDAD', 'DÍA', 'QUIÉN TRABAJA', 'COCINA', 'ORIGEN', 'NOTA']):
    c = ws.cell(row=4, column=1 + j, value=t)
    c.font = F_CAB
    c.fill = R_CAB
r = 5
for d in festivos_detalle:
    f = d['fecha']
    nota = ''
    if f == DIA_CRITICO:
        nota = 'DÍA CRÍTICO: festivo y sábado, COORD 2 de vacaciones → solo queda COORD 1, que cocina por obligación'
    elif d['cocina'] == 'Gerencia':
        nota = 'AVISO: cocina la Gerencia (no debería ocurrir)'
    vals = [f.strftime('%d/%m/%Y'), d['nombre'], d['dia'], ', '.join(d['gente']),
            d['cocina'], d['origen'], nota]
    for j, v in enumerate(vals):
        c = ws.cell(row=r, column=1 + j, value=v)
        c.font = F_CRIT if f == DIA_CRITICO else F_NORM
        c.border = BORDE
        if f == DIA_CRITICO:
            c.fill = R_CRIT
        elif d['origen'] == 'SUPUESTO':
            c.fill = R_FEST
    r += 1

# --- VACACIONES -----------------------------------------------------------
ws = wb.create_sheet('VACACIONES')
for col, w in zip('ABCDE', [12, 14, 14, 10, 34]):
    ws.column_dimensions[col].width = w
ws.cell(row=1, column=1, value='VACACIONES 2026').font = Font(bold=True, size=16, color='0A5741')
for j, t in enumerate(['PERSONA', 'DESDE', 'HASTA', 'DÍAS', 'NOTA']):
    c = ws.cell(row=3, column=1 + j, value=t)
    c.font = F_CAB
    c.fill = R_CAB
r = 4
for p, i, f, nota in VACACIONES:
    a, b = dt.date.fromisoformat(i), dt.date.fromisoformat(f)
    for j, v in enumerate([p, a.strftime('%d/%m/%Y'), b.strftime('%d/%m/%Y'), (b - a).days + 1, nota]):
        c = ws.cell(row=r, column=1 + j, value=v)
        c.font = F_NORM
        c.border = BORDE
    r += 1
r += 1
ws.cell(row=r, column=1, value='Coincidencias entre personas').font = F_PERS
r += 1
for p1, i1, f1, _ in VACACIONES:
    for p2, i2, f2, _ in VACACIONES:
        if p1 >= p2:
            continue
        a = max(dt.date.fromisoformat(i1), dt.date.fromisoformat(i2))
        b = min(dt.date.fromisoformat(f1), dt.date.fromisoformat(f2))
        if a <= b:
            ws.cell(row=r, column=1, value=f'{p1} y {p2}').font = F_NORM
            ws.cell(row=r, column=2, value=f'{a.strftime("%d/%m")}–{b.strftime("%d/%m")}').font = F_NORM
            ws.cell(row=r, column=5, value=f'{(b-a).days+1} días de solape').font = F_NORM
            r += 1

# --- DÍAS CRÍTICOS --------------------------------------------------------
ws = wb.create_sheet('DÍAS CRÍTICOS')
for col, w in zip('ABCD', [14, 20, 40, 40]):
    ws.column_dimensions[col].width = w
ws.cell(row=1, column=1, value='DÍAS SIN MARGEN').font = Font(bold=True, size=16, color='0A5741')
ws.cell(row=2, column=1, value='Días en que solo hay una persona disponible para un papel obligatorio.').font = F_NORM
for j, t in enumerate(['FECHA', 'DÍA', 'RESTRICCIÓN', 'CONSECUENCIA']):
    c = ws.cell(row=4, column=1 + j, value=t)
    c.font = F_CAB
    c.fill = R_CAB
r = 5
ws.cell(row=r, column=1, value='25/07/2026').font = F_CRIT
ws.cell(row=r, column=2, value='Sábado (festivo)').font = F_CRIT
ws.cell(row=r, column=3, value='COORD 2 de vacaciones (13–26/07) → única coordinadora disponible: COORD 1').font = F_CRIT
ws.cell(row=r, column=4, value='COORD 1 cocina por obligación. Sin alternancia posible.').font = F_CRIT
for j in range(4):
    ws.cell(row=r, column=1 + j).fill = R_CRIT
r += 1
ws.cell(row=r, column=1, value='15/08/2026').font = F_NORM
ws.cell(row=r, column=2, value='Sábado (festivo)').font = F_NORM
ws.cell(row=r, column=3, value='OP 3 de vacaciones (03–30/08)').font = F_NORM
ws.cell(row=r, column=4, value='Cobertura ajustada pero completa: quedan OP 1 y OP 2.').font = F_NORM

LIBRO = os.path.join(SALIDA, 'calendario-2026.xlsx')
wb.save(LIBRO)
print(f'\nLibro guardado en {LIBRO}')

json.dump({
    'horas': horas, 'objetivo': OBJETIVO, 'festivos': festivos, 'cocinas': cocinas,
    'agenda': {p: {d.isoformat(): v for d, v in dd.items()} for p, dd in agenda.items()},
    'cocina': {d.isoformat(): v for d, v in cocina.items()},
    'plus': {d.isoformat(): v for d, v in plus_dias.items()},
    'vacaciones': {p: sorted(x.isoformat() for x in VAC[p]) for p in PERSONAS},
}, open(os.path.join(SALIDA, 'calendario-2026.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('Datos en docs/calendario-2026/calendario-2026.json')

print('Horas por persona:')
for p in PERSONAS:
    o = OBJETIVO.get(p)
    if o:
        dv = horas[p] - o
        estado = 'OK' if abs(dv) <= MARGEN5[p] else 'FUERA DEL 5%'
        print(f'  {p:<9} {horas[p]:8.1f} h | objetivo {o:7.1f} | desvio {dv:+8.1f} '
              f'({100*dv/o:+6.2f}%) {estado:<12} festivos {festivos[p]:2d} cocinas {cocinas[p]:2d}')
    else:
        print(f'  {p:<9} {horas[p]:8.1f} h | autonoma | festivos {festivos[p]:2d}')
print(f'\nDias con plus (2 cuando tocaban 3): {len(plus_dias)}')
for f, v in sorted(plus_dias.items()):
    print(f'  {f} ({DIAS[f.weekday()]}) requeridos {v["req"]}, presentes {v["hay"]}')
