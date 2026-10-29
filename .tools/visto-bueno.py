"""Visto bueno del recuento, y el informe del pan siempre para la Jefa."""
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


cambia_srv("""      estado.recuentos[fecha] = {
        pollos: num(v.pollos), codillos: num(v.codillos),
        patatas: num(v.patatas), bravas: num(v.bravas),
        q: marca, h: hora
      };""",
           """      const antes = estado.recuentos[fecha] || {};
      estado.recuentos[fecha] = {
        pollos: num(v.pollos), codillos: num(v.codillos),
        patatas: num(v.patatas), bravas: num(v.bravas),
        q: marca, h: hora,
        /* si lo cambia coordinación, se entiende aprobado */
        aprobado: marca.startsWith('co') ? true : false,
        qAprueba: marca.startsWith('co') ? marca : null
      };""",
           "el recuento nace sin visto bueno (o aprobado si lo apunta coordinación)")

cambia_srv("    /* -------- borrar un recuento",
           """    /* -------- el visto bueno de coordinación al recuento del lunes */
    if (ruta.endsWith('/recuento-aprobar') && metodo === 'POST') {
      const fecha = String((cuerpo && cuerpo.fecha) || '');
      if (!/^\\d{4}-\\d{2}-\\d{2}$/.test(fecha)) {
        return { status: 400, body: { ok: false, error: 'fecha no válida' } };
      }
      if (!marca) return { status: 400, body: { ok: false, error: 'falta quién' } };
      const estado = await leer();
      const r = estado.recuentos && estado.recuentos[fecha];
      if (!r) return { status: 404, body: { ok: false, error: 'no hay recuento ese día' } };
      r.aprobado = true;
      r.qAprueba = marca;
      r.hAprueba = hora;
      const podado = podar(estado, zona);
      await escribir(podado);
      return { status: 200, body: { ok: true, recuentos: podado.recuentos } };
    }

    /* -------- borrar un recuento""",
           "endpoint del visto bueno")

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


# --- el visto bueno en el bloque del recuento
cambia("""  let html = `<h2 class="bloque">Recuento del lunes ${ddmm(lunes)}` +
    `<small>${r ? "apuntado por " + nombreDe(r.q) + " · " + (r.h || "")
                : (editable ? "sin apuntar" : "sin apuntar")}</small></h2>`;""",
       """  const sinVisto = r && !r.aprobado;
  let html = `<h2 class="bloque">Recuento del lunes ${ddmm(lunes)}` +
    `<small>${r ? "apuntado por " + nombreDe(r.q) + " · " + (r.h || "") +
                  (r.aprobado ? "  ·  con el visto bueno de " + nombreDe(r.qAprueba)
                              : "  ·  SIN visto bueno")
                : "sin apuntar"}</small></h2>`;""",
       "el recuento dice si tiene visto bueno")

cambia("""  if(editable){
    html += `<p class="pista">Lo que ha sobrado del asador el fin de semana.` +
      ` Es el stock del que se parte para pedir.</p>` +
      `<button id="rec-guardar" class="btn-add" type="button">Guardar el recuento</button>`;
  }""",
       """  if(editable){
    html += `<p class="pista">Lo que ha sobrado del asador el fin de semana.` +
      ` Es el stock del que se parte para pedir.</p>` +
      `<button id="rec-guardar" class="btn-add" type="button">Guardar el recuento</button>`;
    /* coordinación da el visto bueno */
    if(sinVisto && quien.puesto === "coordinacion"){
      html += ` <button id="rec-ok" class="btn-add" type="button" ` +
        `style="background:linear-gradient(135deg,#2E7D32,#1B5E20)">` +
        `Dar el visto bueno</button>`;
    }
  }""",
       "el botón del visto bueno")

cambia("""  if(e.target.closest("#arr-add")){
    e.stopPropagation(); anadirArreglo(); return;
  }""",
       """  if(e.target.closest("#arr-add")){
    e.stopPropagation(); anadirArreglo(); return;
  }
  if(e.target.closest("#rec-ok")){
    e.stopPropagation(); aprobarRecuento(); return;
  }""",
       "el visto bueno, para todos los puestos")

cambia("function bloqueRecuento(editable, conHistorico){",
       """async function aprobarRecuento(){
  const lunes = lunesDe(fechaSel);
  ponerSync("trabajando", "Dando el visto bueno…");
  try{
    const r = await fetch("/api/recuento-aprobar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ quien: quien.id, fecha: lunes })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    recuentos = d.recuentos || {};
    ponerSync("ok", "Visto bueno dado");
  }catch(e){
    ponerSync("error", "No se pudo dar el visto bueno");
  }
  pinta();
}

function bloqueRecuento(editable, conHistorico){""",
       "la función del visto bueno")

# --- el informe del pan, siempre para la Jefa (no solo del 1 al 5)
cambia("""  const hoy = fechaBuena(DIA);
  const diaMes = Number(hoy.slice(8, 10));
  if(diaMes > 5) return "";
  /* el mes anterior */""",
       """  const hoy = fechaBuena(DIA);
  const diaMes = Number(hoy.slice(8, 10));
  /* del 1 al 5 se enseña el mes anterior (para cotejar la factura);
     el resto de días, el mes en curso (para ir viéndolo) */
  if(diaMes > 5){
    const pref = hoy.slice(0, 7);
    const filasHoy = Object.keys(tahona || {}).filter(f => f.startsWith(pref)).sort();
    if(!filasHoy.length) return "";
    const M = ["enero","febrero","marzo","abril","mayo","junio","julio",
               "agosto","septiembre","octubre","noviembre","diciembre"];
    let html = `<h2 class="bloque bloque-viene">Tahona · el pan de ` +
      M[Number(hoy.slice(5,7)) - 1] +
      `<small>lo que va de mes · entradas menos devoluciones</small></h2>` +
      `<div class="lista lista-viene"><div class="rec-tabla">` +
      `<div class="rec-fila rec-cab"><span>Pan</span><span>Entra</span>` +
      `<span>Sale</span><span>Queda</span><span></span></div>`;
    let tE = 0, tD = 0;
    PANES_TAHONA.forEach(([k, nombre])=>{
      let e = 0, d = 0;
      filasHoy.forEach(f=>{
        const dia = tahona[f] || {};
        if(dia.entrada && dia.entrada[k]) e += Number(dia.entrada[k]);
        if(dia.devolucion && dia.devolucion[k]) d += Number(dia.devolucion[k]);
      });
      tE += e; tD += d;
      html += `<div class="rec-fila"><span>${nombre}</span><span>${e}</span>` +
        `<span>${d}</span><span><b>${e - d}</b></span><span></span></div>`;
    });
    html += `<div class="rec-fila rec-hoy"><span>Total</span><span>${tE}</span>` +
      `<span>${tD}</span><span><b>${tE - tD}</b></span><span></span></div></div></div>`;
    return html;
  }
  /* el mes anterior */""",
       "el informe del pan, siempre para la Jefa")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
