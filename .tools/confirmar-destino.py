"""Al añadir una tarea extra, que diga a dónde ha ido."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

viejo = """async function anadirTareaExtra(){
  const t = (textoTarea || "").trim();
  if(!t) return;
  const puesto = puestoTarea;
  textoTarea = "";
  formTarea = false;
  await mandarEncargo({ t: t, p: puesto, f: fechaSel, turno: turnoTarea || undefined });
  pinta();
}"""

nuevo = """async function anadirTareaExtra(){
  const t = (textoTarea || "").trim();
  if(!t) return;
  const puesto = puestoTarea;
  const turno = turnoTarea;
  const fecha = fechaSel;
  textoTarea = "";
  formTarea = false;
  await mandarEncargo({ t: t, p: puesto, f: fecha, turno: turno || undefined });
  /* se dice A DÓNDE ha ido: cada tarea solo se ve en la pantalla de su puesto,
     así que sin esto no hay forma de comprobar que se ha metido bien. */
  const dondePuesto = NOMBRE_PUESTO[puesto] || puesto;
  const dondeTurno = turno === "tarde" ? " · tarde"
                   : turno === "manana" ? " · mañana" : "";
  ponerSync("ok", "Añadida a " + dondePuesto + dondeTurno + " · " + bonito(fecha));
  pinta();
}"""

if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
open(p, "w", encoding="utf-8").write(t.replace(viejo, nuevo, 1))
print("  ok  la confirmación dice a dónde va")
