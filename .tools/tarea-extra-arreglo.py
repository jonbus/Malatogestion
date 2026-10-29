"""Los campos de la tarea extra llevan su orden dentro, y se limpia la prueba."""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

# ============================================================ 1 · la app
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


cambia('<input type="text" id="tarea-txt" maxlength="200"',
       '<input type="text" id="tarea-txt" oninput="textoTarea=this.value" maxlength="200"',
       "el texto de la tarea extra")

cambia('<select id="tarea-puesto">',
       '<select id="tarea-puesto" onchange="puestoTarea=this.value">',
       "el puesto")

cambia('<select id="tarea-turno">',
       '<select id="tarea-turno" onchange="turnoTarea=this.value">',
       "el turno")

cambia('<select id="tarea-tipo"', '<select id="tarea-tipo" onchange="tipoTarea=this.value"',
       "el tipo")

cambia('<button id="tarea-add" class="btn-add" type="button">Añadir</button>',
       '<button id="tarea-add" class="btn-add" type="button" ' +
       'onclick="anadirTareaExtra()">Añadir</button>',
       "el botón de añadir")

cambia('<button id="btn-nueva-tarea" class="btn-add-2" type="button">',
       '<button id="btn-nueva-tarea" class="btn-add-2" type="button" ' +
       'onclick="formTarea=!formTarea; pinta()">',
       "el botón de abrir el formulario")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  fallos: {fallos}")

# ============================================================ 2 · la basura de las pruebas
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0"}
BASE = "https://app.supermalato.workers.dev"
estado = json.loads(urllib.request.urlopen(urllib.request.Request(
    BASE + "/api/estado", headers=UA), timeout=20).read())

print("\n  === tareas extra que hay ===")
for x in estado.get("encargos") or []:
    marca = "HECHA" if x.get("hecho") else "pendiente"
    print(f"    {x.get('f')} · {x.get('p')} · turno {x.get('turno')} · {marca}")
    print(f"      «{x.get('t')}»")

# las de prueba son las que llevan CF- o PRUEBA
borradas = 0
for x in estado.get("encargos") or []:
    txt = str(x.get("t") or "")
    if "CF-" in txt or txt.startswith("PRUEBA"):
        cuerpo = json.dumps({"id": x["id"]}).encode()
        urllib.request.urlopen(urllib.request.Request(
            BASE + "/api/encargo-borrar", data=cuerpo, method="POST",
            headers={**UA, "Content-Type": "application/json"}), timeout=20)
        print(f"    borrada la de prueba: «{txt}»")
        borradas += 1
print(f"\n  borradas {borradas} de prueba")
sys.exit(0 if fallos == 0 else 1)
