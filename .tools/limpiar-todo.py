"""Deja el estado completamente limpio para empezar a rellenarlo hoy.

Guarda antes una copia de lo que había, por si hiciera falta.
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

FICHERO = Path("docs/nube/.datos/estado.json")

if FICHERO.exists():
    sello = datetime.now().strftime("%Y-%m-%d_%H%M")
    copia = FICHERO.with_name(f"estado-antes-de-limpiar-{sello}.json")
    shutil.copy2(FICHERO, copia)
    print(f"  copia guardada: {copia.name}")
    antes = json.loads(FICHERO.read_text(encoding="utf-8"))["estado"]
    print(f"  lo que había: {len(antes.get('marcas') or {})} marcas · "
          f"{len(antes.get('notas') or {})} notas · "
          f"{len(antes.get('encargos') or [])} tareas extra · "
          f"{len(antes.get('fichajes') or [])} fichajes")

limpio = {
    "estado": {
        "version": 0,
        "marcas": {},
        "fichajes": [],
        "traslados": {},
        "notas": {},
        "encargos": [],
        "recuentos": {},          # los recuentos del lunes
    }
}

FICHERO.write_text(json.dumps(limpio, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  estado limpio escrito en {FICHERO}")
print("  -> 0 marcas · 0 notas · 0 tareas extra · 0 fichajes · 0 recuentos")
