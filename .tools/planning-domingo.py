"""El planning del domingo, con todo lo que ha dicho la propiedad."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools\planning.py"
t = open(p, encoding="utf-8").read()

INICIO = 'y = paso(y, "9:00", "Subir y colocar los globos.'
FIN = '# --- lo que no puede fallar'

i = t.find(INICIO)
j = t.find(FIN)
if i < 0 or j < 0 or j <= i:
    print("  NO ENCONTRADO el bloque del domingo")
    sys.exit(1)

NUEVO = '''y = paso(y, "7:00", "Llegamos nosotras. A las 7:30 llegan LAS PALMERAS.")
y = paso(y, "8:00", "Preparar el LUNCH de la batukada en los platos que se dejaron listos el sábado: jamón, cabecero, pastas, aceitunas, patatas, pan y queso. Todo antes de abrir.")
y = paso(y, "9:00", "Subir y colocar los globos. Hacer o reservar sitio en el parking para la batukada.")
y = paso(y, "9:00", "LA MESA: caballetes y tablón / mantel / tarta / lazos / letras «20 urteurrena» / palmeritas alrededor / gominolas / PIRULETAS")
y = paso(y, "9:30", "La urna/ los carteles / las bolsas / los premios / la papelera y la cajita")
y = paso(y, "10:00", "ABRIR. Los dos niños en la puerta. Y llega EL FOTÓGRAFO (Distira, Javi 647 91 06 17): se queda hasta las 14:30.")
y = paso(y, "10:00", "Empieza EL CANJE: el ticket por una papeleta. Quien no gane, cambia la papeleta por una PIRULETA en la caja.")
y = paso(y, "11:00", "La BATUKADA. El lunch ya tiene que estar puesto.")
y = paso(y, "11:00", "Visitar a ROSA y llevarle unas pastas.")
y = paso(y, "11:30", "LA FOTO DE TODO EL EQUIPO, delante de la tarta.")
y = paso(y, "13:00", "Regalos a la batukada, al acabar: bolsa + calcetines + cantimplora. Los preparan los niños.")
y = paso(y, "14:30", "CERRAR. Recoger. Contar la cajita: tienen que ser 113.")

'''

t = t[:i] + NUEVO + t[j:]

# el pie
t = t.replace('centro(H - 145, "Los turnos de la tienda ya están arreglados.", 44)',
              'centro(H - 145, "Los turnos de la tienda ya están arreglados. El fotógrafo, hasta las 14:30.", 40)')

open(p, "w", encoding="utf-8").write(t)
print("  ok  el planning del domingo, actualizado")
