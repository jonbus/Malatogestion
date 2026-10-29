# La Tahona

> **El pan del panadero.** Entra por la mañana, se devuelve lo que no se vende, y a fin de mes
> se le pasa el resumen para cotejar con su factura.

---

## 1 · Los cinco panes

| Pan | |
|---|---|
| **Txapata** | |
| **Txapatita** | |
| **Barra** | |
| **Cuarto** | |
| **Txoripan** | |

**Se cuentan en unidades**, uno a uno. *No son importes.*

---

## 2 · Quién apunta qué

| Puesto | Cuándo | Tarea |
|---|---|---|
| **Coordinación** | **Por la mañana** | **Tahona · entrada del pan** — lo que trae el panadero |
| **Tienda** | **Por la tarde** | **Tahona · devolución** — lo que se le devuelve |

**Los dos apuntan los cinco panes.** La entrada y la devolución **del mismo día se guardan juntas**:
cada una en su parte, sin pisarse.

**Un valor que no vale** (un negativo, un texto) **se guarda vacío**, no a cero. **Cero significa
«no vino nada», y eso es un dato** — no lo mismo que «no se apuntó».

---

## 3 · El resumen

**Solo lo ve la Jefa**, y **solo entre el día 1 y el 5 del mes siguiente**.

```
Tahona · resumen de octubre          entradas menos devoluciones · para cotejar la factura
  Pan         Entra   Sale   Queda
  Txapata       420     38     382
  Txapatita     240     21     219
  Barra         850     96     754
  Cuarto        315     30     285
  Txoripan      168      9     159
  Total       1.993    194   1.799
```

**Del mes anterior**, no del actual: si hoy es 3 de noviembre, **ves octubre**.

---

## 4 · Lo que falta: los precios

**La propiedad dará los precios más adelante.** Con ellos, el resumen podrá enseñar **el importe**
además de las unidades, y **cuadrar con la factura del panadero**.

**Lo que ya sabemos de cómo funcionan:**

> **«Los precios netos parten de un precio al que se le aplica un descuento.»**

Es decir: **precio neto = precio − descuento**. Cuando lleguen los datos habrá que saber:

1. **El precio de cada uno de los cinco panes**
2. **El descuento** — si es un porcentaje o un importe, y **si es el mismo para todos**
3. **Si el descuento depende del pan** o es único

**Con eso, el resumen añadiría una columna de euros** y el total a pagar.

**Y ojo a una cosa que hay que decidir entonces**: el panadero factura **lo entregado menos lo devuelto**,
así que **el importe se calcula sobre el neto de unidades**, no sobre lo entregado.

---

## 5 · Dónde está en el código

| Qué | Dónde |
|---|---|
| **Los cinco panes** | `PANES_TAHONA` en el generador de la nube |
| **El guardado** | `POST /api/tahona` en `nucleo.js` |
| **Los datos** | `estado.tahona["AAAA-MM-DD"] = { entrada: {...}, devolucion: {...} }` |
| **El resumen** | `bloqueTahonaResumen()` |
| **Las pruebas** | `node .tools\probar-tahona.mjs` |
