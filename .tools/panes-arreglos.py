"""Dos cambios en el registro de panes:

1 · El Enter baja a la casilla de debajo (misma columna), no a la de al lado.
2 · El orden de los panes de Zuaza, el que ha dicho la propiedad.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools\generar-nube.py"
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


# --- 1 · el orden de Zuaza (los precios no se tocan)
VIEJO = """const PANES_ZUAZA = [
  ["casero", "Casero", "3,65"],
  ["barra_casera", "Barra Casera", "2,15"],
  ["molde", "Molde", "3,65"],
  ["integral", "Integral", "3,15"],
  ["cereales", "Cereales", "3,85"],
  ["maiz", "Maíz", "3,85"],
  ["pasas_nueces", "Pasas/Nueces", "4,65"],
  ["txoripan", "Txoripan", "1,85"]
];"""

NUEVO = """const PANES_ZUAZA = [
  ["casero", "Casero", "3,65"],
  ["pasas_nueces", "Pasas/Nueces", "4,65"],
  ["integral", "Integral", "3,15"],
  ["txoripan", "Txoripan", "1,85"],
  ["molde", "Molde", "3,65"],
  ["barra_casera", "Barra Casera", "2,15"],
  ["cereales", "Cereales", "3,85"],
  ["maiz", "Maíz", "3,85"]
];"""

rep(VIEJO, NUEVO, "el orden de los panes de Zuaza")

# --- 2 · el Enter, hacia abajo
ANCLA = '/* ------------------------------------------------ EL NÚMERO GRANDE DEL DÍA'
if ANCLA not in t:
    ANCLA = "function euros(n){"

ENTRADA = """/* ------------------------------------------------ EL ENTER, HACIA ABAJO
   En las casillas del pan, el Enter va a la de debajo (la misma columna),
   no a la de al lado. Se busca la siguiente casilla que tenga el mismo
   principio de identificador (tahE-, tahD-, z-d-, z-e-...). */
document.addEventListener("keydown", function(ev){
  if(ev.key !== "Enter") return;
  const el = ev.target;
  if(!el || el.tagName !== "INPUT" || !el.id) return;
  const m = el.id.match(/^([a-zA-Z]+-)(.+)$/);
  if(!m) return;
  ev.preventDefault();
  const prefijo = m[1];
  const casillas = Array.prototype.filter.call(
    document.querySelectorAll('input'),
    x => x.id && x.id.indexOf(prefijo) === 0 && x.offsetParent !== null
  );
  const i = casillas.indexOf(el);
  if(i >= 0 && i + 1 < casillas.length) casillas[i + 1].focus();
});

"""

rep(ANCLA, ENTRADA + ANCLA, "el Enter, que baje")

t = t.replace("v-2026-10-26-99", "v-2026-10-27-100", 1)

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
