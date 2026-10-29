"""Comprueba el enrutado de las pestañas de la Jefa y que no haya caracteres rotos."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
h = open("docs/nube/public/index.html", encoding="utf-8").read()
js = h.split("<script>")[-1].split("</script>")[0]

fallos = 0


def ok(nombre, bien):
    global fallos
    print(("  OK   " if bien else "  FALLA") + "  " + nombre)
    if not bien:
        fallos += 1


# 1 · el orden del enrutado
i_general = js.find('tab === "general" && quien.puesto !== "gerencia"')
i_gerencia = js.find('if(quien.puesto === "gerencia"){')
ok("«general» excluye a la Jefa", i_general > 0)
ok("esa comprobación va ANTES del bloque de la Jefa", 0 < i_general < i_gerencia)
ok("la Jefa tiene su pestaña «turno»", 'if(tab === "turno"){ pintaTurnos(); return; }' in js)
ok("«turno» lleva a los turnos", 'if(tab === "turno"){ pintaTurnos(); return; }' in js)
ok("la Jefa, si no es turno ni calendario, va a su bandeja", "pintaGerencia(); return;" in js)

# 2 · las pestañas de la Jefa
ok("pestañas: General · Turno · Calendario",
   '[["general","General"],["turno","Turno"],["calendario","Calendario"]]' in h)
ok("ya no hay pestaña Bandeja", '[["bandeja","Bandeja"]' not in h)

# 3 · el navegador de fechas de la Jefa
ok("la Jefa tiene navegador de fechas",
   '(quien.puesto === "gerencia" && tab === "general")' in h)

# 4 · caracteres rotos en la pantalla
rotos = h.count("\ufffd")
ok(f"sin caracteres rotos ({rotos})", rotos == 0)

# 5 · las tildes siguen bien
for palabra in ("Mañana", "Coordinación", "Sábado", "Miércoles", "cartelería"):
    ok(f"sigue diciendo «{palabra}»", palabra in h)

print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
