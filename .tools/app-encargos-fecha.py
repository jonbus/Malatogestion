"""Encargos en la app: alta, aviso y lo del día."""
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


BLOQUE = r'''/* ---------------------------------------------------------- ENCARGOS
   Algo que hay que TENER un día. Si hay que pedirlo antes, aparece un aviso
   el día que toca pedirlo. Se guarda la serie; las fechas se deducen. */
function esDiaDeEntrega(e, f){
  f = fechaBuena(f);
  if(f < e.desde || f > (e.hasta || e.desde)) return false;
  if(e.tipo === "dia") return f === e.desde;
  if(e.tipo === "semana"){
    const p = f.split("-").map(Number);
    const w = (new Date(p[0], p[1] - 1, p[2]).getDay() + 6) % 7;
    return (e.dias || []).map(Number).includes(w);
  }
  return true;                      // rango: todos los días
}

/* ¿hoy toca pedir algo para una entrega futura? */
function encargosParaPedir(f){
  const salida = [];
  (encargosFecha || []).forEach(e=>{
    if(!e.antelacion) return;                  // no hay que pedirlo
    const para = sumarDias(f, e.antelacion);
    if(!esDiaDeEntrega(e, para)) return;
    if(e.pedidos && e.pedidos[para]) return;   // ya se pidió
    salida.push({ e: e, para: para });
  });
  return salida;
}

/* ¿hoy hay que recibir algo? */
function encargosParaRecibir(f){
  return (encargosFecha || []).filter(e => esDiaDeEntrega(e, f));
}

const DIAS_CORTOS = ["L","M","X","J","V","S","D"];

function textoEncargo(e){
  const quien = e.cliente ? `<b>${e.cliente}</b> · ` : "";
  return `${quien}${e.que}`;
}

function cuandoEncargo(e, f){
  if(e.tipo === "dia") return "para hoy";
  const p = e.desde.split("-").map(Number), q = (e.hasta || e.desde).split("-").map(Number);
  const dd = (x) => x[2] + "/" + String(x[1]).padStart(2, "0");
  const dias = (e.dias || []).map(d => DIAS_CORTOS[d]).join("");
  return `${e.tipo === "semana" ? "los " + dias + " " : "todos los días "}` +
         `del ${dd(p)} al ${dd(q)}`;
}

/* EL AVISO GORDO: lo primero de la pantalla */
function bloqueEncargosAviso(){
  const pedir = encargosParaPedir(fechaSel);
  const recibir = encargosParaRecibir(fechaSel);
  if(!pedir.length && !recibir.length) return "";
  let html = "";
  pedir.forEach(({e, para})=>{
    html += `<div class="encargo-gordo">
        <div class="enc-cab">⚠ PEDIR HOY · PARA EL ${para.slice(8)}/${para.slice(5,7)}</div>
        <div class="enc-que">${textoEncargo(e)}</div>
        <div class="enc-cuando">${cuandoEncargo(e, fechaSel)} · lo pide ${nombreDe(e.quienPide)}</div>
        <button class="btn-add enc-btn" type="button"
                onclick="marcarEncargo('${e.id}','pedido','${para}')">Pedido hecho</button>
      </div>`;
  });
  recibir.forEach(e=>{
    const ya = (e.pedidos || {})[fechaSel];
    if(e.antelacion && !ya){
      html += `<div class="encargo-gordo enc-rojo">
          <div class="enc-cab">✕ PARA HOY · NO SE PIDIÓ</div>
          <div class="enc-que">${textoEncargo(e)}</div>
          <div class="enc-cuando">${cuandoEncargo(e, fechaSel)} · tenía que pedirlo ${nombreDe(e.quienPide)}</div>
        </div>`;
      return;
    }
    const hecho = (e.recibidos || {})[fechaSel];
    html += `<div class="encargo-gordo enc-verde">
        <div class="enc-cab">✓ PARA HOY · ${hecho ? "RECIBIDO" : "HA LLEGADO"}</div>
        <div class="enc-que">${textoEncargo(e)}</div>
        <div class="enc-cuando">${cuandoEncargo(e, fechaSel)}</div>
        ${hecho ? "" : `<button class="btn-add enc-btn" type="button"
            onclick="marcarEncargo('${e.id}','recibido','${fechaSel}')">Recibido</button>`}
      </div>`;
  });
  return html;
}

async function marcarEncargo(id, cual, fecha){
  ponerSync("trabajando", "Apuntando…");
  try{
    const r = await fetch("/api/encargo-fecha-hecho", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: id, cual: cual, fecha: fecha, quien: quien.id })
    });
    if(!r.ok) throw new Error("HTTP " + r.status);
    const d = await r.json();
    encargosFecha = d.encargosFecha || [];
    ponerSync("ok", cual === "pedido" ? "Pedido apuntado" : "Recibido");
  }catch(e){
    ponerSync("error", "No se pudo apuntar");
  }
  pinta();
}

'''

cambia("function bloqueSinDia(pre){", BLOQUE + "function bloqueSinDia(pre){",
       "los bloques de encargos")

# la variable
cambia("let tahona = {};      // el pan del panadero, por fecha",
       "let tahona = {};      // el pan del panadero, por fecha\n"
       "let encargosFecha = [];   // los encargos: series con fecha",
       "la variable de los encargos")

# se carga
cambia("      tahona = d.tahona || {};",
       "      tahona = d.tahona || {};\n      encargosFecha = d.encargosFecha || [];",
       "los encargos se cargan al arrancar")

# el aviso, lo primero de todo
cambia("      html += bloqueArreglar();                     /* arriba del todo */",
       "      html += bloqueEncargosAviso();                /* lo más gordo, arriba */\n"
       "      html += bloqueArreglar();",
       "el aviso va por encima de todo (tienda)")

cambia("      html += bloqueArreglar();                     /* arriba del todo */",
       "      html += bloqueEncargosAviso();                /* lo más gordo, arriba */\n"
       "      html += bloqueArreglar();",
       "el aviso va por encima de todo (coordinación)")

# la Jefa también lo tiene
cambia("  html += bloqueRecuento(false, true);   /* la Jefa lo mira, no lo apunta */",
       "  html += bloqueEncargosAviso();\n"
       "  html += bloqueRecuento(false, true);   /* la Jefa lo mira, no lo apunta */",
       "la Jefa también ve el aviso")

# los estilos
cambia("  .bloque-arreglar{color:#8A4B00; border-bottom-color:var(--ambar)}",
       """  /* ENCARGOS: lo que tiene que llamar la atención */
  .encargo-gordo{background:#FFF4E0; border:2px solid var(--ambar); border-radius:12px;
                 padding:14px 16px; margin-bottom:12px}
  .encargo-gordo.enc-rojo{background:#FDE8E6; border-color:var(--rojo)}
  .encargo-gordo.enc-verde{background:#EAF7EE; border-color:var(--verde-oscuro)}
  .enc-cab{font-size:11px; font-weight:800; letter-spacing:.06em; color:#8A4B00;
           text-transform:uppercase; margin-bottom:6px}
  .enc-rojo .enc-cab{color:var(--rojo)}
  .enc-verde .enc-cab{color:var(--verde-oscuro)}
  .enc-que{font-size:16px; font-weight:700; color:var(--tinta); line-height:1.3}
  .enc-cuando{font-size:11.5px; color:var(--gris); margin-top:4px}
  .enc-btn{margin-top:10px}
  .bloque-arreglar{color:#8A4B00; border-bottom-color:var(--ambar)}""",
       "los estilos del aviso")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
