"""Las llamadas: una tarea extra de tipo «llamada», con su teléfono y su motivo."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
fallos = 0

# ============================================================ 1 · el servidor
p = r"docs/nube/netlify/functions/nucleo.js"
t = open(p, encoding="utf-8").read()


def cambia_srv(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO (srv): {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


cambia_srv("        tipo: ['urgente', 'arreglar'].includes(c.tipo) ? c.tipo : 'extra',",
           "        tipo: ['urgente', 'arreglar', 'llamada'].includes(c.tipo) ? c.tipo : 'extra',\n"
           "        /* si es una llamada: a qué número y por qué */\n"
           "        tel: c.tel ? String(c.tel).replace(/[^0-9]/g, '').slice(0, 15) : null,\n"
           "        motivo: c.motivo ? String(c.motivo).slice(0, 200) : null,\n"
           "        antesDe: c.antesDe ? String(c.antesDe).slice(0, 5) : null,",
           "el encargo guarda teléfono y motivo")

cambia_srv("""    cascadas: estado.cascadas || {},""",
           """    cascadas: estado.cascadas || {},
    /* los proveedores no caducan: son una agenda */
    proveedores: estado.proveedores || [],""",
           "podar conserva los proveedores")

cambia_srv("        cascadas: estado.cascadas, nombres: estado.nombres",
           "        cascadas: estado.cascadas, nombres: estado.nombres,\n"
           "        proveedores: estado.proveedores",
           "el estado devuelve los proveedores")

cambia_srv("encargosFecha: [], cascadas: {}, nombres: [] };",
           "encargosFecha: [], cascadas: {}, nombres: [], proveedores: [] };",
           "estadoVacio con proveedores")

cambia_srv("""      nombres: Array.isArray(guardado.nombres) ? guardado.nombres : []""",
           """      nombres: Array.isArray(guardado.nombres) ? guardado.nombres : [],
      proveedores: Array.isArray(guardado.proveedores) ? guardado.proveedores : []""",
           "leer devuelve los proveedores")

open(p, "w", encoding="utf-8").write(t)

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


LLAMADA = r'''/* ---------------------------------------------------------- LLAMADAS
   Llamar a un proveedor es una tarea extra con más datos: a quién, a qué
   número y por qué. Y si tiene hora límite, se avisa. */
let proveedores = [];
let llamProv = "", llamCont = "", llamMotivo = "", llamTipo = "extra";

function telBonito(x){
  const d = String(x || "").replace(/[^0-9]/g, "");
  if(d.length !== 9) return d;
  return d.slice(0, 3) + " " + d.slice(3, 5) + " " + d.slice(5, 7) + " " + d.slice(7);
}

/* todos los contactos, uno a uno, para el desplegable */
function contactosTodos(){
  const salida = [];
  (proveedores || []).forEach((pv, i)=>{
    (pv.cs || []).forEach((c, j)=>{
      salida.push({ i: i, j: j, prov: pv, c: c });
    });
  });
  return salida;
}

function quienSeLlama(){
  const pv = proveedores[llamProv];
  if(!pv) return null;
  const c = (pv.cs || [])[Number(llamCont) || 0];
  return c ? { prov: pv, c: c } : null;
}

function bloqueLlamada(){
  const lista = contactosTodos();
  if(!lista.length) return "";
  const opciones = lista.map(x =>
    `<option value="${x.i}-${x.j}"${(String(x.i) === String(llamProv) && String(x.j) === String(llamCont)) ? " selected" : ""}>` +
    `${x.prov.n} · ${x.c.p} · ${telBonito(x.c.t)}</option>`).join("");
  return `<h2 class="bloque">Llamar a un proveedor` +
    `<small>una llamada es una tarea más</small></h2>` +
    `<div class="lista">` +
    `<div class="nueva-nota"><select id="ll-prov" onchange="elegirContacto(this.value)" ` +
    `style="flex:1 1 100%">${opciones}</select></div>` +
    `<div class="nueva-nota">` +
    `<input type="text" id="ll-motivo" maxlength="200" placeholder="Para qué es la llamada…" ` +
    `oninput="llamMotivo=this.value" value="${llamMotivo}">` +
    `<select id="ll-tipo" onchange="llamTipo=this.value">` +
    `<option value="extra"${llamTipo === "extra" ? " selected" : ""}>Ordinaria</option>` +
    `<option value="urgente"${llamTipo === "urgente" ? " selected" : ""}>Urgente</option>` +
    `</select>` +
    `<button class="btn-add" type="button" onclick="anadirLlamada()">Añadir la llamada</button>` +
    `</div></div>`;
}

function elegirContacto(v){
  const trozos = String(v).split("-");
  llamProv = trozos[0];
  llamCont = trozos[1];
}

async function anadirLlamada(){
  const q = quienSeLlama();
  if(!q){ ponerSync("error", "Elige a quién llamar"); return; }
  const motivo = String(valorDe("ll-motivo", llamMotivo) || "").trim();
  if(!motivo){ ponerSync("error", "Escribe para qué es la llamada"); return; }
  await mandarEncargo({
    t: q.prov.n + " · " + q.c.p,
    p: quien.puesto === "gerencia" ? "gerencia" : quien.puesto,
    f: fechaSel, tipo: valorDe("ll-tipo", llamTipo) || "extra",
    tel: q.c.t, motivo: motivo,
    antesDe: q.prov.antes || undefined,
    clave: "llamada:" + q.prov.n + ":" + q.c.p + ":" + fechaSel
  });
  llamMotivo = "";
  ponerSync("ok", "Llamada añadida para el " + bonito(fechaSel));
  pinta();
}

'''

cambia("function horaAhora(){", LLAMADA + "function horaAhora(){",
       "las funciones de las llamadas")

# la variable y la carga
cambia("let encargosFecha = [];   // los encargos: series con fecha",
       "let encargosFecha = [];   // los encargos: series con fecha\n"
       "let agenda = [];          // los proveedores, con sus teléfonos",
       "la variable de los proveedores")

cambia("      encargosFecha = d.encargosFecha || [];",
       "      encargosFecha = d.encargosFecha || [];\n"
       "      proveedores = d.proveedores || [];",
       "los proveedores se cargan al arrancar")

# el formulario, al lado del de tareas extra
cambia("  html += bloqueFormEncargo();",
       "  html += bloqueLlamada();\n  html += bloqueFormEncargo();",
       "el formulario de la llamada, en el calendario")

# y en la tarea se ve a quién se llama y su número
cambia("""      `<span class="caja"></span><span class="extra-txt">${e.t}</span>${etiqueta}</div>` +""",
       """      `<span class="caja"></span><span class="extra-txt">` +
      (e.tipo === "llamada" ? "📞 " : "") + `${e.t}</span>${etiqueta}</div>` +
      (e.tipo === "llamada" && e.tel
        ? `<div class="extra-pasar"><a class="btn-llamar" href="tel:${e.tel}">Llamar</a>` +
          `<span class="pista">${telBonito(e.tel)}${e.motivo ? " · " + e.motivo : ""}</span>` +
          (e.antesDe ? `<span class="pista ${pasadaLaHora(e.antesDe) ? "tarde" : ""}">` +
            `${pasadaLaHora(e.antesDe) ? "⚠ se pasó la hora · " : "⏰ "}antes de las ` +
            `${e.antesDe}</span>` : "") + `</div>`
        : "") +""",
       "la llamada, con su botón")

cambia("function horaAhora(){",
       """/* ¿ya se ha pasado la hora límite del proveedor? */
function pasadaLaHora(h){
  if(!h) return false;
  const ahora = horaAhora();
  return ahora > h;
}

function horaAhora(){""",
       "el aviso de la hora")

# el estilo
cambia("  .guardado{font-size:11px;",
       """  .btn-llamar{display:inline-block; padding:6px 14px; border-radius:9px;
              background:var(--verde-oscuro); color:#fff; font-size:12px;
              font-weight:800; text-decoration:none}
  .pista.tarde{color:var(--rojo); font-weight:700}
  .guardado{font-size:11px;""",
       "el estilo del botón de llamar")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
