"""Comprueba que los botones de guardar responden en todos los puestos."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
js = open("docs/nube/public/index.html", encoding="utf-8").read().split("<script>")[-1].split("</script>")[0]

fallos = 0


def ok(nombre, bien):
    global fallos
    print(("  OK   " if bien else "  FALLA") + "  " + nombre)
    if not bien:
        fallos += 1


# el escuchador delegado tiene que atender los tres botones
i_atender = js.find("function atenderClic")
i_fin = js.find("\nfunction ", i_atender + 10)
cuerpo = js[i_atender:i_fin]

ok("el guardado del recuento, en el escuchador común", '#rec-guardar' in cuerpo)
ok("el guardado del pan, en el escuchador común", '#tah-guardar' in cuerpo)
ok("el de «Para arreglar», en el escuchador común", '#arr-add' in cuerpo)

# y no debe quedar enganchado solo en la pantalla de la Jefa
i_ger = js.find("function pintaGerencia")
i_ger_fin = js.find("\nfunction ", i_ger + 10)
ger = js[i_ger:i_ger_fin]
ok("ya no se engancha solo en la Jefa",
   'getElementById("rec-guardar")' not in ger)

# el escuchador está puesto sobre el cuerpo de la app
ok("el escuchador va sobre el contenedor",
   'document.getElementById("cuerpo").addEventListener("click", atenderClic)' in js)

print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
