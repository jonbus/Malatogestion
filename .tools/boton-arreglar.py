"""El pan en una columna, y el botón «¿Algo para arreglar?»."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
fallos = 0

# ============================================================ 1 · el tipo, en el servidor
p = r"docs/nube/netlify/functions/nucleo.js"
t = open(p, encoding="utf-8").read()
viejo = "        tipo: c.tipo === 'urgente' ? 'urgente' : 'extra',"
nuevo = ("        /* extra = cuando se pueda · urgente = hoy y ya ·\n"
         "           arreglar = algo que hay que reparar (lo apunta cualquiera, no caduca) */\n"
         "        tipo: ['urgente', 'arreglar'].includes(c.tipo) ? c.tipo : 'extra',")
if viejo in t:
    t = t.replace(viejo, nuevo, 1)
    open(p, "w", encoding="utf-8").write(t)
    print("   ok  el servidor acepta el tipo «arreglar»")
else:
    print("   NO ENCONTRADO en el servidor")
    fallos += 1

# ============================================================ 2 · la app
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()


def cambia(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


# --- el pan, de arriba abajo
cambia(".tahona{grid-template-columns:repeat(2, 1fr)}",
       ".tahona{grid-template-columns:1fr}",
       "el pan en una columna")

# --- el bloque del botón
BLOQUE = r'''/* ---------------------------------------------------------- ¿algo para arreglar?
   Casi todos los días hay algo: un caducado, fruta con mala presencia…
   Lo apunta CUALQUIERA (sobre todo tienda) y NO desaparece hasta que se arregla.
   Va a coordinación, que es quien lo resuelve. */
let textoArreglo = "";

function bloqueArreglar(){
  return `<h2 class="bloque">¿Algo para arreglar?` +
    `<small>no desaparece hasta que se arregla</small></h2>` +
    `<div class="lista"><div class="nueva-nota" style="border:none; margin-top:0">` +
    `<input type="text" id="arr-txt" maxlength="200" ` +
    `placeholder="Un caducado, fruta con mala presencia…" value="${textoArreglo}">` +
    `<button id="arr-add" class="btn-add" type="button">Apuntar</button></div>` +
    `<p class="pista" style="padding:0 14px">Lo verá coordinación hasta que se arregle.</p></div>`;
}

async function anadirArreglo(){
  const txt = (textoArreglo || "").trim();
  if(!txt) return;
  textoArreglo = "";
  /* la clave evita que se apunte dos veces lo mismo mientras no se arregle */
  const clave = "arreglar:" + txt.toLowerCase().replace(/[^a-z0-9]+/g, "-").slice(0, 40);
  await mandarEncargo({ t: txt, p: "coordinacion", f: fechaSel, diario: true,
                        tipo: "arreglar", clave: clave });
  ponerSync("ok", "Apuntado para arreglar");
  pinta();
}

'''

cambia("function bloqueSinDia(pre){", BLOQUE + "function bloqueSinDia(pre){",
       "el bloque de «algo para arreglar»")

# --- el enganche
cambia('  const tg = document.getElementById("tah-guardar");',
       '  const at = document.getElementById("arr-txt");\n'
       '  if(at){\n'
       '    at.addEventListener("input", ()=>{ textoArreglo = at.value; });\n'
       '    at.addEventListener("keydown", e=>{ if(e.key === "Enter"){ e.preventDefault(); anadirArreglo(); } });\n'
       '  }\n'
       '  const ab = document.getElementById("arr-add");\n'
       '  if(ab) ab.addEventListener("click", anadirArreglo);\n'
       '  const tg = document.getElementById("tah-guardar");',
       "el enganche del botón")

# --- tienda: en las dos pestañas del día
cambia('      if(tab === "tarde") html += bloqueTahona("devolucion");',
       '      if(tab === "tarde") html += bloqueTahona("devolucion");\n'
       '      html += bloqueArreglar();',
       "tienda tiene el botón")

# --- coordinación: en El día
cambia('      html += bloqueTahona("entrada");',
       '      html += bloqueTahona("entrada");\n'
       '      html += bloqueArreglar();',
       "coordinación tiene el botón")

# --- estilo: que se distinga lo de arreglar
cambia("  .tag.urgente{background:#FDE8E6; color:var(--rojo); font-weight:700}",
       "  .tag.urgente{background:#FDE8E6; color:var(--rojo); font-weight:700}\n"
       "  .item.es-arreglar .cab-item{border-left:3px solid var(--ambar); padding-left:9px}\n"
       "  .tag.arreglar{background:#FDF1DC; color:#8A4B00; font-weight:700}",
       "el estilo de «arreglar»")

# --- la marca en la tarea
cambia('    const urgente = e.tipo === "urgente";\n'
       '    const etiqueta = urgente ? `<span class="tag urgente">URGENTE</span>` : "";',
       '    const urgente = e.tipo === "urgente";\n'
       '    const arreglo = e.tipo === "arreglar";\n'
       '    const etiqueta = urgente ? `<span class="tag urgente">URGENTE</span>`\n'
       '                   : arreglo ? `<span class="tag arreglar">PARA ARREGLAR</span>` : "";',
       "la etiqueta en la tarea")

cambia('    html += `<div class="item ${urgente ? "es-urgente" : ""}" data-k="${k}">',
       '    html += `<div class="item ${urgente ? "es-urgente" : ""}${arreglo ? " es-arreglar" : ""}" data-k="${k}">',
       "la clase de la tarea")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
