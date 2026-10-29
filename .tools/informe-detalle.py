"""Un archivo aparte con el detalle de cada día, para el proveedor."""
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


DETALLE = r'''/* el detalle, para mandarselo al proveedor: una linea por pan y dia */
function csvDetalle(){
  const r = rangoPan();
  const filas = filasPan();
  const dd = (f) => f.slice(8) + "/" + f.slice(5, 7) + "/" + f.slice(0, 4);
  let c = "Malato · La tahona\n";
  c += "Detalle del " + dd(r.desde) + " al " + dd(r.hasta) + "\n\n";
  c += "DIA;PAN;ENTRA;SALE\n";
  let te = 0, td = 0;
  Object.keys(tahona || {}).filter(f => f >= r.desde && f <= r.hasta).sort()
    .forEach(f=>{
      const dia = tahona[f] || {};
      PANES_TAHONA.forEach(([k, nombre])=>{
        const e = (dia.entrada && dia.entrada[k]) || 0;
        const d = (dia.devolucion && dia.devolucion[k]) || 0;
        if(e || d){
          c += dd(f) + ";" + nombre + ";" + e + ";" + d + "\n";
          te += e; td += d;
        }
      });
    });
  c += "\nTOTAL;;" + te + ";" + td + "\n\n";
  c += "Entradas menos devoluciones: " + (te - td) + "\n\n";
  /* el resumen por pan, al final, para cuadrar de un vistazo */
  c += "PAN;ENTRA;SALE;QUEDA\n";
  filas.forEach(f=>{ c += f.nombre + ";" + f.entra + ";" + f.sale + ";" + f.queda + "\n"; });
  c += "TOTAL;" + te + ";" + td + ";" + (te - td) + "\n";
  return c;
}

function descargarDetalle(){
  const csv = csvDetalle();
  const blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  const r = rangoPan();
  a.download = "tahona-detalle-" + r.desde + "-a-" + r.hasta + ".csv";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(()=> URL.revokeObjectURL(a.href), 2000);
  ponerSync("ok", "Detalle descargado");
}

'''

cambia("function descargarPan(){", DETALLE + "function descargarPan(){",
       "la función del detalle")

# los botones: resumen y detalle
cambia("""    `<button class="btn-add" type="button" onclick="compartirPan()">Compartir</button>` +
    ` <button class="btn-add" type="button" onclick="descargarPan()" ` +
    `style="background:#fff; color:var(--tinta); border:1px solid var(--borde)">` +
    `Descargar para Excel</button></div>`;""",
       """    `<button class="btn-add" type="button" onclick="compartirPan()">Compartir</button>` +
    `</div><div class="nueva-nota" style="border:none">` +
    `<button class="btn-add" type="button" onclick="descargarPan()" ` +
    `style="background:#fff; color:var(--tinta); border:1px solid var(--borde)">` +
    `Resumen para Excel</button>` +
    ` <button class="btn-add" type="button" onclick="descargarDetalle()" ` +
    `style="background:#fff; color:var(--tinta); border:1px solid var(--borde)">` +
    `Detalle por día para el proveedor</button>` +
    `</div>`;""",
       "los dos botones de descarga")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
