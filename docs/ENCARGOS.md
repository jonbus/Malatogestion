# Encargos

> **Lo que hay que tener preparado un día, y que a veces hay que pedir antes.**
> No es una tarea del día: es **algo que tiene fecha** y que **necesita un aviso previo**
> para que esté listo a tiempo.

---

## 1 · La diferencia con las tareas extra

| | Tarea extra | **Encargo** |
|---|---|---|
| **Qué es** | Algo que hay que hacer | **Algo que hay que tener** |
| **Cuándo** | Un día | **Un día, y a veces se pide antes** |
| **Quién** | Un puesto | **El que lo pide y el que lo recibe** |
| **Si no se hace** | Se pasa a otro día | **No hay segunda oportunidad**: si no se pidió, no está |

> **Por eso tiene que llamar la atención.** Si un encargo pasa desapercibido,
> **el día que hace falta no hay forma de conseguirlo.**

---

## 2 · Los dos calendarios

**Ahora hay uno solo, con las notas generales y las personales juntas.** Van separados:

| | Dónde | Qué lleva |
|---|---|---|
| **Calendario general** | **Pantalla principal** (la pestaña General) | **Encargos**, notas generales, y lo de todos |
| **Calendario personal** | **En la pantalla de cada una** | **Lo suyo**: sus notas personales |

**El general lo ve todo el mundo. El personal, solo su dueña.**

---

## 3 · Cómo se da de alta un encargo

**Un botón en el calendario general: «+ Añadir un encargo».**

Y un formulario con **cinco cosas**:

```
┌────────────────────────────────────────────────────────────┐
│ Qué es        [ Tarta de cumpleaños de 20 raciones        ] │
│ Para el día   [ 2026-11-07 ]                                │
│                                                             │
│ ¿Hay que pedirlo antes?        ( ) No   (•) Sí              │
│                                                             │
│   ── solo si hay que pedirlo ──                             │
│   Quién lo pide   [ Coordinación ▾ ]                        │
│   Qué día lo pide [ 2026-11-03 ]                            │
│                                                             │
│                                        [ Dar de alta ]      │
└────────────────────────────────────────────────────────────┘
```

**«¿Hay que pedirlo antes?»** es lo que decide todo:

- **No** → el encargo **solo aparece el día que hace falta**, en la pantalla de quien corresponda.
- **Sí** → **además** nace **un aviso para pedirlo** en la pantalla de **quien lo pide**,
  **el día que toca pedirlo**.

---

## 4 · La cascada

```
DÍA DE PEDIR (3/11)                    DÍA DE ENTREGAR (7/11)
┌──────────────────────────┐          ┌──────────────────────────┐
│  ⚠ PEDIR HOY             │          │  ✓ Tarta de cumpleaños   │
│                          │          │    20 raciones           │
│  Tarta de cumpleaños     │  ──────► │    Ya tiene que estar    │
│  20 raciones             │          │                          │
│  Para el viernes 7       │          │                          │
│                          │          │                          │
│  [ Pedido hecho ]        │          │  [ Recibido ]            │
└──────────────────────────┘          └──────────────────────────┘
   Coordinación                          Quien lo recibe
```

**No se puede marcar «recibido» si antes no se marcó «pedido».** *Esa es la cascada.*

---

## 5 · Que se vea de verdad

**Esto es lo más importante del módulo.** Un aviso que no se ve, no sirve.

| Dónde | Cómo |
|---|---|
| **En la pantalla del día** | **Arriba del todo**, como «Para arreglar» |
| **Color** | **Ámbar fuerte**, con **raya a la izquierda** |
| **La marca** | **«PEDIR HOY»** en mayúsculas, si toca pedir |
| **Si es hoy y no se ha pedido** | **Rojo**, y **no se puede quitar** hasta marcarlo |

```
╔══════════════════════════════════════════════════════════╗
║  ⚠  PEDIR HOY · PARA EL VIERNES 7                        ║
║                                                          ║
║  Tarta de cumpleaños de 20 raciones                      ║
║                                                          ║
║  [ Pedido hecho ]                                        ║
╚══════════════════════════════════════════════════════════╝
```

**Los que se pueden pedir hoy van en un bloque propio, el primero de la pantalla**
— por encima incluso de «Para arreglar».

---

## 6 · Lo que hay que decidir antes de construirlo

| # | Pregunta | Por qué |
|---|---|---|
| **1** | **¿Quién puede dar de alta un encargo?** ¿Cualquiera, o solo coordinación y gerencia? | Cambia el botón y los permisos |
| **2** | **¿Quién puede ser «quien lo pide»?** ¿Coordinación, la Jefa, o también tienda? | El desplegable |
| **3** | **¿Y quién lo recibe?** ¿El que lo pidió, o un puesto fijo? | A quién le sale el día de la entrega |
| **4** | **¿Se puede pedir el mismo día?** ¿O siempre con antelación? | Si hay que poner un mínimo |
| **5** | **¿Qué pasa si llega el día de entregar y no se marcó «pedido»?** | Avisar en rojo, o dejarlo pasar |
| **6** | **¿Los encargos son de cliente o internos?** ¿Hay que apuntar para quién? | Si hace falta un campo más |

---

## 7 · Lo que NO entra en la primera versión

- **Cantidades e importes** — primero que funcione el aviso
- **Proveedores** — el encargo dice qué, no a quién se le compra
- **Repetir un encargo** todos los meses
- **Avisos al móvil** por notificación

**Se puede añadir después sin rehacer nada**, si el modelo está bien puesto.

---

## 8 · Cómo se guardará

```js
encargosFecha: {
  "id-a": {
    que: "Tarta de cumpleaños de 20 raciones",
    para: "2026-11-07",          // el día que hace falta
    pideAntes: true,             // ¿hay que pedirlo?
    quienPide: "coordinacion",   // quién lo pide
    diaPedir: "2026-11-03",      // el día que toca pedirlo
    q: "ge1",                    // quién lo dio de alta
    pedido: false,               // ¿ya se pidió?
    recibido: false              // ¿ya llegó?
  }
}
```

**Y la cascada no se guarda**: **se deduce** de `pideAntes`, `diaPedir` y `para`.
**Un dato, no dos.** *Si se guardara en dos sitios, se podrían contradecir.*
