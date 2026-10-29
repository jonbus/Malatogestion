# Pedidos a proveedor

Reglas de cómo se calcula y se gestiona un pedido. **Este apartado se desarrollará más adelante**;
lo que hay aquí se ha recogido hablando de otras cosas y se guarda para no perderlo.

---

## 1 · El pedido del asador (pollos, codillos, costillas y patatas)

### Cuándo

- **El cálculo se hace los jueves a las 9:00 de la mañana.**
- **El pedido se hace por WhatsApp.**
- **El pedido llega los viernes.** Por tanto el cálculo tiene que estar hecho el jueves.

### Si hay un festivo [NEGOCIO]

- **Festivo en lunes o viernes** → **se hace un pedido más grande**, y la cantidad **sí se calcula**:
  con **el mismo método**, cruzando **la tendencia de los fines de semana** con **el mismo festivo
  del año pasado**.
- **Festivo en martes, miércoles o jueves** → **lo dice el proveedor**. Ahí **no hay cálculo
  posible**: depende de un tercero, y el sistema solo puede **crear una tarea de consulta al
  proveedor** con la antelación suficiente.

> **Corrección:** una versión anterior de este documento decía que en los festivos «la regla no se
> puede calcular». **Es falso para los festivos de lunes y viernes**: se calculan igual, cambiando la
> referencia — en vez del mismo fin de semana del año pasado, **el mismo festivo del año pasado**.
> Solo el caso de en medio (martes a jueves) queda en manos del proveedor.

### La cadena de dependencias (y por qué el dato no puede fallar)

```
Domingo por la noche   →  apuntar lo vendido el domingo
Sábado por la noche    →  apuntar lo vendido el sábado
        ↓
Jueves 9:00            →  calcular el pedido  ← NECESITA los datos del fin de semana
        ↓
Viernes                →  llega el pedido
Viernes                →  limpiar los pollos para el sábado
        ↓
Sábado 13:00           →  primer pollo servido
```

> **El fallo aparece cuatro días después.** Si nadie apuntó lo vendido el fin de semana, **no se
> descubre el jueves a las 9:00**, cuando ya se está calculando el pedido y no hay margen. Por eso el
> sistema **tiene que pedir el dato cuando toca**, no esperar a que falte.

### Cómo se calcula la cantidad

La propiedad cruza **dos series** y estima la tendencia:

1. **Lo que se vendió el mismo fin de semana del año anterior.**
2. **Los cuatro fines de semana anteriores de este año.**

> *«Se compara, se observa si la tendencia es hacia arriba o abajo y se hace un cálculo aproximado.»*

**Productos que se cuentan:** pollos · codillos · costillas · patatas.

### Ejemplo real, con los datos que dio la propiedad

| Semana | Pollos año pasado | Pollos este año | Variación |
|---|---|---|---|
| 20 | 40 | 35 | −12,5 % |
| 21 | 30 | 28 | −6,7 % |

| Semana | Codillos año pasado | Codillos este año | Variación |
|---|---|---|---|
| 20 | 4 | 4 | 0 % |
| 21 | 5 | 3 | −40 % |

**El caso de los codillos es el que justifica el método:** el año pasado **subieron** un 25 % de la
semana 20 a la 21, y este año **bajaron** un 25 %. **Las dos comparaciones dicen cosas distintas.**

- Mirando **solo** el año pasado → pedirías **5 codillos**.
- Cruzando **las dos series** → el sistema propone **4**.

Eso es lo que hoy se hace a mano, pero **en dos segundos y sin depender de que alguien recuerde** cómo
fue la semana 21 del año pasado. Y con **cuatro** fines de semana en lugar de dos, la tendencia es
mucho más fiable.

> **Aviso de rigor:** los ratios salen de **dos puntos** cada serie. Con dos datos no hay tendencia,
> hay una resta. Cuando el sistema tenga los cuatro fines de semana y el año completo, el número será
> firme.

### Las observaciones del día: el dato sin contexto engaña

**Cada día de asador lleva una observación libre.** Porque **el número solo no explica nada**:

- **30 pollos en un pedido no es lo mismo que 30 pedidos de uno.** Un encargo grande —una celebración,
  un banquete— **no es demanda repetible**: no volverá a pasar porque pasó. Treinta clientes distintos,
  sí.
- **Una fiesta en un pueblo cercano** dispara la venta ese día, y **no tiene nada que ver con la
  tendencia**.

> **Y aquí está la consecuencia, que es la importante:** la observación **tiene que viajar con el
> número**, y aparecer **en el momento de calcular el pedido**. Si el sistema enseña «semana 20 del
> año pasado: 40 pollos» y se calla que ese día hubo fiestas en el pueblo, **el sistema propondrá
> pedir de más** — y encima con la autoridad de estar enseñando un dato.

**Ejemplo de lo que debe verse al calcular:**

| Referencia | Cantidad | Observación |
|---|---|---|
| Mismo finde del año pasado | **40 pollos** | ⚠️ *Fiestas del pueblo* |
| Finde anterior | 32 pollos | — |
| Hace 2 findes | 29 pollos | — |
| Hace 3 findes | 31 pollos | — |
| Hace 4 findes | 30 pollos | — |

Con la nota delante, quien decide ve que **los 40 están inflados por la fiesta** y ajusta. Sin la
nota, pide 40.

> **Y hay una segunda utilidad, que es la buena:** las fiestas locales **se repiten cada año**. Así que
> la observación de un día **no es un comentario del pasado: es un aviso para el año siguiente**. Si
> dentro de un año el sistema vuelve a enseñar ese fin de semana, **debe enseñar también la nota** —
> y si ese año la fiesta no cae igual, eso ya es información para decidir.

**[falta] ¿El día de asador se marca además como «festivo» o «fiesta local» de forma estructurada**, o
basta con la observación escrita? Con la nota libre se resuelve; marcarlo aparte permitiría **buscar
por tipo** («enséñame todos los días de fiesta local») y usarlo en el cálculo.

### De dónde salen los datos [NEGOCIO]

> **Ya existe una aplicación para llevar la venta del asador.** El dato **está registrado**, no hay
> que teclearlo desde cero.

**Y la propiedad plantea enlazar las dos aplicaciones.** Eso cambia el trabajo: la tarea de registrar
las ventas **podría desaparecer** y convertirse en una **importación automática**.

**[falta] Qué permite esa aplicación:** ¿tiene exportación (Excel, CSV), se puede conectar de alguna
forma, o solo se puede mirar en pantalla? De eso depende que el enlace sea automático, una importación
de fichero, o que siga habiendo que teclear.

> **Nota de arquitectura:** esto es exactamente para lo que se diseñó la aplicación **con módulos y
> adaptadores**. El asador es un caso más de *«un sistema externo que produce datos»* — igual que el
> TPV cuando se pueda exportar. **El núcleo no cambia**: se añade un adaptador que lee de fuera. Es la
> misma idea que se aplicó con `sale.completed`: el dato viene de donde venga, el resto del sistema no
> se entera.

### Lo que hace falta para que funcione

1. **El histórico de ventas por fin de semana, festivo y producto.** Está en **Excel** y en la
   aplicación del asador. **[falta] ver el formato** para planificar la importación.
2. **Alimentarlo cada semana**, automáticamente si se enlazan las dos aplicaciones.

### Principio de funcionamiento

**El sistema propone el número; la persona decide.** Es el mismo principio que en el motor de tareas:
el sistema aporta el dato, la responsabilidad de decidir sigue siendo de quien conoce la tienda.

---

## 2 · Pendiente de recoger

- **El histórico de ventas está en Excel** y la propiedad puede pasarlo.
  **[falta] Ver el formato** para planificar la importación.
- **[falta] Quién hace el pedido** — ya sé que es **los jueves a las 9:00** y por **WhatsApp**, pero
  no quién es la persona.
- **[falta] Cómo se gestiona hoy un pedido a proveedor** en general (no solo el del asador): qué se
  pide, cada cuánto, quién decide, y cómo se comprueba lo que llega.
