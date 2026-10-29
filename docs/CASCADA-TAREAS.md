# Tareas en cascada

> **Una tarea que, al hacerse, hace nacer la siguiente.**
> *Cortar chorizo ibérico* (coordinación o la Jefa) → al tacharla **nace** *Envasar* (tienda).
> **Y hasta que no se corta, «Envasar» no existe.**

---

## 1 · Lo que ya está hecho y sirve de base

**Esto no se empieza de cero.** **La cascada ya funciona** en dos sitios:

| Dónde | Qué pasa |
|---|---|
| **Las ofertas** | Se prepara la oferta (Jefa) → **al tacharla** nacen la de coordinación y la de cartelería |
| **Los encargos** | Se marca «pedido hecho» → **al marcarlo** nace la de recibir |

**Y en los dos casos hay una cosa en común que es la clave:**

> **El hijo NO EXISTE hasta que el padre se hace.** No está «pendiente»: **no está**.

**Eso es lo que hay que llevar a las tareas normales.**

---

## 2 · Cómo se monta desde la aplicación

**En la tarea, un botón: «Cuando se haga, crear…»**

```
┌────────────────────────────────────────────────────────────┐
│ Cortar chorizo ibérico                                     │
│                                                            │
│ Cuando se haga, crear…                                     │
│   Qué      [ Envasar                                     ] │
│   Para     [ Tienda ▾ ]                                    │
│   Cuándo   [ Ese mismo día ▾ ]                             │
│            · el mismo día                                  │
│            · al día siguiente                              │
│            · en 2 días                                     │
│            · en una semana                                 │
│   Turno    [ Tarde ▾ ]                                     │
│                                                            │
│                                    [ Guardar la cascada ]  │
└────────────────────────────────────────────────────────────┘
```

**Y una tarea puede tener **varias**: cortar → envasar, y además → etiquetar.

---

## 3 · Qué se guarda

**La cascada va pegada a la tarea que la lanza**, no suelta:

```js
cascadas: {
  "cortar chorizo iberico": [
    { que: "Envasar", p: "tienda", turno: "tarde", cuando: 0 },   // 0 = ese día
    { que: "Etiquetar", p: "tienda", cuando: 1 }                 // 1 = al día siguiente
  ]
}
```

**La llave es el texto de la tarea**, normalizado (minúsculas, sin acentos).
**Así funciona igual** con una tarea del día que con una tarea extra.

---

## 4 · Los tres casos que hay que resolver

### a · Si el hijo ya existía
**No se duplica.** *Si «Envasar» ya está puesta para ese día, no se crea otra.*

### b · Si se destacha el padre
**El hijo no se borra.** *Porque puede estar ya empezado o hecho.*
**Lo que hace es avisar**: *«Has deshecho "Cortar chorizo". "Envasar" sigue puesta.»*

**Borrar trabajo hecho por deshacer un tic sería peor que dejarlo.**

### c · Si el padre es de un día pasado y se tacha tarde
**El hijo nace igual**, con la fecha que le toque. **Si esa fecha ya pasó, nace para hoy.**

**Nunca se crea algo en el pasado.**

---

## 5 · Dónde se ve la cadena

**En la tarea, una línea pequeña debajo:**

```
☐ Cortar chorizo ibérico
    cuando se haga → Envasar (tienda, tarde)           ⌫ quitar
```

**Y en el hijo, de dónde viene:**

```
☐ Envasar
    viene de «Cortar chorizo ibérico»
```

> **Con eso se puede seguir la cadena de un vistazo**, sin abrir nada.

---

## 6 · Y si no da tiempo

**El hijo se puede pasar de fecha como cualquier otra tarea** — **ya funciona** con el «si no da tiempo» de las extra.
**Y para las del día hace falta añadirlo** *(hoy no lo tienen)*. **Va en la misma tanda.**

---

## 7 · Lo que hay que decidir

| # | Pregunta |
|---|---|
| **1** | **¿La cascada se monta desde una tarea que ya existe** (botón «cuando se haga…») **o se crea la cadena entera de una vez** (padre + hijos en el mismo formulario)? |
| **2** | **¿Quién puede montar una cascada?** ¿Cualquiera, o solo coordinación y la Jefa? |
| **3** | **¿Un hijo puede ser a su vez padre de otro?** *(cortar → envasar → etiquetar)* O **solo un salto**. |

**Mi recomendación**: **el punto 1, las dos**: montarla desde la tarea **y** poder crear la cadena entera de golpe.
**Y en el punto 3, sí a las cadenas largas** — **sale gratis si está bien puesto**, y **la realidad de la tienda tiene eslabones**.

---

## 8 · Cómo se probaría

**Con el mismo método que hoy**: **simular la tarea padre, tacharla, y comprobar que el hijo nace** — sin navegador y sin tocar tus datos.

```
tachar «Cortar chorizo»       →  nace «Envasar» para tienda, tarde
tacharlo dos veces            →  no se duplica
destachar el padre            →  el hijo sigue ahí y avisa
tachar un padre de ayer       →  el hijo nace para hoy, no en el pasado
```

**Las cuatro pruebas, escritas antes de tocar la pantalla.**
