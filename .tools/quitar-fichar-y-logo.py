"""Quita la tarea de fichar, quita el reloj, y pone el logo verde en la caja blanca."""
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------- 1) fuera «Fichar» del catálogo
p = r".tools/generar-tienda.py"
t = open(p, encoding="utf-8").read()
antes = t
lineas = [l for l in t.splitlines(keepends=True)
          if not l.strip().startswith('{"t": "Fichar"')]
t = "".join(lineas)
if t != antes:
    open(p, "w", encoding="utf-8").write(t)
    print("  tienda: tarea «Fichar» quitada del catálogo")
else:
    print("  tienda: no encontré la tarea «Fichar»")

# ---------------------------------------------------- 2) fuera el reloj del fichaje
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
antes = t

# el fichaje al entrar: se quita
t = t.replace(
    '''  try{
    await fetch("/api/fichar", { method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ quien: quien.id, puesto: quien.puesto }) });
  }catch(e){}''',
    '''  /* ya no se apunta la hora: la app ya sabe el turno por la plantilla */''')

# el fichaje al salir: se quita
t = t.replace(
    '''  try { await fetch("/api/fichar", { method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({ quien: quien.id, puesto: quien.puesto, salir: true }) }); } catch(e){}''',
    '''  /* sin reloj: el turno lo pone la plantilla */''')

# ---------------------------------------------------- 3) el logo verde en la caja blanca
t = t.replace(
    '<div class="logo"><img src="__LOGO__" alt=""></div>',
    '<div class="logo"><img src="__LOGO_VERDE__" alt=""></div>')
t = t.replace(
    'html = HTML.replace("__LOGO__", _LOGO_URI)',
    '_LOGO_VERDE = "data:image/png;base64," + __import__("base64").b64encode(\n'
    '    open("docs/marca/logo-o-verde.png", "rb").read()).decode()\n'
    'html = HTML.replace("__LOGO_VERDE__", _LOGO_VERDE).replace("__LOGO__", _LOGO_URI)')

if t == antes:
    print("  app: SIN CAMBIOS (revisar)")
else:
    open(p, "w", encoding="utf-8").write(t)
    print("  app: reloj quitado y logo verde en la cabecera")
