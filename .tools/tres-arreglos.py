"""Tres arreglos: entrar en bloques terminados, avisar al guardar, y separar
las tareas extra en pendientes y terminadas."""
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


# ---------------------------------------------------------------- 3 · se puede entrar aunque esté terminado
cambia("  const cerrado = completo ? true : (PLEGADOS[claveB] === undefined ? true : PLEGADOS[claveB]);",
       "  /* aunque esté terminado se puede abrir: para mirar y para corregir */\n"
       "  const cerrado = (PLEGADOS[claveB] === undefined) ? true : PLEGADOS[claveB];",
       "se puede entrar en un bloque terminado")

# ---------------------------------------------------------------- 2 · todo guardado avisa
cambia("  let html = panelCascada() + panelEdicion() +\n"
       "    bloqueEncargosAviso() + avisoExtras() + bloqueArreglar();",
       "  let html = panelCascada() + panelEdicion() +\n"
       "    bloqueEncargosAviso() + avisoExtras() + bloqueArreglar();",
       "(sin cambio)")

cambia("function ponerSync(estado, texto){",
       """/* un aviso que se ve siempre, arriba, cuando algo se guarda */
function toast(texto, malo){
  let caja = document.getElementById("toast");
  if(!caja){
    caja = document.createElement("div");
    caja.id = "toast";
    document.body.appendChild(caja);
  }
  caja.className = "toast" + (malo ? " malo" : "");
  caja.textContent = (malo ? "⚠ " : "✓ ") + texto;
  caja.style.display = "block";
  clearTimeout(toast.tiempo);
  toast.tiempo = setTimeout(()=>{ caja.style.display = "none"; }, 2600);
}

function ponerSync(estado, texto){""",
       "el aviso que se ve siempre")

# ---------------------------------------------------------------- 1 · pendientes y terminadas
cambia("""  const pendientes = mias.filter(e => !e.hecho).length;
  const hechas = mias.length - pendientes;
  const titulo = pendientes
    ? `Tienes ${pendientes} ${pendientes===1?"tarea extra":"tareas extra"} hoy`
    : `Tareas extra de hoy · todas hechas`;
  let html = `<div class="aviso-extra">` +
    `<b>${titulo}${hechas ? `  ·  ${hechas} ${hechas===1?"hecha":"hechas"}` : ""}</b>`;""",
       """  const pendientesLista = mias.filter(e => !e.hecho);
  const hechasLista = mias.filter(e => e.hecho);
  let html = "";
  if(!pendientesLista.length && !hechasLista.length) return "";
  if(pendientesLista.length){
    html += `<div class="aviso-extra"><b>Tienes ${pendientesLista.length} ` +
      `${pendientesLista.length === 1 ? "tarea extra" : "tareas extra"} hoy</b>`;
  }""",
       "la cabecera de las pendientes")

cambia("""  mias.forEach(e=>{
    const urgente = e.tipo === "urgente";""",
       """  pendientesLista.forEach(e=>{
    const urgente = e.tipo === "urgente";""",
       "solo las pendientes en su bloque")

cambia("""  });
  html += `</div>`;
  return html;
}

function pintaGerencia(){""",
       """  });
  if(pendientesLista.length) html += `</div>`;

  /* las terminadas, en su propio bloque cerrado: la pantalla se va limpiando */
  if(hechasLista.length){
    const claveH = "extras-hechas";
    const abierto = PLEGADOS[claveH] === false;
    html += `<h2 class="bloque plega hecho" onclick="plegar('${claveH}')">` +
      `<span class="flecha">${abierto ? "▾" : "▸"}</span>` +
      `<span class="bloque-tit">Terminadas</span>` +
      `<small class="bloque-ok">${hechasLista.length} ✓</small></h2>`;
    if(abierto){
      html += `<div class="lista">`;
      hechasLista.forEach(e=>{
        html += `<div class="item"><div class="cab-item">` +
          `<span class="caja hecha"></span><span class="txt"><b>${e.t}</b>` +
          `<span class="extra-de">hecha${e.hHecho ? " · " + e.hHecho : ""}` +
          `${e.turno === "tarde" ? " · por la tarde" : e.turno === "manana" ? " · por la mañana" : ""}` +
          `</span></span></div>` +
          `<div class="casc-linea"><button class="btn-add-2" type="button" ` +
          `onclick="encargoHecho('${e.id}', true)">destachar</button></div></div>`;
      });
      html += `</div>`;
    }
  }
  return html;
}

function pintaGerencia(){""",
       "las terminadas, aparte y cerradas")

# ---------------------------------------------------------------- el estilo del aviso
cambia("  .menu-dibujo{font-size:22px;",
       """  #toast{position:fixed; top:10px; left:50%; transform:translateX(-50%); z-index:99;
         background:var(--verde-oscuro); color:#fff; padding:11px 18px; border-radius:12px;
         font-size:13px; font-weight:700; box-shadow:0 6px 20px rgba(0,0,0,.22); display:none;
         max-width:92vw; text-align:center}
  #toast.malo{background:var(--rojo)}
  .menu-dibujo{font-size:22px;""",
       "el estilo del aviso")

cambia("v-2026-10-26-70", "v-2026-10-26-71", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
