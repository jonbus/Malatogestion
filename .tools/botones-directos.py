"""Los botones de guardar llevan su propia orden: no dependen de nada más."""
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


cambia('<button id="rec-guardar" class="btn-add" type="button">Guardar el recuento</button>',
       '<button id="rec-guardar" class="btn-add" type="button"\n'
       '        onclick="guardarRecuento()">Guardar el recuento</button>',
       "el botón del recuento, con su propia orden")

cambia("""      html += ` <button id="rec-ok" class="btn-add" type="button" ` +
        `style="background:linear-gradient(135deg,#2E7D32,#1B5E20)">` +
        `Dar el visto bueno</button>`;""",
       """      html += ` <button id="rec-ok" class="btn-add" type="button" ` +
        `onclick="aprobarRecuento()" ` +
        `style="background:linear-gradient(135deg,#2E7D32,#1B5E20)">` +
        `Dar el visto bueno</button>`;""",
       "el botón del visto bueno")

cambia("""    `<button id="tah-guardar" class="btn-add" type="button" ` +
    `data-cual="${cual}">Guardar el pan</button></div></div>`;""",
       """    `<button id="tah-guardar" class="btn-add" type="button" ` +
    `data-cual="${cual}" onclick="guardarTahona(this.dataset.cual)">` +
    `Guardar el pan</button></div></div>`;""",
       "el botón del pan")

cambia('`<button id="arr-add" class="btn-add" type="button">Apuntar</button></div>` +',
       '`<button id="arr-add" class="btn-add" type="button" ' +
       'onclick="anadirArreglo()">Apuntar</button></div>` +',
       "el botón de para arreglar")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
