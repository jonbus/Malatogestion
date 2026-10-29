"""El aviso de tareas extra pasa a ser la tarea de verdad: se marca y se pasa.

Era un cartel que solo informaba («Tienes 2 tareas extra hoy · …») y no dejaba
hacer nada. Ahora cada línea lleva su casilla y su «si no da tiempo».
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


NUEVO = r'''function avisoExtras(){
  const mias = (encargos || []).filter(e => !e.hecho &&
    (e.diario || e.f === DIA) &&
    (quien.puesto === "gerencia" ? e.p === "gerencia" : e.p === quien.puesto));
  if(!mias.length) return "";
  let html = `<div class="aviso-extra">` +
    `<b>Tienes ${mias.length} ${mias.length===1?"tarea extra":"tareas extra"} hoy</b>`;
  /* cada una se marca tocandola, y se puede pasar a otro dia */
  mias.forEach(e=>{
    const urgente = e.tipo === "urgente";
    const arreglo = e.tipo === "arreglar";
    const etiqueta = urgente ? `<span class="tag urgente">URGENTE</span>`
                   : arreglo ? `<span class="tag arreglar">PARA ARREGLAR</span>` : "";
    const quienLaPuso = nombreDe(e.q);
    html += `<div class="extra-linea ${urgente?"es-urgente":""}" ` +
      `onclick="encargoHecho('${e.id}')">` +
      `<span class="caja"></span><span class="extra-txt">${e.t}</span>${etiqueta}</div>` +
      `<div class="extra-pasar">` +
      `<span class="pista">para el ${bonito(e.f)} · la puso ${quienLaPuso}` +
      `${e.turno ? " · " + (e.turno === "tarde" ? "tarde" : "mañana") : ""}</span>` +
      `<span class="pista">si no da tiempo:</span>` +
      `<input type="date" class="inp-enc" data-enc="${e.id}" min="${DIA}" ` +
      `onchange="if(this.value) moverEncargo(this.dataset.enc, this.value)"></div>`;
  });
  html += `</div>`;
  return html;
}
'''

i = t.find("function avisoExtras(){")
j = t.find("function pintaGerencia(){")
if i < 0 or j < 0:
    print("   NO ENCONTRADO el aviso")
    sys.exit(1)
t = t[:i] + NUEVO + "\n" + t[j:]
print("   ok  el aviso, convertido en tarea")

# los estilos
cambia("  .bloque-arreglar{color:#8A4B00; border-bottom-color:var(--ambar)}",
       """  .bloque-arreglar{color:#8A4B00; border-bottom-color:var(--ambar)}
  /* las tareas extra del aviso: se marcan y se pasan */
  .extra-linea{display:flex; align-items:center; gap:9px; margin-top:9px;
               cursor:pointer; font-size:13.5px; color:var(--tinta);
               font-weight:600; line-height:1.3}
  .extra-linea .caja{flex:0 0 auto; width:18px; height:18px; border-radius:6px;
                     border:2px solid rgba(139,92,246,.55); background:#fff}
  .extra-linea.activa .caja{background:rgba(139,92,246,.55)}
  .extra-txt{flex:1 1 auto}
  .extra-pasar{display:flex; align-items:center; gap:7px; flex-wrap:wrap;
               margin:5px 0 2px 27px}
  .extra-pasar .inp-enc{font-size:11.5px; padding:3px 6px; border-radius:6px;
                        border:1px solid rgba(139,92,246,.4); background:#fff}""",
       "los estilos de la línea")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
