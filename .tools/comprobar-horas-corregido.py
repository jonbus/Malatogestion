"""Comprueba el cálculo corregido de HORAS-ANUALES.md."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

VACACIONES = 30 / 7          # un mes, en semanas
FESTIVOS = 14 / 7            # los 14 festivos, en semanas
SEM = 52.14 - VACACIONES - FESTIVOS

print(f"  semanas del año:        52,14")
print(f"  menos vacaciones:       -{VACACIONES:.2f}   (30 días)")
print(f"  menos festivos:         -{FESTIVOS:.2f}    (14 días)")
print(f"  semanas que se trabaja:  {SEM:.2f}")
print()

PERSONAS = [
    ("Tienda 1", 20.33, 938.5),
    ("Tienda 2", 20.33, 938.5),
    ("Tienda 3", 20.33, 938.5),
    ("Coordinadora 1", 31.25, 1396.8),
    ("Coordinadora 2", 21.00, 938.5),
    ("Oficina", 39.125, 2034.0),
]

print(f"  {'Persona':<16}{'media':>8}{'al año':>10}{'contrato':>11}{'dif':>8}")
print("  " + "-" * 53)
for nombre, media, contrato in PERSONAS:
    horas = media * SEM
    print(f"  {nombre:<16}{media:>8.2f}{horas:>10.0f}{contrato:>11.1f}{horas-contrato:>+8.0f}")

print()
print("  === y lo que hay que cubrir en verano ===")
print(f"  una persona de tienda, un mes de vacaciones:")
print(f"    {SEM/11.29:.0f} semanas... no: son 4,29 semanas x 20,33 h")
print(f"    = {4.29 * 20.33:.0f} h que deja de trabajar")
print(f"  y esas horas las tiene que hacer otra")
print()
print("  === el yacimiento: días a 2 en vez de 3 ===")
print(f"  cada día de lunes a viernes en que se trabaje a 2 en vez de 3,")
print(f"  libera las horas de una persona ese día.")
print(f"  Para cubrir {4.29 * 20.33:.0f} h hacen falta {4.29 * 20.33 / 6.5:.0f} días asi.")
