"""Los encargos también en el calendario: aviso y marcas en los días."""
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


# 1 · el aviso, lo primero del calendario
cambia("""  let html = `<div class="cal-cab">""",
       """  /* el aviso de pedir, también aquí: es donde se mira el mes */
  let html = bloqueEncargosAviso();
  html += `<div class="cal-cab">""",
       "el aviso en el calendario")

# 2 · los días con encargo, marcados
cambia("""    const hayEnc = (encargos || []).some(e => !e.hecho && e.f === f);
    const hay = hayNota || hayEnc;""",
       """    const hayEnc = (encargos || []).some(e => !e.hecho && e.f === f);
    /* el día tiene encargo si ese día hay entrega, o si ese día toca pedirlo */
    const hayEncF = (encargosFecha || []).some(e =>
      esDiaDeEntrega(e, f) ||
      (e.antelacion && esDiaDeEntrega(e, sumarDias(f, e.antelacion))));
    const hay = hayNota || hayEnc || hayEncF;""",
       "los días con encargo")

cambia("""    const punto = hay
      ? `<span class="punto-nota${hayEnc ? " es-encargo" : ""}"></span>` : "";""",
       """    const punto = hay
      ? `<span class="punto-nota${(hayEnc || hayEncF) ? " es-encargo" : ""}"></span>` : "";""",
       "el punto del día")

# 3 · y el detalle del día elegido
cambia("""  const lista = notasDe(fechaSel);
  const gen = lista.filter(n => n.a === "general");
  const per = lista.filter(n => n.a === "personal");""",
       """  /* los encargos de este día: los que hay que pedir y los que llegan */
  const encPedir = encargosParaPedir(fechaSel);
  const encLlegan = encargosParaRecibir(fechaSel);
  if(encPedir.length || encLlegan.length){
    html += `<h2 class="bloque">Encargos de este día` +
      `<small>${encPedir.length ? encPedir.length + " que pedir" : ""}` +
      `${encPedir.length && encLlegan.length ? " · " : ""}` +
      `${encLlegan.length ? encLlegan.length + " que llegan" : ""}</small></h2>` +
      `<div class="lista">`;
    encPedir.forEach(({e, para})=>{
      html += `<div class="item es-urgente"><div class="cab-item">` +
        `<span class="caja"></span><span class="txt"><b>Pedir: ${e.que}</b>` +
        `<span class="extra-de">${e.cliente || ""} · para el ${para.slice(8)}/${
          para.slice(5,7)} · lo pide ${nombreDe(e.quienPide)}</span></span></div></div>`;
    });
    encLlegan.forEach(e=>{
      const hecho = (e.recibidos || {})[fechaSel];
      html += `<div class="item"><div class="cab-item">` +
        `<span class="caja${hecho ? " hecha" : ""}"></span><span class="txt">` +
        `<b>Llega: ${e.que}</b><span class="extra-de">${e.cliente || ""}` +
        `${hecho ? " · recibido" : ""}</span></span></div></div>`;
    });
    html += `</div>`;
  }

  const lista = notasDe(fechaSel);
  const gen = lista.filter(n => n.a === "general");
  const per = lista.filter(n => n.a === "personal");""",
       "el detalle de los encargos del día")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
