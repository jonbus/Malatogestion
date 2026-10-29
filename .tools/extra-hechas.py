"""Las tareas extra hechas se quedan a la vista, tachadas.

Antes desaparecían al marcarlas, así que no había forma de saber qué se hizo.
Las tareas del día se quedan tachadas; las extra tienen que hacer lo mismo.
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


cambia("""function avisoExtras(){
  const mias = (encargos || []).filter(e => !e.hecho &&
    (e.diario || e.f === DIA) &&
    (quien.puesto === "gerencia" ? e.p === "gerencia" : e.p === quien.puesto));
  if(!mias.length) return "";
  let html = `<div class="aviso-extra">` +
    `<b>Tienes ${mias.length} ${mias.length===1?"tarea extra":"tareas extra"} hoy</b>`;""",
       """function avisoExtras(){
  /* las hechas NO se esconden: se quedan tachadas, para poder ver qué se hizo */
  const mias = (encargos || []).filter(e =>
    (e.diario || e.f === DIA) &&
    (quien.puesto === "gerencia" ? e.p === "gerencia" : e.p === quien.puesto));
  if(!mias.length) return "";
  const pendientes = mias.filter(e => !e.hecho).length;
  const hechas = mias.length - pendientes;
  const titulo = pendientes
    ? `Tienes ${pendientes} ${pendientes===1?"tarea extra":"tareas extra"} hoy`
    : `Tareas extra de hoy · todas hechas`;
  let html = `<div class="aviso-extra">` +
    `<b>${titulo}${hechas ? `  ·  ${hechas} ${hechas===1?"hecha":"hechas"}` : ""}</b>`;""",
       "las hechas se quedan, y se cuentan")

cambia("""    const quienLaPuso = nombreDe(e.q);
    html += `<div class="extra-linea ${urgente?"es-urgente":""}" ` +
      `onclick="encargoHecho('${e.id}')">` +
      `<span class="caja"></span><span class="extra-txt">${e.t}</span>${etiqueta}</div>` +""",
       """    const quienLaPuso = nombreDe(e.q);
    const hecho = e.hecho;
    html += `<div class="extra-linea ${urgente?"es-urgente":""}${hecho?" hecha":""}" ` +
      `${hecho ? "" : `onclick="encargoHecho('${e.id}')"`}>` +
      `<span class="caja"></span><span class="extra-txt">${e.t}</span>${etiqueta}</div>` +""",
       "la hecha se queda tachada y ya no se toca")

cambia("""      `<span class="pista">para el ${bonito(e.f)} · la puse ${quienLaPuso}` +
      `${e.turno === "tarde" ? " · por la tarde" : e.turno === "manana" ? " · por la mañana" : ""}</span>` +
      `<span class="pista">si no da tiempo:</span>` +
      `<input type="date" class="inp-enc" data-enc="${e.id}" min="${DIA}" ` +
      `onchange="if(this.value) moverEncargo(this.dataset.enc, this.value)"></div>`;""",
       """      `<span class="pista">para el ${bonito(e.f)} · la puse ${quienLaPuso}` +
      `${e.turno === "tarde" ? " · por la tarde" : e.turno === "manana" ? " · por la mañana" : ""}` +
      `${hecho && e.hHecho ? " · hecha a las " + e.hHecho : ""}</span>` +
      (hecho ? "" :
        `<span class="pista">si no da tiempo:</span>` +
        `<input type="date" class="inp-enc" data-enc="${e.id}" min="${DIA}" ` +
        `onchange="if(this.value) moverEncargo(this.dataset.enc, this.value)">`) +
      `</div>`;""",
       "la hecha dice a qué hora se hizo")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
