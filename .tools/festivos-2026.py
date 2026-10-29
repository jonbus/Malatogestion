"""Festivos 2026: como cae cada uno y que pasa con el."""
import sys
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")
DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "DOMINGO"]

# Pascua 2026: domingo 5 de abril
MOVILES = {"Jueves Santo": date(2026, 4, 2),
           "Viernes Santo": date(2026, 4, 3),
           "Lunes de Pascua": date(2026, 4, 6)}

# Lista definitiva dictada por la propiedad
LISTA = [
    ("01/01", "Ano Nuevo", "CERRADA"),
    ("06/01", "Dia de Reyes", ""),
    ("19/03", "Dia del Padre", ""),
    ("", "Jueves Santo", ""),
    ("", "Viernes Santo", ""),
    ("", "Lunes de Pascua", ""),
    ("28/04", "San Prudencio", ""),
    ("01/05", "Dia del Trabajador", ""),
    ("25/07", "Dia de Santiago", ""),
    ("15/08", "Nuestra Senora", ""),
    ("12/10", "Dia de la Hispanidad", ""),
    ("01/11", "Todos los Santos", ""),
    ("06/12", "Dia de la Constitucion", ""),
    ("08/12", "La Inmaculada Concepcion", ""),
    ("25/12", "Navidad", "CERRADA"),
]

print("FESTIVOS 2026 · como cae cada uno y que pasa con el")
print("-" * 74)
abre = cerrada = domingo = 0
for f, nombre, est in LISTA:
    if not f:
        d = MOVILES[nombre]
    else:
        dd, mm = f.split("/")
        d = date(2026, int(mm), int(dd))
    wd = DIAS[d.weekday()]
    if est == "CERRADA":
        estado = "tienda CERRADA"
        cerrada += 1
    elif d.weekday() == 6:
        estado = "cae en DOMINGO (no genera trabajo aparte)"
        domingo += 1
    else:
        estado = "se trabaja 8:00-15:00 y 17:00-21:30"
        abre += 1
    print(f"  {d:%d/%m/%Y}  {wd:<9} {nombre:<26} {estado}")

print("-" * 74)
print(f"  fechas en la lista: {len(LISTA)}")
print(f"  cerrada: {cerrada} · se trabaja: {abre} · caen en domingo: {domingo}")
print(f"  festivos 'de calendario' (la lista menos los 2 cerrados): {len(LISTA) - cerrada}")
