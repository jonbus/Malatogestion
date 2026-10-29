"""Comprueba el lote: pestañas, navegador, título y lista de ofertas."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
h = open("docs/nube/public/index.html", encoding="utf-8").read()
js = h.split("<script>")[-1].split("</script>")[0]

pruebas = [
    ("fechaBuena existe", "function fechaBuena"),
    ("semanaDe protegida", "function semanaDe(f){                     // \"2026-10-22\" -> \"JUE\"\n  f = fechaBuena(f);"),
    ("turnoDe protegido", "fecha = fechaBuena(fecha);"),
    ("coord a prueba de semana mala", "((T.coord[semana] || {})[numero])"),
    ("pestañas: General · Turno · Calendario",
     '[["general","General"],["turno","Turno"],["calendario","Calendario"]]'),
    ("ya no dice Bandeja", '[["bandeja","Bandeja"]'),
    ("turno lleva a los turnos", 'if(tab === "turno"){ pintaTurnos(); return; }'),
    ("la Jefa tiene navegador de fechas",
     '(quien.puesto === "gerencia" && tab === "general")'),
    ("el título va detrás de las fechas", 'id="of-titulo"'),
    ("lista de ofertas", "Ofertas dadas de alta"),
    ("orden cronológico", 'localeCompare(String(b.f || ""))'),
    ("versión -27", "v-2026-10-23-27"),
]
fallos = 0
for nombre, aguja in pruebas:
    if nombre == "ya no dice Bandeja":
        bien = aguja not in h
    else:
        bien = aguja in h
    print(("  OK   " if bien else "  FALLA") + "  " + nombre)
    if not bien:
        fallos += 1

# el título tiene que ir DESPUÉS de las fechas en el código
i_fechas = js.find('id="of-desde"')
i_titulo = js.find('id="of-titulo"')
bien = 0 < i_fechas < i_titulo
print(("  OK   " if bien else "  FALLA") + "  en el código, las fechas van antes que el título")
if not bien:
    fallos += 1

print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
