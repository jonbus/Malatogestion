# Gerencia

> **Es el puesto más grande de los tres**, y el que más cosas con fecha tiene. La propiedad lo irá
> completando *«según me vaya acordando»*.
>
> **Nota sobre los nombres.** En el dictado salen nombres de personas de fuera (el comercial, los dos
> de la asesoría). **Por la norma de este proyecto, aquí van por su papel, no por su nombre.**

---

## 0 · Cómo entra la gerencia (y por qué no es como los otros dos)

**Esto salió al preguntar si la gerencia debía tener «casilla de coordinadora», y descubre dos cosas.**

### 0.1 · Hoy la gerencia no puede entrar

El login tiene **Tienda** y **Coordinación**. **La gerencia no está.** No es que no pueda hacer de
coordinadora: **es que no está en la puerta.**

### 0.2 · Y no se arregla llamándola «Coordinadora 1»

> **«Coordinadora 1» no es un nombre: es una silla.** Y **la silla no se presta.**

Si la gerencia ocupa la casilla de la coordinadora:

- **Sus horas se apuntan a la coordinadora** y **desaparecen** de la relación que va a la asesoría
- Si ese día **trabajan las dos**, **son la misma persona** para la aplicación
- Y el informe de horas **es un documento laboral** — no es un sitio donde permitirse el lío

**La persona no cambia; el sombrero sí.** Son dos cosas distintas y hay que preguntarlas por separado:

```
¿Quién eres?      ->  no cambia nunca
¿Qué toca hoy?    ->  cambia según el día, y según la hora
```

### 0.3 · Y el sombrero es **por rato**, no por jornada

> *«No tiene por qué estar todo el día de coordinadora: entra un rato y después va a lo suyo.»*

Así que **no se elige un puesto para el día**. Se elige **qué se está haciendo en cada momento**.

### 0.4 · La consecuencia, y es la importante

**La gerencia no recorre una lista: elige.**

| Puesto | Cómo trabaja |
|---|---|
| **Tienda** | Tiene **un orden** que seguir: lo de siempre, lo de hoy, antes de irse |
| **Coordinación** | Tiene **un orden**: apertura, el día, cierre |
| **Gerencia** | Tiene **una bandeja**: bancos, caja, pedidos, precios, ofertas… **y elige por dónde empieza** |

> *«Me ha gustado entrar en gerencia y poder elegir la tarea.»*
>
> **Y es lógico:** la gerencia no tiene un turno con principio y final. Tiene cosas que hacer, con
> fechas detrás, y **las ordena según lo que aprieta**. Por eso **no le sirve la pantalla de las
> otras dos**: si le pusiéramos una lista en orden, le estaríamos imponiendo una jornada que no tiene.

**[falta]** Diseñar esa bandeja cuando se monte la pantalla.

---

## 1 · Lo que hay, de un vistazo

| Cuándo | Qué |
|---|---|
| **Lunes a viernes** | 5 tareas del día a día |
| **Los lunes** | **4 bloques de pedidos**, uno con hora límite |
| **Los martes** | Cerrar el pedido de planta · talones · papeles |
| **Cada mes, 4 ventanas** | Horas · asesoría fiscal · hipoteca · extracto bancario |
| **Cada 2 o 3 semanas** | La cadena de las ofertas |
| **Cuando no hay coordinadora** | La apertura, como coordinadora |

---

## 2 · El día a día (lunes a viernes)

| # | Tarea | |
|---|---|---|
| 1 | **Mirar los bancos** | |
| 2 | **Hacer la caja del día, o de días anteriores** | Se **acumula** — ver §6 |
| 3 | **Dar entrada a todo el género que llega** | |
| 4 | **Actualizar precios** | |
| 5 | **Sacar etiquetas de precios** | Por **género nuevo** o por **actualización** |

---

## 3 · Los lunes: los pedidos

**Son cuatro cosas, y una tiene hora.**

### 3.1 · Cofresa — **antes de las 11:00**

| # | Paso |
|---|---|
| 1 | **Preparar** el pedido |
| 2 | **Validar** el pedido |
| 3 | **Transmitir** el pedido, por **DiTrans** |

> **Es la única tarea de todo el proyecto con hora límite dentro del día.** Si se pasa de las 11:00,
> no hay pedido. **La aplicación tiene que avisar antes, no después.**

### 3.2 · Digasa, primera parte — contar y pedir al comercial

| # | Paso |
|---|---|
| 1 | **Contar**: leche · refrescos · cervezas |
| 2 | Con eso, **hacer el pedido al comercial** de Digasa **por WhatsApp** |

### 3.3 · La oferta manual del comercial

**El comercial manda todos los lunes la oferta manual.** Y hay tres pasos:

| # | Paso |
|---|---|
| 1 | **Estudiarla** |
| 2 | **Preparar el pedido** |
| 3 | **Hacer el pedido al comercial**, por WhatsApp |

### 3.4 · Digasa, segunda parte — el pedido de planta

| # | Paso | |
|---|---|---|
| 1 | **Mirar el stock del almacén** | |
| 2 | **Mirar el stock de la tienda** | |
| 3 | **Ir haciendo el pedido con la pistola** | |
| 4 | **Al terminar, validar en la pistola** | |
| 5 | **Cargarlo en el ordenador de la tienda**, en *«pedidos planta»* | |
| 6 | **Dejarlo pendiente hasta el martes** | **← aquí no acaba** |

---

## 4 · Los martes: cerrar lo del lunes

| # | Tarea |
|---|---|
| 1 | **Revisar el pedido de planta** |
| 2 | **Validarlo** |
| 3 | **Transmitirlo a la central**, por **DiTrans** |
| 4 | **Hacer los talones** |
| 5 | **Organizar los papeles** |

> **El pedido de planta es una cadena de dos días**, igual que las ofertas: **lo que se empieza el lunes
> no está terminado hasta que se transmite el martes.** Si el martes no se revisa, **el pedido se queda
> a medias y nadie lo sabe.**

---

## 5 · Lo mensual: cuatro ventanas

### 5.1 · Horas — entre los **2 últimos días del mes** y los **3 primeros** del siguiente

| | |
|---|---|
| **Qué** | Una **relación de horas de todos los trabajadores** |
| **Con qué detalle** | **Horas de domingo · horas de festivo · vacaciones** |
| **Cómo** | Se hace la relación *(hoy, en Excel)* y **se manda por correo al asesor laboral** |

> **Esto ya lo tenemos construido por otro lado.** El **resumen mensual del fichaje** que pediste
> (D-…): día, entrada, salida, total, **con domingos y festivos desglosados**. **Es lo mismo.**
> Cuando el fichaje funcione, **esta tarea se hace sola** — y ahí está el ahorro de verdad.

### 5.2 · Asesoría fiscal — en los **10 primeros días del mes**

| Qué se le pasa | |
|---|---|
| **Ventas totales del mes** | |
| **Comisión total mensual del datáfono del Sabadell** | |
| **Comisión total mensual del datáfono de la Caja Rural** | |
| **Recibo bancario de la mutua** *(el igualatorio de gerencia)* | |
| **Todas las comisiones que hayan cobrado los bancos** | Ver abajo |

**Las comisiones que hay que buscar, en los cuatro bancos:**

| Comisión | Nota |
|---|---|
| **Aval trimestral** | |
| **Mantenimiento de cuenta** | |
| **Descubierto** | |
| **Abono campaña TPV** | **Esta devuelve dinero** |

**Los bancos:** Caja Rural · Caja Laboral · Kutxabank · Sabadell.

### 5.3 · Hipoteca — **el día 17, como muy tarde**

| | |
|---|---|
| **Qué** | Una **transferencia** para pagar la hipoteca del día 18 |
| **Cuándo** | **El último día hábil antes del 17** |
| **Por qué** | *«Los sábados y domingos no son hábiles, con lo cual habría que hacerlo en viernes, no un día antes sino un día hábil antes»* |

> **La aplicación tiene que saber qué día es hábil.** No vale restar uno: si el 16 cae en domingo, la
> transferencia es el **viernes 14**.

### 5.4 · Extracto bancario — **entre el 20 y el 30, en martes o miércoles**

| # | Paso |
|---|---|
| 1 | **Sacar el extracto** desde una fecha **hasta** otra, en Excel |
| 2 | **Comprobar que todos los cargos e ingresos** corresponden a facturas o ventas |
| 3 | **Cotejar** los dos documentos |
| 4 | **Apuntar desde qué día hay que sacar el siguiente** |

> **Y aquí está lo bueno, y es idea tuya:** *«al sacarlo, apunto en el mes que viene desde qué día tengo
> que sacar el siguiente extracto»*. **El rango no empieza donde uno se acuerde: empieza donde acabó el
> anterior.**
>
> **La aplicación puede llevar esa cuenta sola.** Es exactamente el tipo de cosa que se olvida y que
> **deja un hueco en la contabilidad**.

---

## 6 · Lo que la aplicación tiene que saber calcular

| Cálculo | Por qué |
|---|---|
| **Días hábiles** | La hipoteca no se puede pagar en sábado |
| **El rango del extracto** | Empieza donde acabó el anterior |
| **La caja acumulada** | «3 cajas pendientes: viernes, sábado y domingo», **con fechas** |
| **Ventanas de mes** | Primeros 3 días · primeros 10 · del 20 al 30 · el 17 |

> **Cuatro cálculos, y los cuatro son de calendario.** Ninguno es de lógica de tienda.
> **Van juntos en un mismo sitio del sistema**, no repartidos.

---

## 7 · Una cosa que dices y que cambia el orden

> *«Todo esto intento hacerlo entre martes y miércoles, ya que son los días con menos trabajo en la
> tienda.»*

**Así que lo mensual no cae cuando el calendario dice, sino cuando hay hueco.** Las ventanas (10
primeros días, 20-30) son **plazos máximos**, no fechas de hacerlo.

**[falta] ¿Quieres que la aplicación te proponga hacerlo el martes o el miércoles**, dentro de cada
ventana? Porque es lo que haces de verdad.

> **Contestado: sí, y con aviso unos días antes.** *«Me gustaría que unos días antes me lo vaya
> recordando la aplicación.»*

---

## 8 · Lo que se parece a algo que ya tenemos

| Gerencia | Ya existe | ¿Qué relación? |
|---|---|---|
| **Dar entrada al género que llega** | Coordinación: **tickar los pedidos** | **[falta]** ¿Comprobar y meter son dos pasos, o el mismo? |
| **Actualizar precios** | Coordinación: **poner precios nuevos** | **[falta]** ¿Cadena? Gerencia actualiza → coordinación los pone |
| **Sacar etiquetas de precios** | Coordinación: **poner precios nuevos** | **Contestado: cadena.** Gerencia las saca, coordinación las coloca |
| **Hacer la caja** | Coordinación: **cerrar Caja 3** | **[falta]** ¿Cerrar el turno y hacer la caja son lo mismo? |
| **Los pedidos del lunes** | PEDIDOS: el del asador (jueves) | **Son el mismo módulo**: pedidos a proveedor |
| **La relación de horas** | **El fichaje** | **Es lo mismo** — y se hará sola |

---

## 9 · Preguntas

### 9.1 · Contestadas

| Pregunta | Respuesta |
|---|---|
| **¿Cuántas cajas un lunes normal?** | **Tres: viernes, sábado y domingo.** Si trabaja el domingo, hace la del sábado y la del domingo |
| **Si el 16 es festivo, ¿se adelanta la transferencia?** | **Sí: los festivos funcionan como domingos.** Día hábil = ni sábado, ni domingo, ni festivo |
| **El rango del extracto** | **Empieza el MISMO día en que se sacó el anterior**, no al siguiente: *«después de sacarlo podría tener más movimientos»* |
| **Las etiquetas: ¿las saca gerencia y las pone coordinación?** | **Sí.** Es una cadena |
| **Lo mensual: ¿te lo propongo el martes o el miércoles?** | **Sí, y con aviso unos días antes** |

### 9.2 · Siguen abiertas

1. **Los pedidos**: Cofresa y Digasa son **proveedores del módulo PEDIDOS**, no tareas sueltas.
   *«No lo sé, lo dejamos pendiente.»*
2. **«Dar de alta las ofertas o no»**: qué decide exactamente la gerencia ahí.
3. **Los pasos de «preparar las ofertas»**: tengo tres y creo que faltan.

---

## 10 · Estado del puesto

**Sigue sin pantalla**, y ahora da más pena: **este puesto ya tiene mucho contenido y nada que lo
enseñe.**

| | |
|---|---|
| **Tareas de día a día** | 5 |
| **Bloques de los lunes** | 4 |
| **Tareas de los martes** | 5 |
| **Ventanas mensuales** | 4 |
| **Cadena quincenal** | Las ofertas |

> **Con esto ya se puede montar la pantalla de gerencia.** Antes eran cuatro cosas; **ahora hay
> bastante más.** Pero lo dejo a tu criterio: **¿monto gerencia, o termino antes las de coordinación?**
