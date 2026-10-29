"""«Para arreglar» arriba del todo, siempre a la vista."""
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


# 1 · el nombre: de pregunta a rótulo
cambia('return `<h2 class="bloque">¿Algo para arreglar?` +\n'
       '    `<small>no desaparece hasta que se arregla</small></h2>` +',
       'return `<h2 class="bloque bloque-arreglar">Para arreglar` +\n'
       '    `<small>lo ve coordinación · no desaparece hasta que se arregla</small></h2>` +',
       "el rótulo, más corto")

cambia('`<p class="pista" style="padding:0 14px">Lo verá coordinación hasta que se arregle.</p></div>`;',
       '`<p class="pista" style="padding:0 14px">Apunta aquí lo que veas: un caducado, fruta fea, algo roto.</p></div>`;',
       "la pista de debajo")

cambia('placeholder="Un caducado, fruta con mala presencia…"',
       'placeholder="Un caducado, fruta con mala presencia…"',
       "(el ejemplo del campo ya vale)")

# 2 · quitar de donde estaba
cambia('      if(tab === "tarde") html += bloqueTahona("devolucion");\n'
       '      html += bloqueArreglar();',
       '      if(tab === "tarde") html += bloqueTahona("devolucion");',
       "se quita del medio (tienda)")

cambia('      html += bloqueTahona("entrada");\n'
       '      html += bloqueArreglar();',
       '      html += bloqueTahona("entrada");',
       "se quita del medio (coordinación)")

# 3 · ponerlo arriba del todo, antes de la primera lista
cambia('      html += bloque("Lo de siempre · en este orden", P.rutina, tab[0] + "r");',
       '      html += bloqueArreglar();                     /* arriba del todo */\n'
       '      html += bloque("Lo de siempre · en este orden", P.rutina, tab[0] + "r");',
       "arriba en tienda")

cambia('      html += bloque("Rutina · todos los días", DATOS.coordinacion.dia.rutina, "dr");',
       '      html += bloqueArreglar();                     /* arriba del todo */\n'
       '      html += bloque("Rutina · todos los días", DATOS.coordinacion.dia.rutina, "dr");',
       "arriba en coordinación")

# 4 · estilo del rótulo
cambia("  .item.es-arreglar .cab-item{border-left:3px solid var(--ambar); padding-left:9px}",
       "  .bloque-arreglar{color:#8A4B00; border-bottom-color:var(--ambar)}\n"
       "  .item.es-arreglar .cab-item{border-left:3px solid var(--ambar); padding-left:9px}",
       "el color del rótulo")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
