"""El informe del pan, siempre visible y junto a las ventanas del mes."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def cambia(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


# 1 · que salga aunque no haya pan: con los cinco panes y ceros
cambia("""  const filas = Object.keys(tahona || {}).filter(f => f.startsWith(prefijo)).sort();
  if(!filas.length) return "";""",
       """  const filas = Object.keys(tahona || {}).filter(f => f.startsWith(prefijo)).sort();
  /* aunque no haya pan apuntado, el informe tiene que verse:
     asi se sabe donde esta y que hay que apuntarlo. */""",
       "el informe sale aunque no haya pan")

# 2 · junto a las ventanas del mes, no antes del recuento
cambia("  html += bloqueTahonaResumen();   /* del 1 al 5, el mes anterior */\n"
       "  html += bloqueRecuento(false, true);   /* la Jefa lo mira, no lo apunta */",
       "  html += bloqueRecuento(false, true);   /* la Jefa lo mira, no lo apunta */",
       "se quita de donde estaba")

cambia("""  /* el estado de las cuatro ventanas */""",
       """  /* el informe del pan, junto a las ventanas */
  html += bloqueTahonaResumen();

  /* el estado de las cuatro ventanas */""",
       "va junto a las ventanas del mes")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
