# Encargos por proveedor · Zuaza, Tahona y Varios

> **Lo que hay hoy**: un botón de encargos que abre una lista donde se escribe un
> texto libre.
>
> **Lo que queremos**: dentro de encargos, **un botón por proveedor**, con sus
> productos en un desplegable, y un resumen por días para mandar el pedido.

---

## 1 · La pantalla

**Calendario → 📦 Encargos** y, dentro, **los botones de arriba**:

```
┌─────────┐ ┌─────────┐ ┌─────────┐
│  Zuaza  │ │ Tahona  │ │ Varios  │
└─────────┘ └─────────┘ └─────────┘
```

- **Zuaza** — los 8 panes de Zuaza
- **Tahona** — los 5 panes de la Tahona
- **Varios** — **lo que haya que pedir y no es pan**: el encargo libre de siempre
- **Y se añadirán más** cuando haga falta: **la lista de botones está en un solo sitio del código**, así que añadir uno es una línea

**Esto es lo mismo que se acaba de hacer en el registro de panes** — **Tahona y Zuaza conviviendo bajo un botón** — **y ya sabemos que funciona.**

---

## 2 · El formulario de cada botón

| Campo | Cómo |
|---|---|
| **Producto** | **desplegable**, solo con los suyos |
| **Cantidad** | **número** |
| **Observaciones** | **texto libre** — **se puede escribir lo que sea** |
| **Fecha** | **el día para el que es el encargo** |

**Y se guarda como un encargo más**, con **su fecha, su puesto y quién lo apuntó** ✓ — **que es lo que ya hace.**

**Lo que hay que añadir al guardar**: **el producto**, **la cantidad** y **la observación**. **El primero y el segundo ya los guarda el servidor** *(se hizo esta tarde)*; **la observación es nueva y hay que añadirla.**

---

## 3 · El resumen — y aquí está lo importante

**Debajo de los botones, un sitio reservado para el resumen de los encargos que vienen, vistos por días:**

```
PENDIENTES

MIÉRCOLES 5
   Zuaza    20 Casero · 60 Barra Casera · 10 Molde
   Tahona   10 Txapata

JUEVES 6
   Zuaza    24 Txoripan
   Varios   (lo que sea)
```

**Agrupado por día**, **y dentro de cada día, por proveedor** — **que es como se hace el pedido**: *«para el jueves, esto de Zuaza y esto de Tahona»*.

**Y ese mismo resumen será el que se mande por WhatsApp al proveedor.** **Por eso hay que hacerlo bien ahora**: **si el resumen está mal agrupado, el pedido sale mal.**

---

## 4 · Lo que hay que tocar

| | |
|---|---|
| **El servidor** | guardar también **la observación** del encargo |
| **La pantalla** | **los botones**, **el desplegable de cada proveedor**, **cantidad y observaciones** |
| **El resumen** | **agrupado por día y por proveedor** — **primero en pantalla, después el WhatsApp** |

**Y en los dos sitios**: **Cloudflare y el Orange Pi**.

---

## 5 · Un aviso que viene de esta tarde

**Tres veces se ha roto la aplicación por tocar dos cosas a la vez.** **Y todas las veces lo encontró la propiedad, no yo.**

> **Así que esto va en dos bloques**: **primero los botones y el formulario** *(que ya se guarda)* · **después el resumen** *(que es leer y agrupar)*.

**El primero se puede usar desde el minuto uno** — **el pedido ya queda apuntado, aunque el resumen todavía no esté.**

---

## 6 · Lo que ya está decidido

| | |
|---|---|
| **«Varios»** | **NO lleva cantidad** — **es texto libre, como ahora** |
| **El resumen** | **enseña TODO, también los días pasados** — **para poder comprobar cualquier cosa en cualquier momento** |
| **La observación** | **se ve en el resumen** |

> **Y lo de «enseña todo» tiene una consecuencia buena**: **el resumen no es solo para pedir, es también el histórico**. **Si un día alguien pregunta «¿qué pedimos el jueves pasado?», se mira ahí.**
