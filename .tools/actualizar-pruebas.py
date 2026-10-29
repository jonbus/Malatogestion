"""Actualiza las pruebas a los cambios de hoy: fechaBuena y pestañas de la Jefa."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

# --- 1) las pruebas que extraen turnoDe necesitan fechaBuena delante
for ruta, viejo, nuevo in [
    (".tools/probar-tres-perfiles.mjs",
     "const turnoDe = new Function('DATOS', sacar('turnoDe') + '\\nreturn turnoDe;')(DATOS);",
     "const turnoDe = new Function('DATOS', 'const DIA=\"2026-10-23\";' +\n"
     "  sacar('fechaBuena') + sacar('turnoDe') + '\\nreturn turnoDe;')(DATOS);"),
    (".tools/probar-turnos-reales.mjs",
     "const turnoDe = new Function('DATOS', sacar('turnoDe') + '\\nreturn turnoDe;')(DATOS);",
     "const turnoDe = new Function('DATOS', 'const DIA=\"2026-10-23\";' +\n"
     "  sacar('fechaBuena') + sacar('turnoDe') + '\\nreturn turnoDe;')(DATOS);"),
]:
    t = open(ruta, encoding="utf-8").read()
    if viejo in t:
        open(ruta, "w", encoding="utf-8").write(t.replace(viejo, nuevo))
        print(f"  ok  {ruta}")
    else:
        print(f"  NO ENCONTRADO en {ruta}")

# --- 2) la pestaña de la Jefa ya no se llama Bandeja
ruta = ".tools/prueba-usuario-completa.mjs"
t = open(ruta, encoding="utf-8").read()
viejo = ('ok(\'C\', \'la Jefa tiene Bandeja, General y Calendario\',\n'
         '  pagina.includes(\'"bandeja","Bandeja"\') && pagina.includes(\'"general","General"\'));')
nuevo = ('ok(\'C\', \'la Jefa tiene General, Turno y Calendario\',\n'
         '  pagina.includes(\'"general","General"\') && pagina.includes(\'"turno","Turno"\') &&\n'
         '  pagina.includes(\'"calendario","Calendario"\'));')
if viejo in t:
    open(ruta, "w", encoding="utf-8").write(t.replace(viejo, nuevo))
    print(f"  ok  {ruta}")
else:
    print(f"  NO ENCONTRADO en {ruta}")
