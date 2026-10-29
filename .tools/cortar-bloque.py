"""El bloque no pintaba cerrado: solo se saltaba la cabecera de la lista.

Se metía `<div class="lista">` o nada, pero las tareas se añadían siempre.
Ahora se pinta todo y, si está cerrado, se corta por una marca.
"""
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


cambia("""  /* el contenido, solo si está abierto */
  html += cerrado ? "" : `<div class="lista">`;""",
       """  /* Se pinta todo y, si está cerrado, se corta por la marca.
     Antes solo se saltaba la cabecera y las tareas salían igual. */
  const MARCA = "\\u00A7CORTE\\u00A7";
  html += cerrado ? MARCA : `<div class="lista">`;""",
       "la marca del corte")

cambia("""  });
  if(!cerrado) html += `</div>`;
  return html;
}""",
       """  });
  if(cerrado){
    const i = html.indexOf(MARCA);
    if(i >= 0) html = html.slice(0, i);
  } else {
    html += `</div>`;
  }
  return html;
}""",
       "el corte de verdad")

cambia("v-2026-10-26-45", "v-2026-10-26-46", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
