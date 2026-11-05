"""Limpia los carteles viejos: se quedan solo los buenos."""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

CARPETAS = [
    r"C:\Users\Usuario\Desktop\APP Malato",
    r"C:\Users\Usuario\Desktop\APP Malato Documentación",
    r"C:\Users\Usuario\Desktop",
]

# lo viejo, superado por los nuevos
VIEJOS = [
    "CARTEL-URNA.pdf", "CARTEL-URNA.jpg",
    "CARTEL-PREMIOS.pdf", "CARTEL-PREMIOS.jpg",
    "CARTEL-INVITACION.pdf",
    "KARTEL-URTEURRENA.jpg",
    "CARTEL-ANIVERSARIO-EUSKERA.pdf",
    "CARTEL-ANIVERSARIO-EUSKERA.jpg",
    "CARTEL-ANIVERSARIO-EUSKERA-whatsapp.jpg",
]

borrados = []
for carpeta in CARPETAS:
    for nombre in VIEJOS:
        ruta = os.path.join(carpeta, nombre)
        if os.path.exists(ruta):
            os.remove(ruta)
            borrados.append(ruta)
            print("  borrado: " + ruta)

print(f"\n  total borrados: {len(borrados)}")

# lo que se queda
print("\n  === lo que se queda ===")
for nombre in sorted(os.listdir(CARPETAS[1])):
    if any(x in nombre for x in ("Kartel", "PLANNING", "PAPELETAS", "CARTA", "ANIVERSARIO")):
        ruta = os.path.join(CARPETAS[1], nombre)
        if os.path.isfile(ruta):
            print(f"   {nombre:<44} {round(os.path.getsize(ruta)/1024,0):>5} KB")
