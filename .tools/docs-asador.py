"""Un documento por cada producto del asador, con las palabras de la propiedad.

Salen de AsadorPollosCodillosCostilla.doc. No se cambia ni una palabra: solo se
ordena para que luego la aplicación lo pueda enseñar.
"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

DESTINO = os.path.join("docs", "asador")
os.makedirs(DESTINO, exist_ok=True)

PRODUCTOS = {
    "pollo": {
        "nombre": "Pollo",
        "emoji": "🍗",
        "tiempo": "2,5 horas en total",
        "cuerpo": """## Antes de meterlo al asador

- Se limpian por dentro y por fuera
- Se colocan los muslos
- Se les mete el relleno:
  1. **Sal**
  2. **Condimento** (ajo, perejil, guindilla, aceite, vinagre)
- Se trinchan en las barras (**máximo 6**)
- Se meten al asador

## Cuando están dentro del asador

- Se riegan continuamente con **agua**
- Se riegan continuamente con **su propia salsa**

## Antes de sacarlos

- Se riegan con agua y se les echa **Brandy** (oscuro)
- Esperamos **5 minutos**
- Se riegan con agua y se le echa **Vino Blanco** (claro)
- Esperamos **5 minutos** y se sacan

> **TIEMPO: 2,5 horas en total**
""",
    },
    "codillo": {
        "nombre": "Codillo",
        "emoji": "🍖",
        "tiempo": "2 horas en total",
        "cuerpo": """## Antes de meterlo al asador

- Se limpian bien por fuera y **se les quita toda la gelatina**
- Se meten en la jaula (**máximo 4**)
- Para cerrar la jaula **pedimos ayuda**
- Se meten al asador

## Cuando están dentro del asador

- Se riegan continuamente con **agua**
- Se riegan continuamente con **su propia salsa**

## Antes de sacarlos

- Se riegan con agua y se les echa **Brandy** (oscuro)
- Esperamos **5 minutos**
- Se riegan con agua y se le echa **Vino Blanco** (claro)
- Esperamos **5 minutos** y se sacan

> **TIEMPO: 2 horas en total**
""",
    },
    "costilla": {
        "nombre": "Costilla",
        "emoji": "🥩",
        "tiempo": "2 horas en total, más 1 hora de reposo",
        "cuerpo": """## Antes de meterla al asador

- **Una ración es 1 kg**
- Se pica **ajo** y lo echamos al mortero
- Se pica **perejil** y lo echamos al mortero
- Se añade **una pizca de sal** al mortero
- Machacamos bien hasta que se haga **puré**
- Añadimos **aceite** y revolvemos hasta que sea homogéneo
- Le echamos un poco de **sal** a la costilla
- Untamos la costilla con el preparado del mortero
- Dejamos reposar **1 hora aprox en cámara** (nevera)

## Para meterla: dos formas

### Opción A

- Se les clava el cuchillo **en forma de X** cada 2-3 huesos
- Se trincha en las barras **como si fuera una acordeón**
- Se meten al asador

### Opción B

- Se meten en una jaula
- Para cerrar la jaula **pedimos ayuda**
- Se meten al asador

## Cuando están dentro del asador

- Se riegan continuamente con **agua**
- Se riegan continuamente con **su propia salsa**

## Antes de sacarlas

- Se riegan con agua y se les echa **Brandy** (oscuro)
- Esperamos **5 minutos**
- Se riegan con agua y se le echa **Vino Blanco** (claro)
- Esperamos **5 minutos** y se sacan

> **TIEMPO: 2 horas en total**
""",
    },
    "patatas-fritas": {
        "nombre": "Patatas fritas",
        "emoji": "🍟",
        "tiempo": "30 minutos antes del primer encargo",
        "cuerpo": """> ⚠ **Las patatas fritas son SIN GLUTEN**, con lo cual **sólo se pueden hacer en SU FREIDORA**,
> al igual que **esa freidora sólo se puede utilizar para HACER PATATAS** (ningún otro frito).

## 30 minutos antes del primer encargo con patatas

- Se calcula el **total de raciones** (el peso total) que hay encargadas
- Se sacan en **una bandeja** todas juntas

## 20 minutos antes

- Se enciende la **freidora de PATATAS** (sin gluten)
- Cuando **se apaga la luz roja**, ha llegado a la temperatura necesaria y es cuando
  empezamos a freír todas las patatas
- Al mismo tiempo que empezamos a freír, **encendemos la mantenedora de calor**

## Sacar de la freidora

- Cuando las patatas estén hechas, se sacarán a **SU BANDEJA** de aluminio
  a la que habremos puesto un **PAPEL SECANTE**
- De la bandeja de aluminio se pasan a la **mantenedora de calor**

## Mantenedora de calor

- **Cada 10 minutos** se revuelven las patatas que estén en el recipiente de la mantenedora,
  de manera que **no se nos queden pasadas** y que las **mezclemos continuamente**

## Sale el pedido

- Cuando nos toque sacar patatas, se cogerán **directamente de la mantenedora**
  en el envase que le corresponda
""",
    },
}

for clave, p in PRODUCTOS.items():
    ruta = os.path.join(DESTINO, clave + ".md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"# {p['emoji']} {p['nombre']}\n\n")
        f.write("> **Instrucciones del asador.** Las palabras son las de la propiedad.\n\n")
        f.write(p["cuerpo"])
        f.write("\n---\n\n")
        f.write("## Resumen\n\n")
        f.write(f"| | |\n|---|---|\n| **Producto** | {p['emoji']} {p['nombre']} |\n")
        f.write(f"| **Tiempo** | {p['tiempo']} |\n")
    print(f"  escrito {ruta}")

# el índice, que es lo que verá el botón
lineas = ["# 🔥 Asador", "",
          "> **Cómo se asan los productos.** Un documento por producto.",
          "> Las palabras son las de la propiedad: no se han cambiado.", "",
          "## Los productos", ""]
for clave, p in PRODUCTOS.items():
    lineas.append(f"| {p['emoji']} | **{p['nombre']}** | {p['tiempo']} | [{clave}.md]({clave}.md) |")
lineas += ["", "---", "",
           "## Cómo se va a ver en la aplicación", "",
           "**Un botón: «🔥 Instrucciones del asador». Al pinchar, los productos con su dibujo:**", "",
           "```",
           "🔥 INSTRUCCIONES DEL ASADOR",
           "",
           "┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐",
           "│    🍗    │ │    🍖    │ │    🥩    │ │    🍟    │",
           "│  Pollo   │ │ Codillo  │ │ Costilla │ │ Patatas  │",
           "└──────────┘ └──────────┘ └──────────┘ └──────────┘",
           "```",
           "",
           "**Y al pinchar en uno, sus instrucciones, con su tiempo arriba.**", ""]

with open(os.path.join(DESTINO, "index.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lineas))
print(f"  escrito {os.path.join(DESTINO, 'index.md')}")
print(f"\n  productos: {len(PRODUCTOS)}")
