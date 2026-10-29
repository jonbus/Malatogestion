"""Cierre de horas del año 2026.

Calcula, persona a persona, las horas que salen de la rotación en el año
completo, descontando vacaciones y festivos, y las compara con el contrato.

TODOS LOS PARÁMETROS ESTÁN EN EL BLOQUE DE ABAJO. Si uno no cuadra con la
realidad, se cambia aquí y se vuelve a lanzar.
"""
import datetime
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ============================================================ PARÁMETROS
ANIO = 2026

# Los 15 festivos del año (el 25/12 y el 1/1 la tienda está cerrada)
FESTIVOS = {
    "2026-01-01", "2026-01-06", "2026-03-19", "2026-04-02", "2026-04-03",
    "2026-04-06", "2026-04-28", "2026-05-01", "2026-07-25", "2026-08-15",
    "2026-10-12", "2026-11-01", "2026-12-06", "2026-12-08", "2026-12-25",
}

# Horas de cada turno de tienda, por día
M_HORAS = 6.5      # mañana: 8:00-14:30
M_SABADO = 5.5     # sábado: 9:00-14:30
T_HORAS = 4.5      # tarde: 17:00-21:30
FD_LUNES = 4.5     # lunes tarde
FD_SABADO = 4.5    # sábado tarde
FD_DOMINGO = 6.5   # domingo entero (9:00-15:00) + tarde -> se ajusta abajo

# El domingo entero son dos tramos
DOMINGO_MANANA = 6.0     # 9:00-15:00
DOMINGO_TARDE = 4.5      # 17:00-21:30

# Contratos (horas al año), del convenio de 2024
CONTRATO = {
    "Tienda 1": 938.5,
    "Tienda 2": 938.5,
    "Tienda 3": 938.5,
    "Coordinadora 1": 1396.8,
    "Coordinadora 2": 938.5,
    "Oficina": 2034.0,
}

# Un mes de vacaciones para cada una (se puede cambiar la fecha)
VACACIONES = {
    "Tienda 1": ("2026-07-01", "2026-07-31"),
    "Tienda 2": ("2026-08-01", "2026-08-31"),
    "Tienda 3": ("2026-06-15", "2026-07-14"),
    "Coordinadora 1": ("2026-09-01", "2026-09-30"),
    "Coordinadora 2": ("2026-07-15", "2026-08-13"),
    "Oficina": ("2026-08-01", "2026-08-31"),
}

# ============================================================ CALENDARIO
INICIO = datetime.date(ANIO, 1, 1)
FIN = datetime.date(ANIO, 12, 31)


def dias():
    d = INICIO
    while d <= FIN:
        yield d
        d += datetime.timedelta(days=1)


def iso(d):
    return d.isoformat()


# El año 2026 empieza en jueves. Índice: lunes=0 ... domingo=6
def idx_semana(d):
    return d.weekday()


# ============================================================ LOS TURNOS DE TIENDA
# MAÑANA       : martes a sábado por la mañana
# TARDE        : lunes por la mañana + martes a viernes por la tarde
# FIN DE SEMANA: lunes tarde + sábado tarde + domingo entero

def horas_tienda(turno, d):
    w = idx_semana(d)
    if turno == "M":
        if 1 <= w <= 4:          # martes a viernes
            return M_HORAS
        if w == 5:               # sábado
            return M_SABADO
        return 0.0
    if turno == "T":
        if w == 0:               # lunes por la mañana
            return M_HORAS
        if 1 <= w <= 4:          # martes a viernes por la tarde
            return T_HORAS
        return 0.0
    if turno == "FD":
        if w == 0:
            return FD_LUNES
        if w == 5:
            return FD_SABADO
        if w == 6:
            return DOMINGO_MANANA + DOMINGO_TARDE
        return 0.0
    return 0.0


# Las tres personas rotan: cada 3 semanas cambian de turno
ROTACION = {"Tienda 1": "FD", "Tienda 2": "M", "Tienda 3": "T"}
SIGUIENTE = {"M": "T", "T": "FD", "FD": "M"}

# ============================================================ EL CICLO DE OFICINA
# 4 semanas. La semana 1 de oficina va con la semana 1 de coordinación.
# Se ancla el lunes 26/10/2026 como semana 1... pero para el año se cuenta
# desde el primer lunes del año.
CICLO_OFICINA = {
    1: {"L-V": 7.5, "sab": 0.0, "dom": 7.0},    # L-V 7:00-14:30, sábado libre, domingo 8:00-15:00
    2: {"L-V": 7.5, "sab": 0.0, "dom": 0.0},    # L-V
    3: {"L-V": 7.5, "sab": 0.0, "dom": 7.0},    # como la 1
    4: {"L-V": 7.5, "sab": 0.0, "dom": 0.0},    # L-J; viernes, sábado y domingo libres
}
# Ojo: la semana 4 tiene el viernes libre
CICLO_OFICINA[4]["viernes"] = 0.0


def horas_oficina(semana, d):
    w = idx_semana(d)
    p = CICLO_OFICINA[semana]
    if w == 6:
        return p["dom"]
    if w == 5:
        return p["sab"]
    if w == 4 and semana == 4:      # viernes de la semana 4: libre
        return 0.0
    return p["L-V"]


# ============================================================ EL CÁLCULO
def en_vacaciones(quien, d):
    if quien not in VACACIONES:
        return False
    a, b = VACACIONES[quien]
    return a <= iso(d) <= b


def calcular(poner_vacaciones=True):
    """Devuelve las horas de cada uno en el año."""
    totales = {"Tienda 1": 0.0, "Tienda 2": 0.0, "Tienda 3": 0.0, "Oficina": 0.0}
    dias_trabajados = {k: 0 for k in totales}

    # las 3 de tienda
    turnos = dict(ROTACION)
    semana_rotacion = 0
    lunes = None
    for d in dias():
        if d.weekday() == 0:                      # cada lunes empieza una semana
            if lunes is not None:
                semana_rotacion += 1
            lunes = d
            if semana_rotacion % 3 == 1:
                turnos = {k: SIGUIENTE[v] for k, v in turnos.items()}
        if iso(d) in FESTIVOS:
            continue
        for quien in ("Tienda 1", "Tienda 2", "Tienda 3"):
            if poner_vacaciones and en_vacaciones(quien, d):
                continue
            h = horas_tienda(turnos[quien], d)
            if h:
                totales[quien] += h
                dias_trabajados[quien] += 1

    # la oficina
    # se toma el primer lunes del año como semana 1
    lunes_anio = datetime.date(ANIO, 1, 1)
    while lunes_anio.weekday() != 0:
        lunes_anio += datetime.timedelta(days=1)
    for d in dias():
        if iso(d) in FESTIVOS:
            continue
        if poner_vacaciones and en_vacaciones("Oficina", d):
            continue
        semana = ((d - lunes_anio).days // 7) % 4 + 1
        h = horas_oficina(semana, d)
        if h:
            totales["Oficina"] += h
            dias_trabajados["Oficina"] += 1

    return totales, dias_trabajados


print("=" * 74)
print(f"  CIERRE DE HORAS {ANIO}")
print("=" * 74)

for etiqueta, con_vac in (("A) AÑO COMPLETO, sin vacaciones", False),
                          ("B) CON UN MES DE VACACIONES", True)):
    totales, dias_t = calcular(poner_vacaciones=con_vac)
    print(f"\n  {etiqueta}")
    print(f"  {'Persona':<16} {'días':>5} {'horas':>8} {'contrato':>10} {'diferencia':>12}")
    print("  " + "-" * 56)
    suma_dif = 0.0
    for quien in ("Tienda 1", "Tienda 2", "Tienda 3", "Oficina"):
        h = totales[quien]
        c = CONTRATO[quien]
        dif = h - c
        if quien != "Oficina":
            suma_dif += dif
        print(f"  {quien:<16} {dias_t[quien]:>5} {h:>8.1f} {c:>10.1f} {dif:>+12.1f}")
    print("  " + "-" * 56)
    print(f"  {'(tienda, suma)':<16} {'':>5} {'':>8} {'':>10} {suma_dif:>+12.1f}")

print()
print("  === cuántos días de trabajo salen al año ===")
totales, dias_t = calcular(True)
for quien in ("Tienda 1", "Oficina"):
    print(f"    {quien:<16} {dias_t[quien]:>5} días")
