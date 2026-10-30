"""Añade la decoración de globos al manual y renumera lo que va detrás."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"docs\ANIVERSARIO-PROCEDIMIENTO.md"
t = open(p, encoding="utf-8").read()

NUEVA = """## 3 · La decoración de globos

**Se monta con el compresor, y se empieza el jueves.** **Se deja en el almacén y el mismo día se sube.**

### Cómo se monta

- [ ] **Sacar el compresor** y comprobar que sopla
- [ ] **Ir inflando y montando por partes**, no todo al final
- [ ] **Dejar cada pieza terminada y atada** — **una pieza a medias no se puede mover**
- [ ] **Apuntar cuántos globos entran en cada pieza** — para poder reponer el día del evento
- [ ] **Dejarlo todo en el almacén**, en el sitio donde no se pise

### El día: subirlo

- [ ] **Subir las piezas ya montadas**, no inflar en la tienda
- [ ] **Colocarlas** sin tapar la entrada ni la mesa de la tarta
- [ ] **Comprobar que no molestan al paso** — **ni a los dos niños de la puerta**
- [ ] **Repasar los globos que se hayan desinflado** y cambiarlos

### Lo que hay que tener en cuenta

> **El compresor es de AIRE, no de helio.** **Los globos no van a volar**: **van en arco, en columna o pegados a una estructura.** **Conviene decidirlo antes de empezar** — **un arco necesita su base hecha** (un alambre, un tubo, una malla), **y eso no se improvisa el jueves por la mañana**.

> **Los globos se desinflan.** **Montado el jueves, el sábado está mustio.** **Lo que se monte el jueves, que sea lo que aguanta** (estructuras, columnas); **lo que se vea de cerca, mejor el viernes por la noche o el mismo día.**

> **Y el calor**: **en el almacén, si hace calor, los globos se dilatan y revientan.** **Cuanto más frescos, mejor.**

> **Y el transporte**: **de la puerta de atrás a la tienda hay un recorrido**. **Lo que no pase por ahí, no sirve** — **comprobar el ancho de paso antes de montar nada.**

"""

# se renumera del 3 en adelante
def sube(m):
    n = int(m.group(1))
    return f"## {n + 1} ·" if n >= 3 else m.group(0)


t = re.sub(r"## (\d+) ·", sube, t)

# se inserta antes del antiguo 3 (que ahora es 4)
marca = "## 4 · La mesa de la tarta — EN ESTE ORDEN"
if marca not in t:
    print("  NO ENCONTRADO el sitio")
    sys.exit(1)
t = t.replace(marca, NUEVA + marca, 1)

# la lista de "lo que tiene que estar listo"
viejo = "| **La mesa auxiliar** | para la batukada | — | — |"
nuevo = ("| **La mesa auxiliar** | para la batukada | — | — |\n"
         "| **Los globos** | la decoración, **montada desde el jueves** | **almacén** | — |\n"
         "| **El compresor** | para inflar los globos | — | — |")
if viejo in t:
    t = t.replace(viejo, nuevo, 1)
    print("  ok  globos y compresor en la lista")
else:
    print("  NO ENCONTRADO la lista")

# la línea del tiempo
viejo2 = "| **Antes de abrir** | **Recortar y doblar las papeletas** · montar la mesa de la tarta · el picoteo · la carpa si toca |"
nuevo2 = ("| **Jueves y viernes** | **Montar los globos** con el compresor · dejarlos en el almacén |\n"
          "| **Antes de abrir** | **Subir los globos** · **recortar y doblar las papeletas** · montar la mesa de la tarta · el picoteo · la carpa si toca |")
if viejo2 in t:
    t = t.replace(viejo2, nuevo2, 1)
    print("  ok  el jueves y el viernes en el calendario")
else:
    print("  NO ENCONTRADO la linea del tiempo")

# y en "lo que no puede pasar"
viejo3 = "| **Que la batukada llegue y no haya mesa** | **el picoteo se prepara antes** |"
nuevo3 = ("| **Que la batukada llegue y no haya mesa** | **el picoteo se prepara antes** |\n"
          "| **Que los globos estén mustios** | **montados el jueves, el sábado se desinflan** |\n"
          "| **Que una pieza de globos no pase por la puerta** | **comprobar el ancho antes de montarla** |")
if viejo3 in t:
    t = t.replace(viejo3, nuevo3, 1)
    print("  ok  riesgos de los globos")

open(p, "w", encoding="utf-8").write(t)

# se comprueba que los números van seguidos
numeros = [int(x) for x in re.findall(r"^## (\d+) ·", t, re.M)]
print(f"  apartados: {numeros}")
print(f"  seguidos: {numeros == list(range(1, len(numeros) + 1))}")
