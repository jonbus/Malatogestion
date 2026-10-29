"""Busca el ciclo base (temporada normal) de coordinación en los Excel originales."""
import sys

from openpyxl import load_workbook

sys.stdout.reconfigure(encoding="utf-8")

RUTAS = [
    r"C:\Users\Usuario\Desktop\APP Malato Documentación\EjemploHorariosVacacionesVerano2026.xlsx",
    r"docs\referencia\horarios-verano-2026-anonimizado.xlsx",
]

for ruta in RUTAS:
    print(f"\n=== {ruta} ===")
    try:
        wb = load_workbook(ruta, data_only=True)
    except Exception as e:
        print(f"  no se pudo abrir: {e}")
        continue
    print(f"  hojas: {wb.sheetnames}")
    for nombre in wb.sheetnames:
        ws = wb[nombre]
        filas = sum(1 for _ in ws.iter_rows(values_only=True))
        print(f"    {nombre:<26} filas={ws.max_row:<5} columnas={ws.max_column:<4}")
