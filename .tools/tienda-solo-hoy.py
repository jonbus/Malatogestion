"""La tienda solo apunta el pan de HOY. Los días anteriores, gerencia y coordinación.

Se hace de una vez: la tienda no ve los botones del día, y el día que se pinta
y se guarda es siempre el de hoy, aunque se llegue por el botón de atrás.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if v in t:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    else:
        print("  NO ENCONTRADO: " + e)


# 1 · una sola puerta para saber qué día se está tocando
rep("function botonesDia(){",
    '''/* el día que se puede tocar: la tienda, solo hoy */
function fechaPan(){
  return (quien && quien.puesto === "tienda") ? DIA : fechaSel;
}

function botonesDia(){
  /* la tienda no cambia de día: solo apunta el de hoy */
  if(quien && quien.puesto === "tienda") return "";''',
    "el día permitido, y sin botones para la tienda")

# 2 · la Tahona: pinta y guarda el día permitido
rep('''  const f = fechaSel;
  const dia = (tahona || {})[f] || {};
  const ent = dia.entrada || {};
  const dev = dia.devolucion || {};''',
    '''  const f = fechaPan();
  const dia = (tahona || {})[f] || {};
  const ent = dia.entrada || {};
  const dev = dia.devolucion || {};''',
    "la Tahona pinta el día permitido")

rep('''async function guardarTahonaDos(){
  const f = fechaSel;''',
    '''async function guardarTahonaDos(){
  const f = fechaPan();''',
    "la Tahona guarda el día permitido")

# 3 · Zuaza: pinta y guarda el día permitido
rep('''function pintaZuaza(){
  const c = document.getElementById("cuerpo");
  const f = fechaSel;''',
    '''function pintaZuaza(){
  const c = document.getElementById("cuerpo");
  const f = fechaPan();''',
    "Zuaza pinta el día permitido")

rep('''async function guardarZuaza(){
  const f = fechaSel;''',
    '''async function guardarZuaza(){
  const f = fechaPan();''',
    "Zuaza guarda el día permitido")

# 4 · los botones del día, solo para quien puede cambiar de día
rep('''  html += `<div style="display:flex;gap:8px;margin:10px 0;flex-wrap:wrap">
      <button class="btn-add-2" type="button" onclick="moverFechaZuaza(-1)">◀ día anterior</button>
      <button class="btn-add-2" type="button" onclick="hoyZuaza()">hoy</button>
      <button class="btn-add-2" type="button" onclick="moverFechaZuaza(1)">día siguiente ▶</button>
    </div>`;''',
    '''  if(quien.puesto !== "tienda"){
    html += `<div style="display:flex;gap:8px;margin:10px 0;flex-wrap:wrap">
      <button class="btn-add-2" type="button" onclick="moverFechaZuaza(-1)">◀ día anterior</button>
      <button class="btn-add-2" type="button" onclick="hoyZuaza()">hoy</button>
      <button class="btn-add-2" type="button" onclick="moverFechaZuaza(1)">día siguiente ▶</button>
    </div>`;
  }''',
    "Zuaza: los botones, solo si se puede cambiar de día")

rep("v-2026-10-26-87", "v-2026-10-26-88", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
