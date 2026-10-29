"""Los bloques, cerrados: solo el título y cómo va. Se abren al tocarlos.

Cierra y abre no es un adorno: la lista entera de golpe agobia, y así se ve
de un vistazo qué queda y no hay que bajar y subir todo el rato.
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


FUNCIONES = r'''/* ---------------------------------------------------------- desplegar bloques
   Un bloque enseña solo su título y cómo va. Se abre al tocarlo.
   Cuando está completo se cierra solo y lo dice. */
let PLEGADOS = {};      /* clave del bloque -> true si está cerrado */

function claveBloque(pre, titulo){
  return pre + "|" + titulo;
}

function plegar(clave){
  PLEGADOS[clave] = !PLEGADOS[clave];
  pinta();
}

/* cuántas van hechas de este bloque */
function cuentaBloque(tareas, pre){
  let tot = 0, hec = 0;
  (tareas || []).forEach((t, i)=>{
    if(t.aviso) return;
    const k = pre + i, partes = t.partes || [];
    if(partes.length){
      tot += partes.length;
      partes.forEach((_, j)=>{ if(hecha(k + "." + j)) hec++; });
    } else {
      tot += 1;
      if(hecha(k)) hec++;
    }
  });
  return { tot: tot, hec: hec };
}

'''

cambia("function bloque(titulo, tareas, pre, extra){", FUNCIONES + "function bloque(titulo, tareas, pre, extra){",
       "las funciones de plegar")

cambia("""  if(!tareas || !tareas.length) return extra || "";
  let html = `<h2 class="bloque">${titulo}<small>${tareas.length} ${
    tareas.length===1?"tarea":"tareas"}</small></h2><div class="lista">`;""",
       """  if(!tareas || !tareas.length) return extra || "";
  const cuenta = cuentaBloque(tareas, pre);
  const completo = cuenta.tot > 0 && cuenta.hec === cuenta.tot;
  const clave = claveBloque(pre, titulo);
  /* por defecto, cerrados. Los completos, siempre cerrados. */
  const cerrado = completo ? true : (PLEGADOS[clave] === undefined ? true : PLEGADOS[clave]);
  const comoVa = completo
    ? `<small class="bloque-ok">✓ completo</small>`
    : `<small>${cuenta.hec} de ${cuenta.tot}</small>`;
  let html = `<h2 class="bloque plega${completo ? " hecho" : ""}" ` +
    `onclick="plegar('${clave}')">` +
    `<span class="flecha">${cerrado ? "▸" : "▾"}</span>` +
    `<span class="bloque-tit">${titulo}</span>${comoVa}</h2>`;
  /* el contenido, solo si está abierto */
  html += cerrado ? "" : `<div class="lista">`;""",
       "el bloque, cerrado con su progreso")

cambia("""  });
  return html;
}

/* Lo de cada día que se quedó sin hacer y NO tiene destino""",
       """  });
  if(!cerrado) html += `</div>`;
  return html;
}

/* Lo de cada día que se quedó sin hacer y NO tiene destino""",
       "el cierre del bloque")

# el estilo
cambia("  .menu-grupo{display:grid;",
       """  /* los bloques que se abren y se cierran */
  h2.bloque.plega{display:flex; align-items:center; gap:8px; cursor:pointer;
                  user-select:none; pointer-events:auto}
  h2.bloque.plega .flecha{font-size:12px; color:var(--gris); width:12px; flex:0 0 12px}
  h2.bloque.plega .bloque-tit{flex:1 1 auto}
  h2.bloque.plega small{flex:0 0 auto; margin-left:auto}
  h2.bloque.plega.hecho .bloque-tit{color:var(--verde-oscuro)}
  .bloque-ok{color:var(--verde-oscuro) !important; font-weight:800}
  .menu-grupo{display:grid;""",
       "el estilo de plegar")

cambia("v-2026-10-26-43", "v-2026-10-26-44", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
