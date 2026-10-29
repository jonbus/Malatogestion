"""La clave de la Jefa se pide una vez y dura hasta las 15:00.

Antes se pedía en cada entrada: al ir hacia atrás, al salir y volver. Un peaje.
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


# 1 · el recordatorio hasta las 15:00
cambia("function pintarLogin(){",
       """/* La clave de la Jefa, una vez metida, vale hasta las 15:00 del día. */
function horaCierreJefa(){
  const d = new Date();
  d.setHours(15, 0, 0, 0);
  return d.getTime();
}

function gerenciaAbierta(){
  try{
    const hasta = Number(localStorage.getItem("gerencia-hasta") || 0);
    return hasta > Date.now();
  }catch(e){ return false; }
}

function recordarGerencia(abrir){
  try{
    if(abrir) localStorage.setItem("gerencia-hasta", String(horaCierreJefa()));
    else localStorage.removeItem("gerencia-hasta");
  }catch(e){}
}

function pintarLogin(){""",
       "el recordatorio de la clave")

# 2 · al meter la clave, se recuerda
cambia("""  document.getElementById("caja-clave").hidden = true;
  quien = { puesto: "gerencia", numero: 1, id: "ge1" };""",
       """  document.getElementById("caja-clave").hidden = true;
  recordarGerencia(true);
  quien = { puesto: "gerencia", numero: 1, id: "ge1" };""",
       "al entrar, se recuerda hasta las 15:00")

# 3 · si ya está abierta, no se pregunta
cambia("""    const i = document.getElementById("pin-inp");
    i.value = ""; document.getElementById("aviso-pin").textContent = "";
    i.focus();""",
       """    const i = document.getElementById("pin-inp");
    i.value = ""; document.getElementById("aviso-pin").textContent = "";
    i.focus();""",
       "(sin cambio)")

cambia("""  const caja = document.getElementById("caja-clave");
  caja.hidden = !caja.hidden;""",
       """  /* si ya se metió la clave y no son las 15:00, no se vuelve a pedir */
  if(gerenciaAbierta()){
    quien = { puesto: "gerencia", numero: 1, id: "ge1" };
    try { localStorage.setItem("tienda-quien", JSON.stringify(quien)); } catch(e){}
    entrar();
    return;
  }
  const caja = document.getElementById("caja-clave");
  caja.hidden = !caja.hidden;""",
       "si ya está abierta, entra directa")

# 4 · al salir, se olvida
cambia("""  document.getElementById("btn-salir").addEventListener("click", ()=>{""",
       """  document.getElementById("btn-salir").addEventListener("click", ()=>{
    if(quien && quien.puesto === "gerencia") recordarGerencia(false);""",
       "al salir de la Jefa, se olvida")

cambia("v-2026-10-26-75", "v-2026-10-26-76", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")
sys.exit(0 if fallos == 0 else 1)
