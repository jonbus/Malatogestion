# Zuaza · el pan

> **Segundo proveedor de pan, con su propio registro.** **Se apunta como la Tahona, pero al revés y solo de miércoles a domingo.**

---

## 1 · El pan

| Pan | Precio |
|---|---|
| **Casero** | 3,65 € |
| **Barra Casera** | 2,15 € |
| **Molde** | 3,65 € |
| **Integral** | 3,15 € |
| **Cereales** | 3,85 € |
| **Maíz** | 3,85 € |
| **Pasas/Nueces** | 4,65 € |
| **Txoripan** | 1,85 € |

**Proveedor**: **Zuaza** — **Patxi** — **635 73 99 26**

**Llega de MIÉRCOLES a DOMINGO.** **Lunes y martes no hay pan de Zuaza.**

---

## 2 · El orden de apuntarlo — y es al revés que la Tahona

**En la Tahona** primero entra y luego se devuelve. **En Zuaza es al contrario:**

```
1º  LAS DEVOLUCIONES   (lo que sobra del día anterior)
2º  LO QUE LLEGA       (lo que trae el repartidor hoy)
```

**Los dos los apunta COORDINACIÓN.** **Y en ese orden**, **que es el orden en que pasan las cosas**: **primero se recoge lo de ayer, después se recibe lo de hoy**.

> **Es importante que el orden esté claro en la pantalla**: **si se apunta primero lo que llega, la devolución se mezcla con lo nuevo y el número deja de valer.**

---

## 3 · El registro del día

**Para cada día que hay pan:**

| | Qué se apunta |
|---|---|
| **Devoluciones** | **cuántas unidades de cada pan** se devuelven |
| **Entradas** | **cuántas unidades de cada pan** llegan |

**Los ocho panes siempre a la vista**, **aunque queden a cero** — **un pan que no aparece no se sabe si es que no hay o es que nadie lo apuntó.**

**Se puede corregir**: **un día se apunta, se modifica y se borra** — **como todo lo demás**.

---

## 4 · El informe mensual

**Del día 1 al último del mes.** **Y solo cuenta de MIÉRCOLES a DOMINGO** — **los lunes y martes no existen para este informe.**

```
INFORME DE ZUAZA · NOVIEMBRE 2026

              ENTRADAS          DEVOLUCIONES
Casero            120                 14
Barra Casera      340                 22
Molde               80                  6
...
TOTAL unidades    680                 48
TOTAL euros    2.014,50 €          128,40 €
```

**Dos sumas separadas, nunca mezcladas** ✓ — **y el neto** (*entradas − devoluciones*) **como dato de abajo**, **pero no como el único número**.

> **Por qué separadas**: **el pan que entra y el que vuelve son dos cosas distintas**. **Si solo se mira el neto, se pierde la información de cuánto se ha devuelto** — **que es justo lo que dice si el pedido está bien ajustado.**

**Y la comprobación del mes**: **¿cuántos días de miércoles a domingo ha habido?** **Si han sido 20 y el informe dice 18**, **faltan dos días sin apuntar**.

---

## 5 · El pedido de mañana, por WhatsApp

**Al final del día se manda el resumen del pedido del día siguiente a Patxi** (635 73 99 26).

```
Buenos días Patxi:

Pedido para mañana, jueves 12:

Casero           20
Barra Casera     60
Molde            10
Integral         15
Cereales         10
Maíz              8
Pasas/Nueces      6
Txoripan         24

Gracias.
```

**Con un botón que abra WhatsApp con el mensaje ya escrito** — **solo hay que dar a enviar.**

> **Así no hay que copiar nada, y no se puede mandar un mensaje a medias.**

**Y un aviso**: **si es lunes o martes, no hay pedido** — **el botón de mandar tiene que desaparecer esos días**, **no salir en gris**. **Un botón gris invita a pulsarlo.**

---

## 6 · Lo que hay que construir

| | |
|---|---|
| **En el servidor** | guardar `zuaza` por día: **devoluciones** y **entradas** · poder **borrar** un día · **no perder** lo que ya hay |
| **En la pantalla** | **apartado Zuaza** dentro de encargos · **los ocho panes** · **primero devoluciones, después entradas** · **selector de día** |
| **El informe** | **mensual**, **solo de miércoles a domingo**, **entradas por un lado y devoluciones por otro**, **con los días apuntados y los que faltan** |
| **El WhatsApp** | **botón que abre el mensaje escrito** con el pedido de mañana |

**Y en los dos sitios**: **Cloudflare y el Orange Pi** — **son dos copias de la aplicación y hay que tocar las dos.**
