"""Añade el recuento del lunes a la app: apuntarlo y ver el histórico."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = len(t)
fallos = 0


def cambia(viejo, nuevo, etiqueta):
    global t, fallos
    if viejo not in t:
        print(f"   NO ENCONTRADO: {etiqueta}")
        fallos += 1
        return
    t = t.replace(viejo, nuevo, 1)
    print(f"   ok  {etiqueta}")


BLOQUE = r'''/* ---------------------------------------------------------- el recuento del lunes
   Lo que sobró del asador el fin de semana: es el stock inicial antes de pedir.
   Lo cuenta tienda el lunes, lo apunta coordinación, y la Jefa lo mira el jueves
   para hacer los pedidos. */
const RECUENTO_CAMPOS = [
  ["pollos", "Pollos"], ["codillos", "Codillos"],
  ["patatas", "Patatas normales"], ["bravas", "Patatas bravas"]
];

/* el lunes de la semana de una fecha */
function lunesDe(f){
  f = fechaBuena(f);
  const [a, m, d] = f.split("-").map(Number);
  const x = new Date(a, m - 1, d);
  const w = (x.getDay() + 6) % 7;          // lunes = 0
  x.setDate(x.getDate() - w);
  return x.toLocaleDateString("en-CA");
}

function ddmm(f){ return f ? f.slice(8) + "/" + f.slice(5, 7) : ""; }

/* editable: puede apuntar los números. conHistorico: enseña los lunes anteriores. */
function bloqueRecuento(editable, conHistorico){
  const lunes = lunesDe(fechaSel);
  const r = (recuentos || {})[lunes] || null;
  let html = `<h2 class="bloque">Recuento del lunes ${ddmm(lunes)}` +
    `<small>${r ? "apuntado por " + nombreDe(r.q) + " · " + (r.h || "")
                : (editable ? "sin apuntar" : "sin apuntar")}</small></h2>`;
  html += `<div class="lista"><div class="recuento">`;
  RECUENTO_CAMPOS.forEach(([k, nombre])=>{
    const v = r && r[k] !== undefined ? r[k] : "";
    if(editable){
      html += `<label class="rec-campo"><span>${nombre}</span>` +
        `<input type="number" min="0" step="0.5" inputmode="decimal" ` +
        `data-rec="${k}" value="${v}"></label>`;
    } else {
      html += `<div class="rec-campo"><span>${nombre}</span>` +
        `<b>${v === "" ? "—" : v}</b></div>`;
    }
  });
  html += `</div>`;
  if(editable){
    html += `<p class="pista">Lo que ha sobrado del asador el fin de semana.` +
      ` Es el stock del que se parte para pedir.</p>` +
      `<button id="rec-guardar" class="btn-add" type="button">Guardar el recuento</button>`;
  }
  html += `</div>`;

  /* el histórico, para poder pedir mirando cómo han ido los lunes anteriores */
  if(conHistorico){
    const lunesTodos = Object.keys(recuentos || {}).sort().reverse().slice(0, 8);
    if(lunesTodos.length){
      html += `<h2 class="bloque bloque-viene">Los lunes anteriores` +
        `<small>${lunesTodos.length} · de más reciente a más antiguo</small></h2>` +
        `<div class="lista lista-viene"><div class="rec-tabla">` +
        `<div class="rec-fila rec-cab"><span>Lunes</span><span>Pollos</span>` +
        `<span>Codillos</span><span>Patatas</span><span>Bravas</span></div>`;
      lunesTodos.forEach(f=>{
        const x = recuentos[f] || {};
        html += `<div class="rec-fila ${f === lunes ? "rec-hoy" : ""}">` +
          `<span>${ddmm(f)}</span><span>${x.pollos ?? "—"}</span>` +
          `<span>${x.codillos ?? "—"}</span><span>${x.patatas ?? "—"}</span>` +
          `<span>${x.bravas ?? "—"}</span></div>`;
      });
      html += `</div></div>`;
    }
  }
  return html;
}

async function guardarRecuento(){
  const vals = {};
  document.querySelectorAll("[data-rec]").forEach(i=>{ vals[i.dataset.rec] = i.value; });
  const lunes = lunesDe(fechaSel);
  const jueves = sumarDias(lunes, 3);
  ponerSync("trabajando", "Guardando el recuento…");
  try{
    const r = await fetch("/api/recuento", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, fecha: lunes, valores: vals })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    recuentos = d.recuentos || {};
    if(typeof d.version === "number") versionVista = d.version;
    ponerSync("ok", "Recuento guardado");
    /* la cascada: al apuntarlo, la Jefa recibe el encargo del jueves */
    await mandarEncargo({
      t: "Hacer los pedidos con el recuento del " + ddmm(lunes),
      p: "gerencia", f: jueves, clave: "recuento:" + lunes + ":pedido",
      partes: ["Mirar el recuento del lunes", "Hacer los pedidos"]
    });
  }catch(e){
    ponerSync("error", "No se pudo guardar el recuento");
  }
  pinta();
}

'''

cambia("function bloqueSinDia(pre){", BLOQUE + "function bloqueSinDia(pre){",
       "el bloque del recuento")

# --- el estado global
cambia("let formOfertas = false, ofertasDesde = \"\", ofertasHasta = \"\", ofertasTitulo = \"\";",
       "let formOfertas = false, ofertasDesde = \"\", ofertasHasta = \"\", ofertasTitulo = \"\";\n"
       "let recuentos = {};   // el recuento del lunes, por fecha del lunes",
       "la variable de los recuentos")

# --- se carga con el estado
cambia("      encargos = d.encargos || [];",
       "      encargos = d.encargos || [];\n      recuentos = d.recuentos || {};",
       "los recuentos se cargan al arrancar")

# --- estilos
cambia("  /* ---- lo que viene ---- */",
       """  /* ---- el recuento del lunes ---- */
  .recuento{display:grid; grid-template-columns:repeat(2, 1fr); gap:10px; padding:14px}
  .rec-campo{display:flex; flex-direction:column; gap:5px; font-size:12px; color:var(--gris)}
  .rec-campo b{font-size:17px; color:var(--tinta)}
  .rec-campo input{border:1px solid var(--borde); border-radius:8px; padding:9px 10px;
                   font-family:inherit; font-size:15px; font-weight:700; color:var(--tinta)}
  .rec-tabla{padding:6px 0}
  .rec-fila{display:grid; grid-template-columns:repeat(5, 1fr); gap:6px;
            padding:8px 14px; font-size:12.5px; border-top:1px solid #F2F7F3}
  .rec-fila:first-child{border-top:none}
  .rec-fila span:not(:first-child){text-align:right}
  .rec-cab{font-size:10.5px; font-weight:700; color:var(--gris);
           text-transform:uppercase; letter-spacing:.04em}
  .rec-hoy{background:var(--verde-suave); font-weight:700}
  /* ---- lo que viene ---- */""",
       "estilos del recuento")

# --- el enganche del botón
cambia("  const bn = document.getElementById(\"of-nueva\");",
       "  const rg = document.getElementById(\"rec-guardar\");\n"
       "  if(rg) rg.addEventListener(\"click\", guardarRecuento);\n"
       "  const bn = document.getElementById(\"of-nueva\");",
       "el botón de guardar")

# --- tienda: en el día, solo los lunes
cambia("      html += bloqueViene(fechaSel);\n      html += bloque(\"Antes de irse\", P.antes, tab[0] + \"a\");",
       "      if(W === \"LUN\" && tab === \"manana\") html += bloqueRecuento(true, false);\n"
       "      html += bloqueViene(fechaSel);\n"
       "      html += bloque(\"Antes de irse\", P.antes, tab[0] + \"a\");",
       "tienda apunta el recuento el lunes por la mañana")

# --- coordinación: en el día, solo los lunes
cambia("      html += bloqueViene(fechaSel);\n      sumar(DATOS.coordinacion.dia.rutina, \"dr\");",
       "      if(W === \"LUN\") html += bloqueRecuento(true, true);\n"
       "      html += bloqueViene(fechaSel);\n"
       "      sumar(DATOS.coordinacion.dia.rutina, \"dr\");",
       "coordinación apunta el recuento el lunes")

# --- gerencia: siempre, y con histórico
cambia("  html += bloque(\"Las ofertas\", DATOS.gerencia.ofertas, \"go\", listaOfertas());",
       "  html += bloqueRecuento(false, true);   /* la Jefa lo mira, no lo apunta */\n"
       "  html += bloque(\"Las ofertas\", DATOS.gerencia.ofertas, \"go\", listaOfertas());",
       "la Jefa lo tiene siempre a la vista")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  {antes} -> {len(t)} bytes · fallos {fallos}")
