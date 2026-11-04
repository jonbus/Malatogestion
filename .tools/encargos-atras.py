"""Que al entrar en encargos, y al darle a atrás, se vuelva a los tres botones.

Dos puertas:
  · abrirCal("encargos") — el botón del calendario
  · vuelveVista        — el botón de atrás del navegador

Las dos tienen que limpiar el estado de encargos, o te quedas dentro de Zuaza.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if t.count(v) == 1:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    elif t.count(v) == 0:
        print("  NO ENCONTRADO: " + e)
    else:
        print(f"  OJO, aparece {t.count(v)} veces: " + e)


# --- 1 · el botón del calendario
rep("""function abrirCal(k){
  calBloque = (calBloque === k) ? "" : k;""",
    """function abrirCal(k){
  calBloque = (calBloque === k) ? "" : k;
  /* al entrar en encargos, siempre por los tres botones */
  if(calBloque === "encargos"){ formEncargo = false; encProveedor = ""; resumenEncargos = false; }""",
    "abrirCal limpia el estado de encargos")

# --- 2 · el botón de atrás del navegador
rep("""function vuelveVista(s){
  s = s || {};""",
    """function vuelveVista(s){
  s = s || {};
  /* atrás es subir un escalón: se cierra el bloque del calendario y encargos vuelve al principio */
  calBloque = "";
  formEncargo = false; encProveedor = ""; resumenEncargos = false;""",
    "atrás vuelve a los tres botones")

rep("v-2026-10-26-94", "v-2026-10-26-95", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
