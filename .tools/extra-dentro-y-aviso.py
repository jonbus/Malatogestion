"""Mete las tareas extra DENTRO de «Lo de hoy» y pone el aviso al entrar."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t

# --- 1) el bloque de las extra devuelve SOLO los trozos, para poder meterlos en la lista
t = t.replace(
    '''  let html = `<h2 class="bloque bloque-encargo">${titulo}` +
    `<small>${lista.length} ${lista.length===1?"tarea":"tareas"}</small></h2><div class="lista">`;''',
    '''  let html = "";''')
t = t.replace(
    '''    html += `<div class="item" data-k="${k}">
        <div class="cab-item"><span class="caja"></span>
        <span class="txt"><b>${e.t}</b>${que}
        <span class="arrastre-de">${cuando} · ${de}</span></span></div>${borrar}</div>`;
  });
  return html + "</div>";
}''',
    '''    html += `<div class="item" data-k="${k}">
        <div class="cab-item"><span class="caja"></span>
        <span class="txt"><b>${e.t}</b>${que}
        <span class="extra-de">${cuando} · ${de}</span></span></div>${borrar}</div>`;
  });
  return html;
}''')

# --- 2) tienda: las extra van DENTRO de «Lo de hoy»
t = t.replace(
    '''      html += bloque("Lo de hoy · " + NOMBRE_DIA, P.porDia[W] || [], pre);
      html += bloquePasadas();
      html += bloqueSinDia(pre);
      html += bloqueEncargos("tienda", fechaSel, tab, "Tareas extra");''',
    '''      html += bloque("Lo de hoy · " + NOMBRE_DIA, P.porDia[W] || [], pre,
                     bloqueEncargos("tienda", fechaSel, tab, ""));
      html += bloquePasadas();
      html += bloqueSinDia(pre);''')

# --- 3) coordinación: igual
t = t.replace(
    '''      html += bloque("Lo de hoy · " + NOMBRE_DIA,
                     DATOS.coordinacion.dia.porDia[W] || [], "dd");
      html += bloquePasadas();
      html += bloqueSinDia("dd");
      html += bloqueEncargos("coordinacion", fechaSel, null, "Tareas extra");''',
    '''      html += bloque("Lo de hoy · " + NOMBRE_DIA,
                     DATOS.coordinacion.dia.porDia[W] || [], "dd",
                     bloqueEncargos("coordinacion", fechaSel, null, ""));
      html += bloquePasadas();
      html += bloqueSinDia("dd");''')

# --- 4) el aviso: cuántas tareas extra tengo hoy
t = t.replace(
    "  const laborable = (W !== \"SAB\" && W !== \"DOM\");\n  let html = `<div class=\"ger-cab\">",
    "  const laborable = (W !== \"SAB\" && W !== \"DOM\");\n  let html = avisoExtras();\n  html += `<div class=\"ger-cab\">")

t = t.replace(
    "function pintaGerencia(){",
    '''/* El aviso: solo lo ve quien tiene tareas extra hoy. */
function avisoExtras(){
  const mias = (encargos || []).filter(e => !e.hecho &&
    (e.diario || e.f === DIA) &&
    (quien.puesto === "gerencia" ? e.p === "gerencia" : e.p === quien.puesto));
  if(!mias.length) return "";
  return `<div class="aviso-extra">
      <b>Tienes ${mias.length} ${mias.length===1?"tarea extra":"tareas extra"} hoy</b>
      <span>${mias.map(e => e.t).join(" · ")}</span>
    </div>`;
}

function pintaGerencia(){''')

if t == antes:
    print("  SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  tareas extra dentro de la lista + aviso")
