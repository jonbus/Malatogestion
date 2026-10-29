"""Sacar el informe del pan: compartir por WhatsApp e imprimir en Excel."""
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


AYUDAS = r'''/* ---------------------------------------------------- sacar el informe fuera
   Compartir usa el menu del propio movil: WhatsApp, correo, imprimir.
   Descargar da un .csv que Excel abre con doble clic.
   No se anade nada al servidor: se hace en el propio aparato. */
const MESES_LARGOS = ["enero","febrero","marzo","abril","mayo","junio","julio",
                      "agosto","septiembre","octubre","noviembre","diciembre"];

function mesPan(){
  const hoy = fechaBuena(DIA);
  const diaMes = Number(hoy.slice(8, 10));
  let a = Number(hoy.slice(0, 4)), m = Number(hoy.slice(5, 7));
  if(diaMes <= 5){ m = m - 1; if(m < 1){ m = 12; a--; } }
  return { a: a, m: m, prefijo: a + "-" + String(m).padStart(2, "0"),
           nombre: MESES_LARGOS[m - 1] + " de " + a };
}

function filasPan(){
  const prefijo = mesPan().prefijo;
  const dias = Object.keys(tahona || {}).filter(f => f.startsWith(prefijo)).sort();
  return PANES_TAHONA.map(([k, nombre])=>{
    let e = 0, d = 0;
    dias.forEach(f=>{
      const dia = tahona[f] || {};
      if(dia.entrada && dia.entrada[k]) e += Number(dia.entrada[k]);
      if(dia.devolucion && dia.devolucion[k]) d += Number(dia.devolucion[k]);
    });
    return { nombre: nombre, entra: e, sale: d, queda: e - d };
  });
}

function textoPan(){
  const mes = mesPan();
  const filas = filasPan();
  const linea = (n, e, s, q) =>
    String(n).padEnd(11) + String(e).padStart(6) + String(s).padStart(6) +
    String(q).padStart(7);
  let te = 0, td = 0;
  let t = "MALATO · LA TAHONA\n" + mes.nombre +
          "\nEntradas menos devoluciones\n\n" +
          linea("Pan", "Entra", "Sale", "Queda") + "\n";
  filas.forEach(f=>{
    te += f.entra; td += f.sale;
    t += linea(f.nombre, f.entra, f.sale, f.queda) + "\n";
  });
  t += linea("TOTAL", te, td, te - td) + "\n";
  t += "\nUnidades. Para cotejar con la factura del panadero.";
  return t;
}

function csvPan(){
  const mes = mesPan();
  const filas = filasPan();
  let te = 0, td = 0;
  let c = "Malato · La tahona;" + mes.nombre + "\n\n";
  c += "Pan;Entra;Sale;Queda\n";
  filas.forEach(f=>{
    te += f.entra; td += f.sale;
    c += f.nombre + ";" + f.entra + ";" + f.sale + ";" + f.queda + "\n";
  });
  c += "TOTAL;" + te + ";" + td + ";" + (te - td) + "\n";
  return c;
}

async function compartirPan(){
  const texto = textoPan();
  try{
    if(navigator.share){
      await navigator.share({ title: "La tahona", text: texto });
      ponerSync("ok", "Compartido");
    }else{
      /* sin menú de compartir: se copia, para pegarlo en WhatsApp */
      await navigator.clipboard.writeText(texto);
      ponerSync("ok", "Copiado · pégalo en WhatsApp");
    }
  }catch(e){
    if(String(e && e.name) === "AbortError") return;   /* lo cerró la persona */
    ponerSync("error", "No se pudo compartir");
  }
}

function descargarPan(){
  const csv = csvPan();
  /* la marca para que Excel abra bien los acentos */
  const blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "tahona-" + mesPan().prefijo + ".csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(()=> URL.revokeObjectURL(a.href), 2000);
  ponerSync("ok", "Descargado para Excel");
}

'''

cambia("function bloqueTahonaResumen(){", AYUDAS + "function bloqueTahonaResumen(){",
       "las funciones para sacar el informe")

# los dos botones, dentro del informe
cambia("""  html += `<div class="rec-fila rec-hoy"><span>Total</span><span>${totE}</span>` +
    `<span>${totD}</span><span><b>${totE - totD}</b></span><span></span></div>`;
  html += `</div></div>`;
  return html;
}""",
       """  html += `<div class="rec-fila rec-hoy"><span>Total</span><span>${totE}</span>` +
    `<span>${totD}</span><span><b>${totE - totD}</b></span><span></span></div>`;
  html += `</div>`;
  /* sacarlo de la aplicación: al panadero por WhatsApp, o a papel */
  html += `<div class="nueva-nota" style="border:none; margin-top:10px">` +
    `<button class="btn-add" type="button" onclick="compartirPan()">` +
    `Compartir</button>` +
    ` <button class="btn-add" type="button" onclick="descargarPan()" ` +
    `style="background:#fff; color:var(--tinta); border:1px solid var(--borde)">` +
    `Descargar para Excel</button></div>`;
  html += `</div>`;
  return html;
}""",
       "los dos botones del informe")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
